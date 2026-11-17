"""The stock card (with its barcode scanner) and the websocket commands it calls."""

from __future__ import annotations

import base64
import binascii
import logging
import uuid
from pathlib import Path

import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.loader import async_get_integration

from .const import CONF_AI, CONF_LOW, CONF_SPOOL, DOMAIN
from .logic import clean_code, find_barcode, item_facets, label_match, label_prompt

URL = f"/{DOMAIN}/panel.js"
CARD_URL = f"/{DOMAIN}/filament-stock-card.js"

_LOGGER = logging.getLogger(__name__)


async def async_setup_panel(hass: HomeAssistant) -> None:
    """Register the panel once; it stays until Home Assistant restarts."""
    if hass.data.get(DOMAIN):
        return
    hass.data[DOMAIN] = True
    here = Path(__file__).parent
    await hass.http.async_register_static_paths(
        [
            StaticPathConfig(URL, str(here / "panel.js"), False),
            StaticPathConfig(CARD_URL, str(here / "filament-stock-card.js"), False),
        ]
    )
    for command in (ws_scan, ws_assign, ws_undo, ws_recognize, ws_items, ws_set, ws_spool, ws_barcode, ws_sync, ws_merge, ws_brands):
        websocket_api.async_register_command(hass, command)
    version = (await async_get_integration(hass, DOMAIN)).version
    # No sidebar panel: the card has the scan button (panel.js is only a module it imports).
    await _register_card(hass, f"{CARD_URL}?v={version}")


async def _register_card(hass: HomeAssistant, url: str) -> None:
    """Load the card on dashboards without adding it to the resources by hand.

    A Lovelace resource, not extra_module_url: that one runs before the frontend sets up its
    scoped element registry and the card would not exist for it. YAML dashboards fall back to it.
    """
    try:
        lovelace = hass.data.get("lovelace")
        resources = getattr(lovelace, "resources", None)
        if resources is None and isinstance(lovelace, dict):
            resources = lovelace.get("resources")
        if resources is not None and hasattr(resources, "async_create_item"):
            if not getattr(resources, "loaded", True):
                await resources.async_load()
            for item in resources.async_items():
                if str(item.get("url", "")).split("?")[0] == CARD_URL:
                    if item["url"] != url:
                        await resources.async_update_item(item["id"], {"url": url})
                    return
            await resources.async_create_item({"res_type": "module", "url": url})
            return
    except Exception as err:  # noqa: BLE001 - YAML mode or a changed internal API
        _LOGGER.debug("Lovelace resource for the card: %s", err)
    add_extra_js_url(hass, url)


def _stocks(hass: HomeAssistant) -> list:
    return [e.runtime_data for e in hass.config_entries.async_entries(DOMAIN) if e.state is ConfigEntryState.LOADED]


def _added(stock, key: str, code: str) -> dict:
    return {
        "known": True,
        "code": code,
        "entry_id": stock.entry.entry_id,
        "key": key,
        "label": stock.label(key),
        "grams": stock.items[key],
        "added": stock.option(CONF_SPOOL),
    }


def _item(hass: HomeAssistant, connection, msg):
    """Stock holding the item named in the message; sends an error when there is none."""
    code = clean_code(msg["code"])
    for stock in _stocks(hass):
        if stock.entry.entry_id == msg["entry_id"] and msg["key"] in stock.items and code:
            return stock, code
    connection.send_error(msg["id"], websocket_api.ERR_NOT_FOUND, "Unknown item or empty code")
    return None, code


@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/scan", vol.Required("code"): str})
@callback
def ws_scan(hass: HomeAssistant, connection, msg) -> None:
    """Known barcode: add one spool. Unknown: return the items it can be assigned to."""
    code = clean_code(msg["code"])
    stocks = _stocks(hass)
    for stock in stocks:
        if key := find_barcode(stock.meta, code):
            stock.add_spool(key)
            connection.send_result(msg["id"], _added(stock, key, code))
            return
    items = [
        {
            "entry_id": stock.entry.entry_id,
            "key": key,
            **item_facets(key, stock.meta.get(key, {}), hass.config.language, stock.brands),
        }
        for stock in stocks
        for key in stock.items
    ]
    ai = any(stock.entry.options.get(CONF_AI) for stock in stocks)
    connection.send_result(msg["id"], {"known": False, "code": code, "items": items, "ai": ai})


MAX_IMAGE = 8_000_000


@websocket_api.websocket_command(
    {vol.Required("type"): f"{DOMAIN}/recognize", vol.Required("image"): str, vol.Optional("mime", default="image/jpeg"): str}
)
@websocket_api.async_response
async def ws_recognize(hass: HomeAssistant, connection, msg) -> None:
    """Photo of a label (base64): the AI task reads brand, material and colour and picks the item."""
    stocks = _stocks(hass)
    entity = next((s.entry.options[CONF_AI] for s in stocks if s.entry.options.get(CONF_AI)), None)
    if not entity:
        connection.send_error(msg["id"], websocket_api.ERR_NOT_SUPPORTED, "No AI task entity set in the options")
        return
    try:
        image = base64.b64decode(msg["image"], validate=True)
    except (binascii.Error, ValueError):
        image = b""
    if not image or len(image) > MAX_IMAGE or not msg["mime"].startswith("image/"):
        connection.send_error(msg["id"], websocket_api.ERR_INVALID_FORMAT, "Not an image or too large")
        return
    # ponytail: items of all printers in one list; the same key on two printers goes to the first
    owners = {}
    for stock in stocks:
        for key in stock.items:
            owners.setdefault(key, stock)
    # The AI task takes attachments from a media source: a temporary file in the local media folder.
    folder = Path(hass.config.media_dirs.get("local", hass.config.path("media"))) / DOMAIN
    name = f"{uuid.uuid4().hex}.{msg['mime'].split('/')[1].split('+')[0]}"

    def write() -> None:
        folder.mkdir(parents=True, exist_ok=True)
        (folder / name).write_bytes(image)

    await hass.async_add_executor_job(write)
    try:
        response = await hass.services.async_call(
            "ai_task",
            "generate_data",
            {
                "task_name": "Filament label",
                "entity_id": entity,
                "instructions": label_prompt({k: s.label(k) for k, s in owners.items()}, hass.config.language),
                "structure": {
                    "brand": {"required": True, "selector": {"text": {}}},
                    "material": {"required": True, "selector": {"text": {}}},
                    "color": {"required": True, "selector": {"text": {}}},
                    "key": {"required": True, "selector": {"select": {"options": [*owners, "none"]}}},
                },
                "attachments": [
                    {"media_content_id": f"media-source://media_source/local/{DOMAIN}/{name}", "media_content_type": msg["mime"]}
                ],
            },
            blocking=True,
            return_response=True,
        )
    except HomeAssistantError as err:
        connection.send_error(msg["id"], "ai_failed", str(err))
        return
    finally:
        await hass.async_add_executor_job((folder / name).unlink, True)
    data = (response or {}).get("data") or {}
    key = label_match(data, owners)
    connection.send_result(
        msg["id"],
        {
            **{f: str(data.get(f) or "") for f in ("brand", "material", "color")},
            "key": key,
            "entry_id": owners[key].entry.entry_id if key else None,
        },
    )


_ITEM = {vol.Required("entry_id"): str, vol.Required("key"): str, vol.Required("code"): str}


@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/assign", **_ITEM})
@callback
def ws_assign(hass: HomeAssistant, connection, msg) -> None:
    """Assign a barcode to an item and add one spool."""
    stock, code = _item(hass, connection, msg)
    if stock:
        stock.assign_barcode(msg["key"], code)
        stock.add_spool(msg["key"])
        connection.send_result(msg["id"], _added(stock, msg["key"], code))


@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/undo", **_ITEM})
@callback
def ws_undo(hass: HomeAssistant, connection, msg) -> None:
    """Take back a scan: remove the spool again. The barcode stays assigned (the card removes it)."""
    stock, code = _item(hass, connection, msg)
    if stock:
        stock.set(msg["key"], stock.items[msg["key"]] - stock.option(CONF_SPOOL))
        connection.send_result(msg["id"], {})


def _find(hass: HomeAssistant, connection, msg):
    """Stock holding the item named in the message; sends an error when there is none."""
    for stock in _stocks(hass):
        if stock.entry.entry_id == msg["entry_id"] and msg["key"] in stock.items:
            return stock
    connection.send_error(msg["id"], websocket_api.ERR_NOT_FOUND, "Unknown item")
    return None


_KEY = {vol.Required("entry_id"): str, vol.Required("key"): str}


@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/items"})
@callback
def ws_items(hass: HomeAssistant, connection, msg) -> None:
    """Every stock item with its brand, material, colour, grams and barcodes (for the card)."""
    stocks = _stocks(hass)
    items = []
    for stock in stocks:
        for key, grams in stock.items.items():
            meta = stock.meta.get(key, {})
            items.append(
                {
                    "entry_id": stock.entry.entry_id,
                    "key": key,
                    **item_facets(key, meta, hass.config.language, stock.brands),
                    "hex": meta.get("color"),
                    "grams": grams,
                    "low": grams < stock.option(CONF_LOW),
                    "spool": stock.option(CONF_SPOOL),
                    "barcodes": meta.get("barcodes", []),
                }
            )
    connection.send_result(msg["id"], {"items": items})


@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/set", **_KEY, vol.Required("grams"): vol.Coerce(float)})
@callback
def ws_set(hass: HomeAssistant, connection, msg) -> None:
    """Set the grams left of an item."""
    if stock := _find(hass, connection, msg):
        stock.set(msg["key"], msg["grams"])
        connection.send_result(msg["id"], {"grams": stock.items[msg["key"]]})


@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/spool", **_KEY})
@callback
def ws_spool(hass: HomeAssistant, connection, msg) -> None:
    """Add one full spool to an item."""
    if stock := _find(hass, connection, msg):
        stock.add_spool(msg["key"])
        connection.send_result(msg["id"], {"grams": stock.items[msg["key"]]})


@websocket_api.websocket_command(
    {vol.Required("type"): f"{DOMAIN}/barcode", **_KEY, vol.Required("code"): str, vol.Optional("remove", default=False): bool}
)
@callback
def ws_barcode(hass: HomeAssistant, connection, msg) -> None:
    """Link a barcode to an item (taken from any other item), or unlink it; no spool is added."""
    code = clean_code(msg["code"])
    if not code:
        connection.send_error(msg["id"], websocket_api.ERR_INVALID_FORMAT, "Empty code")
        return
    if stock := _find(hass, connection, msg):
        # A code belongs to one item in all printers, so it leaves the others first.
        for other in _stocks(hass):
            other.forget_barcode(code)
        if not msg["remove"]:
            stock.assign_barcode(msg["key"], code)
        connection.send_result(msg["id"], {"barcodes": stock.meta.get(msg["key"], {}).get("barcodes", [])})


@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/sync"})
@websocket_api.async_response
async def ws_sync(hass: HomeAssistant, connection, msg) -> None:
    """Read the profile list from ha-bambulab now (the card's reload button), not in 15 minutes."""
    total = {"profiles": 0, "new": 0, "changed": 0}
    for stock in _stocks(hass):
        result = await stock.async_sync_profiles()
        if result is None:
            connection.send_error(msg["id"], "sync_failed", "Profile list from ha-bambulab not available")
            return
        for k in total:
            total[k] += result[k]
    connection.send_result(msg["id"], total)


@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/merge", **_KEY, vol.Required("into"): str})
@websocket_api.async_response
async def ws_merge(hass: HomeAssistant, connection, msg) -> None:
    """Merge an item into another one of the same printer: grams and barcodes are added, prints count for the target."""
    stock = _find(hass, connection, msg)
    if stock is None:
        return
    if msg["into"] == msg["key"] or msg["into"] not in stock.items:
        connection.send_error(msg["id"], websocket_api.ERR_NOT_FOUND, "Unknown target item")
        return
    await stock.async_merge(msg["key"], msg["into"])
    connection.send_result(msg["id"], {"key": msg["into"], "grams": stock.items.get(msg["into"])})


@websocket_api.websocket_command(
    {vol.Required("type"): f"{DOMAIN}/brands", vol.Required("entry_id"): str, vol.Required("brands"): {str: str}}
)
@websocket_api.async_response
async def ws_brands(hass: HomeAssistant, connection, msg) -> None:
    """Set the brand map, e.g. {'Smart Print': 'PL/SM', 'Professional Lab': 'PL/SM'}."""
    for stock in _stocks(hass):
        if stock.entry.entry_id == msg["entry_id"]:
            await stock.async_set_brands(msg["brands"])
            connection.send_result(msg["id"], {"brands": stock.brands})
            return
    connection.send_error(msg["id"], websocket_api.ERR_NOT_FOUND, "Unknown entry")

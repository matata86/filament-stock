"""Pure deduction logic, no Home Assistant imports (see tests/test_logic.py)."""

from __future__ import annotations

PRINTING = {"prepare", "running", "pause"}
# States that say nothing about the job; a running job stays open across them.
NO_INFO = {None, "", "unknown", "unavailable", "offline"}


# What the printer tells about an item, as opposed to what the user adds (name, barcodes).
FACTS = ("profile", "brand", "material", "color")


def is_custom(key: str) -> bool:
    """True for the user's own slicer profile; built-in Bambu profile ids start with 'GF'."""
    return not key.upper().startswith("GF")


def hex_color(color: str | None) -> str | None:
    """'#898989FF' -> '898989'."""
    col = (color or "").strip().lstrip("#")[:6].upper()
    return col if len(col) == 6 else None


def item_key(filament_id: str | None, color: str | None) -> str | None:
    """Stock item id for what a slot reports.

    The user's own profile is one item ('P98f186c'): it stands for one brand, material
    and colour. A built-in profile is shared by many spools, so the colour is added
    ('GFG99_FFFFFF').
    """
    fid = (filament_id or "").strip()
    if not fid:
        return None
    if is_custom(fid):
        return fid
    col = hex_color(color)
    return f"{fid}_{col}" if col else None


def slot_item(attrs: dict, profiles: dict) -> tuple[str, dict] | None:
    """Stock item (key, facts) for the attributes of a spool slot; None when it holds nothing known.

    profiles maps a profile id to {'name', 'filament_vendor', 'filament_type'}.
    """
    if attrs.get("empty") or attrs.get("unknown"):
        return None
    fid = (attrs.get("filament_id") or "").strip()
    key = item_key(fid, attrs.get("color"))
    if not key:
        return None
    return key, profile_facts(profiles.get(fid, {}), attrs)


def profile_facts(profile: dict, attrs: dict | None = None) -> dict:
    """What is known about an item: profile name, brand, material and colour."""
    attrs = attrs or {}
    material = attrs.get("type") or profile.get("filament_type")
    name = attrs.get("name")
    facts = {
        # The slot reports the bare material as the name of a profile it does not know.
        "profile": profile.get("name") or (name if name != material else None),
        "brand": profile.get("filament_vendor"),
        "material": material,
        "color": hex_color(attrs.get("color")) or name_color(profile.get("name")),
    }
    return {k: v for k, v in facts.items() if v}


PALETTE = {
    "black": (0, 0, 0),
    "white": (255, 255, 255),
    "grey": (128, 128, 128),
    "red": (220, 30, 30),
    "orange": (255, 130, 0),
    "yellow": (250, 220, 0),
    "green": (40, 160, 60),
    "blue": (30, 90, 220),
    "purple": (130, 50, 180),
    "pink": (245, 120, 180),
    "brown": (120, 75, 40),
    "beige": (225, 205, 170),
}
COLOR_NAMES = {
    "cs": dict(zip(PALETTE, "černá bílá šedá červená oranžová žlutá zelená modrá fialová růžová hnědá béžová".split())),
}


def name_color(name: str | None) -> str | None:
    """Hex of a basic colour named in a profile name ('Smart Print PETG šedá' -> '808080').

    Words are compared without the last letter, so Czech endings match (černý, černá).
    """
    stems = {}
    for key in PALETTE:
        stems[key[:-1]] = key
        for names in COLOR_NAMES.values():
            stems[names[key][:-1]] = key
    stems["gra"] = "grey"
    for word in (name or "").lower().split():
        if key := stems.get(word[:-1]):
            return "".join(f"{c:02X}" for c in PALETTE[key])
    return None


def color_name(color: str) -> str:
    """Nearest basic colour name for a 6-digit hex colour."""
    rgb = [int(color[i : i + 2], 16) for i in (0, 2, 4)]
    # ponytail: plain RGB distance, switch to a perceptual space if names come out wrong
    return min(PALETTE, key=lambda n: sum((a - b) ** 2 for a, b in zip(rgb, PALETTE[n])))


def brand_of(meta: dict, brands: dict | None = None) -> str:
    """Brand shown for an item: the printer's vendor, renamed by the user's brand map ('Smart Print' -> 'PL/SM')."""
    vendor = meta.get("brand") or ""
    if not vendor:
        # The printer gave no vendor (a slot without a profile): take it from the profile name.
        vendor = next((v for v in brands or () if (meta.get("profile") or "").startswith(f"{v} ")), "")
    return (brands or {}).get(vendor, vendor)


def item_label(key: str, meta: dict, language: str = "en", brands: dict | None = None) -> str:
    """Human name of an item.

    The user's own profile goes by its name in the slicer ('Professional Lab PETG Red
    Matte'). Otherwise a name typed by the user, or the nearest basic colour added to the
    profile or material ('Generic PETG white' / 'Generic PETG bílá').
    """
    profile = meta.get("profile")
    if profile and is_custom(key):
        shown = brand_of(meta, brands)
        vendor = next((v for v in brands or () if profile.startswith(f"{v} ") and brands[v] == shown), "")
        if vendor and shown != vendor:
            return f"{shown}{profile[len(vendor):]}"
        return profile
    if meta.get("name"):
        return meta["name"]
    base = profile or meta.get("material") or key
    if not meta.get("color"):
        return base
    name = color_name(meta["color"])
    return f"{base} {COLOR_NAMES.get(language, {}).get(name, name)}"


def item_facets(key: str, meta: dict, language: str = "en", brands: dict | None = None) -> dict:
    """Brand, material and colour of an item, for picking it in three steps.

    The colour is whatever the label says after the brand and material
    ('Smart Print PETG šedá' -> 'šedá'), so it stays unique per item.
    """
    label = item_label(key, meta, language, brands)
    brand, material = brand_of(meta, brands), meta.get("material") or ""
    color = label
    for prefix in (f"{brand} {material} ", f"{meta.get('profile')} "):
        if label.startswith(prefix) and len(label) > len(prefix):
            color = label[len(prefix):]
            break
    else:
        # Typed name without a known brand ('Professional Lab PETG šedá'): split it at the material.
        before, found, after = label.partition(f" {material} ") if material else ("", "", "")
        if found and after:
            brand, color = brand or before, after
    # Shore hardness in the name ('TPU 95A černá') belongs to the material, the colour is the last word.
    hardness, _, rest = color.partition(" ")
    if rest and len(hardness) in (3, 4) and hardness[:-1].isdigit() and hardness[-1] in "AD":
        material, color = f"{material} {hardness}".strip(), rest
    return {"label": label, "brand": brand, "material": material, "color": color}


class JobTracker:
    """Follows one print job and returns grams used per stock item when it ends."""

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.active = False
        self.weights: dict[str, float] = {}  # slot name -> grams, from the printer integration
        self.total = 0.0
        self.slot_items: dict[str, str] = {}  # slot name -> item key, as seen during the job
        self.shares: dict[str, float] = {}  # item key -> progress points printed from it
        self.progress = 0.0
        self.last_item: str | None = None
        self.slot: str | None = None  # slot active right now
        self.backups: dict[str, list[str]] = {}  # planned slot -> slots that took over when it ran out

    def update(
        self,
        status: str | None,
        progress: float | None,
        total: float | None,
        weights: dict[str, float],
        slots: dict[str, tuple[str | None, bool]],
        stock: dict[str, float] | None = None,
    ) -> dict[str, float] | None:
        """Feed the current printer state.

        slots maps slot name ('AMS 1 Tray 2', 'External Spool') to (item key, is active).
        stock is the grams on stock per item; it tells how much a slot that ran out had left.
        Returns {item key: grams} once, when a job ends; otherwise None.
        """
        if status in PRINTING:
            if not self.active:
                self.reset()
                self.active = True
            self._observe(progress, total, weights, slots)
            return None
        if not self.active or status in NO_INFO:
            return None
        # Job ended. Final values may arrive together with the status change.
        if weights:
            self.weights = dict(weights)
        if total:
            self.total = total
        factor = 1.0 if status == "finish" else self.progress / 100
        usage = self._usage(factor, stock or {})
        self.reset()
        return usage

    def _observe(self, progress, total, weights, slots) -> None:
        current = slot = None
        for name, (item, is_active) in slots.items():
            if item:
                self.slot_items[name] = item
                if is_active:
                    current, slot = item, name
        if progress is not None:
            if progress < self.progress:
                # Progress left over from the previous job; start counting again.
                self.shares = {}
            elif current:
                self.shares[current] = self.shares.get(current, 0.0) + progress - self.progress
            self.progress = progress
        if current:
            self.last_item = current
        if weights:
            self.weights = dict(weights)
        if total:
            self.total = total
        if slot and slot != self.slot:
            # The job moved to a slot the slicer planned nothing for: AMS auto refill took over
            # from a slot that ran out. Chained refills are kept in order under the planned slot.
            origin = self.slot if self.slot in self.weights else next(
                (planned for planned, chain in self.backups.items() if self.slot in chain), None
            )
            if origin and slot not in self.weights and slot not in self.backups.get(origin, ()):
                self.backups.setdefault(origin, []).append(slot)
            self.slot = slot

    def _usage(self, factor: float, stock: dict[str, float]) -> dict[str, float]:
        out: dict[str, float] = {}
        for slot, grams in self.weights.items():
            item = self.slot_items.get(slot)
            if not item:
                continue
            chain = [item, *(self.slot_items[b] for b in self.backups.get(slot, ()) if b in self.slot_items)]
            left = grams * factor
            for spent in chain[:-1]:
                # A slot that ran out used up what the stock said it held; the next one printed the rest.
                used = min(left, max(stock.get(spent, 0.0), 0.0))
                out[spent] = out.get(spent, 0.0) + used
                left -= used
            out[chain[-1]] = out.get(chain[-1], 0.0) + left
        if not out and self.total > 0:
            # No per-slot data (e.g. print started from the touchscreen):
            # split the total by how much progress each spool was active for.
            share_sum = sum(self.shares.values())
            if share_sum > 0:
                out = {i: self.total * factor * s / share_sum for i, s in self.shares.items()}
            elif self.last_item:
                out = {self.last_item: self.total * factor}
        return {i: round(g, 1) for i, g in out.items() if g > 0}


def loaded_grams(slot_items: dict[str, str | None], stock: dict[str, float], spool: float) -> dict[str, float]:
    """Grams on the spool in each slot, when the stock of an item is whole spools plus one opened spool.

    The opened spool is the remainder of the stock ('3092 g' with 1000 g spools -> 92 g).
    When one item is in several slots, the first slot (by name) holds the opened spool
    and the others a full one each, as long as the stock lasts.
    """
    out: dict[str, float] = {}
    left: dict[str, float] = {}
    for slot in sorted(slot_items):
        item = slot_items[slot]
        if not item:
            continue
        if item in left:
            grams = min(spool, left[item])
        else:
            total = max(stock.get(item, 0.0), 0.0)
            grams = total % spool if spool > 0 else total
            if total > 0 and grams < 1:
                # Whole spools only: the one in the slot is full.
                grams = min(total, spool) if spool > 0 else total
            left[item] = total
        left[item] -= grams
        out[slot] = round(grams, 1)
    return out


def shortages(
    weights: dict[str, float],
    slot_items: dict[str, str | None],
    loaded: dict[str, float],
    factor: float = 1.0,
) -> dict[str, tuple[float, float]]:
    """Items the job needs more of than the slots hold: {item key: (grams needed, grams loaded)}.

    weights are the slicer grams of the whole job per slot, factor adds the waste. The stock is
    deducted only when the job ends, so the whole job is compared at any progress. A slot the
    job does not use but that holds the same item counts too: AMS auto refill continues from it.
    """
    need: dict[str, float] = {}
    for slot, grams in weights.items():
        if item := slot_items.get(slot):
            need[item] = need.get(item, 0.0) + grams * factor
    have: dict[str, float] = {}
    for slot, item in slot_items.items():
        if item in need:
            have[item] = have.get(item, 0.0) + loaded.get(slot, 0.0)
    return {i: (round(n, 1), round(have.get(i, 0.0), 1)) for i, n in need.items() if n > have.get(i, 0.0)}


def merge_plan(items: dict, meta: dict, source: str, target: str) -> tuple[float, list]:
    """Grams and barcodes the target item holds after absorbing the source item."""
    codes = [*meta.get(target, {}).get("barcodes", [])]
    codes += [c for c in meta.get(source, {}).get("barcodes", []) if c not in codes]
    return round(items.get(target, 0.0) + items.get(source, 0.0), 1), codes


def clean_code(code) -> str:
    """Barcode as scanned or typed, without whitespace."""
    return "".join(str(code or "").split())


def find_barcode(meta: dict, code: str) -> str | None:
    """Key of the item the barcode is assigned to."""
    return next((key for key, m in meta.items() if code and code in m.get("barcodes", ())), None)


LABEL_LANGUAGES = {"cs": "Czech", "en": "English"}


def label_prompt(items: dict[str, str], language: str = "en") -> str:
    """Instructions for an AI task that reads a filament label photo and picks the stock item."""
    lines = "\n".join(f"- {key}: {label}" for key, label in items.items())
    return (
        "The photo shows the label of a 3D printer filament spool or its box. Read the brand, "
        "the material (PLA, PETG, TPU, ABS, ASA...) and the colour, the colour name in "
        f"{LABEL_LANGUAGES.get(language, 'English')}. Then pick the stock item with the same brand, "
        "material and colour from this list (key: name), or 'none' when no item matches:\n" + lines
    )


def label_match(data, keys) -> str | None:
    """The stock item key the AI picked, only when it is one of ours."""
    key = data.get("key") if isinstance(data, dict) else None
    return key if key in keys else None

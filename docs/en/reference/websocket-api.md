# Websocket API

The integration registers these Home Assistant websocket commands. They are what the card and the scanner use, and you can use them from scripts or from the developer tools of your browser. None of them is restricted to admins: any logged-in user can call them.

Every command follows the usual websocket convention: send `{"id": <n>, "type": "...", ...}`, receive `{"id": <n>, "type": "result", "success": true, "result": ...}` or `"success": false` with an `error` object.

An item is identified by `entry_id` (the config entry of the printer) and `key` (the item key, see [Storage format](storage.md#item-keys)). Both come from `filament_stock/items`.

## filament_stock/items

Every stock item of every loaded printer. Used by the card.

```json
{"id": 1, "type": "filament_stock/items"}
```

```json
{"id": 1, "type": "result", "success": true, "result": {"items": [
  {"entry_id": "01J...", "key": "GFG99_FFFFFF", "label": "Generic PETG white",
   "brand": "Generic", "material": "PETG", "color": "white", "hex": "FFFFFF",
   "grams": 1234.0, "low": false, "spool": 1000.0, "barcodes": ["8590000000000"]}
]}}
```

`hex` is the colour from the slot (without `#`, or `null`), `low` is true below the low stock threshold, `spool` is the option "Weight of a new spool".

## filament_stock/set

`{entry_id, key, grams}` sets the grams of an item (not below 0, rounded to 0.1). Returns `{"grams": <value>}`. Error `not_found` for an unknown item.

## filament_stock/spool

`{entry_id, key}` adds one spool (the option "Weight of a new spool"). Returns `{"grams": <value>}`. Error `not_found` for an unknown item.

## filament_stock/barcode

`{entry_id, key, code, remove?}` links a barcode to an item. The code is first taken away from every item of every printer (a code belongs to one item). With `"remove": true` it is only removed. No spool is added. Returns `{"barcodes": [...]}` of the item. Errors: `invalid_format` for an empty code, `not_found` for an unknown item.

## filament_stock/scan

`{code}` handles a scanned code. A known code adds one spool and returns

```json
{"known": true, "code": "8590000000000", "entry_id": "01J...", "key": "GFG99_FFFFFF",
 "label": "Generic PETG white", "grams": 2234.0, "added": 1000.0}
```

An unknown code returns the items it can be assigned to and whether an AI Task entity is set:

```json
{"known": false, "code": "8590000000000", "ai": true,
 "items": [{"entry_id": "01J...", "key": "GFG99_FFFFFF", "label": "Generic PETG white",
            "brand": "Generic", "material": "PETG", "color": "white"}]}
```

## filament_stock/assign

`{entry_id, key, code}` links a barcode to an item and adds one spool. Returns the same object as a known `scan`. Error `not_found` for an unknown item or an empty code.

## filament_stock/undo

`{entry_id, key, code}` takes one spool off again. The barcode stays linked. Returns `{}`. Error `not_found` for an unknown item or an empty code.

## filament_stock/recognize

`{image, mime?}` reads a label photo through the AI Task entity from the options. `image` is base64 (up to 8 MB), `mime` defaults to `image/jpeg` and must start with `image/`. The image is saved temporarily in `/media/filament_stock/`, passed to `ai_task.generate_data` and deleted afterwards.

```json
{"brand": "Smart Print", "material": "PETG", "color": "grey", "key": "P1234567", "entry_id": "01J..."}
```

`key` and `entry_id` are `null` when the AI found no matching item (a key that is not in your stock is discarded). Errors: `not_supported` when no AI Task entity is set, `invalid_format` for a bad or too large image, `ai_failed` when the AI Task call fails.

## filament_stock/sync

No parameters. Reads your own profiles from Bambu Cloud now, for every loaded printer. Returns the sums:

```json
{"profiles": 20, "new": 0, "changed": 0}
```

Error `sync_failed` when ha-bambulab does not provide the profile list.

## filament_stock/merge

`{entry_id, key, into}` merges item `key` into item `into` of the same printer: the grams and barcodes are added up, the merged profile counts as the target from then on (a print with it deducts from the target) and the merged item and its entities disappear. Returns `{"key": <into>, "grams": <value>}`. Error `not_found` for an unknown item or target (or when both are the same). The integration reloads. There is no screen for it in the card; it is used through the API.

## filament_stock/brands

`{entry_id, brands}` sets a map of brand names shown instead of the vendor reported by the printer, for example `{"Smart Print": "PL/SM"}`. Returns `{"brands": {...}}`; the integration reloads to apply the new names. Error `not_found` for an unknown entry. There is no screen for it in the card; it is used through the API.

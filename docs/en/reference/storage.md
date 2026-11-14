# Storage format

The stock of each printer is kept in `/config/.storage/filament_stock.<entry_id>`, a JSON file written by Home Assistant (saved a few seconds after a change). Do not edit it while Home Assistant runs.

```json
{
  "schema": 2,
  "items": {"GFG99_FFFFFF": 1234.0, "P1234567": 0.0},
  "meta": {
    "GFG99_FFFFFF": {
      "profile": "Generic PETG",
      "brand": "Generic",
      "material": "PETG",
      "color": "FFFFFF",
      "name": "my own name",
      "barcodes": ["8590000000000"]
    }
  },
  "brands": {"Smart Print": "PL/SM"},
  "aliases": {"P7654321": "P1234567"}
}
```

| Key | Content |
|-----|---------|
| `schema` | Layout version, currently `2` |
| `items` | Item key to grams in stock |
| `meta` | Item key to the facts about the item |
| `brands` | Brand map: vendor from the printer to the brand shown (set by `filament_stock/brands`) |
| `aliases` | Merged item key to the item that holds its grams (set by `filament_stock/merge`) |

## Item keys { #item-keys }

- A built-in profile (id starts with `GF`): `filament_id` and the hex colour of the slot, for example `GFG99_FFFFFF`.
- Your own profile: just the `filament_id`, for example `P1234567`.

## meta

`profile`, `brand`, `material` and `color` are written by what the printer reports and are overwritten by it. `name` (your own name) and `barcodes` come from Home Assistant. `color` is a hex colour without `#`.

## Older data

Data without `"schema": 2` (versions up to 0.4.1, items by material and colour) cannot be converted. It is discarded when loaded, together with its entities, and the stock starts again from the profiles.

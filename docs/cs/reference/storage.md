# Formát úložiště

Sklad každé tiskárny je v `/config/.storage/filament_stock.<entry_id>`, což je JSON soubor, který zapisuje Home Assistant (uloží se pár sekund po změně). Neupravuj ho, když Home Assistant běží.

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
      "name": "vlastní název",
      "barcodes": ["8590000000000"]
    }
  },
  "brands": {"Smart Print": "PL/SM"},
  "aliases": {"P7654321": "P1234567"}
}
```

| Klíč | Obsah |
|------|-------|
| `schema` | Verze rozložení, nyní `2` |
| `items` | Klíč položky na gramy na skladě |
| `meta` | Klíč položky na údaje o položce |
| `brands` | Mapa značek: výrobce z tiskárny na zobrazenou značku (nastavuje `filament_stock/brands`) |
| `aliases` | Klíč sloučené položky na položku, která drží její gramy (nastavuje `filament_stock/merge`) |

## Klíče položek { #item-keys }

- Vestavěný profil (id začíná `GF`): `filament_id` a hex barvy ze slotu, například `GFG99_FFFFFF`.
- Vlastní profil: jen `filament_id`, například `P1234567`.

## meta

`profile`, `brand`, `material` a `color` zapisuje to, co hlásí tiskárna, a tiskárna je i přepisuje. `name` (vlastní název) a `barcodes` jsou z Home Assistantu. `color` je hex barva bez `#`.

## Starší data

Data bez `"schema": 2` (verze do 0.4.1, položky podle materiálu a barvy) nejde převést. Při načtení se zahodí i s entitami a sklad začne znovu z profilů.

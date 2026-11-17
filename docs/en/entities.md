# Entities and options

## Entities

Per stock item, on the device `Filament <printer name>`:

| Entity | Description |
|--------|-------------|
| `number.<device>_<filament>` | Grams in stock, editable (0 to 100000). Attributes: `profile`, `filament_id`, `material`, `brand`, `color`, `barcodes`, `spools` (grams divided by the spool weight) |
| `button.<device>_<filament>_add_spool` | Adds the weight of a new spool |
| `binary_sensor.<device>_<filament>_low` | On when the stock is below the low stock threshold (device class problem) |

One per integration:

| Entity | Description |
|--------|-------------|
| `button.<device>_reload_profiles` | Reads the profile list from ha-bambulab now (entity category Configuration; `sync_with_bambu` when installed before 0.7.2) |

The exact ids depend on the name of the device and of the filament; they are made when the item is created and then stay.

## Options

**Settings, Devices & services, Filament Stock, Configure**, entry **Settings**:

| Option | Default | Description |
|--------|---------|-------------|
| Extra for waste (purge, failed starts) | 5 % | Added on top of every deduction |
| Low stock threshold | 300 g | Below this a filament counts as running low |
| Weight of a new spool | 1000 g | Added by "add spool" and by a scan |
| AI to read the label (unknown barcode) | none | An `ai_task` entity that accepts images; without it the photo button is not shown |

The other two entries of the menu are **Rename filament** and **Remove filament**, see [Bambu profiles](profiles.md#rename-and-remove).

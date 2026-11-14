# Dashboard card

## Add the card

The integration registers the card at start, no resource to add by hand. In the dashboard editor pick **Filament Stock** from the card list, or use YAML:

```yaml
type: custom:filament-stock-card
title: Filament
show_header: true
show_empty: false
```

| Option | Default | Description |
|--------|---------|-------------|
| `title` | `Filament` | Heading of the card |
| `show_header` | `true` | `false` hides the heading |
| `show_empty` | `false` | `true` shows filaments with 0 g from the start |

## The list

- **Search filament** finds by name, brand, material and colour.
- The filters **Brand**, **Material** and **Colour** each offer only the values that are left after the other filters and the search.
- Each row shows the colour dot, the name, brand and material, and the grams. A filament below the low stock threshold is orange.
- Filaments with 0 g are hidden. **Show empty (N)** shows them, **Hide empty** hides them again.
- Above the list is the total of what the search and filters leave, for example "11 of 21 · 20 kg".

The card shows grams, not a spool count: the integration keeps only grams per filament, and grams divided by a spool size would mislead when two spools are started.

## Buttons

- **Scan barcode** opens the scanner in a dialog, see [Barcodes and labels](barcodes.md).
- The sync icon (tooltip "Load profiles from Bambu Cloud") reads your profiles from Bambu Cloud now. The icon spins while it runs; the result comes as a toast, for example "Profiles loaded: 20 own, 0 new, 0 changed."

## Filament dialog

Click a filament to open its dialog:

- **Grams left** with **Save** sets the stock to the number you type, for example after weighing the spool.
- **Add a full spool (+1,000 g)** adds the weight of a new spool (the option "Weight of a new spool").
- **Barcodes** lists the codes linked to this filament. The pencil edits a code (the new one is linked, the old one removed), the cross removes it.
- **Scan barcode** (camera or app scanner) or typing a code into **Barcode** with **Link** links a new code. A code belongs to one filament: linking it here takes it from any other.
- A "Running low" mark appears next to the grams when the stock is under the threshold.

The card reloads its data when a stock entity changes and after every action.

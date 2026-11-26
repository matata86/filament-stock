<p align="center"><img src="https://raw.githubusercontent.com/matata86/filament-stock/master/custom_components/filament_stock/brand/icon.png" alt="Filament Stock logo" width="96"></p>

# Filament Stock

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz)
[![GitHub release](https://img.shields.io/github/v/release/matata86/filament-stock)](https://github.com/matata86/filament-stock/releases)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/matata86/filament-stock/blob/master/LICENSE)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2025.1%2B-blue.svg)](https://www.home-assistant.io)
[![Ko-fi](https://img.shields.io/badge/Ko--fi-support-ff5e5b?logo=ko-fi&logoColor=white)](https://ko-fi.com/matata86)
[![PayPal](https://img.shields.io/badge/PayPal-donate-00457C?logo=paypal&logoColor=white)](https://paypal.me/matata86)
[![Bitcoin](https://img.shields.io/badge/Bitcoin-donate-F7931A?logo=bitcoin&logoColor=white)](#support)

[![Open your Home Assistant instance and open the repository inside HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=matata86&repository=filament-stock&category=integration)
[![Open your Home Assistant instance and start setting up Filament Stock](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=filament_stock)

A filament stock in grams for Bambu Lab printers in Home Assistant. After every print it reads what each slot used from the community integration [ha-bambulab](https://github.com/greghesp/ha-bambulab) and deducts it from the right filament. The stock items come from your Bambu filament profiles, so there is nothing to create in Home Assistant. Scan the barcode on a box to add a spool, optionally let an AI Task entity read a spool label, and keep an eye on everything in a dashboard card.

**Documentation:** [English](https://matata86.github.io/filament-stock/) | [Česky](https://matata86.github.io/filament-stock/cs/)

## Features

- One stock item per Bambu filament profile: your own profile is one item, a built-in profile is split by colour. Nothing to set up by hand.
- Deduction per slot after every print, with a fallback by print progress when the per-slot weights are missing (for example a print started from the printer display).
- Extra for waste, added to every deduction (default 5 %).
- Grams on the spool in each AMS slot, and a check when a print starts: a notification and an event when the filament in the AMS will not last, also for multicolour prints.
- Low stock: a notification and a `binary_sensor` per filament when it drops below a threshold.
- Dashboard card with search, Brand / Material / Colour filters, a total, and a dialog per filament (set the grams, add a full spool, manage barcodes).
- Barcode scanning to add a spool: the Home Assistant app scanner, the browser camera, or typing the code (works with a USB reader too). Numeric EAN / GTIN codes are checked, so a misread is rejected.
- An unknown code is assigned once with three picks (Brand, Material, Colour); next time it is recognised. Optionally photograph the label and let an AI Task entity suggest the filament.
- Your profiles come from the public `bambu_lab.get_filament_data` service of ha-bambulab: read at start, every 15 minutes and with a button.
- English and Czech.

## Requirements

- Home Assistant 2025.1.0 or newer.
- [ha-bambulab](https://github.com/greghesp/ha-bambulab) set up with your Bambu account (cloud mode).
- A Bambu Lab printer. Tested with a P2S and an AMS 2 Pro; other models are not verified.
- Own filament profiles must be created in Bambu Studio with **Create Filament**, not **Save as**: a profile saved with Save as keeps the id of its Generic base profile and cannot be told apart from Generic in a slot.

## Installation

HACS:

1. In HACS open the three-dot menu, **Custom repositories**, add `https://github.com/matata86/filament-stock` with category **Integration**.
2. Find **Filament Stock** and **Download** it.
3. Restart Home Assistant.

Manually: copy `custom_components/filament_stock` into `/config/custom_components/` and restart Home Assistant.

Then go to **Settings, Devices & services, Add integration, Filament Stock** and pick the printer. Details: [Installation](https://matata86.github.io/filament-stock/installation/).

## Dashboard card

The integration registers the card by itself. Add it to a dashboard:

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
| `show_empty` | `false` | `true` shows filaments with 0 g from the start (the card also has a toggle) |

More: [Dashboard card](https://matata86.github.io/filament-stock/card/).

## Entities

Per stock item, on the device `Filament <printer name>`:

| Entity | Description |
|--------|-------------|
| `number.<device>_<filament>` | Grams in stock, editable. Attributes: `profile`, `filament_id`, `material`, `brand`, `color`, `barcodes`, `spools` |
| `button.<device>_<filament>_add_spool` | Adds the weight of a new spool |
| `binary_sensor.<device>_<filament>_low` | On when the stock is below the low stock threshold |

One per spool slot (each AMS slot and the external spool):

| Entity | Description |
|--------|-------------|
| `sensor.<device>_<slot>` | Grams on the spool in the slot: the stock left after whole spools. Attributes: `item`, `label`, `stock` |

One per integration:

| Entity | Description |
|--------|-------------|
| `button.<device>_reload_profiles` | Reads the profile list from ha-bambulab now |

## Options

**Settings, Devices & services, Filament Stock, Configure.**

| Option | Default | Description |
|--------|---------|-------------|
| Extra for waste (purge, failed starts) | 5 % | Added on top of every deduction |
| Low stock threshold | 300 g | Below this a filament counts as running low |
| Weight of a new spool | 1000 g | Added by "add spool" and by a scan |
| AI to read the label (unknown barcode) | none | An `ai_task` entity that accepts images; without it the photo button is not shown |

The menu also has **Rename filament** (only the name shown in Home Assistant, empty goes back to the Bambu name) and **Remove filament** (deletes the item and its entities).

## How deduction works

- A print is followed from `prepare` / `running` / `pause` until it ends.
- Main path: the grams per slot from the attributes of the printer's `print_weight` sensor, assigned to the filament that was in each slot during the print.
- AMS auto refill: when the job switches to a slot the slicer planned nothing for, the slot that ran out is deducted what the stock had left for it, the backup slot the rest.
- Fallback (a print without a cloud job, for example from the display): the total weight is split by how much of the progress each slot was active.
- `finish` deducts 100 %; any other end (`failed`, `idle`) deducts the share reached by the progress.
- The extra for waste is added to the deduction.
- At print start the job is compared with the spools in the AMS (the opened spool is assumed to be the loaded one); when a filament falls short, a notification and the event `filament_stock_shortage` (for a phone push via an automation).

Details: [How deduction works](https://matata86.github.io/filament-stock/deduction/).

## Known limitations

- The grams in a slot are a guess: the stock does not know which spool is loaded. It assumes the opened spool (stock modulo the spool weight) is in the AMS.
- An unfinished print is not stored: restarting Home Assistant during a print loses the progress fallback (the per-slot weights still work).
- A built-in profile is split by the exact hex colour: a different shade in a slot is a new item.
- Own profiles saved with **Save as** share the id of the built-in profile, are not listed by ha-bambulab and are not recognised in a slot.
- Two shades with the same nearest basic colour get the same name and differ only by the colour dot.
- Whether the weight from the cloud includes purge and the prime tower is not verified, hence the extra for waste.
- The AMS HT slot name (`AMS HT n`) comes from the ha-bambulab source and is not verified on a device.
- ha-bambulab fetches your profiles from Bambu Cloud only when it connects. A profile created later shows up after ha-bambulab reconnects or is reloaded.
- The app scanner uses an internal API of the Home Assistant frontend; a Home Assistant update may break it (the browser camera and typing the code keep working).

## Support

Questions, bugs and feature requests: [GitHub issues](https://github.com/matata86/filament-stock/issues). The [FAQ](https://matata86.github.io/filament-stock/faq/) covers the common problems.

If Filament Stock saves you time, you can support its development:

- **Ko-fi:** https://ko-fi.com/matata86
- **PayPal:** https://paypal.me/matata86
- **Bitcoin:** `bc1qhjwt8xxmuym0xsd50yfpvjph00386uz73gqwlc` ([QR code](https://matata86.github.io/filament-stock/support/))

## License

[MIT](https://github.com/matata86/filament-stock/blob/master/LICENSE)

# Filament Stock

Filament Stock keeps your filament stock in grams in Home Assistant, for Bambu Lab printers. After every print it reads what each slot used from the community integration [ha-bambulab](https://github.com/greghesp/ha-bambulab) and deducts it from the right filament.

The stock items come from your Bambu filament profiles, so there is nothing to create in Home Assistant. In Home Assistant you only add a barcode and a quantity in grams to what Bambu already knows.

It is for you if you print with an AMS, own several spools of different brands and want to know what is left without weighing every spool.

What you get:

- A stock item per Bambu filament profile, with the grams left, an "add spool" button and a "running low" sensor.
- Automatic deduction after every print, with an extra for waste.
- A [dashboard card](card.md) with search, filters and a dialog per filament.
- [Barcode scanning](barcodes.md) to add a spool, optionally with a photo of the label read by an AI Task entity.

Start with the [installation](installation.md), then read how the items come from [Bambu profiles](profiles.md).

!!! example "Like Filament Stock?"
    Support it on [Ko-fi](https://ko-fi.com/matata86), with [PayPal](https://paypal.me/matata86) or with [Bitcoin](support.md).

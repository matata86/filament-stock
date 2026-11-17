# FAQ

## A filament does not show up

- It was saved in Bambu Studio with **Save as**. Such a profile has the id of its Generic base and cannot be recognised. Create it again with **Create Filament**, see [Bambu profiles](profiles.md#create-filament-not-save-as).
- It is only in an empty or unknown slot: a slot without a profile is skipped.
- It is a new profile: ha-bambulab has not loaded it yet. To see a new profile right away, reload the Bambu Lab integration (**Settings → Devices & services → Bambu Lab → ⋮ → Reload**) and then press **Reload profiles**.
- It has 0 g: the card hides empty filaments, use **Show empty**.

## The card is the old version after an update

The browser (or the Home Assistant app) caches the card file. Reload the page with the cache cleared, in the app clear the app cache. The address of the file changes with the version after a Home Assistant restart.

## The camera does not work

The browser camera needs a page opened over **HTTPS**. Use the Home Assistant app (its own scanner), open Home Assistant over HTTPS, or type the code into the **Barcode** field (a USB reader works too). See [Barcodes and labels](barcodes.md).

## Why did restarting Home Assistant during a print lose grams?

An unfinished print is not stored. The per-slot weights from ha-bambulab still work, but the fallback by progress is lost for that print. Avoid restarting during a print.

## A different shade of the same colour became a new item

A built-in profile is split by its exact colour: a different shade in the slot is another item. Remove the one you do not need, or use your own profile (one item whatever the colour in the slot).

## Two filaments have the same name

Two shades with the same nearest basic colour get the same name and differ only by the colour dot. Rename one with **Rename filament**.

## Is purge included in the deducted weight?

It is not verified whether the weight from the cloud contains purge and the prime tower. The **Extra for waste** option covers it; weigh a spool before and after a few prints to find your value.

## Does it work with AMS HT?

The name of its slot (`AMS HT n`) comes from the ha-bambulab source and is not verified on a device.

## Will the app scanner keep working after a Home Assistant update?

The app scanner is called through an internal API of the Home Assistant frontend, not a public one. An update may break it. The browser camera and typing the code keep working.

## Which printers work?

Tested with a Bambu Lab P2S and an AMS 2 Pro in cloud mode. Other models that ha-bambulab supports are not verified.

Not solved? Open an [issue on GitHub](https://github.com/matata86/filament-stock/issues).

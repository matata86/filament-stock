# Bambu profiles

## One item per profile

A stock item is a filament profile from Bambu, identified by its `filament_id`:

- **Your own profile** is one item (for example "Professional Lab PETG Red Matte"). One profile is one brand, material and colour.
- **A built-in profile** (the Bambu and Generic ones, id starts with `GF`) is split by colour: a Generic PETG with a white spool and one with a black spool are two items.

You do not add filaments in Home Assistant. Items appear on their own:

- As soon as a slot reports a profile the stock does not know yet, an item with 0 g is created. An empty or unknown slot is skipped.
- Your own profiles are read from Bambu Cloud (through ha-bambulab) and each one becomes an item, even when it is not in the AMS.

## Create Filament, not Save as

A custom profile needs its own `filament_id`. In Bambu Studio create it with **Create Filament**; it gets an id starting with `P`.

A profile saved with **Save as** from a Generic profile inherits the id of its base (for example `GFG99` or `GFU99`). ha-bambulab does not list it and a slot cannot tell it from Generic, so it never becomes an item of its own.

## Synchronisation

Your own profiles are read again:

- when Home Assistant starts,
- every 15 minutes,
- when you press the **Sync with Bambu** button (the integration has one), or the sync icon next to **Scan barcode** in the [card](card.md).

New profiles become items, changed names are updated. A name from Bambu always wins over a name you typed.

## Names and colours

The name of a custom profile comes from Bambu. For other items the name is the profile (or material) plus the nearest of 12 basic colours, for example "Generic PETG white". The colour dot comes from the last colour seen in a slot; until then it is guessed from the profile name.

Entity ids are made from the name when the item is created and do not change afterwards. When a name or colour from Bambu changes, the integration reloads itself to apply it.

## Rename and remove

**Settings, Devices & services, Filament Stock, Configure:**

- **Rename filament** changes only the name shown in Home Assistant, as a fallback when Bambu does not send one. Leave the field empty to go back to the Bambu name.
- **Remove filament** deletes the item and its entities. If the filament is still in a slot, it is created again with 0 g.

Deleting a profile in Bambu does not delete the stock item (it holds your stock), remove it by hand.

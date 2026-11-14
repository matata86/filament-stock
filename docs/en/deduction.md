# How deduction works

## Following a print

A print is followed from the printer states `prepare` / `running` / `pause` until it ends. The integration watches the printer sensors of ha-bambulab: `print_status`, `print_progress` and `print_weight`.

## Grams per slot

The main source is the `print_weight` sensor of the printer. Its attributes hold the grams per slot, for example `AMS 1 Tray 2: 12.5` or `External Spool: 4.8`. Each slot is turned into a stock item by what was in it during the print, so a multi-colour print deducts from every spool used.

## Fallback by progress

A print without a cloud job (for example started from the printer display) has no per-slot weights. Then the total weight is split by how many percent of the progress each slot was active.

## How a print ended

- `finish`: 100 % of the weight is deducted.
- Anything else (`failed`, `idle`): the share given by the progress reached.

## Extra for waste

The option **Extra for waste (purge, failed starts)** (default 5 %) is added to every deduction: a print of 100 g deducts 105 g. Whether the weight from the cloud already includes purge and the prime tower is not verified, hence the extra. Set it by weighing a spool before and after a few prints.

## Low stock

When a filament drops below **Low stock threshold** (default 300 g), a persistent notification "Filament running low" appears and its `binary_sensor` `…_low` turns on. The notification is created once, when the stock crosses the threshold.

## Corrections

The stock is a number you can overwrite at any time: in the filament dialog, with the `number` entity, or with the **add spool** button.

## Limits

An unfinished print is not stored: restarting Home Assistant during a print loses the progress fallback (the per-slot weights from ha-bambulab still work).

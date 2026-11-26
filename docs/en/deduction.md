# How deduction works

## Following a print

A print is followed from the printer states `prepare` / `running` / `pause` until it ends. The integration watches the printer sensors of ha-bambulab: `print_status`, `print_progress` and `print_weight`.

## Grams per slot

The main source is the `print_weight` sensor of the printer. Its attributes hold the grams per slot, for example `AMS 1 Tray 2: 12.5` or `External Spool: 4.8`. Each slot is turned into a stock item by what was in it during the print, so a multi-colour print deducts from every spool used.

With AMS auto refill (filament backup) the slicer plans the grams on one slot, and the printer moves on to another slot when the first one runs out. The integration sees the switch to a slot the slicer planned nothing for. The slot that ran out is deducted what the stock still had for it (so it ends at 0 g), and the backup slot gets the rest. Keep the stock of a nearly empty spool right before such a print.

## Fallback by progress

A print without a cloud job (for example started from the printer display) has no per-slot weights. Then the total weight is split by how many percent of the progress each slot was active.

## How a print ended

- `finish`: 100 % of the weight is deducted.
- Anything else (`failed`, `idle`): the share given by the progress reached.

## Extra for waste

The option **Extra for waste (purge, failed starts)** (default 5 %) is added to every deduction: a print of 100 g deducts 105 g. Whether the weight from the cloud already includes purge and the prime tower is not verified, hence the extra. Set it by weighing a spool before and after a few prints.

## Low stock

When a filament drops below **Low stock threshold** (default 300 g), a persistent notification "Filament running low" appears and its `binary_sensor` `…_low` turns on. The notification is created once, when the stock crosses the threshold.

## Spool in each slot and the check at print start

The stock does not know which spool is in the AMS. It assumes the stock is whole spools plus one opened spool, and that the opened spool is the one loaded: with 3092 g in stock and **Weight of a new spool** 1000 g, the slot holds 92 g. When the stock is exactly whole spools, the slot holds a full one. When one filament is in two slots, the first slot (by name) holds the opened spool and the next one a full spool, as long as the stock lasts. The sensor `sensor.<device>_<slot>` shows these grams for each AMS slot and the external spool.

When a print starts and the per-slot weights arrive, the job is compared once with these spools, waste included, for every filament of a multicolour print. A slot that holds the same filament but is not used by the job counts too, since AMS auto refill continues from it. When a filament falls short, a persistent notification "Filament in the AMS may run out" appears and the event `filament_stock_shortage` is fired, with `title`, `message` and `items` (`item`, `label`, `needed`, `loaded`, `slots`). A print without per-slot weights (started from the printer display) is not checked.

To get the warning on a phone, add an automation:

```yaml
triggers:
  - trigger: event
    event_type: filament_stock_shortage
actions:
  - action: notify.mobile_app_<your_phone>
    data:
      title: "{{ trigger.event.data.title }}"
      message: "{{ trigger.event.data.message }}"
```

## Corrections

The stock is a number you can overwrite at any time: in the filament dialog, with the `number` entity, or with the **add spool** button.

## Limits

An unfinished print is not stored: restarting Home Assistant during a print loses the progress fallback (the per-slot weights from ha-bambulab still work).

# Changelog

Every release is listed with notes in the [GitHub releases](https://github.com/matata86/filament-stock/releases). This page lists what changed for users, one line per version.

## 0.1.0 – 0.7.2

- **0.7.2:** Filament Stock no longer refreshes ha-bambulab's cloud session itself; it reads profiles only through the public `bambu_lab.get_filament_data` service. The **Sync with Bambu** button is now **Reload profiles**. A profile new in Bambu Cloud appears after ha-bambulab is reloaded.
- **0.7.1:** a sync icon next to **Scan barcode** in the card reads your profiles from Bambu Cloud at once and shows the result as a toast. Brand aliases (show several vendors as one brand) and merging one item into another are available through the websocket API (`filament_stock/brands`, `filament_stock/merge`).
- **0.7.0:** the dashboard card `custom:filament-stock-card` with search, Brand / Material / Colour filters, a total, empty filaments hidden and a dialog per filament. Scanning moved into the card and the sidebar panel is gone. **Undo** after a scan no longer unlinks the code; codes are edited and removed in the filament dialog. The integration registers the card itself.
- **0.6.2:** EAN / GTIN barcodes are checked by their check digit, a misread is rejected instead of added.
- **0.6.1:** assigning an unknown code goes step by step, starting with an empty Brand; the label photo uses a live camera view.
- **0.6.0:** the option **AI to read the label (unknown barcode)**: photograph a label and an AI Task entity suggests the filament.
- **0.5.6:** new profiles get a colour dot guessed from the profile name.
- **0.5.5:** an unknown code is assigned with Brand, Material and Colour instead of one long list.
- **0.5.4:** your profiles are also read from Bambu Cloud when Home Assistant starts.
- **0.5.3:** fix: your own profiles from ha-bambulab were silently dropped.
- **0.5.2:** the **Sync with Bambu** button.
- **0.5.1:** your own profiles are synced from Bambu Cloud every 15 minutes; the name from Bambu wins over a typed one.
- **0.5.0:** stock items follow Bambu filament profiles instead of material and colour, and are created automatically. The "add filament" form is gone. Items and entities of earlier versions are removed on upgrade.
- **0.4.1:** the scanner uses Home Assistant's own controls and works when opened directly.
- **0.4.0:** barcode scanner in a sidebar panel: a known code adds a spool, an unknown one is assigned once, **Undo**.
- **0.3.0:** brand and a custom colour name when adding or editing a filament (replaced in 0.5.0).
- **0.2.0:** add and remove a filament by hand, colour names and a colour dot (replaced in 0.5.0).
- **0.1.0:** first release: stock in grams per material and colour, deduction after a print per slot, add spool button, low stock notification.

# Installation

## Requirements

- Home Assistant 2025.1.0 or newer.
- The [ha-bambulab](https://github.com/greghesp/ha-bambulab) integration, set up with your Bambu account (cloud mode). Filament Stock has no credentials of its own: only ha-bambulab talks to Bambu Cloud.
- A Bambu Lab printer. Tested with a P2S and an AMS 2 Pro; other models are not verified.

## Install with HACS

1. In HACS open the three-dot menu and **Custom repositories**.
2. Add `https://github.com/matata86/filament-stock` with category **Integration**.
3. Find **Filament Stock** and click **Download**.
4. Restart Home Assistant.

## Install manually

Copy the folder `custom_components/filament_stock` from the repository into `/config/custom_components/` and restart Home Assistant.

## Add the integration

1. **Settings, Devices & services, Add integration, Filament Stock.**
2. Pick the printer (the printer itself, not the AMS). A device that has no print weight sensor is refused with "This device is not a printer".
3. Done. The stock items appear from the filament profiles in your slots and from your own Bambu profiles, see [Bambu profiles](profiles.md).

Each printer is added once; a second attempt shows "This printer is already set up".

The card is registered automatically at start. To use it, see [Dashboard card](card.md).

## Update

Update through HACS, then restart Home Assistant. The card is a file the browser caches: if the card still looks like the old version after an update, clear the browser cache (in the Home Assistant app: clear the app cache or reload the app).

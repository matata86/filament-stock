# Entity a volby

## Entity

Na každou položku skladu, na zařízení `Filament <název tiskárny>`:

| Entita | Popis |
|--------|-------|
| `number.<zařízení>_<filament>` | Gramy na skladě, přepisovatelné (0 až 100000). Atributy: `profile`, `filament_id`, `material`, `brand`, `color`, `barcodes`, `spools` (gramy dělené hmotností cívky) |
| `button.<zařízení>_<filament>_pridat_civku` | Přičte hmotnost nové cívky |
| `binary_sensor.<zařízení>_<filament>_dochazi` | Zapnuto, když je sklad pod prahem nízkého stavu (třída zařízení problém) |

Jedna na integraci:

| Entita | Popis |
|--------|-------|
| `button.<zařízení>_znovu_nacist_profily` | Hned přečte seznam profilů z ha-bambulab (kategorie entity Konfigurace; při instalaci před 0.7.2 `synchronizovat_s_bambu`) |

Přesná ID závisejí na názvu zařízení a filamentu a na jazyku Home Assistantu (v angličtině končí `_add_spool`, `_low` a `reload_profiles`); vznikají při založení položky a pak se nemění.

## Volby

**Nastavení, Zařízení a služby, Filament Stock, Nastavit**, položka **Nastavení**:

| Volba | Výchozí | Popis |
|-------|---------|-------|
| Přirážka na odpad (purge, nepovedené starty) | 5 % | Přičte se ke každému odečtu |
| Práh nízkého stavu | 300 g | Pod ním filament dochází |
| Hmotnost nové cívky | 1000 g | Přičte ji „přidat cívku“ a sken |
| AI na čtení štítku (neznámý čárový kód) | žádná | Entita `ai_task`, která umí obrázky; bez ní se tlačítko fotky neukáže |

Další dvě položky menu jsou **Přejmenovat filament** a **Odebrat filament**, viz [Profily Bambu](profiles.md#prejmenovani-a-odebrani).

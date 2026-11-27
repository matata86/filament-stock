# Instalace

## Požadavky

- Home Assistant 2025.1.0 nebo novější.
- Integrace [ha-bambulab](https://github.com/greghesp/ha-bambulab) nastavená s tvým účtem Bambu (cloudový režim). Filament Stock nemá vlastní přihlašovací údaje: s cloudem Bambu komunikuje jen ha-bambulab.
- Tiskárna Bambu Lab. Ověřeno s P2S a AMS 2 Pro, ostatní modely ověřené nejsou.

## Instalace přes HACS

Filament Stock je ve výchozím katalogu HACS.

1. V HACS vyhledej **Filament Stock**.
2. Otevři ji a klikni na **Stáhnout** (Download).
3. Restartuj Home Assistant.

### Jako vlastní repozitář

Pokud se ve vyhledávání neukáže (třeba ve starším HACS):

1. V HACS otevři menu se třemi tečkami a **Vlastní repozitáře** (Custom repositories).
2. Přidej `https://github.com/matata86/filament-stock` s kategorií **Integrace** (Integration).
3. Najdi **Filament Stock** a klikni na **Stáhnout** (Download).
4. Restartuj Home Assistant.

## Ruční instalace

Zkopíruj složku `custom_components/filament_stock` z repozitáře do `/config/custom_components/` a restartuj Home Assistant.

## Přidání integrace

1. **Nastavení, Zařízení a služby, Přidat integraci, Filament Stock.**
2. Vyber tiskárnu (přímo tiskárnu, ne AMS). Zařízení bez senzoru hmotnosti tisku se odmítne hláškou „Toto zařízení není tiskárna“.
3. Hotovo. Položky skladu vzniknou z filamentových profilů ve slotech a z tvých vlastních profilů v Bambu, viz [Profily Bambu](profiles.md).

Každá tiskárna se přidá jednou, další pokus ukáže „Tato tiskárna je už nastavená“.

Karta se při startu zaregistruje sama. Jak ji použít: [Karta na dashboard](card.md).

## Aktualizace

Aktualizuj přes HACS a restartuj Home Assistant. Karta je soubor, který si prohlížeč drží v cache: když po aktualizaci vypadá karta pořád jako stará verze, vyčisti cache prohlížeče (v aplikaci Home Assistant vyčisti cache aplikace nebo ji načti znovu).

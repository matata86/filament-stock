# Jak funguje odečet

## Sledování tisku

Tisk se sleduje od stavů tiskárny `prepare` / `running` / `pause` do konce. Integrace sleduje senzory tiskárny z ha-bambulab: `print_status`, `print_progress` a `print_weight`.

## Gramy po slotech

Hlavním zdrojem je senzor `print_weight` tiskárny. Jeho atributy drží gramy po slotech, například `AMS 1 Tray 2: 12.5` nebo `External Spool: 4.8`. Každý slot se převede na položku skladu podle toho, co v něm během tisku bylo, takže vícebarevný tisk odečítá z každé použité cívky.

Při AMS auto refill (záloha filamentu) slicer naplánuje gramy na jeden slot a tiskárna po jeho doběhnutí pokračuje z jiného slotu. Integrace pozná přepnutí na slot, pro který slicer nic nenaplánoval. Slotu, který došel, se odečte to, co měl ještě na skladě (skončí na 0 g), a záložní slot dostane zbytek. U skoro prázdné cívky měj stav skladu před takovým tiskem aktuální.

## Záloha podle průběhu

Tisk bez cloudové úlohy (například spuštěný z displeje tiskárny) nemá hmotnosti po slotech. Pak se celková hmotnost rozdělí podle toho, kolik procent průběhu byl který slot aktivní.

## Jak tisk skončil

- `finish`: odečte se 100 % hmotnosti.
- Cokoli jiného (`failed`, `idle`): odečte se podíl podle dosaženého průběhu.

## Přirážka na odpad

Volba **Přirážka na odpad (purge, nepovedené starty)** (výchozí 5 %) se přičte ke každému odečtu: tisk na 100 g odečte 105 g. Jestli hmotnost z cloudu už obsahuje purge a věž, není ověřeno, proto ta přirážka. Nastav ji zvážením cívky před a po několika tiscích.

## Nízký stav

Když filament klesne pod **Práh nízkého stavu** (výchozí 300 g), vznikne trvalé oznámení „Dochází filament“ a jeho `binary_sensor` `…_dochazi` se zapne. Oznámení vznikne jednou, ve chvíli, kdy sklad práh překročí.

## Cívka ve slotu a kontrola při startu tisku

Sklad neví, která cívka je v AMS. Počítá s tím, že sklad jsou celé cívky a jedna načatá a že ve slotu je ta načatá: při 3092 g na skladě a **Hmotnosti nové cívky** 1000 g je ve slotu 92 g. Když sklad vychází na celé cívky, je ve slotu plná. Když je jeden filament ve dvou slotech, první slot (podle názvu) má načatou cívku a další plnou, dokud sklad stačí. Senzor `sensor.<zařízení>_<slot>` ukazuje tyto gramy u každého slotu AMS i externí cívky.

Když tisk začne a přijdou gramy po slotech, porovná se úloha jednou s těmito cívkami, včetně přirážky na odpad, u vícebarevného tisku pro každý filament. Počítá se i slot se stejným filamentem, který úloha nepoužívá, protože z něj pokračuje automatické doplnění AMS. Když některý filament nestačí, vznikne trvalé oznámení „Filament v AMS nemusí stačit“ a spustí se událost `filament_stock_shortage` s `title`, `message` a `items` (`item`, `label`, `needed`, `loaded`, `slots`). Tisk bez gramů po slotech (spuštěný z displeje tiskárny) se nekontroluje.

Upozornění do telefonu přidáš automatizací:

```yaml
triggers:
  - trigger: event
    event_type: filament_stock_shortage
actions:
  - action: notify.mobile_app_<tvuj_telefon>
    data:
      title: "{{ trigger.event.data.title }}"
      message: "{{ trigger.event.data.message }}"
```

## Opravy

Stav skladu je číslo, které můžeš kdykoli přepsat: v dialogu filamentu, entitou `number` nebo tlačítkem **přidat cívku**.

## Omezení

Rozpracovaný tisk se neukládá: restart Home Assistantu během tisku ztratí zálohu podle průběhu (rozpad po slotech z ha-bambulab funguje dál).

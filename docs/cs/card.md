# Karta na dashboard

## Přidání karty

Integrace kartu při startu zaregistruje, žádný prostředek nemusíš přidávat ručně. V editoru dashboardu vyber v nabídce karet **Filament Stock**, nebo použij YAML:

```yaml
type: custom:filament-stock-card
title: Filament
show_header: true
show_empty: false
```

| Volba | Výchozí | Popis |
|-------|---------|-------|
| `title` | `Filament` | Nadpis karty |
| `show_header` | `true` | `false` nadpis skryje |
| `show_empty` | `false` | `true` ukáže filamenty s 0 g hned od začátku |

## Seznam

- **Hledat filament** hledá podle názvu, značky, materiálu a barvy.
- Filtry **Značka**, **Materiál** a **Barva** nabízejí vždy jen hodnoty, které zbývají po ostatních filtrech a hledání.
- Řádek ukazuje barevnou tečku, název, značku a materiál a gramy. Filament pod prahem nízkého stavu je oranžový.
- Filamenty s 0 g jsou skryté. **Zobrazit prázdné (N)** je ukáže, **Skrýt prázdné** je zase schová.
- Nad seznamem je součet toho, co hledání a filtry nechají, například „11 z 21 · 20 kg“.

Karta ukazuje gramy, ne počet cívek: integrace eviduje jen gramy na filament a gramy dělené velikostí cívky by u dvou načatých cívek klamaly.

## Tlačítka

- **Skenovat kód** otevře skener v dialogu, viz [Čárové kódy a štítky](barcodes.md).
- Ikona vedle (popisek „Znovu načíst profily z ha-bambulab“) hned přečte seznam profilů z ha-bambulab; nový profil z cloudu Bambu potřebuje nejdřív znovu načíst ha-bambulab, viz [Profily Bambu](profiles.md#nacteni-profilu). Za běhu se ikona točí, výsledek přijde jako toast, například „Profily načtené: 20 vlastních, 0 nových, 0 změněných.“

## Dialog filamentu

Klikni na filament, otevře se jeho dialog:

- **Zbývá gramů** a **Uložit** nastaví sklad na číslo, které zadáš, například po zvážení cívky.
- **Přidat celou cívku (+1 000 g)** přičte hmotnost nové cívky (volba „Hmotnost nové cívky“).
- **Čárové kódy** vypisují kódy přiřazené k filamentu. Tužka kód upraví (nový se přiřadí, starý odebere), křížek ho odebere.
- **Skenovat kód** (kamera nebo skener aplikace) nebo zadání kódu do pole **Čárový kód** s tlačítkem **Přiřadit** přiřadí nový kód. Kód patří jednomu filamentu: přiřazením tady se odebere ze všech ostatních.
- Značka „Dochází“ se objeví vedle gramů, když je sklad pod prahem.

Karta si data načte znovu při změně entity skladu a po každé akci.

# Změny

Každé vydání je s poznámkami v [GitHub releases](https://github.com/matata86/filament-stock/releases). Tato stránka uvádí, co se změnilo pro uživatele, jedním řádkem na verzi.

## 0.1.0 – 0.7.3

- **0.7.3:** senzor u každého slotu AMS ukazuje gramy na vložené cívce (sklad po odečtení celých cívek). Při startu tisku se úloha porovná s cívkami v AMS, i u vícebarevného tisku; když filament nestačí, přijde oznámení a událost `filament_stock_shortage`. Automatické doplnění AMS: slotu, kterému došel filament, se odečte, co mu zbývalo, záložnímu slotu zbytek.
- **0.7.2:** Filament Stock už sám neobnovuje cloudovou relaci ha-bambulab; profily čte jen přes veřejnou službu `bambu_lab.get_filament_data`. Tlačítko **Synchronizovat s Bambu** se jmenuje **Znovu načíst profily**. Nový profil z cloudu Bambu se objeví po znovunačtení ha-bambulab.
- **0.7.1:** ikona synchronizace vedle **Skenovat kód** v kartě hned přečte tvoje profily z cloudu Bambu a výsledek ukáže jako toast. Aliasy značek (víc výrobců jako jedna značka) a sloučení položky do jiné jsou dostupné přes websocket API (`filament_stock/brands`, `filament_stock/merge`).
- **0.7.0:** karta na dashboard `custom:filament-stock-card` s hledáním, filtry Značka / Materiál / Barva, součtem, skrytými prázdnými filamenty a dialogem u každého filamentu. Skenování se přesunulo do karty a panel v postranním menu zmizel. **Zpět** po skenu už kód neodpojí, kódy se upravují a odebírají v dialogu filamentu. Integrace kartu zaregistruje sama.
- **0.6.2:** čárové kódy EAN / GTIN se kontrolují podle kontrolní číslice, špatné čtení se odmítne místo přičtení.
- **0.6.1:** přiřazení neznámého kódu jde krok za krokem od prázdné značky, fotka štítku používá živý náhled kamery.
- **0.6.0:** volba **AI na čtení štítku (neznámý čárový kód)**: vyfoť štítek a entita AI Task navrhne filament.
- **0.5.6:** nové profily dostanou barevnou tečku odhadnutou podle názvu profilu.
- **0.5.5:** neznámý kód se přiřazuje výběrem Značka, Materiál a Barva místo jednoho dlouhého seznamu.
- **0.5.4:** profily se čtou z cloudu Bambu i při startu Home Assistantu.
- **0.5.3:** oprava: vlastní profily z ha-bambulab se tiše zahazovaly.
- **0.5.2:** tlačítko **Synchronizovat s Bambu**.
- **0.5.1:** vlastní profily se synchronizují z cloudu Bambu každých 15 minut, název z Bambu má přednost před ručním.
- **0.5.0:** položky skladu sledují filamentové profily Bambu místo materiálu a barvy a zakládají se samy. Formulář „přidat filament“ zmizel. Položky a entity starších verzí se při aktualizaci odstraní.
- **0.4.1:** skener používá výchozí prvky Home Assistantu a funguje i při přímém otevření.
- **0.4.0:** skener čárových kódů v panelu v postranním menu: známý kód přičte cívku, neznámý se jednou přiřadí, **Zpět**.
- **0.3.0:** značka a vlastní název barvy při přidání nebo úpravě filamentu (nahrazeno v 0.5.0).
- **0.2.0:** ruční přidání a odebrání filamentu, názvy barev a barevná tečka (nahrazeno v 0.5.0).
- **0.1.0:** první verze: sklad v gramech podle materiálu a barvy, odečet po tisku po slotech, tlačítko přidat cívku, oznámení o nízkém stavu.

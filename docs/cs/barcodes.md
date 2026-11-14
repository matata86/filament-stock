# Čárové kódy a štítky

Naskenuj čárový kód z krabice nebo cívky a správnému filamentu se přičte jedna celá cívka.

## Jak se kód čte

Skener zkouší v tomto pořadí:

1. **Skener aplikace Home Assistant** (když ho aplikace má).
2. **Kamera v prohlížeči** (`BarcodeDetector` prohlížeče), jen na stránce otevřené přes **HTTPS**.
3. **Ruční zadání kódu** do pole **Čárový kód** a **Přidat**. Funguje i s USB čtečkou, která píše jako klávesnice.

Skener otevřeš tlačítkem **Skenovat kód** v [kartě](card.md), nebo z dialogu filamentu, když chceš kód přiřadit k tomuto filamentu.

### Kontrola čtení

Číselný kód délky 8, 12, 13 nebo 14 musí mít správnou kontrolní číslici EAN / GTIN, jinak je to špatné čtení. Skener aplikace zůstane otevřený a ukáže „Špatně načteno, podržte kameru v klidu a zkuste znovu.“, kamera v prohlížeči čte dál a kód přijme, až se shodnou dva snímky po sobě. Kódy bez kontrolní číslice (QR, Code 128 s písmeny) projdou.

## Známý kód

K filamentu se přičte hmotnost cívky (volba „Hmotnost nové cívky“) a karta ukáže například „Generic PETG bílá: +1000 g, nyní 1500 g“. **Zpět** cívku zase odečte. Kód zůstane přiřazený, když byl špatně, odeber ho v dialogu filamentu.

## Neznámý kód

Přiřadíš ho jednou, příště se pozná sám:

1. Vyber **Značku**. Další výběr se ukáže až po volbě předchozího a výběr s jedinou možností se vybere sám.
2. Vyber **Materiál**.
3. Vyber **Barvu**.
4. **Přiřadit a přidat cívku.**

## Vyfotit štítek

Když máš v nastavení vybranou entitu AI Task (**AI na čtení štítku (neznámý čárový kód)**), nabídne neznámý kód navíc **Vyfotit štítek**. Otevře se živý náhled kamery (**Vyfotit**); tam, kde stránka kameru použít nesmí (obyčejné `http://`), vybereš místo toho soubor. Fotka se zmenší (delší strana 1600 px) a pošle do Home Assistantu, ten ji na chvíli uloží do `/media/filament_stock/`, předá entitě AI Task a potom smaže.

AI vrátí značku, materiál a barvu a vybere odpovídající položku ze skladu. Tři výběry se předvyplní a ty potvrdíš tlačítkem **Přiřadit a přidat cívku**. Když nic neodpovídá, uvidíš „Ve skladu nic odpovídajícího není, vyberte ručně.“

Kterou AI fotku čte, záleží na entitě, kterou vybereš; obrázek jde na tuto službu.

## Pozdější změna kódu

V [dialogu filamentu](card.md#dialog-filamentu): tužka kód upraví, křížek ho odebere.

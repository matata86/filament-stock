# Websocket API

Integrace registruje tyto websocket příkazy Home Assistantu. Používá je karta a skener a můžeš je volat ze skriptů nebo z vývojářských nástrojů prohlížeče. Žádný z nich není omezen na administrátory: volat je může každý přihlášený uživatel.

Každý příkaz se řídí obvyklou konvencí websocketu: pošli `{"id": <n>, "type": "...", ...}`, dostaneš `{"id": <n>, "type": "result", "success": true, "result": ...}` nebo `"success": false` s objektem `error`.

Položka se určuje dvojicí `entry_id` (config entry tiskárny) a `key` (klíč položky, viz [Formát úložiště](storage.md#item-keys)). Obojí vrací `filament_stock/items`.

## filament_stock/items

Všechny položky skladu všech načtených tiskáren. Používá je karta.

```json
{"id": 1, "type": "filament_stock/items"}
```

```json
{"id": 1, "type": "result", "success": true, "result": {"items": [
  {"entry_id": "01J...", "key": "GFG99_FFFFFF", "label": "Generic PETG bílá",
   "brand": "Generic", "material": "PETG", "color": "bílá", "hex": "FFFFFF",
   "grams": 1234.0, "low": false, "spool": 1000.0, "barcodes": ["8590000000000"]}
]}}
```

`hex` je barva ze slotu (bez `#`, nebo `null`), `low` je true pod prahem nízkého stavu, `spool` je volba „Hmotnost nové cívky“.

## filament_stock/set

`{entry_id, key, grams}` nastaví gramy položky (ne pod 0, zaokrouhleno na 0,1). Vrací `{"grams": <hodnota>}`. Chyba `not_found` pro neznámou položku.

## filament_stock/spool

`{entry_id, key}` přičte jednu cívku (volba „Hmotnost nové cívky“). Vrací `{"grams": <hodnota>}`. Chyba `not_found` pro neznámou položku.

## filament_stock/barcode

`{entry_id, key, code, remove?}` přiřadí položce čárový kód. Kód se nejdřív odebere ze všech položek všech tiskáren (kód patří jedné položce). S `"remove": true` se jen odebere. Cívka se nepřičítá. Vrací `{"barcodes": [...]}` dané položky. Chyby: `invalid_format` pro prázdný kód, `not_found` pro neznámou položku.

## filament_stock/scan

`{code}` zpracuje naskenovaný kód. Známý kód přičte jednu cívku a vrátí

```json
{"known": true, "code": "8590000000000", "entry_id": "01J...", "key": "GFG99_FFFFFF",
 "label": "Generic PETG bílá", "grams": 2234.0, "added": 1000.0}
```

Neznámý kód vrátí položky, ke kterým ho jde přiřadit, a zda je nastavená entita AI Task:

```json
{"known": false, "code": "8590000000000", "ai": true,
 "items": [{"entry_id": "01J...", "key": "GFG99_FFFFFF", "label": "Generic PETG bílá",
            "brand": "Generic", "material": "PETG", "color": "bílá"}]}
```

## filament_stock/assign

`{entry_id, key, code}` přiřadí kód položce a přičte jednu cívku. Vrací stejný objekt jako známý `scan`. Chyba `not_found` pro neznámou položku nebo prázdný kód.

## filament_stock/undo

`{entry_id, key, code}` cívku zase odečte. Kód zůstane přiřazený. Vrací `{}`. Chyba `not_found` pro neznámou položku nebo prázdný kód.

## filament_stock/recognize

`{image, mime?}` přečte fotku štítku přes entitu AI Task z voleb. `image` je base64 (do 8 MB), `mime` je výchozí `image/jpeg` a musí začínat `image/`. Obrázek se dočasně uloží do `/media/filament_stock/`, předá službě `ai_task.generate_data` a poté smaže.

```json
{"brand": "Smart Print", "material": "PETG", "color": "šedá", "key": "P1234567", "entry_id": "01J..."}
```

`key` a `entry_id` jsou `null`, když AI nenašla odpovídající položku (klíč, který ve tvém skladu není, se zahodí). Chyby: `not_supported`, když není nastavená entita AI Task, `invalid_format` pro špatný nebo příliš velký obrázek, `ai_failed`, když volání AI Task selže.

## filament_stock/sync

Bez parametrů. Hned přečte tvoje vlastní profily z cloudu Bambu, pro každou načtenou tiskárnu. Vrací součty:

```json
{"profiles": 20, "new": 0, "changed": 0}
```

Chyba `sync_failed`, když ha-bambulab seznam profilů nedodá.

## filament_stock/merge

`{entry_id, key, into}` sloučí položku `key` do položky `into` stejné tiskárny: gramy a kódy se sečtou, sloučený profil od té chvíle platí jako cíl (tisk s ním odečte z cíle) a sloučená položka i její entity zmizí. Vrací `{"key": <into>, "grams": <hodnota>}`. Chyba `not_found` pro neznámou položku nebo cíl (nebo když jsou oba stejné). Integrace se znovu načte. V kartě pro to obrazovka není, používá se přes API.

## filament_stock/brands

`{entry_id, brands}` nastaví mapu názvů značek, které se zobrazí místo výrobce, jak ho hlásí tiskárna, například `{"Smart Print": "PL/SM"}`. Vrací `{"brands": {...}}`; integrace se znovu načte, aby se nové názvy použily. Chyba `not_found` pro neznámý záznam. V kartě pro to obrazovka není, používá se přes API.

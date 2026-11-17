# Časté otázky

## Filament se nezobrazuje

- V Bambu Studiu je uložený přes **Save as**. Takový profil má id svého základu Generic a nepozná se. Založ ho znovu přes **Create Filament**, viz [Profily Bambu](profiles.md#create-filament-ne-save-as).
- Je jen v prázdném nebo neznámém slotu: slot bez profilu se přeskakuje.
- Je to nový profil, který ha-bambulab ještě nenačetla. Nový profil uvidíš hned, když znovu načteš integraci Bambu Lab (**Nastavení → Zařízení a služby → Bambu Lab → ⋮ → Znovu načíst**) a pak stiskneš **Znovu načíst profily**.
- Má 0 g: karta prázdné filamenty skrývá, použij **Zobrazit prázdné**.

## Karta je po aktualizaci stará

Prohlížeč (nebo aplikace Home Assistant) drží soubor karty v cache. Načti stránku znovu s vyčištěnou cache, v aplikaci vyčisti cache aplikace. Adresa souboru se mění s verzí po restartu Home Assistantu.

## Kamera nejde

Kamera v prohlížeči potřebuje stránku otevřenou přes **HTTPS**. Použij aplikaci Home Assistant (má vlastní skener), otevři Home Assistant přes HTTPS, nebo zadej kód do pole **Čárový kód** (funguje i USB čtečka). Viz [Čárové kódy a štítky](barcodes.md).

## Proč restart Home Assistantu během tisku ztratil gramy?

Rozpracovaný tisk se neukládá. Hmotnosti po slotech z ha-bambulab fungují dál, ale záloha podle průběhu se pro ten tisk ztratí. Během tisku Home Assistant radši nerestartuj.

## Jiný odstín stejné barvy je nová položka

Vestavěný profil se dělí podle přesné barvy: jiný odstín ve slotu je jiná položka. Nepotřebnou odeber, nebo použij vlastní profil (jedna položka bez ohledu na barvu ve slotu).

## Dva filamenty mají stejný název

Dva odstíny se stejnou nejbližší základní barvou mají stejný název a liší se jen barevnou tečkou. Jeden přejmenuj přes **Přejmenovat filament**.

## Je v odečtené hmotnosti purge?

Není ověřeno, jestli hmotnost z cloudu obsahuje purge a věž. Kryje to volba **Přirážka na odpad**; svoji hodnotu zjistíš zvážením cívky před a po několika tiscích.

## Funguje to s AMS HT?

Název jeho slotu (`AMS HT n`) je odvozen ze zdrojáku ha-bambulab a na zařízení není ověřen.

## Bude skener aplikace fungovat i po aktualizaci Home Assistantu?

Skener aplikace se volá přes interní API frontendu Home Assistantu, ne veřejné. Aktualizace ho může rozbít. Kamera v prohlížeči a ruční zadání kódu fungují dál.

## Které tiskárny fungují?

Ověřeno s Bambu Lab P2S a AMS 2 Pro v cloudovém režimu. Ostatní modely, které ha-bambulab podporuje, ověřené nejsou.

Nevyřešeno? Otevři [issue na GitHubu](https://github.com/matata86/filament-stock/issues).

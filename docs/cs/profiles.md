# Profily Bambu

## Jedna položka na profil

Položka skladu je filamentový profil z Bambu, určený svým `filament_id`:

- **Tvůj vlastní profil** je jedna položka (například „Professional Lab PETG Red Matte“). Jeden profil je jedna značka, materiál a barva.
- **Vestavěný profil** (Bambu a Generic, id začíná `GF`) se dělí po barvách: Generic PETG s bílou cívkou a s černou cívkou jsou dvě položky.

V Home Assistantu filamenty nezakládáš. Položky vznikají samy:

- Jakmile slot hlásí profil, který sklad ještě nezná, založí se položka s 0 g. Prázdný nebo neznámý slot se přeskočí.
- Tvoje vlastní profily se čtou z cloudu Bambu (přes ha-bambulab) a každý se stane položkou, i když není v AMS.

## Create Filament, ne Save as

Vlastní profil potřebuje vlastní `filament_id`. V Bambu Studiu ho založ přes **Create Filament**, dostane id začínající `P`.

Profil uložený přes **Save as** z Generic dědí id svého základu (například `GFG99` nebo `GFU99`). ha-bambulab ho v seznamu neuvede a slot ho od Generic nerozezná, takže se z něj nikdy nestane samostatná položka.

## Synchronizace

Vlastní profily se čtou znovu:

- při startu Home Assistantu,
- každých 15 minut,
- po stisku tlačítka **Synchronizovat s Bambu** (integrace ho má), nebo ikony synchronizace vedle **Skenovat kód** v [kartě](card.md).

Nové profily se stanou položkami, změněné názvy se přepíšou. Název z Bambu má vždy přednost před názvem, který jsi zadal ručně.

## Názvy a barvy

Název vlastního profilu přichází z Bambu. U ostatních položek je název profil (nebo materiál) a nejbližší ze 12 základních barev, například „Generic PETG bílá“. Barevná tečka vychází z poslední barvy, která byla ve slotu; dokud profil ve slotu nebyl, odhadne se barva z názvu profilu.

ID entit vzniká z názvu při založení položky a pak se nemění. Když se název nebo barva z Bambu změní, integrace se sama znovu načte.

## Přejmenování a odebrání

**Nastavení, Zařízení a služby, Filament Stock, Nastavit:**

- **Přejmenovat filament** změní jen název zobrazený v Home Assistantu, nouzově, když Bambu název nepošle. Prázdné pole vrátí název z Bambu.
- **Odebrat filament** smaže položku i její entity. Je-li filament dál ve slotu, založí se znovu s 0 g.

Smazání profilu v Bambu položku skladu nesmaže (drží tvůj stav skladu), odeber ji ručně.

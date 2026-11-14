# Barcodes and labels

Scan the barcode on a box or a spool and one full spool is added to the right filament.

## How the code is read

The scanner tries these in order:

1. The **scanner of the Home Assistant app** (when the app has one).
2. **The camera in the browser** (the `BarcodeDetector` of the browser), only on a page opened over **HTTPS**.
3. **Typing the code** into the **Barcode** field and **Add**. This also works with a USB barcode reader that types like a keyboard.

Open the scanner with **Scan barcode** in the [card](card.md), or from a filament's dialog to link a code to that filament.

### Misread check

A numeric code of length 8, 12, 13 or 14 must have a valid EAN / GTIN check digit, otherwise it counts as a misread. The app scanner stays open and shows "Misread, hold the camera still and try again."; the browser camera keeps reading and accepts a code when two frames in a row agree. Codes without a check digit (QR, Code 128 with letters) pass.

## A known code

The spool weight (option "Weight of a new spool") is added to the filament and the card says, for example, "Generic PETG white: +1000 g, now 1500 g". **Undo** takes the spool off again. The code stays linked; remove it in the filament's dialog if it was wrong.

## An unknown code

You assign it once, next time it is recognised:

1. Pick **Brand**. The next list appears only after the previous one is chosen, and a list with a single option picks itself.
2. Pick **Material**.
3. Pick **Colour**.
4. **Assign and add a spool.**

## Photograph the label

If you set an AI Task entity in the options (**AI to read the label (unknown barcode)**), an unknown code also offers **Photograph label**. It opens a live camera view (**Take photo**); where the page may not use the camera (plain `http://`), you pick a file instead. The photo is shrunk (longest side 1600 px) and sent to Home Assistant, which stores it briefly in `/media/filament_stock/`, hands it to the AI Task entity and deletes it afterwards.

The AI returns brand, material and colour and picks a matching item from your stock. The three selections are filled in and you confirm with **Assign and add a spool**. If nothing matches, you see "No matching filament in stock, pick it by hand."

Which AI reads the photo depends on the entity you chose; the picture goes to that service.

## Change a code later

In the [filament dialog](card.md#filament-dialog): the pencil edits a code, the cross removes it.

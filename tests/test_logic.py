"""Self-check for the deduction logic. Run: python3 tests/test_logic.py"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "custom_components" / "filament_stock"))
from logic import (  # noqa: E402
    JobTracker,
    clean_code,
    find_barcode,
    hex_color,
    is_custom,
    item_facets,
    label_match,
    label_prompt,
    loaded_grams,
    shortages,
    name_color,
    item_key,
    merge_plan,
    item_label,
    profile_facts,
    slot_item,
)

GREY, BLACK, TPU = "PETG_898989", "PETG_161616", "TPU_161616"


def slots(active=None):
    return {
        "AMS 1 Tray 1": (GREY, active == 1),
        "AMS 1 Tray 2": (BLACK, active == 2),
        "External Spool": (TPU, active == "ext"),
    }


def test_keys():
    # Built-in profile: id + colour. The user's own profile: the id alone.
    assert item_key("GFG99", "#FFFFFFFF") == "GFG99_FFFFFF"
    assert item_key("GFG99", "") is None
    assert item_key("P98f186c", "#898989FF") == "P98f186c"
    assert item_key("P98f186c", None) == "P98f186c"
    assert item_key("", "00000000") is None
    assert item_key(None, "#898989FF") is None
    assert is_custom("P98f186c") and not is_custom("GFG99_FFFFFF")
    assert hex_color("#898989FF") == "898989" and hex_color("12") is None


def test_labels():
    generic = {"profile": "Generic PETG", "material": "PETG", "color": "FFFFFF"}
    assert item_label("GFG99_FFFFFF", generic) == "Generic PETG white"
    assert item_label("GFG99_FFFFFF", generic, "cs") == "Generic PETG bílá"
    assert item_label("GFL99_F5E6C8", {"profile": "Generic PLA", "color": "F5E6C8"}, "de") == "Generic PLA beige"
    own = {"profile": "Professional Lab PETG Red Matte", "material": "PETG", "color": "C81E1E"}
    assert item_label("P98f186c", own, "cs") == "Professional Lab PETG Red Matte"
    # Profile name not known (the printer integration has no list yet): material + colour.
    assert item_label("P98f186c", {"material": "PETG", "color": "898989"}, "cs") == "PETG šedá"
    assert item_label("P98f186c", {}) == "P98f186c"
    # The slicer name of an own profile beats a typed name; a typed name beats the fallback.
    assert item_label("P98f186c", {**own, "name": "red"}) == "Professional Lab PETG Red Matte"
    assert item_label("P98f186c", {"material": "PETG", "color": "898989", "name": "red"}) == "red"
    assert item_label("GFG99_FFFFFF", {**generic, "name": "Majkl white"}) == "Majkl white"


def test_facets():
    own = {"profile": "Smart Print PETG šedá", "brand": "Smart Print", "material": "PETG", "color": "898989"}
    assert item_facets("Pa48c853", own)["color"] == "šedá"
    generic = {"profile": "Generic PETG", "brand": "Generic", "material": "PETG", "color": "FFFFFF"}
    assert item_facets("GFG99_FFFFFF", generic, "cs") == {
        "label": "Generic PETG bílá", "brand": "Generic", "material": "PETG", "color": "bílá"}
    # Profile name without the brand ('Bambu TPU 90A', vendor 'Bambu Lab'): strip the profile.
    tpu = {"profile": "Bambu TPU 90A", "brand": "Bambu Lab", "material": "TPU", "color": "161616"}
    assert item_facets("GFU03_161616", tpu, "cs")["color"] == "černá"
    # Typed name, no brand: split at the material, not the whole name as the colour.
    typed = {"name": "Professional Lab PETG šedá", "material": "PETG", "color": "898989"}
    assert item_facets("P98f186c", typed, "cs") == {
        "label": "Professional Lab PETG šedá", "brand": "Professional Lab", "material": "PETG", "color": "šedá"}
    # Nothing known: the colour is the whole label, brand and material empty.
    assert item_facets("P98f186c", {}) == {"label": "P98f186c", "brand": "", "material": "", "color": "P98f186c"}


def test_name_color():
    assert name_color("Smart Print PETG šedá") == "808080"
    assert name_color("Smart Print PLA dřevo černý ořech") == "000000"
    assert name_color("Professional Lab PETG Red Matte") == "DC1E1E"
    assert name_color("Smart Print PLA pastelově oranžová") == "FF8200"
    assert name_color("Generic PETG") is None and name_color(None) is None
    # The slot colour wins over the guess from the name.
    profile = {"name": "Smart Print PETG šedá", "filament_type": "PETG"}
    assert profile_facts(profile)["color"] == "808080"
    assert profile_facts(profile, {"type": "PETG", "color": "898989FF"})["color"] == "898989"


def test_label():
    prompt = label_prompt({"Pa48c853": "Smart Print PETG šedá"}, "cs")
    assert "- Pa48c853: Smart Print PETG šedá" in prompt and "Czech" in prompt
    assert label_match({"key": "Pa48c853", "brand": "Smart Print"}, {"Pa48c853"}) == "Pa48c853"
    # Made-up keys, 'none' and odd answers do not pick anything.
    assert label_match({"key": "none"}, {"Pa48c853"}) is None
    assert label_match({"key": "Pxxx"}, {"Pa48c853"}) is None
    assert label_match("Smart Print", {"Pa48c853"}) is None


def test_slot_item():
    profiles = {
        "GFG99": {"name": "Generic PETG", "filament_vendor": "Generic", "filament_type": "PETG"},
        "Pabc": {"name": "Professional Lab PETG Red Matte", "filament_vendor": "Professional Lab", "filament_type": "PETG"},
    }
    slot = {"filament_id": "GFG99", "name": "Generic PETG", "type": "PETG", "color": "#FFFFFFFF", "empty": False}
    assert slot_item(slot, profiles) == (
        "GFG99_FFFFFF",
        {"profile": "Generic PETG", "brand": "Generic", "material": "PETG", "color": "FFFFFF"},
    )
    assert slot_item({**slot, "filament_id": "Pabc", "color": "#C81E1EFF"}, profiles) == (
        "Pabc",
        {"profile": "Professional Lab PETG Red Matte", "brand": "Professional Lab", "material": "PETG", "color": "C81E1E"},
    )
    # Own profile the printer integration has no name for: the slot says just 'PETG'.
    assert slot_item({"filament_id": "P98f186c", "name": "PETG", "type": "PETG", "color": "#898989FF"}, profiles) == (
        "P98f186c",
        {"material": "PETG", "color": "898989"},
    )
    # Nothing to stock: empty or unknown slot, no profile.
    assert slot_item({**slot, "empty": True}, profiles) is None
    assert slot_item({**slot, "unknown": True}, profiles) is None
    assert slot_item({"filament_id": "", "type": "", "color": "#00000000"}, profiles) is None
    assert profile_facts(profiles["Pabc"]) == {
        "profile": "Professional Lab PETG Red Matte",
        "brand": "Professional Lab",
        "material": "PETG",
        "color": "DC1E1E",
    }


def test_per_slot_weights():
    t = JobTracker()
    w = {"AMS 1 Tray 1": 30.0, "AMS 1 Tray 2": 12.5}
    assert t.update("running", 10, 42.5, w, slots(1)) is None
    assert t.update("running", 90, 42.5, w, slots(2)) is None
    assert t.update("finish", 100, 42.5, w, slots()) == {GREY: 30.0, BLACK: 12.5}
    # Reported once only.
    assert t.update("finish", 100, 42.5, w, slots()) is None
    assert t.update("idle", 100, 42.5, w, slots()) is None


def test_external_spool_attribute_gone_at_finish():
    t = JobTracker()
    t.update("running", 50, 4.8, {"External Spool": 4.8}, slots("ext"))
    assert t.update("finish", 100, 4.8, {}, slots()) == {TPU: 4.8}


def test_failed_scales_by_progress():
    t = JobTracker()
    t.update("running", 40, 100.0, {"AMS 1 Tray 1": 100.0}, slots(1))
    assert t.update("failed", 0, 100.0, {}, slots()) == {GREY: 40.0}


def test_fallback_split_by_progress():
    t = JobTracker()
    t.update("prepare", 100, 0, {}, slots())  # stale progress from the previous job
    t.update("running", 0, 80.0, {}, slots(1))
    t.update("running", 75, 80.0, {}, slots(1))
    t.update("running", 100, 80.0, {}, slots(2))
    assert t.update("finish", 100, 80.0, {}, slots()) == {GREY: 60.0, BLACK: 20.0}


def test_auto_refill_uses_up_the_empty_spool():
    t = JobTracker()
    w = {"AMS 1 Tray 1": 300.0}  # the slicer planned the whole job on tray 1
    stock = {GREY: 120.0, BLACK: 1000.0}
    t.update("running", 10, 300.0, w, slots(1), stock)
    t.update("running", 40, 300.0, w, slots(2), stock)  # tray 1 ran out, tray 2 took over
    assert t.update("finish", 100, 300.0, w, slots(), stock) == {GREY: 120.0, BLACK: 180.0}
    # Failed job: only the printed part is split, the empty spool first.
    t.update("running", 10, 300.0, w, slots(1), stock)
    t.update("running", 50, 300.0, w, slots(2), stock)
    assert t.update("failed", 0, 300.0, {}, slots(), stock) == {GREY: 120.0, BLACK: 30.0}
    # No refill: a planned slot becoming active is not a backup.
    t.update("running", 10, 300.0, {"AMS 1 Tray 1": 200.0, "AMS 1 Tray 2": 100.0}, slots(1), stock)
    t.update("running", 50, 300.0, {"AMS 1 Tray 1": 200.0, "AMS 1 Tray 2": 100.0}, slots(2), stock)
    assert t.update("finish", 100, 300.0, {}, slots(), stock) == {GREY: 200.0, BLACK: 100.0}


def test_dropout_keeps_job_open():
    t = JobTracker()
    t.update("running", 50, 10.0, {"AMS 1 Tray 1": 10.0}, slots(1))
    assert t.update("unavailable", None, None, {}, {}) is None
    assert t.update("finish", 100, 10.0, {}, slots()) == {GREY: 10.0}


def test_no_job_no_deduction():
    assert JobTracker().update("finish", 100, 10.0, {"AMS 1 Tray 1": 10.0}, slots()) is None


def test_barcodes():
    meta = {GREY: {"brand": "X", "barcodes": ["8594185640011"]}, BLACK: {"name": "night"}}
    assert clean_code(" 8594 185640011\n") == "8594185640011"
    assert clean_code(None) == ""
    assert find_barcode(meta, "8594185640011") == GREY
    assert find_barcode(meta, "123") is None
    assert find_barcode(meta, "") is None


def test_brand_map_and_merge():
    brands = {"Smart Print": "PL/SM", "Professional Lab": "PL/SM"}
    sp = {"profile": "Smart Print PETG šedá", "brand": "Smart Print", "material": "PETG", "color": "808080"}
    pl = {"profile": "Professional Lab PETG šedá", "brand": "Professional Lab", "material": "PETG", "color": "808080"}
    assert item_label("Pa", sp, "cs", brands) == "PL/SM PETG šedá"
    assert item_label("Pb", pl, "cs", brands) == "PL/SM PETG šedá"
    assert item_label("Pa", sp, "cs") == "Smart Print PETG šedá"  # no map, unchanged
    assert item_facets("Pa", sp, "cs", brands) == {"label": "PL/SM PETG šedá", "brand": "PL/SM", "material": "PETG", "color": "šedá"}
    assert item_label("GFG99_FFFFFF", {"profile": "Generic PETG", "brand": "Generic", "color": "FFFFFF"}, "cs", brands) == "Generic PETG bílá"
    assert item_label("Pc", {"profile": "Professional Lab PETG šedá", "material": "PETG"}, "cs", brands) == "PL/SM PETG šedá"
    tpu = {"profile": "The Filament TPU 95A černá", "brand": "The Filament", "material": "TPU", "color": "161616"}
    f = item_facets("P04818ab", tpu, "cs", brands)
    assert (f["brand"], f["material"], f["color"]) == ("The Filament", "TPU 95A", "černá")
    items = {"Pa": 1000.0, "Pb": 250.5}
    meta = {"Pa": {"barcodes": ["1", "2"]}, "Pb": {"barcodes": ["2", "3"]}}
    assert merge_plan(items, meta, "Pb", "Pa") == (1250.5, ["1", "2", "3"])
    assert merge_plan(items, {}, "Pb", "Pc") == (250.5, [])


def test_loaded_and_shortage():
    stock = {"A": 3092.0, "B": 2000.0, "C": 0.0, "D": 1500.0}
    slots = {"AMS 1 Tray 1": "A", "AMS 1 Tray 2": "B", "AMS 1 Tray 3": "C", "AMS 1 Tray 4": None,
             "External Spool": "D", "AMS 2 Tray 1": "D"}
    loaded = loaded_grams(slots, stock, 1000.0)
    # opened spool = remainder; whole spools -> a full one; second slot of D gets what is left
    assert loaded == {"AMS 1 Tray 1": 92.0, "AMS 1 Tray 2": 1000.0, "AMS 1 Tray 3": 0.0,
                      "AMS 2 Tray 1": 500.0, "External Spool": 1000.0}
    assert loaded_grams({"AMS 1 Tray 1": "A", "AMS 1 Tray 2": "A"}, {"A": 1050.0}, 1000.0) == {
        "AMS 1 Tray 1": 50.0, "AMS 1 Tray 2": 1000.0}
    assert loaded_grams({"x": "A", "y": "A"}, {"A": 300.0}, 1000.0) == {"x": 300.0, "y": 0.0}
    weights = {"AMS 1 Tray 1": 71.3, "AMS 1 Tray 2": 18.7}
    assert shortages(weights, slots, loaded) == {}
    # 5 % waste pushes A over the 92 g on the spool
    assert shortages({"AMS 1 Tray 1": 90.0}, slots, loaded, 1.05) == {"A": (94.5, 92.0)}
    # auto refill: a second slot with the same item adds to what is loaded
    assert shortages({"AMS 2 Tray 1": 1200.0}, slots, loaded) == {}
    assert shortages({"AMS 1 Tray 3": 5.0, "AMS 1 Tray 4": 5.0}, slots, loaded) == {"C": (5.0, 0.0)}


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
    print("ok")

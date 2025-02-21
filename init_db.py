from tinydb import TinyDB

# Datenbankpfad
db = TinyDB("database.json", encoding="utf-8", ensure_ascii=False)

# ❗ ALTE DATENBANK LÖSCHEN (nur ausführen, wenn du die Daten neu aufbauen willst)
db.drop_tables()

# Tabellen mit Daten befüllen
points_table = db.table("points")
points_table.insert_multiple([
    { "name": "p1", "coords": [-25.0, 0.0], "fixed": False },
    { "name": "p2", "coords": [-35.0, 0.0], "fixed": True },
    { "name": "p3", "coords": [-60.0, 40.0], "fixed": False },
    { "name": "p4", "coords": [-68.0, -7.8], "fixed": True },
    { "name": "p5", "coords": [-62.0, -38.0], "fixed": False },
    { "name": "p6", "coords": [-72.0, -88.0], "fixed": False },
    { "name": "p7", "coords": [-84.0, -32.0], "fixed": False },
    { "name": "p8", "coords": [-95.0, 2.0], "fixed": False }
])

links_table = db.table("links")
links_table.insert_multiple([
    { "start": "p1", "end": "p2" },
    { "start": "p1", "end": "p3" },
    { "start": "p3", "end": "p4" },
    { "start": "p4", "end": "p5" },
    { "start": "p5", "end": "p1" },
    { "start": "p5", "end": "p6" },
    { "start": "p6", "end": "p7" },
    { "start": "p5", "end": "p7" },
    { "start": "p7", "end": "p8" },
    { "start": "p8", "end": "p3" },
    { "start": "p8", "end": "p4" }
])

drivers_table = db.table("drivers")
drivers_table.insert_multiple([])  # Falls später Daten hinzukommen

print("✅ Datenbank wurde erfolgreich initialisiert!")

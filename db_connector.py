import os
from tinydb import TinyDB

class DatabaseConnector:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.json')
            cls._instance = super(DatabaseConnector, cls).__new__(cls)
            cls._instance.db = TinyDB(db_path, encoding='utf-8', ensure_ascii=False)
        return cls._instance

    def get_table(self, table_name):
        """Ruft eine spezifische Tabelle aus der Datenbank ab."""
        return self.db.table(table_name)

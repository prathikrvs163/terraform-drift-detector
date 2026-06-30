import sqlite3
from pathlib import Path
from datetime import datetime


class DriftDatabase:

    def __init__(self):

        self.db_path = (
            Path(__file__).resolve().parent.parent / "drift_history.db"
        )

        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()

        self.create_table()

    def create_table(self):

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS drift_history (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            timestamp TEXT NOT NULL,

            resource TEXT NOT NULL,

            action TEXT NOT NULL,

            property TEXT NOT NULL,

            azure_value TEXT,

            terraform_value TEXT

        )
        """)

        self.connection.commit()

    def save_drift(self, resource):

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for change in resource["changes"]:

            self.cursor.execute("""
            INSERT INTO drift_history(

                timestamp,
                resource,
                action,
                property,
                azure_value,
                terraform_value

            )
            VALUES (?, ?, ?, ?, ?, ?)
            """, (

                timestamp,
                resource["resource"],
                resource["action"],
                change["property"],
                change["azure"],
                change["terraform"]

            ))

        self.connection.commit()

    def save_all(self, resources):

        for resource in resources:
            self.save_drift(resource)

    def close(self):

        self.connection.close()
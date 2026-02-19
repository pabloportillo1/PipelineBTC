"""
storage_filter.py
-----------------
Filter 5 - Storage Filter

Persists the fully processed transaction into a SQLite database.
This is the final stage of the pipeline — it saves all enriched data
produced by the previous filters into a permanent record.

Database: data/transactions.db (SQLite)
Table:    transactions
"""

import sqlite3
import uuid
import os
from datetime import datetime
from filters.base_filter import BaseFilter


class StorageFilter(BaseFilter):
    """
    Pipeline Filter #5 — Storage

    Responsibilities:
        - Initialize the SQLite database and create the transactions table if needed.
        - Generate a unique transaction ID (UUID4).
        - Insert the complete processed transaction record into the database.
        - Enrich the transaction with the generated ID, timestamp, and final status.
    """

    def __init__(self, db_path: str = "data/transactions.db"):
        """
        Initialize the storage filter and ensure the database is ready.

        Args:
            db_path (str): Path to the SQLite database file.
        """
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        """
        Create the transactions table if it does not already exist.
        Also ensures the data directory exists.
        """
        # Ensure the data directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    transaction_id   TEXT PRIMARY KEY,
                    user_id          TEXT    NOT NULL,
                    user_name        TEXT    NOT NULL,
                    user_email       TEXT    NOT NULL,
                    btc_amount       REAL    NOT NULL,
                    currency         TEXT    NOT NULL,
                    btc_price        REAL    NOT NULL,
                    subtotal         REAL    NOT NULL,
                    fee              REAL    NOT NULL,
                    total_with_fee   REAL    NOT NULL,
                    api_source       TEXT,
                    status           TEXT    NOT NULL,
                    timestamp        TEXT    NOT NULL
                )
            """)
            conn.commit()
        finally:
            conn.close()

        print(f"  ┌─ Database ready: '{self.db_path}'")

    def process(self, transaction: dict) -> dict:
        """
        Save the processed transaction to the SQLite database.

        Args:
            transaction (dict): Fully enriched transaction context from all previous filters.

        Returns:
            dict: Transaction enriched with:
                  - 'transaction_id': Unique UUID for this transaction
                  - 'timestamp'     : ISO-format datetime of storage
                  - 'status'        : Final status = 'completed'

        Raises:
            sqlite3.Error: If the database insert operation fails.
        """
        transaction_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()

        record = (
            transaction_id,
            transaction["user_id"],
            transaction.get("user_name", ""),
            transaction.get("user_email", ""),
            transaction["btc_amount"],
            transaction["currency"],
            transaction["btc_price"],
            transaction["subtotal"],
            transaction["fee"],
            transaction["total_with_fee"],
            transaction.get("api_source", ""),
            "completed",
            timestamp,
        )

        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO transactions (
                    transaction_id, user_id, user_name, user_email,
                    btc_amount, currency, btc_price,
                    subtotal, fee, total_with_fee,
                    api_source, status, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, record)
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            raise sqlite3.Error(
                f"[StorageFilter] Database error while saving transaction: {e}"
            )
        finally:
            conn.close()

        # --- Enrich transaction with final metadata ---
        transaction["transaction_id"] = transaction_id
        transaction["timestamp"] = timestamp
        transaction["status"] = "completed"

        print(f"  ├─ Record inserted into '{self.db_path}'")
        print(
            f"  └─ ✓ Storage complete | "
            f"Transaction ID: {transaction_id} | Timestamp: {timestamp}"
        )
        return transaction

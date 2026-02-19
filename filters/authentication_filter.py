"""
authentication_filter.py
------------------------
Filter 2 - Authentication Filter

Confirms the identity of the user by verifying their credentials
against a simulated user database (users.json — mock RDS/DynamoDB).

Checks:
    - User exists in the database.
    - User account is active (not suspended/disabled).
"""

import json
import os
from filters.base_filter import BaseFilter


class AuthenticationFilter(BaseFilter):
    """
    Pipeline Filter #2 — Authentication

    Responsibilities:
        - Load the user database from a JSON file (simulates an RDS/DynamoDB lookup).
        - Verify that the user_id exists in the database.
        - Verify that the user account is active.
        - Enrich the transaction with user profile data (name, email).
    """

    def __init__(self, users_db_path: str = "data/users.json"):
        """
        Initialize the filter and load the user database.

        Args:
            users_db_path (str): Path to the JSON file acting as the user database.
        """
        self.users_db_path = users_db_path
        self.users = {}
        self._load_users()

    def _load_users(self) -> None:
        """
        Load users from the JSON database file into memory.

        Raises:
            FileNotFoundError: If the users database file does not exist.
            ValueError: If the JSON structure is invalid.
        """
        if not os.path.exists(self.users_db_path):
            raise FileNotFoundError(
                f"[AuthenticationFilter] Users database not found at: '{self.users_db_path}'"
            )

        with open(self.users_db_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"[AuthenticationFilter] Invalid JSON in users database: {e}"
                )

        if "users" not in data or not isinstance(data["users"], list):
            raise ValueError(
                "[AuthenticationFilter] Users database must contain a 'users' list."
            )

        # Index users by user_id for O(1) lookup
        self.users = {user["user_id"]: user for user in data["users"]}
        print(f"  ┌─ User database loaded: {len(self.users)} users registered.")

    def process(self, transaction: dict) -> dict:
        """
        Authenticate the user against the database.

        Args:
            transaction (dict): Transaction context from the previous filter.

        Returns:
            dict: Transaction enriched with user profile data and 'authenticated' = True.

        Raises:
            PermissionError: If the user is not found or the account is inactive.
        """
        user_id = transaction["user_id"]

        # --- Check user existence ---
        if user_id not in self.users:
            raise PermissionError(
                f"[AuthenticationFilter] Authentication failed: "
                f"user '{user_id}' does not exist in the database."
            )

        user = self.users[user_id]

        # --- Check account status ---
        if not user.get("active", False):
            raise PermissionError(
                f"[AuthenticationFilter] Authentication failed: "
                f"user '{user_id}' ({user.get('name', 'Unknown')}) account is inactive/suspended."
            )

        # --- Enrich transaction with user data ---
        transaction["authenticated"] = True
        transaction["user_name"] = user["name"]
        transaction["user_email"] = user["email"]
        transaction["user_role"] = user.get("role", "unknown")

        print(
            f"  └─ ✓ Authentication passed | User: {user['name']} "
            f"({user_id}) | Role: {user.get('role', 'unknown')}"
        )
        return transaction

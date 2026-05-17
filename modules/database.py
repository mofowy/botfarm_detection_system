import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent.parent / "data" / "suspicious_accounts.db"


DEFAULT_SUSPICIOUS_ACCOUNTS = [
    (
        "acc_1",
        "high",
        "Повторювані повідомлення про приховування інформації та заклики до поширення контенту",
        "test_dataset"
    ),
    (
        "acc_2",
        "medium",
        "Повідомлення мають схожість із групою акаунтів, що поширюють тези про приховування фактів",
        "test_dataset"
    ),
    (
        "acc_4",
        "medium",
        "Схожі повідомлення із закликами до масового поширення інформації",
        "test_dataset"
    ),
    (
        "acc_6",
        "medium",
        "Текстова схожість з іншими акаунтами підозрілої групи",
        "test_dataset"
    ),
]


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_database():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS suspicious_accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id TEXT UNIQUE NOT NULL,
            risk_level TEXT NOT NULL,
            reason TEXT,
            source TEXT,
            added_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    connection.commit()
    connection.close()


def seed_database_if_empty():
    """
    Автоматично заповнює базу тестовими підозрілими акаунтами,
    якщо таблиця ще порожня. Кнопок для цього в інтерфейсі немає.
    """

    init_database()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM suspicious_accounts")
    count = cursor.fetchone()[0]

    if count == 0:
        cursor.executemany(
            """
            INSERT INTO suspicious_accounts
            (account_id, risk_level, reason, source)
            VALUES (?, ?, ?, ?)
            """,
            DEFAULT_SUSPICIOUS_ACCOUNTS
        )

    connection.commit()
    connection.close()


def find_suspicious_account(account_id):
    seed_database_if_empty()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT account_id, risk_level, reason, source, added_at
        FROM suspicious_accounts
        WHERE account_id = ?
        """,
        (account_id,)
    )

    result = cursor.fetchone()
    connection.close()

    return result

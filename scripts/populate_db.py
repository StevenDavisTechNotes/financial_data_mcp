#!python3
# usage: python scripts\populate_db.py --data <data_type>
import argparse
import os
import sqlite3
import random
import string

DB_FILE: str = "data.db"
# Assumed to be in the same directory as the script
STAR_WARS_SQL_FILE: str = "scripts/star_wars.sql"


def generate_random_string(
        length: int,
        chars: str = string.ascii_uppercase + string.digits,
) -> str:
    """Generates a random string."""
    return ''.join(random.choices(chars, k=length))


def populate_financial_data(cursor: sqlite3.Cursor) -> None:
    """Creates and populates tables with financial data."""
    # Create tables
    cursor.execute('''
        CREATE TABLE account (
            acct_cd TEXT PRIMARY KEY,
            mkt_val REAL
        )
    ''')
    cursor.execute('''
        CREATE TABLE issuer (
            issuer_cd TEXT PRIMARY KEY
        )
    ''')
    cursor.execute('''
        CREATE TABLE investable (
            sec_id TEXT PRIMARY KEY,
            cusip TEXT UNIQUE,
            mkt_price REAL,
            beta_value REAL,
            duration REAL,
            issuer_cd TEXT,
            FOREIGN KEY (issuer_cd) REFERENCES issuer(issuer_cd)
        )
    ''')
    cursor.execute('''
        CREATE TABLE investment (
            acct_cd TEXT,
            sec_id TEXT,
            weight REAL,
            PRIMARY KEY (acct_cd, sec_id),
            FOREIGN KEY (acct_cd) REFERENCES account(acct_cd),
            FOREIGN KEY (sec_id) REFERENCES investable(sec_id)
        )
    ''')

    # Populate account table
    accounts_data: list[tuple[str, float]] = []
    account_ids: list[str] = []
    for i in range(1, 11):  # 10 accounts
        acct_cd: str = f"ACCT{i:003d}"
        account_ids.append(acct_cd)
        mkt_val: float = round(random.uniform(100000, 5000000), 2)
        accounts_data.append((acct_cd, mkt_val))
    cursor.executemany(
        "INSERT INTO account (acct_cd, mkt_val) VALUES (?, ?)", accounts_data)

    # Populate issuer table
    issuers_data: list[tuple[str]] = []
    generated_issuer_cds: set[str] = set()
    for _ in range(5):  # 5 issuers
        while True:
            issuer_cd: str = (
                "ISS_"
                + generate_random_string(4, string.ascii_uppercase)
            )
            if issuer_cd not in generated_issuer_cds:
                generated_issuer_cds.add(issuer_cd)
                issuers_data.append((issuer_cd,))
                break
    cursor.executemany(
        "INSERT INTO issuer (issuer_cd) VALUES (?)", issuers_data)
    issuer_cd_list: list[str] = sorted(generated_issuer_cds)

    # Populate investable table
    investables_data: list[tuple[str, str, str, float, float, float]] = []
    security_ids: list[str] = []
    generated_cusips: set[str] = set()
    for i in range(1, 21):  # 20 securities
        sec_id: str = f"SEC{i:004d}"
        security_ids.append(sec_id)

        while True:
            cusip: str = generate_random_string(9)
            if cusip not in generated_cusips:
                generated_cusips.add(cusip)
                break

        mkt_price: float = round(random.uniform(10, 1000), 2)
        beta_value: float = round(random.uniform(0.5, 2.5), 4)
        duration: float = round(random.uniform(1, 10), 2)
        # Randomly assign an issuer_cd from the populated issuers
        assigned_issuer_cd: str = random.choice(issuer_cd_list)

        investables_data.append(
            (sec_id, assigned_issuer_cd, cusip,
             mkt_price, beta_value, duration))
    cursor.executemany(
        """
        INSERT INTO investable
        (sec_id, issuer_cd, cusip, mkt_price, beta_value, duration)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        investables_data
    )

    # Populate investment table
    investments_data: list[tuple[str, str, float]] = []
    for acct_cd in account_ids:
        # Each account holds 2 to 5 securities
        num_investments: int = random.randint(2, min(5, len(security_ids)))
        if not security_ids:
            continue

        chosen_securities: list[str] = random.sample(
            security_ids, num_investments)
        for sec_id in chosen_securities:
            weight: float = round(random.uniform(0.05, 0.3),
                                  4)  # Weights between 5% and 30%
            investments_data.append((acct_cd, sec_id, weight))

    # Use INSERT OR IGNORE in case of any (unlikely) duplicate
    # (acct_cd, sec_id) pairs from random sampling logic
    cursor.executemany(
        """
        INSERT OR IGNORE INTO investment
        (acct_cd, sec_id, weight)
        VALUES (?, ?, ?)
        """, investments_data)


def main() -> None:
    parser = argparse.ArgumentParser(description="Populate a SQLite database.")
    parser.add_argument(
        "--data",
        choices=["blank", "star-wars", "financial"],
        required=True,
        help="Type of data to populate the database with."
    )
    args: argparse.Namespace = parser.parse_args()

    # Remove existing database file
    try:
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
            print(f"Removed existing database '{DB_FILE}'.")
    except Exception as e:
        print(f"Error removing existing database '{DB_FILE}': {e}")
        return

    conn: sqlite3.Connection | None = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor: sqlite3.Cursor = conn.cursor()
        print(f"Successfully created database '{DB_FILE}'.")

        if args.data == "blank":
            # No tables to create for a blank database
            print("Database is blank as requested.")

        elif args.data == "star-wars":
            print(
                "Attempting to populate database from"
                f" '{STAR_WARS_SQL_FILE}'...")
            try:
                with open(STAR_WARS_SQL_FILE, 'r') as f:
                    sql_script: str = f.read()
                cursor.executescript(sql_script)
                print("Database populated with Star Wars data.")
            except FileNotFoundError:
                print(
                    f"Error: SQL script file '{STAR_WARS_SQL_FILE}' not found."
                    " Star Wars data not populated.")
            except sqlite3.Error as e:
                print(f"SQLite error during Star Wars data population: {e}")

        elif args.data == "financial":
            print("Populating database with financial data...")
            try:
                populate_financial_data(cursor)
                print("Database populated with financial data.")
            except sqlite3.Error as e:
                print(f"SQLite error during financial data population: {e}")

        conn.commit()
        print(
            f"Operation complete. Database '{DB_FILE}' processed"
            f" for '{args.data}' data type.")

    except sqlite3.Error as e:
        print(f"A database error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print(f"Database connection to '{DB_FILE}' closed.")


if __name__ == "__main__":
    main()

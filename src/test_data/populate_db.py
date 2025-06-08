#!python3
# usage: python -m src.test_data.populate_db --data <data_type>
import argparse
import os
import sqlite3
import random
import string
import math  # Import math module
from dataclasses import dataclass, astuple  # Import dataclass and astuple

DB_FILE: str = "data.db"
# Assumed to be in the same directory as the script
STAR_WARS_SQL_FILE: str = "src/test_data/star_wars.sql"

CASH_ISSUER_CD = "CASH"
CASH_SEC_ID = "CASH"
CASH_CUSIP = "CASH"


@dataclass
class InvestmentRecord:
    acct_cd: str
    sec_id: str
    weight: float


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
        CREATE TABLE security (
            sec_id TEXT PRIMARY KEY,
            issuer_cd TEXT,
            cusip TEXT UNIQUE,
            mkt_price REAL,
            beta_value REAL,
            duration REAL,
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
            FOREIGN KEY (sec_id) REFERENCES security(sec_id)
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

    # Add CASH issuer first
    issuers_data.append((CASH_ISSUER_CD,))
    generated_issuer_cds.add(CASH_ISSUER_CD)

    for _ in range(4):  # 4 more random issuers to make a total of 5
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
    # Convert set to list before sorting
    issuer_cd_list: list[str] = sorted(list(generated_issuer_cds))

    # Populate security table
    securities_data: list[tuple[str, str, str, float, float, float]] = []
    security_ids: list[str] = []
    generated_cusips: set[str] = set()

    # Add CASH security first
    cash_security_tuple = (CASH_SEC_ID, CASH_ISSUER_CD,
                           CASH_CUSIP, 1.0, 0.0, 0.0)
    securities_data.append(cash_security_tuple)
    security_ids.append(CASH_SEC_ID)
    generated_cusips.add(CASH_CUSIP)

    for i in range(1, 20):  # 19 more random securities to make a total of 20
        sec_id: str = f"SEC{i:004d}"  # Starts from SEC0001 up to SEC0019
        security_ids.append(sec_id)

        while True:
            cusip: str = generate_random_string(9)
            if cusip not in generated_cusips:
                generated_cusips.add(cusip)
                break

        # Randomly assign an issuer_cd from the populated issuers (can include CASH, or filter it out if needed)
        # For simplicity, allowing random securities to also be issued by "CASH" or other issuers.
        # If CASH issuer should only issue CASH security, filter CASH_ISSUER_CD from random assignment.
        random_issuer_cd_list = [icd for icd in issuer_cd_list if icd != CASH_ISSUER_CD] if len(
            issuer_cd_list) > 1 else issuer_cd_list
        assigned_issuer_cd: str = random.choice(
            random_issuer_cd_list if random_issuer_cd_list else [CASH_ISSUER_CD])

        mkt_price: float = round(random.uniform(10, 1000), 2)
        beta_value: float = round(random.uniform(0.5, 2.5), 4)
        duration: float = round(random.uniform(1, 10), 2)

        securities_data.append(
            (sec_id, assigned_issuer_cd, cusip,
             mkt_price, beta_value, duration))
    cursor.executemany(
        """
        INSERT INTO security
        (sec_id, issuer_cd, cusip, mkt_price, beta_value, duration)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        securities_data
    )

    # Populate investment table
    investments_data_objects: list[InvestmentRecord] = []
    other_security_ids = [sid for sid in security_ids if sid != CASH_SEC_ID]

    for acct_cd in account_ids:
        total_available_other_securities = len(other_security_ids)

        if total_available_other_securities == 0:
            # Only CASH security is available, or no other securities to choose from
            investments_data_objects.append(InvestmentRecord(
                acct_cd=acct_cd, sec_id=CASH_SEC_ID, weight=1.0))
            continue

        # Determine the number of *additional* investments from other_security_ids
        lower_bound_raw = 0.20 * total_available_other_securities
        upper_bound_raw = 0.80 * total_available_other_securities

        min_additional_investments = math.ceil(lower_bound_raw)
        max_additional_investments = math.floor(upper_bound_raw)

        # Must pick at least 1 other if available
        min_additional_investments = max(1, int(min_additional_investments))
        max_additional_investments = min(
            total_available_other_securities, int(max_additional_investments))

        if min_additional_investments > max_additional_investments:
            max_additional_investments = min_additional_investments

        max_additional_investments = min(
            max_additional_investments, total_available_other_securities)

        num_additional_investments: int
        # Should not happen if total_available_other_securities > 0 due to min_additional_investments = max(1,...)
        if max_additional_investments == 0:
            # Fallback, though logic aims to prevent this if others available
            num_additional_investments = 0
        elif min_additional_investments > max_additional_investments:  # Should be resolved
            num_additional_investments = min_additional_investments if min_additional_investments > 0 else 0
        else:
            num_additional_investments = random.randint(
                min_additional_investments, max_additional_investments)

        if num_additional_investments == 0:
            # No additional securities chosen, so CASH gets 100%
            investments_data_objects.append(InvestmentRecord(
                acct_cd=acct_cd, sec_id=CASH_SEC_ID, weight=1.0))
        else:
            # Invest 10% in CASH
            investments_data_objects.append(InvestmentRecord(
                acct_cd=acct_cd, sec_id=CASH_SEC_ID, weight=0.1))
            remaining_weight_to_distribute = 0.9

            chosen_other_securities: list[str] = random.sample(
                other_security_ids, num_additional_investments)

            calculated_weights: list[float]
            if num_additional_investments == 1:  # Only one other security to give the remaining 0.9
                calculated_weights = [remaining_weight_to_distribute]
            else:
                raw_proportions = [random.uniform(
                    0.05, 1.0) for _ in range(num_additional_investments)]
                total_proportion = sum(raw_proportions)

                scaled_target_sum = int(
                    remaining_weight_to_distribute * 10000)  # e.g. 9000 for 0.9

                if total_proportion == 0:  # Fallback, highly unlikely
                    equal_weight = round(
                        remaining_weight_to_distribute / num_additional_investments, 4)
                    calculated_weights = [equal_weight] * \
                        num_additional_investments
                    current_sum_of_equal_weights = sum(calculated_weights[:-1])
                    calculated_weights[-1] = round(
                        remaining_weight_to_distribute - current_sum_of_equal_weights, 4)
                else:
                    exact_scaled_weights = [
                        (p / total_proportion) * scaled_target_sum for p in raw_proportions]
                    rounded_down_scaled_weights = [
                        int(sw) for sw in exact_scaled_weights]
                    sum_of_rounded_down = sum(rounded_down_scaled_weights)
                    points_to_distribute = scaled_target_sum - sum_of_rounded_down

                    fractional_parts_with_indices = sorted(
                        [(exact_scaled_weights[i] - rounded_down_scaled_weights[i], i)
                         for i in range(num_additional_investments)],
                        reverse=True
                    )

                    for j in range(points_to_distribute):
                        idx_to_increment = fractional_parts_with_indices[j %
                                                                         num_additional_investments][1]
                        rounded_down_scaled_weights[idx_to_increment] += 1

                    calculated_weights = [
                        sw / 10000.0 for sw in rounded_down_scaled_weights]

            for i, sec_id_other in enumerate(chosen_other_securities):
                weight_to_assign = calculated_weights[i]
                investments_data_objects.append(InvestmentRecord(
                    acct_cd=acct_cd, sec_id=sec_id_other, weight=weight_to_assign))

    # Convert list of dataclass objects to list of tuples for executemany
    # This part was updated in a previous step to use a generator expression
    # For clarity, ensuring it's compatible:
    investments_data_tuples = [astuple(record)
                               for record in investments_data_objects]

    # Use INSERT OR IGNORE in case of any (unlikely) duplicate
    # (acct_cd, sec_id) pairs from random sampling logic
    cursor.executemany(
        """
        INSERT OR IGNORE INTO investment
        (acct_cd, sec_id, weight)
        VALUES (?, ?, ?)
        """,
        investments_data_tuples,  # Use the generated list of tuples
    )


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

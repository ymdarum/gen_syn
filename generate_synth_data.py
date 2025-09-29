#!/usr/bin/env python3
"""
Synthetic Data Generator for Customer Profile & Transactions

Reads rules/value references from an Excel file (sheets: requirement, profile_tbl, transaction_tbl, occu, state),
then generates two CSVs:
 - CUSTOMER_PROFILE_YYYYMMDD.csv (profile_tbl)
 - CUSTOMER_TXN_YYYYMMDD.csv     (transaction_tbl)

Usage:
  python generate_synth_data.py --rules rule_to_observe.xlsx --profiles 1000 --avg_txn 15 --seed 42 --outdir output

"""
import argparse, os, string
from datetime import datetime, timedelta, timezone
import pandas as pd
import numpy as np

def read_rules(xlsx_path: str):
    with pd.ExcelFile(xlsx_path) as xls:
        sheets = {name: xls.parse(sheet_name=name) for name in xls.sheet_names}
    # Extract occupation list
    occu = []
    if "occu" in sheets:
        occu_df = sheets["occu"]
        for col in occu_df.columns:
            occu += [str(v).strip() for v in occu_df[col].dropna().tolist() if str(v).strip()]
        occu = [o for o in occu if o.lower() != 'nan']
    # Extract states
    states = []
    if "state" in sheets:
        state_df = sheets["state"]
        for col in state_df.columns:
            states += [str(v).strip() for v in state_df[col].dropna().tolist() if str(v).strip()]
        states = [s for s in states if s.lower() != 'nan']
    # Date range for txns
    txn_start = datetime(2024,1,1, tzinfo=timezone.utc)
    txn_end   = datetime(2025,9,24, tzinfo=timezone.utc)  # today's date (UTC)
    # Channels
    channels = ["QR P2P", "DuitNOW", "Credit Transfer", "QR POS", "Other"]
    return {
        "occu": occu or ["TEACHER/LECTURER","ENGINEER","DOCTOR","NURSE","DRIVER","HOUSEWIFE","STUDENT","CHEF","POLICE","ARMY","CASHIER","FARMER","RETIREE"],
        "states": states or ["Johor","Kedah","Kelantan","Melaka","Negeri Sembilan","Pahang","Pulau Pinang","Perak","Perlis","Selangor","Terengganu","Sabah","Sarawak","WP KL","WP Labuan","WP Putrajaya"],
        "txn_start": txn_start,
        "txn_end": txn_end,
        "channels": channels
    }

_ALPHABET = np.array(list(string.ascii_uppercase + string.ascii_lowercase + string.digits))


def rand_alnum(n, rng: np.random.Generator):
    idx = rng.integers(0, len(_ALPHABET), size=n)
    return ''.join(_ALPHABET[idx])


def make_customer_id(rng: np.random.Generator):
    suffix_len = max(1, 10 - len("CUST_"))
    return "CUST_" + rand_alnum(suffix_len, rng)


def make_account_id(rng: np.random.Generator):
    suffix_len = max(1, 12 - len("CACC_"))
    return "CACC_" + rand_alnum(suffix_len, rng)


def make_txn_id(rng: np.random.Generator):
    suffix_len = max(1, 15 - len("TXN_"))
    return "TXN_" + rand_alnum(suffix_len, rng)

def random_timestamp_utc(start_dt, end_dt, rng: np.random.Generator):
    delta = int((end_dt - start_dt).total_seconds())
    if delta <= 0:
        return start_dt.isoformat().replace("+00:00","Z")
    sec = int(rng.integers(0, delta))
    ts = start_dt + timedelta(seconds=sec)
    return ts.isoformat().replace("+00:00","Z")

def generate_profiles(n_customers, rules, rng: np.random.Generator):
    occu = rules["occu"]
    states = rules["states"]
    profiles = []
    used_cust = set()
    used_acc = set()
    for _ in range(n_customers):
        cid = make_customer_id(rng)
        while cid in used_cust:
            cid = make_customer_id(rng)
        used_cust.add(cid)

        acc = make_account_id(rng)
        while acc in used_acc:
            acc = make_account_id(rng)
        used_acc.add(acc)
        
        age = int(rng.integers(10, 100))  # 10-99 inclusive
        occupation = str(rng.choice(occu)).upper()
        state = str(rng.choice(states))
        tenure = int(rng.integers(5, 241))  # 5-240 inclusive
        acct_type = str(rng.choice(["CA", "SA"]))
        avg_bal = float(np.round(rng.uniform(100, 1_000_000), 2))
        
        profiles.append({
            "Customer_ID": cid,
            "Customer_Acc": acc,
            "Age": age,
            "Stated_Occupation": occupation,
            "Location_State": state,
            "Account_Tenure_Months": tenure,
            "Account_Type": acct_type,
            "Avg_Balance": avg_bal,
        })
    return pd.DataFrame(profiles)

FIRST_NAMES = [
    "Adam", "Aisha", "Daniel", "Hana", "Irfan", "Nurul", "Zara",
    "Farid", "Azlan", "Siti", "John", "Jane", "Ali", "Fatimah",
    "Kumar", "Rajesh", "Mei Ling", "Wei", "Chong", "Liyana",
    "Amir", "Syafiq", "Farah", "Suresh", "Vijaya", "Anand",
]

LAST_NAMES = [
    "Rahman", "Abdullah", "Tan", "Lim", "Lee", "Ng", "Wong",
    "Ismail", "Hussin", "Hashim", "Doe", "Kaur", "Singh", "Chan",
    "Ong", "Gopal", "Subramaniam", "Mohamed", "Salleh", "Ahmad"
]

COMPANY_PREFIXES = ["Kedai", "Restoran", "Warung", "Syarikat", "Perusahaan", "Bengkel", "Online"]
COMPANY_SUFFIXES = ["Maju", "Jaya", "Sentosa", "Makmur", "Bestari", "Hebat", "Sejahtera", "Baroena"]


def generate_txns(profile_df, avg_txn, rules, rng: np.random.Generator):
    channels = rules["channels"]
    start_dt = rules["txn_start"]
    end_dt = rules["txn_end"]
    txns = []
    lam = max(1, avg_txn)
    for _, row in profile_df.iterrows():
        n_txn = max(1, int(rng.poisson(lam)))
        acc = row["Customer_Acc"]
        for _ in range(n_txn):
            txn_id = make_txn_id(rng)
            ts = random_timestamp_utc(start_dt, end_dt, rng)
            amount = float(np.round(rng.uniform(100, 1_000_000), 2))
            ttype = str(rng.choice(["credit", "debit"]))
            channel = str(rng.choice(channels))

            # Randomly pick Malaysian-like personal or company names
            if rng.random() < 0.8:
                cp_name = f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"
            else:
                company_prefix = rng.choice(COMPANY_PREFIXES)
                company_suffix = rng.choice(COMPANY_SUFFIXES)
                cp_name = f"{company_prefix} {company_suffix}"

            cp_acc = make_account_id(rng)
            txns.append({
                "Customer_Acc": acc,
                "Transaction_ID": txn_id,
                "Timestamp": ts,
                "Amount": amount,
                "Type": ttype,
                "Channel": channel,
                "Counterparty_Name": cp_name,
                "Counterparty_Account": cp_acc
            })
    return pd.DataFrame(txns)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rules", required=True, help="Path to the Excel rules file (rule_to_observe.xlsx)")
    parser.add_argument("--profiles", type=int, default=1000, help="Number of customer profiles to generate")
    parser.add_argument("--avg_txn", type=int, default=15, help="Average number of transactions per customer (Poisson)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--outdir", default="output", help="Output directory")
    args = parser.parse_args()
    
    rng = np.random.default_rng(args.seed)
    rules = read_rules(args.rules)
    os.makedirs(args.outdir, exist_ok=True)

    profile_df = generate_profiles(args.profiles, rules, rng)
    txn_df = generate_txns(profile_df, args.avg_txn, rules, rng)
    
    today = datetime.utcnow().strftime("%Y%m%d")
    profile_path = os.path.join(args.outdir, f"CUSTOMER_PROFILE_{today}.csv")
    txn_path = os.path.join(args.outdir, f"CUSTOMER_TXN_{today}.csv")
    
    profile_df.to_csv(profile_path, index=False)
    txn_df.to_csv(txn_path, index=False)
    
    print(f"Generated {len(profile_df)} profiles -> {profile_path}")
    print(f"Generated {len(txn_df)} transactions -> {txn_path}")
    print("Done.")

if __name__ == "__main__":
    main()

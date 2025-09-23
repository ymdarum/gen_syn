#!/usr/bin/env python3
"""
Generate synthetic data from an Excel rules file with realistic balances, tenure-aware averages,
ID prefixes, and optional MCAR missingness.

USAGE
-----
python generate_synthetic_from_rules_v2.py \
  --rules rule_to_observe.xlsx \
  --out synthetic_data.csv \
  --rows 1000 \
  --seed 42 \
  --enable-mcar \
  --mcar-rate-occ 0.08 \
  --mcar-rate-acctype 0.01 \
  --mcar-rate-age 0.02

Excel layout expected:
- Sheet 'field_req' with columns: field, data type, rule, range
  Examples:
    cust_id | string | random 8 digit number        | 10000000 - 99999999
    Customer_Acc | string | random 14 digit number  | 10000000000000 - 99999999999999
    Stated_Occupation | string | based on listing occu | based on listing
    Account_Type | string | based on listing acc_type | based on listing
    Age | int | random 2 digit number | 10 - 99
    Account_Tenure_Months | int | range | 1 - 180
- Sheet 'acc_type' : single column list of valid account types
- Sheet 'occu'     : single column list of valid occupations
"""
import argparse, re, math
from pathlib import Path

import numpy as np
import pandas as pd


# -----------------------------
# Helpers
# -----------------------------
def values_from_singlecol(df: pd.DataFrame):
    col = df.columns[0]
    vals = df[col].dropna().astype(str).str.strip()
    # de-duplicate while preserving order
    return [v for v in dict.fromkeys(vals) if v]


def digits_only(s: str) -> str:
    return ''.join(ch for ch in str(s) if ch.isdigit())


def rand_int_range(rng, low: int, high: int, size: int):
    return rng.integers(low, high + 1, size=size)


def rand_numeric_string(rng, low: int, high: int, size: int):
    nums = rng.integers(low, high + 1, size=size)
    return [str(n) for n in nums]


def sample_from_list(rng, lst, size: int):
    # safe sampling even if lst has 1 item
    return list(rng.choice(lst, size=size, replace=True))


# -----------------------------
# Core generation
# -----------------------------
def generate_from_rules(xl: pd.ExcelFile, rows: int, seed: int,
                        enable_mcar: bool,
                        mcar_rate_occ: float,
                        mcar_rate_acctype: float,
                        mcar_rate_age: float) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    # Load sheets
    field_req = xl.parse('field_req')
    acc_types_list = values_from_singlecol(xl.parse('acc_type'))
    occupations_list = values_from_singlecol(xl.parse('occu'))

    # Create empty frame
    df = pd.DataFrame(index=range(rows))

    # Generate columns based on 'field_req' rules
    for _, row in field_req.iterrows():
        field = row.get('field')
        dtype = str(row.get('data type')).strip().lower()
        rule = str(row.get('rule')).strip().lower()
        rng_text = str(row.get('range')).strip()

        if not isinstance(field, str) or not field:
            continue

        # Listing-based
        if 'based on listing' in rule and 'occu' in rule:
            df[field] = sample_from_list(rng, occupations_list, rows)
            continue
        if 'based on listing' in rule and ('acc_type' in rule or 'account_type' in str(field).lower() or 'account' in str(field).lower()):
            df[field] = sample_from_list(rng, acc_types_list, rows)
            continue

        # Numeric ranges like "10000000 - 99999999"
        if ('random' in rule or 'range' in rule) and '-' in rng_text:
            try:
                parts = [p.strip() for p in rng_text.split('-')]
                low, high = int(parts[0]), int(parts[1])
                vals = rand_int_range(rng, low, high, rows)
                if dtype == 'string':
                    width = max(len(parts[0]), len(parts[1]))
                    df[field] = pd.Series(vals).astype(str).str.zfill(width)
                else:
                    df[field] = vals
                continue
            except Exception:
                pass

        # Fallback: detect "N digit"
        if 'digit' in rule:
            m = re.search(r'(\d+)\s*digit', rule)
            if m:
                width = int(m.group(1))
                low = 10**(width-1)
                high = (10**width) - 1
                vals = rand_numeric_string(rng, low, high, rows)
                if dtype == 'string':
                    df[field] = [v.zfill(width) for v in vals]
                else:
                    df[field] = [int(v) for v in vals]
                continue

        # Another fallback for simple int 2-digit
        if dtype in ('int','integer','number') and '2 digit' in rule:
            df[field] = rand_int_range(rng, 10, 99, rows)
            continue

        # If nothing matched, put blanks
        df[field] = sample_from_list(rng, [''], rows)

    # --------------------------------------
    # ID uniqueness & prefixes
    # --------------------------------------
    def enforce_unique_and_format(df: pd.DataFrame, col: str, width: int, prefix: str):
        if col not in df.columns:
            return
        # Convert to digits only, fill if empty
        s = df[col].astype(str).apply(digits_only)
        # If all empty (e.g., rules didn't generate), generate fresh
        if (s.str.len() == 0).all():
            low = 10**(width-1)
            high = (10**width) - 1
            s = pd.Series(rand_numeric_string(rng, low, high, len(df)))
        else:
            # Ensure numeric; non-numeric -> random fallback
            def safe_int(x):
                try:
                    return int(x)
                except Exception:
                    return int(''.join(rand_numeric_string(rng, 10**(width-1), (10**width)-1, 1)))
            s = s.apply(lambda x: str(safe_int(x)).zfill(width))

        # Uniqueness: perturb duplicates
        tmp = s.astype(int)
        while tmp.duplicated().any():
            dups = tmp.duplicated()
            tmp.loc[dups] = tmp.loc[dups] + rng.integers(1, 999, size=dups.sum())
        s = tmp.astype(str).str.zfill(width)

        df[col] = prefix + s

    enforce_unique_and_format(df, 'cust_id', 8, 'cust_')
    enforce_unique_and_format(df, 'Customer_Acc', 14, 'acc_')

    # --------------------------------------
    # Balance (by account type) & tenure-aware Average_Balance
    # --------------------------------------
    # Type ranges (domain-ish priors)
    type_ranges = {
        "GIA": (5_000, 150_000),
        "GIA AWFAR": (10_000, 200_000),
        "Al-AWFAR": (2_000, 80_000),
        "IHSAN": (500, 20_000),
        "STDT": (15_000, 200_000),
    }

    def sample_balance(at: str):
        at = (at or "").strip()
        low, high = type_ranges.get(at, (2_000, 80_000))
        # Log-uniform for realism (heavy right tail)
        log_low, log_high = math.log(low+1), math.log(high+1)
        val = math.exp(rng.uniform(log_low, log_high)) - 1
        return int(max(low, min(val, high)))

    # Ensure Account_Type exists; if not, sample from list
    if 'Account_Type' not in df.columns:
        df['Account_Type'] = sample_from_list(rng, acc_types_list or ["GIA"], rows)

    df['Balance'] = df['Account_Type'].apply(sample_balance)

    # Minor softness: Age < 18 → cap lower balances
    if 'Age' in df.columns:
        ages = pd.to_numeric(df['Age'], errors='coerce')
        minors_mask = ages < 18
        n_minors = minors_mask.fillna(False).sum()
        if n_minors:
            cap_vals = rand_int_range(rng, 100, 8_000, n_minors)
            df.loc[minors_mask.fillna(False), 'Balance'] = np.minimum(df.loc[minors_mask.fillna(False), 'Balance'], cap_vals)

    # Tenure
    if 'Account_Tenure_Months' in df.columns:
        tenure = pd.to_numeric(df['Account_Tenure_Months'], errors='coerce').fillna(0).clip(lower=0)
    else:
        tenure = pd.Series(rand_int_range(rng, 1, 180, rows))

    # Tenure-aware average ratio: approaches ~0.9 as tenure grows
    tenure_factor = 0.35 + 0.55 * (1 - np.exp(-tenure / 36.0))
    noise = rng.normal(0, 0.03, size=rows).clip(-0.05, 0.05)
    avg_ratio = np.clip(tenure_factor + noise, 0.25, 0.92)

    df['Average_Balance'] = (df['Balance'] * avg_ratio).astype(int)
    # Guarantee strictly less than Balance
    ge_mask = df['Average_Balance'] >= df['Balance']
    if ge_mask.any():
        df.loc[ge_mask, 'Average_Balance'] = df.loc[ge_mask, 'Balance'] - rand_int_range(rng, 1, 50, ge_mask.sum())

    # Keep only two balance columns
    to_drop = [c for c in df.columns if 'balance' in c.lower() and c not in ['Balance', 'Average_Balance']]
    df = df.drop(columns=to_drop, errors='ignore')

    # --------------------------------------
    # Optional MCAR missingness
    # --------------------------------------
    if enable_mcar:
        mcar_cfg = {
            'Stated_Occupation': mcar_rate_occ,
            'Account_Type': mcar_rate_acctype,
            'Age': mcar_rate_age,
        }
        for col, rate in mcar_cfg.items():
            if col in df.columns and float(rate) > 0:
                mask = np.array(rng.random(rows) < float(rate))
                if mask.any():
                    df.loc[mask, col] = pd.NA

    return df


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--rules', required=True, help='Path to Excel rules file')
    ap.add_argument('--out', required=True, help='Output CSV path')
    ap.add_argument('--rows', type=int, default=1000, help='Number of rows')
    ap.add_argument('--seed', type=int, default=42, help='Random seed')

    # MCAR switches
    ap.add_argument('--enable-mcar', action='store_true', help='Enable MCAR missingness')
    ap.add_argument('--mcar-rate-occ', type=float, default=0.08, help='MCAR rate for Stated_Occupation')
    ap.add_argument('--mcar-rate-acctype', type=float, default=0.01, help='MCAR rate for Account_Type')
    ap.add_argument('--mcar-rate-age', type=float, default=0.02, help='MCAR rate for Age')

    args = ap.parse_args()

    xl = pd.ExcelFile(args.rules)
    df = generate_from_rules(
        xl=xl,
        rows=args.rows,
        seed=args.seed,
        enable_mcar=args.enable_mcar,
        mcar_rate_occ=args.mcar_rate_occ,
        mcar_rate_acctype=args.mcar_rate_acctype,
        mcar_rate_age=args.mcar_rate_age,
    )

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out, index=False)
    print(f"Wrote {len(df)} rows to {args.out}")


if __name__ == '__main__':
    main()

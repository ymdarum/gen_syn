# Synthetic Data Generator

This project provides a **Python-based synthetic data generator** driven by simple Excel rule sheets.  
It is designed to create **realistic banking-style datasets** with configurable missingness (MCAR).

---

## 📂 Project Structure

```
.
├── generate_synthetic_from_rules_v2.py   # Main generator script
├── requirements.txt                      # Dependencies
├── rule_to_observe.xlsx                  # Input rule definitions
├── sample_output.csv                     # Example generated dataset
└── README.md                             # Documentation
```

---

## ⚙️ Setup

1. **Clone or download this repository**
   ```bash
   git clone https://github.com/yourusername/synthetic-data-generator.git
   cd synthetic-data-generator
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

---

## 🚀 Usage

### Generate without missing values
```bash
python generate_synthetic_from_rules_v2.py \
  --rules rule_to_observe.xlsx \
  --out synthetic_data_no_mcar.csv \
  --rows 1000 \
  --seed 42
```

### Generate with MCAR missingness
```bash
python generate_synthetic_from_rules_v2.py \
  --rules rule_to_observe.xlsx \
  --out synthetic_data_mcar.csv \
  --rows 1000 \
  --seed 42 \
  --enable-mcar \
  --mcar-rate-occ 0.08 \
  --mcar-rate-acctype 0.01 \
  --mcar-rate-age 0.02
```

- `--rows`: number of records to generate (default: 1000)  
- `--seed`: reproducibility seed (default: 42)  
- `--enable-mcar`: toggle to inject MCAR missing values  
- `--mcar-rate-*`: configure missingness rates for specific columns  

---

## 📋 Rules Implemented

### A. Rule-driven generation
1. **Excel sheets expected**
   - `field_req` → defines field, data type, rule, and range  
   - `acc_type` → valid account types  
   - `occu` → valid occupations
2. **Listing-based fields**
   - `Stated_Occupation` → sampled from `occu` list  
   - `Account_Type` → sampled from `acc_type` list
3. **Range-based fields**
   - If `range` is `"min - max"`, values sampled uniformly in `[min, max]`  
   - If type is `string`, numbers are zero-padded
4. **Digit-based fallback**
   - If rule says `"N digit"`, generate `N`-digit values
5. **2-digit int fallback**
   - If rule says `"2 digit number"`, generate 10–99

---

### B. ID formatting
6. **`cust_id`**
   - Always unique, 8 digits, prefixed `cust_` → `cust_12345678`
7. **`Customer_Acc`**
   - Always unique, 14 digits, prefixed `acc_` → `acc_12345678901234`

---

### C. Balance realism
8. **Final dataset has only 2 balance columns**
   - `Balance`, `Average_Balance`
9. **Balance ranges by Account Type**
   - `GIA`: 5,000 – 150,000  
   - `GIA AWFAR`: 10,000 – 200,000  
   - `Al-AWFAR`: 2,000 – 80,000  
   - `IHSAN`: 500 – 20,000  
   - `STDT`: **20,000 – 100,000** ✅ *(updated)*  
   - Default: 2,000 – 80,000
10. **Minors (Age < 18)** → balances softly capped ≤ 8,000  
11. **Average_Balance**
    - Tenure-aware: closer to Balance as tenure grows  
    - Formula: `Balance × ratio`, where `ratio ∈ [0.25, 0.92]` increases with tenure  
    - Noise ±3% included for realism  
12. Always enforces `Average_Balance < Balance`

---

### D. Missingness (optional MCAR)
13. Controlled with `--enable-mcar`  
14. Configurable rates:
    - `Stated_Occupation`: default 8%  
    - `Account_Type`: default 1%  
    - `Age`: default 2%  
15. IDs and balances are **never** missing  
16. MCAR = values dropped completely at random, independent of other columns

---

## 📊 Example Output

| cust_id     | Customer_Acc      | Stated_Occupation | Account_Type | Age | Account_Tenure_Months | Balance | Average_Balance |
|-------------|------------------|-------------------|--------------|-----|-----------------------|---------|-----------------|
| cust_12345678 | acc_12345678901234 | Teacher          | GIA          | 45  | 120                   | 82,450  | 72,389          |
| cust_87654321 | acc_98765432109876 | Pensioner        | STDT         | 20  | 24                    | 45,238  | 18,550          |

---

## 📝 Notes
- You can disable MCAR by omitting `--enable-mcar`.  
- To change ranges, prefixes, or missingness logic, update the script directly.  
- Extend easily with MAR (Missing At Random) logic if you want missingness tied to observed columns (e.g., `Age < 25` → more missing occupations).  

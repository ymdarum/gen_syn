# Synthetic Data Generator for Customer Profiles & Transactions

A Python-based synthetic data generator that creates realistic customer profiles and transaction data for banking/financial applications. This tool reads configuration rules from an Excel file and generates two CSV files containing customer demographic information and their corresponding transaction history.

## 🚀 Features

- **Realistic Customer Profiles**: Generates customer data with Malaysian demographics including names, occupations, states, and account information
- **Transaction Simulation**: Creates realistic transaction data with various payment channels (QR P2P, DuitNOW, Credit Transfer, etc.)
- **Configurable Rules**: Uses Excel file for customizable data generation rules and reference values
- **Reproducible Results**: Supports random seed for consistent data generation
- **Scalable**: Generate thousands of customer profiles and their associated transactions
- **Malaysian Context**: Specifically designed for Malaysian banking scenarios with local names, states, and occupations

## 📋 Generated Data

### Customer Profile Data (`CUSTOMER_PROFILE_YYYYMMDD.csv`)
- **Customer_ID**: Unique customer identifier (e.g., CUST_XMN3g)
- **Customer_Acc**: Unique account identifier (e.g., CACC_tektXwA)
- **Age**: Customer age (10-99 years)
- **Stated_Occupation**: Occupation from predefined list
- **Location_State**: Malaysian state/territory
- **Account_Tenure_Months**: Account age in months (5-240 months)
- **Account_Type**: Account type (CA = Current Account, SA = Savings Account)
- **Avg_Balance**: Average account balance (RM 100 - RM 1,000,000)

### Transaction Data (`CUSTOMER_TXN_YYYYMMDD.csv`)
- **Customer_Acc**: Links to customer profile
- **Transaction_ID**: Unique transaction identifier (e.g., TXN_dSds2GEj0q8)
- **Timestamp**: UTC timestamp (2024-01-01 to 2025-09-24)
- **Amount**: Transaction amount (RM 100 - RM 1,000,000)
- **Type**: Transaction type (credit/debit)
- **Channel**: Payment channel (QR P2P, DuitNOW, Credit Transfer, QR POS, Other)
- **Counterparty_Name**: Counterparty name (Malaysian names or business names)
- **Counterparty_Account**: Counterparty account identifier

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Setup

#### For Windows Users

1. **Clone the repository**
   ```powershell
   # Using PowerShell (Recommended)
   git clone <repository-url>
   cd synthetic_data
   ```
   
   ```cmd
   # Using Command Prompt
   git clone <repository-url>
   cd synthetic_data
   ```

2. **Install dependencies**
   ```powershell
   # Using PowerShell
   pip install -r requirements.txt
   ```
   
   ```cmd
   # Using Command Prompt
   pip install -r requirements.txt
   ```

3. **Verify installation**
   ```powershell
   # Using PowerShell
   python generate_synth_data.py --help
   ```
   
   ```cmd
   # Using Command Prompt
   python generate_synth_data.py --help
   ```

#### For Linux/Mac Users

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd synthetic_data
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify installation**
   ```bash
   python generate_synth_data.py --help
   ```

## 📖 Usage

### Basic Usage

#### Windows (PowerShell - Recommended)
```powershell
python generate_synth_data.py --rules rule_to_observe.xlsx --profiles 1000 --avg_txn 15 --seed 42 --outdir output
```

#### Windows (Command Prompt)
```cmd
python generate_synth_data.py --rules rule_to_observe.xlsx --profiles 1000 --avg_txn 15 --seed 42 --outdir output
```

#### Linux/Mac
```bash
python generate_synth_data.py --rules rule_to_observe.xlsx --profiles 1000 --avg_txn 15 --seed 42 --outdir output
```

### Command Line Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--rules` | ✅ Yes | - | Path to Excel rules file (rule_to_observe.xlsx) |
| `--profiles` | ❌ No | 1000 | Number of customer profiles to generate |
| `--avg_txn` | ❌ No | 15 | Average transactions per customer (Poisson distribution) |
| `--seed` | ❌ No | 42 | Random seed for reproducible results |
| `--outdir` | ❌ No | output | Output directory for generated CSV files |

### Example Commands

#### Windows Examples

**Generate 500 customers with 20 average transactions (PowerShell):**
```powershell
python generate_synth_data.py --rules rule_to_observe.xlsx --profiles 500 --avg_txn 20
```

**Generate 2000 customers with custom output directory (Command Prompt):**
```cmd
python generate_synth_data.py --rules rule_to_observe.xlsx --profiles 2000 --outdir my_data
```

**Generate data with specific seed for reproducibility (PowerShell):**
```powershell
python generate_synth_data.py --rules rule_to_observe.xlsx --profiles 1000 --seed 12345
```

**Using full path to Excel file (Windows):**
```powershell
python generate_synth_data.py --rules "C:\Users\YourName\Documents\rule_to_observe.xlsx" --profiles 1000
```

#### Linux/Mac Examples

**Generate 500 customers with 20 average transactions:**
```bash
python generate_synth_data.py --rules rule_to_observe.xlsx --profiles 500 --avg_txn 20
```

**Generate 2000 customers with custom output directory:**
```bash
python generate_synth_data.py --rules rule_to_observe.xlsx --profiles 2000 --outdir my_data
```

**Generate data with specific seed for reproducibility:**
```bash
python generate_synth_data.py --rules rule_to_observe.xlsx --profiles 1000 --seed 12345
```

## 📊 Configuration

The tool uses an Excel file (`rule_to_observe.xlsx`) for configuration. The Excel file should contain the following sheets:

- **requirement**: General requirements and settings
- **profile_tbl**: Customer profile field definitions
- **transaction_tbl**: Transaction field definitions
- **occu**: List of occupations (optional - uses default if not provided)
- **state**: List of Malaysian states (optional - uses default if not provided)

### Default Values
If the Excel file doesn't contain occupation or state data, the tool uses these defaults:

**Occupations:**
TEACHER/LECTURER, ENGINEER, DOCTOR, NURSE, DRIVER, HOUSEWIFE, STUDENT, CHEF, POLICE, ARMY, CASHIER, FARMER, RETIREE

**States:**
Johor, Kedah, Kelantan, Melaka, Negeri Sembilan, Pahang, Pulau Pinang, Perak, Perlis, Selangor, Terengganu, Sabah, Sarawak, WP KL, WP Labuan, WP Putrajaya

## 📁 Output Structure

```
output/
├── CUSTOMER_PROFILE_20250925.csv    # Customer demographic data
└── CUSTOMER_TXN_20250925.csv        # Transaction history data
```

## 🔧 Technical Details

### Dependencies
- **pandas** (≥2.0.0): Data manipulation and Excel file reading
- **numpy** (≥1.24.0): Random number generation and statistical functions
- **faker**: Name generation (optional, uses custom Malaysian names)

### Data Generation Logic
- **Customer IDs**: Format `CUST_` + random alphanumeric (e.g., CUST_XMN3g)
- **Account IDs**: Format `CACC_` + random alphanumeric (e.g., CACC_tektXwA)
- **Transaction IDs**: Format `TXN_` + random alphanumeric (e.g., TXN_dSds2GEj0q8)
- **Transaction Count**: Uses Poisson distribution with specified average
- **Amounts**: Uniform distribution between RM 100 - RM 1,000,000
- **Timestamps**: Random distribution between 2024-01-01 and 2025-09-24 (UTC)

### Malaysian Context Features
- **Names**: Mix of Malaysian personal names and business names
- **Business Names**: Format like "Kedai Maju", "Restoran Jaya", "Syarikat Sentosa"
- **Geographic**: All 16 Malaysian states and federal territories
- **Payment Channels**: Local payment methods (DuitNOW, QR P2P, etc.)

## 🧪 Testing

After generating data, you can verify the output:

### Windows Testing Commands

1. **Check file generation (PowerShell):**
   ```powershell
   Get-ChildItem output\ -Name
   # or
   dir output\
   ```

2. **Verify data structure (PowerShell):**
   ```powershell
   Get-Content output\CUSTOMER_PROFILE_*.csv | Select-Object -First 5
   Get-Content output\CUSTOMER_TXN_*.csv | Select-Object -First 5
   ```

3. **Check data counts (PowerShell):**
   ```powershell
   (Get-Content output\CUSTOMER_PROFILE_*.csv).Count
   (Get-Content output\CUSTOMER_TXN_*.csv).Count
   ```

4. **Open files in Excel (Windows):**
   ```powershell
   # Open the generated CSV files in Excel
   Start-Process output\CUSTOMER_PROFILE_*.csv
   Start-Process output\CUSTOMER_TXN_*.csv
   ```

### Linux/Mac Testing Commands

1. **Check file generation:**
   ```bash
   ls -la output/
   ```

2. **Verify data structure:**
   ```bash
   head -5 output/CUSTOMER_PROFILE_*.csv
   head -5 output/CUSTOMER_TXN_*.csv
   ```

3. **Check data counts:**
   ```bash
   wc -l output/CUSTOMER_PROFILE_*.csv
   wc -l output/CUSTOMER_TXN_*.csv
   ```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🆘 Support

### Windows-Specific Troubleshooting

**Common Windows Issues:**

1. **Python not found error:**
   ```powershell
   # Check if Python is installed
   python --version
   # If not found, install Python from https://python.org
   ```

2. **Permission denied errors:**
   ```powershell
   # Run PowerShell as Administrator
   # Or change execution policy
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

3. **Excel file path issues:**
   ```powershell
   # Use quotes for paths with spaces
   python generate_synth_data.py --rules "C:\My Documents\rule_to_observe.xlsx"
   ```

4. **Output directory creation issues:**
   ```powershell
   # Create output directory manually if needed
   New-Item -ItemType Directory -Path "output" -Force
   ```

5. **CSV files not opening in Excel:**
   ```powershell
   # Files are generated with UTF-8 encoding
   # Open in Excel: Data > From Text/CSV > Select file > UTF-8 encoding
   ```

### General Support

If you encounter any issues or have questions:

1. Check the [Issues](../../issues) page for existing solutions
2. Create a new issue with detailed description
3. Include your Python version, operating system, and error messages

## 🔄 Version History

- **v1.0.0**: Initial release with basic customer profile and transaction generation
- Features Malaysian demographic data and local payment channels
- Configurable via Excel rules file
- Reproducible results with random seed support

---

**Note**: This tool is designed for testing and development purposes. Generated data is synthetic and should not be used for production banking systems without proper validation and security measures.

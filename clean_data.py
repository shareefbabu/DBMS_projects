"""
Data Cleaning Script for Flight Dataset
Checks for duplicates, missing values, and data consistency
Generates a comprehensive cleaning report
"""
import pandas as pd
import logging
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# File paths
DATA_FILE = 'flight_dataset_cleaned.csv'
REPORT_FILE = 'data_cleaning_report.md'


def load_dataset():
    """Load the flight dataset"""
    try:
        df = pd.read_csv(DATA_FILE)
        logger.info(f"Loaded dataset with {len(df)} rows and {len(df.columns)} columns")
        return df
    except FileNotFoundError:
        logger.error(f"Dataset file '{DATA_FILE}' not found")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error loading dataset: {e}")
        sys.exit(1)


def analyze_dataset(df):
    """Perform comprehensive data analysis"""
    report = []
    report.append("# Data Cleaning Report\n")
    report.append(f"**Generated:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append(f"**Total Records:** {len(df):,}\n\n")
    
    # Dataset overview
    report.append("## Dataset Overview\n")
    report.append(f"- **Columns:** {len(df.columns)}\n")
    report.append(f"- **Memory Usage:** {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB\n\n")
    
    # Column info
    report.append("### Columns\n")
    for col in df.columns:
        report.append(f"- `{col}` ({df[col].dtype})\n")
    report.append("\n")
    
    # Missing values
    report.append("## Missing Values Analysis\n")
    missing = df.isnull().sum()
    if missing.sum() == 0:
        report.append("✅ No missing values found\n\n")
    else:
        report.append("| Column | Missing Count | Percentage |\n")
        report.append("|--------|---------------|------------|\n")
        for col in missing[missing > 0].index:
            count = missing[col]
            pct = (count / len(df)) * 100
            report.append(f"| `{col}` | {count:,} | {pct:.2f}% |\n")
        report.append("\n")
    
    # Duplicates
    report.append("## Duplicate Records\n")
    duplicates = df.duplicated()
    dup_count = duplicates.sum()
    if dup_count == 0:
        report.append("✅ No duplicate rows found\n\n")
    else:
        report.append(f"⚠️ Found {dup_count:,} duplicate rows ({(dup_count/len(df)*100):.2f}%)\n\n")
    
    # Duplicate flight numbers
    report.append("## Duplicate Flight Numbers\n")
    flight_dups = df.groupby('Flight_Number').size()
    flight_dups = flight_dups[flight_dups > 1].sort_values(ascending=False)
    if len(flight_dups) == 0:
        report.append("✅ All flight numbers are unique\n\n")
    else:
        report.append(f"⚠️ Found {len(flight_dups):,} flight numbers with multiple entries\n")
        report.append(f"- Top 5 duplicates:\n")
        for flight, count in flight_dups.head().items():
            report.append(f"  - `{flight}`: {count} occurrences\n")
        report.append("\n")
    
    # Data quality checks
    report.append("## Data Quality Checks\n")
    
    # Price validation
    if 'Fare' in df.columns:
        invalid_prices = (df['Fare'] <= 0).sum()
        if invalid_prices > 0:
            report.append(f"⚠️ Found {invalid_prices:,} records with invalid prices (≤ 0)\n")
        else:
            report.append("✅ All prices are valid (> 0)\n")
    
    # Stop validation
    if 'Stop' in df.columns:
        negative_stops = (df['Stop'] < 0).sum()
        if negative_stops > 0:
            report.append(f"⚠️ Found {negative_stops:,} records with negative stops\n")
        else:
            report.append("✅ All stop values are valid (≥ 0)\n")
    
    # Time format validation
    time_cols = ['Departure_Time', 'Arrival_Time', 'Duration_Time']
    for col in time_cols:
        if col in df.columns:
            try:
                pd.to_datetime(df[col], format='%H:%M:%S', errors='coerce')
                report.append(f"✅ `{col}` format is valid\n")
            except:
                report.append(f"⚠️ `{col}` has format issues\n")
    
    report.append("\n")
    
    # Statistics
    report.append("## Numeric Column Statistics\n")
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
    if len(numeric_cols) > 0:
        report.append("| Column | Min | Max | Mean | Median |\n")
        report.append("|--------|-----|-----|------|--------|\n")
        for col in numeric_cols:
            stats = df[col].describe()
            report.append(f"| `{col}` | {stats['min']:.2f} | {stats['max']:.2f} | {stats['mean']:.2f} | {stats['50%']:.2f} |\n")
        report.append("\n")
    
    # Unique values for categorical columns
    report.append("## Categorical Columns - Unique Values\n")
    categorical_cols = df.select_dtypes(include=['object']).columns
    for col in categorical_cols[:10]:  # Limit to first 10
        unique_count = df[col].nunique()
        report.append(f"- `{col}`: {unique_count:,} unique values\n")
    report.append("\n")
    
    # Recommendations
    report.append("## Recommendations\n")
    if dup_count > 0:
        report.append("- ⚠️ Consider removing duplicate rows\n")
    if missing.sum() > 0:
        report.append("- ⚠️ Handle missing values appropriately\n")
    if len(flight_dups) > 0:
        report.append("- ⚠️ Review duplicate flight numbers - may be valid for different dates/routes\n")
    if dup_count == 0 and missing.sum() == 0:
        report.append("- ✅ Dataset is clean and ready for use\n")
    
    return ''.join(report)


def main():
    """Main execution function"""
    logger.info("Starting data cleaning analysis...")
    
    # Load dataset
    df = load_dataset()
    
    # Analyze dataset
    logger.info("Analyzing dataset...")
    report = analyze_dataset(df)
    
    # Write report
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write(report)
    
    logger.info(f"✅ Analysis complete! Report saved to '{REPORT_FILE}'")
    print(f"\n[SUCCESS] Data Cleaning Report generated: {REPORT_FILE}")


if __name__ == "__main__":
    main()

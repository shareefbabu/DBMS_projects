# Data Cleaning Report
**Generated:** 2025-12-05 19:54:19
**Total Records:** 11,420

## Dataset Overview
- **Columns:** 14
- **Memory Usage:** 7.58 MB

### Columns
- `Airlines_Name` (object)
- `Airline_Code` (object)
- `Flight_Number` (int64)
- `Cabin_Class` (object)
- `Aircraft_Type` (object)
- `Departure_Time` (object)
- `Departure_Port` (object)
- `Arrival_Time` (object)
- `Arrival_Port` (object)
- `Duration_Time` (object)
- `Stop` (int64)
- `Fare` (int64)
- `Departure_Port_Name` (object)
- `Arrival_Port_Name` (object)

## Missing Values Analysis
✅ No missing values found

## Duplicate Records
✅ No duplicate rows found

## Duplicate Flight Numbers
⚠️ Found 1,307 flight numbers with multiple entries
- Top 5 duplicates:
  - `2740`: 42 occurrences
  - `2914`: 42 occurrences
  - `2008`: 34 occurrences
  - `2508`: 32 occurrences
  - `434`: 31 occurrences

## Data Quality Checks
✅ All prices are valid (> 0)
✅ All stop values are valid (≥ 0)
✅ `Departure_Time` format is valid
✅ `Arrival_Time` format is valid
✅ `Duration_Time` format is valid

## Numeric Column Statistics
| Column | Min | Max | Mean | Median |
|--------|-----|-----|------|--------|
| `Flight_Number` | 103.00 | 9982.00 | 3519.68 | 2628.00 |
| `Stop` | 0.00 | 2.00 | 0.97 | 1.00 |
| `Fare` | 1498.00 | 115431.00 | 9015.18 | 7588.00 |

## Categorical Columns - Unique Values
- `Airlines_Name`: 8 unique values
- `Airline_Code`: 8 unique values
- `Cabin_Class`: 3 unique values
- `Aircraft_Type`: 20 unique values
- `Departure_Time`: 276 unique values
- `Departure_Port`: 33 unique values
- `Arrival_Time`: 273 unique values
- `Arrival_Port`: 33 unique values
- `Duration_Time`: 290 unique values
- `Departure_Port_Name`: 33 unique values

## Recommendations
- ⚠️ Review duplicate flight numbers - may be valid for different dates/routes
- ✅ Dataset is clean and ready for use

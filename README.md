# Sector Index

A Python-based tool for calculating and managing sector indices for Chinese commodity futures markets. This project computes sector-specific indices based on weighted turnover of constituent futures contracts across multiple classification schemes.

## Features

- **Multiple Classification Schemes**: Supports three classification levels (c0, c1, c2) with various sector groupings:
  - **c0**: Basic sectors (BLK, MTL, PMT, ENG, OIP, AGR, FRG)
  - **c1**: Alternative groupings (AUG, MTL, OIL, CHM, BLK, AGR)
  - **c2**: Detailed sector and thematic indices (STL, BDM, COL, NEG, PLC, POC, GRN, FED, SFT, OIL, BRD, CPI, PPI, IMT, RTS, ELT, MAC, HOU, INF, IND, LQC, SLC, OIC, CLC, and more)

- **Multiple Frequencies**: Calculate indices at both daily (`d`) and minute (`m`) frequencies

- **Turnover-Weighted Calculation**: Uses square-root of turnover as weighting mechanism for constituent instruments

- **Incremental Updates**: Support for both full historical recalculation and daily incremental updates

## Project Structure

```
sector_index/
├── config.py           # Configuration loader and data descriptors
├── config.yaml         # Main configuration file (sectors, instruments, data sources)
├── main.py            # Entry point for index calculation
├── typedef.py         # Type definitions and data classes
├── solutions/
│   ├── calculators.py # Core sector index calculation logic
│   └── misc.py        # Helper functions (init price, amount, span)
├── run_all.sh         # Script for full historical calculation
├── run_daily_increment.sh  # Script for daily updates
└── run_test.sh        # Test script
```

## Requirements

This project depends on:
- Python 3.10+
- qtools_sxzq (internal library for calendar, data access, and utilities)
- transmatrix (strategy framework and signal processing)
- pandas
- numpy
- pyyaml
- logbook

## Installation

1. Clone the repository:
```bash
git clone https://github.com/huxiaoou/sector_index.git
cd sector_index
```

2. Install dependencies:
```bash
pip install -r requirements.txt  # If available
# Note: Requires access to qtools_sxzq and transmatrix libraries
```

3. Configure the project:
   - Update `config.yaml` with appropriate database names and paths
   - Set the calendar path to your trading calendar file
   - Adjust sector classifications if needed

## Configuration

The `config.yaml` file contains:

- **Database Settings**:
  - `dbs.public`: Public metadata database name (default: `meta_data`)
  - `dbs.user`: User private database for storing results (default: `huxiaoou_private`)

- **Calendar Path**: 
  - `path_calendar`: Path to the CNE trading calendar CSV file

- **Index Base**:
  - `index_base.date`: Base date for index calculation (default: `20171229`)
  - `index_base.value`: Initial index value (default: `100.00`)

- **Classifications**: 
  - Three levels of sector classifications (c0, c1, c2)
  - Each sector contains a list of futures instruments (e.g., `RB9999_SHFE`, `CU9999_SHFE`)

- **Source Tables**:
  - Daily data: `future_bar_1day_aft` 
  - Minute data: `future_bar_1min`

## Usage

### Command Line Interface

The main script accepts the following arguments:

```bash
python main.py <command> --freq <d|m> --bgn <YYYYMMDD> [--end <YYYYMMDD>]
```

**Arguments**:
- `command`: Classification name (e.g., `c0`, `c1`, `c2`)
- `--freq`: Frequency (`d` for daily, `m` for minute)
- `--bgn`: Begin date in format YYYYMMDD (must be a trading day)
- `--end`: Optional end date in format YYYYMMDD (defaults to begin date if not specified)

**Examples**:

1. Calculate daily sector indices for c2 classification on a single date:
```bash
python main.py c2 --freq d --bgn 20240101
```

2. Calculate minute-level sector indices for c0 classification over a date range:
```bash
python main.py c0 --freq m --bgn 20240101 --end 20240131
```

### Batch Processing Scripts

1. **Full Historical Calculation** (`run_all.sh`):
```bash
./run_all.sh [YYYYMMDD]
# Or for automatic end date:
./run_all.sh --auto
```

This script:
- Removes existing data for the c2 classification
- Recalculates indices from 20180102 to specified end date
- Processes both daily and minute frequencies

2. **Daily Incremental Update** (`run_daily_increment.sh`):
```bash
./run_daily_increment.sh [YYYYMMDD]
# Or for automatic date:
./run_daily_increment.sh --auto
```

This script:
- Appends new data for the current date
- Processes both daily and minute frequencies
- Does not remove existing data

## How It Works

1. **Initialization**: 
   - Loads previous day's closing prices (or base value if starting from base date)
   - Fetches previous day's turnover for weighting

2. **Weight Calculation**:
   - Each instrument is weighted by the square root of its turnover
   - Weights are normalized within each sector
   - Weights are updated daily (at 16:00:00)

3. **Index Calculation**:
   - Sector returns are calculated as weighted average of constituent returns
   - Index values are compounded: `new_price = old_price * (1 + sector_return)`
   - Daily indices updated at 15:00:00
   - Minute indices updated with each new data point

4. **Output**:
   - Results saved to database tables named `sector_{classification}_{frequency}`
   - Each record contains: return (`ret`) and closing price (`close`)

## Data Flow

```
Source Data (future_bar_1day_aft / future_bar_1min)
    ↓
Load initial prices and turnover
    ↓
Calculate turnover-based weights
    ↓
Compute sector returns (weighted average)
    ↓
Update sector index values
    ↓
Save to sector_{classification}_{freq} table
```

## Validation

The project includes validation checks:
- Begin and end dates must be valid trading days
- Begin date must be after the index base date
- Missing initialization data triggers warnings

## License

[Specify license here]

## Author

huxiaoou

## Notes

- The project is designed for Chinese commodity futures markets
- Requires access to market data databases
- Uses custom internal libraries (qtools_sxzq, transmatrix)
- All dates use format YYYYMMDD
- Trading hours consideration: minute data starts from 21:00:00 of previous day

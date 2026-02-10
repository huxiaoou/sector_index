# Sector Index

A Python-based tool for calculating and managing sector indices for Chinese commodity futures markets. This project computes sector-specific indices based on weighted turnover of constituent futures contracts across multiple classification schemes.

## Features

- **Multiple Classification Schemes**: Supports three classification levels (c0, c1, c2) with various sector groupings:
  - **c0**: Basic sectors (BLK, MTL, PMT, ENG, OIP, AGR, FRG)
  - **c1**: Alternative groupings (AUG, MTL, OIL, CHM, BLK, AGR)
  - **c2**: Detailed sector and thematic indices (STL, BDM, COL, NEG, PLC, POC, GRN, FED, SFT, OIL, BRD, CPI, PPI, IMT, RTS, ELT, MAC, HOU, INF, IND, LQC, SLC, OIC, CLC, and more)

### C0 Sector Code Mapping

| Sector Code | Chinese Name | Description           |
| ----------- | ------------ | --------------------- |
| BLK         | 黑色         | Black (Coal & Steel)  |
| MTL         | 有色金属     | Metals                |
| PMT         | 贵金属       | Precious Metals       |
| ENG         | 能源化工     | Energy & Chemicals    |
| OIP         | 油产品       | Oil Industry Products |
| AGR         | 农产品       | Agriculture           |
| FRG         | 航运         | Freight               |

### C1 Sector Code Mapping

| Sector Code | Chinese Name | Description             |
| ----------- | ------------ | ----------------------- |
| AUG         | 黄金白银     | Gold & Silver (Au & Ag) |
| MTL         | 有色金属     | Metals                  |
| OIL         | 油脂油料     | Oil Seeds               |
| CHM         | 化工         | Chemicals               |
| BLK         | 黑色         | Black (Coal & Steel)    |
| AGR         | 农产品       | Agriculture             |

### C2 Sector Code Mapping

| Sector Code | Chinese Name | Description               |
| ----------- | ------------ | ------------------------- |
| STL         | 钢铁         | Steel                     |
| BDM         | 建材         | Building Materials        |
| COL         | 煤炭         | Coal                      |
| BLK         | 黑链         | Black Chain               |
| FEA         | 铁合金       | Ferroalloys               |
| NEG         | 新能源       | New Energy                |
| PLC         | 塑化链       | Plastic Chain             |
| POC         | 聚酯链       | Polyester Chain           |
| GRN         | 谷物         | Grains                    |
| FED         | 饲料         | Feed                      |
| SFT         | 软商品       | Soft Commodities          |
| OIL         | 油脂链       | Oil & Fats Chain          |
| BRD         | 养殖链       | Breeding Chain            |
| CPI         | CPI          | Consumer Price Index      |
| PPI         | PPI          | Producer Price Index      |
| IMT         | 进口依赖度   | Import Dependency         |
| RTS         | 利率影响     | Interest Rate Sensitivity |
| ELT         | 电力影响     | Electricity Impact        |
| MAC         | 宏观         | Macro                     |
| HOU         | 房地产       | Real Estate               |
| INF         | 基建         | Infrastructure            |
| IND         | 工业品       | Industrial Products       |
| LQC         | 液体化工     | Liquid Chemicals          |
| SLC         | 固体化工     | Solid Chemicals           |
| OIC         | 油化工       | Oil Chemicals             |
| CLC         | 煤化工       | Coal Chemicals            |

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
- Python 3.9+
- qtools_sxzq (internal library for calendar, data access, and utilities)
- transmatrix (strategy framework and signal processing)
- pandas
- numpy
- pyyaml
- logbook

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

## Author

huxiaoou

## Notes

- The project is designed for Chinese commodity futures markets
- Requires access to market data databases
- Uses custom internal libraries (qtools_sxzq, transmatrix)
- All dates use format YYYYMMDD
- Trading hours consideration: minute data starts from 21:00:00 of previous day

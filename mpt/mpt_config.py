import os
import sys
DIR_THIS = os.path.abspath(os.path.dirname(__file__))

# Add ChainLink utilities to path.
sys.path.append(f"{DIR_THIS}/../datasource/")

# CSV file ready for use with pandas:
FNF_DATA_CSV_BZ2 = f"{DIR_THIS}/data/ts.csv.bz2"

# Risk-free rate (for Sharpe ratio). Using 0 for simplicity.
risk_free_rate = 0.00

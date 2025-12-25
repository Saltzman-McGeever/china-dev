#%% Open AidData China's Global Loans and Grants Dataset, Version 1.0
import pandas as pd
from pathlib import Path

# Get the directory where this script is located, create a Path object for the Excel file
script_dir = Path(__file__).parent
excel_path = script_dir.parent / "AidDatas_CLG_Global_Dataset_v1.0.xlsx"

clg = pd.read_excel(excel_path, sheet_name="CLG-Global 1.0_Records")

clg = clg[clg['Recommended_for_Aggregates'] == 'Yes']

#%% Open AidData China's Global Loans and Grants Dataset, Version 1.0
import pandas as pd
import geopandas as gpd
from pathlib import Path

# Get the directory where this script is located, create a Path object for the Excel file
script_dir = Path(__file__).parent

# Define paths to data files
clg_path = script_dir.parent.parent / "datasets" / "AidDatas_CLG_Global_Dataset_v1.0.xlsx"
gpoc_path = script_dir.parent.parent / "datasets" / "GPOC 1.0.xlsx"
geo_path = script_dir.parent.parent / "datasets" / "aid_data_geospatial.gpkg"

# Load CLG dataset and filter for recommended development projects
clg = pd.read_excel(clg_path, sheet_name="CLG-Global 1.0_Records")
clg = clg[clg['Recommended_for_Aggregates'] == 'Yes']
clg_dev = clg[clg['Intent'] == 'Development']

# Aggregate total amount by year
annual_totals = clg_dev.groupby('Implementation_Start_Year')['Amount_Constant_USD_2023'].sum().reset_index()
annual_totals.columns = ['Implementation_Start_Year', 'Amount_Constant_USD_2023']

# Load Global Public Opinion on China dataset
gpoc = pd.read_excel(gpoc_path)


# Load geospatial dataset
geo = gpd.read_file(geo_path)

#%%
geo.sample(200).explore()
# %%

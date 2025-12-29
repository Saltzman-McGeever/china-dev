
#%%
from load_data import gpoc, clg_dev
import pandas as pd

# Merge CLG development projects with GPOC data on Country
merged_data = pd.merge(
    clg_dev,
    gpoc,
    how='left',
    left_on=['Country_of_Activity_ISO3'],
    right_on=['iso3'])

merged_data
# %%

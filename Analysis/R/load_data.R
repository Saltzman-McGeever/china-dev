library(readxl)
library(dplyr)
library(here)

clg_path <- here("datasets", "AidDatas_CLG_Global_Dataset_v1.0.xlsx")

# Load CLG dataset and filter for recommended development projects
clg     <- read_excel(clg_path, sheet = "CLG-Global 1.0_Records", guess_max = 100000)
clg     <- clg |> filter(Recommended_for_Aggregates == "Yes")
clg_dev <- clg |> filter(Intent == "Development")

# Aggregate total amount by year
annual_totals <- clg_dev |>
  group_by(Implementation_Start_Year) |>
  summarise(Amount_Constant_USD_2023 = sum(Amount_Constant_USD_2023, na.rm = TRUE))

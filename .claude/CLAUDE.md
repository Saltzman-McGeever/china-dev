# ChinaDev Project — Claude Instructions

## Project Overview

This project analyzes Chinese development finance in Africa, linking AidData's CLG dataset with geospatial data and (forthcoming) African household microdata (likely LSMS/DHS). The goal is a geodata-enriched causal or descriptive analysis of Chinese aid effects on household and enumeration-area-level outcomes.

Primary deliverable: interactive Quarto HTML report with plotly visualizations.

---

## Directory Structure

```
ChinaDev/
├── _targets.R              # targets pipeline entry point
├── _targets/               # pipeline cache — do not edit manually
├── analysis/
│   ├── R/                  # R scripts (load_clg_dev.R, plots.R, regress.R, style.R)
│   ├── quarto/             # Quarto documents (.qmd) and rendered _output/
│   ├── packages.R          # package declarations
│   └── TRANSITION_CODEBOOK.md  # Python→R migration reference
├── datasets/
│   ├── AidDatas_CLG_Global_Dataset_v1.0.xlsx   # primary dataset (large)
│   └── aid_data_geospatial.gpkg                # geospatial layer (excluded from git)
└── research/               # PDFs, bibliography, literature notes
```

---

## Datasets

### AidData CLG Global Dataset v1.0
- **File**: `datasets/AidDatas_CLG_Global_Dataset_v1.0.xlsx`
- Chinese-led globalization dataset; primary sheet is `CLG-Global 1.0_Records`
- Filtered to `Recommended_for_Aggregates == "Yes"` for analysis
- Loaded via targets as `clg_dev` and `clg_codebook`

### AidData Geospatial (.gpkg)
- **File**: `datasets/aid_data_geospatial.gpkg`
- Excluded from git tracking
- Merged with CLG as `clg_plus_geo` in the targets pipeline

### LSMS/DHS (forthcoming)
- African household panel — not yet integrated

---

## Tooling

- **Pipeline**: `targets` (`_targets.R`) — always use `tar_make()` / `tar_load()` rather than running scripts directly
- **Language**: R (fully migrated from Python)
- **Reporting**: Quarto (`quarto render` from project root so `here::here()` resolves)
- **Visualization**: plotly (R)
- **Path resolution**: `here::here()` throughout

---

## Token Efficiency Rules

- **Never read** `datasets/AidDatas_CLG_Global_Dataset_v1.0.xlsx` directly — it is large and already handled by the targets pipeline
- **Never read** files under `analysis/quarto/_output/` — rendered HTML is not useful as context
- **Skip** verbose plan summaries — act directly
- Prefer reading specific functions or line ranges over entire scripts when the relevant section is known
- Prefer `tar_load()` / `tar_read()` patterns over re-running data loading code

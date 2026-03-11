# Python → R Transition Codebook

## File Mapping

| Python (analysis/python/) | R (analysis/R/) | Purpose |
|---------------------------|-----------------|---------|
| `load_data.py`            | `load_data.R`   | Load raw datasets |
| `merge_data.py`           | *(deleted)*     | Merged CLG + GPOC — removed with GPOC |
| `Plots.py`                | `plots.R`       | Visualization functions |
| `regress.py`              | `regress.R`     | OLS regression + forest plot |
| `analysis/quarto/data_inventory.qmd` | same path | Updated to `{r}` chunks |
| `analysis/quarto/analysis.qmd`       | same path | Updated to `{r}` chunks |

---

## Library Equivalents

| Python | R | Notes |
|--------|---|-------|
| `pandas` | `dplyr`, `base R` | Data manipulation |
| `pandas.read_excel()` | `readxl::read_excel()` | Sheet argument identical |
| `geopandas` | *(skipped)* | `.gpkg` excluded from tracking |
| `pathlib.Path` | `here::here()` | Project-root-relative paths |
| `plotly.express` | `plotly` (R) | R uses `plot_ly()` + `add_*()` |
| `plotly.graph_objects` | `plotly` (R) | Same package |
| `plotly.subplots.make_subplots` | `layout(yaxis2 = ...)` | Dual y-axis via layout |
| `statsmodels.OLS` | `lm()` | Base R OLS |
| `matplotlib.pyplot` | `plotly` (R) | Forest plot rewritten in plotly |

---

## Key API Differences

### Data loading
```python
# Python
clg = pd.read_excel(path, sheet_name="CLG-Global 1.0_Records")
clg = clg[clg['Recommended_for_Aggregates'] == 'Yes']
```
```r
# R
clg <- read_excel(path, sheet = "CLG-Global 1.0_Records")
clg <- clg |> filter(Recommended_for_Aggregates == "Yes")
```

### GroupBy aggregation
```python
# Python
df.groupby('col')['val'].nunique().reset_index()
```
```r
# R
df |> group_by(col) |> summarise(val = n_distinct(val))
```

### Dual y-axis charts
```python
# Python (Plotly)
fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(..., secondary_y=False)
fig.add_trace(..., secondary_y=True)
```
```r
# R (Plotly)
plot_ly() |>
  add_bars(..., yaxis = "y") |>
  add_lines(..., yaxis = "y2") |>
  layout(yaxis2 = list(overlaying = "y", side = "right"))
```

### Choropleth maps
```python
# Python
px.choropleth(df, locations='Country', locationmode='country names',
              color='Value', color_continuous_scale='YlOrRd')
```
```r
# R
plot_ly(df, type = "choropleth",
        locations = ~Country, locationmode = "country names",
        z = ~Value, colorscale = "YlOrRd")
```

### OLS regression
```python
# Python
X = sm.add_constant(reg_data[x_value])
reg = sm.OLS(y, X).fit()
print(reg.summary().tables[1])
print(f"R²: {reg.rsquared:.4f}")
ci = reg.conf_int()
```
```r
# R
fit <- lm(y ~ x, data = reg_data)
print(summary(fit)$coefficients)
cat(sprintf("R²: %.4f\n", summary(fit)$r.squared))
ci <- confint(fit)
```

### Figure display in Quarto
```python
# Python — explicit show() call required
fig.show(config={...})
```
```r
# R — pipe config, then return the object; Quarto renders automatically
create_temporal_trends(clg_dev) |> config(...)
```

### Outlier countries parameter
```python
# Python — dict of {name: (lat, lon)}
outlier_countries={'Pakistan': (30.3752, 69.3451)}
```
```r
# R — named list (lat/lon stored but unused for map rendering)
outlier_countries = list(Pakistan = c(30.3752, 69.3451))
```

---

## Decisions & Omissions

| Item | Decision | Reason |
|------|----------|--------|
| `geopandas` / `.gpkg` | Skipped | File excluded from git tracking |
| `geo.sample(200).explore()` | Skipped | No geospatial data available |
| GPOC dataset + all opinion functions | Removed | Dataset dropped from project |
| `merge_data.py` / `merge_data.R` | Deleted | Only purpose was merging CLG with GPOC |
| Matplotlib forest plot | Replaced with plotly | Consistent with rest of codebase |
| `px.choropleth` hover_data | Ported via `customdata` + `hovertemplate` | R plotly has no `hover_data` shorthand |
| Python bug: `is_currency` undefined | Fixed | Outlier value formatted via `format_fn` |
| `sys.path` manipulation in Quarto | Replaced with `here::here()` + `source()` | R's standard project-relative sourcing |

---

## R Package Requirements

```r
install.packages(c("readxl", "dplyr", "plotly", "here"))
```

All packages are CRAN-available. No Bioconductor dependencies.

---

## Running the Analysis

### Render Quarto documents
```bash
quarto render analysis/quarto/data_inventory.qmd
quarto render analysis/quarto/analysis.qmd
```

### Run R scripts interactively
```r
library(here)
source(here("analysis", "R", "load_data.R"))   # loads clg_dev, annual_totals
source(here("analysis", "R", "plots.R"))       # loads plot functions
source(here("analysis", "R", "regress.R"))     # loads regress()
```

Quarto must be run from the project root (where `.git` lives) so that `here::here()` resolves correctly.

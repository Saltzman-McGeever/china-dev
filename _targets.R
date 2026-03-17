library(targets)

tar_source("analysis/packages.R")
tar_source("analysis/R/load_clg_dev.R")

list(
  tar_target(clg_path, "datasets/AidDatas_CLG_Global_Dataset_v1.0.xlsx", format = "file"),
  tar_target(geo_path, "datasets/aid_data_geospatial.gpkg",              format = "file"),

  tar_target(clg_dev,      load_clg_dev(clg_path)),
  tar_target(clg_codebook, load_clg_codebook(clg_path)),
  tar_target(geo,          load_geo(geo_path)),
  tar_target(clg_plus_geo, merge_clg_geo(clg_dev, geo))
)

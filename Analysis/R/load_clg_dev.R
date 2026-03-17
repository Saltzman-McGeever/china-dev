load_clg_codebook <- function(path) {
  df <- readxl::read_excel(path, sheet = "Definitions_Records", skip = 2)
  names(df) <- c("Field_Name", "Description")
  df[!is.na(df$Field_Name), ]
}

load_clg_dev <- function(path) {
  readxl::read_excel(
    path, sheet = "CLG-Global 1.0_Records", guess_max = 100000
  ) |>
    dplyr::filter(Recommended_for_Aggregates == "Yes") |>
    dplyr::filter(Intent == "Development")
}

load_geo <- function(path) {
  sf::st_read(path, layer = "all_combined_global", quiet = TRUE)
}

merge_clg_geo <- function(clg_dev, geo) {
  dplyr::inner_join(
    clg_dev,
    geo,
    by = c("AidData_Record_ID" = "id")
  ) |>
    sf::st_as_sf()
}

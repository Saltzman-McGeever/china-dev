library(dplyr)
library(plotly)

# Shared geo layout used by all choropleth maps
.geo_layout <- list(
  showframe      = TRUE,
  framecolor     = "rgb(100, 100, 100)",
  showcoastlines = TRUE,
  coastlinecolor = "rgb(120, 120, 120)",
  coastlinewidth = 0.8,
  projection     = list(type = "natural earth"),
  showland       = TRUE,
  landcolor      = "rgb(242, 242, 242)",
  showcountries  = TRUE,
  countrycolor   = "rgb(255, 255, 255)",
  showocean      = TRUE,
  oceancolor     = "rgb(230, 245, 255)",
  showlakes      = TRUE,
  lakecolor      = "rgb(230, 245, 255)",
  bgcolor        = "rgba(255, 255, 255, 0)"
)


# ---------------------------------------------------------------------------
# create_temporal_trends
# ---------------------------------------------------------------------------
create_temporal_trends <- function(df,
                                   year_col    = "Commitment_Year",
                                   amount_col  = "Amount_Constant_USD_2023",
                                   project_col = "AidData_Record_ID") {
  yearly <- df |>
    group_by(Year = .data[[year_col]]) |>
    summarise(
      Project_Count          = n_distinct(.data[[project_col]]),
      Total_Spending_Billions = sum(.data[[amount_col]], na.rm = TRUE) / 1e9
    )

  plot_ly(yearly) |>
    add_bars(
      x      = ~Year, y = ~Project_Count,
      name   = "Number of Projects",
      marker = list(color = "rgb(253, 141, 60)", opacity = 0.8),
      yaxis  = "y"
    ) |>
    add_lines(
      x      = ~Year, y = ~Total_Spending_Billions,
      name   = "Total Spending (Billions USD)",
      line   = list(color = "rgb(70, 130, 180)", width = 3),
      mode   = "lines+markers",
      marker = list(size = 8, color = "rgb(54, 100, 139)"),
      yaxis  = "y2"
    ) |>
    layout(
      xaxis = list(
        title     = "Year",
        showgrid  = FALSE,
        showline  = TRUE,
        linewidth = 1,
        linecolor = "rgb(200, 200, 200)"
      ),
      yaxis = list(
        title      = "Number of Projects",
        showgrid   = TRUE,
        gridwidth  = 1,
        gridcolor  = "rgb(240, 240, 240)",
        showline   = FALSE
      ),
      yaxis2 = list(
        title     = "Total Spending (Billions USD 2023)",
        overlaying = "y",
        side       = "right",
        showgrid   = FALSE,
        showline   = FALSE
      ),
      hovermode    = "x unified",
      showlegend   = TRUE,
      legend       = list(
        orientation = "h", yanchor = "bottom", y = 1.02,
        xanchor = "left", x = 0,
        bgcolor = "rgba(255,255,255,0)", bordercolor = "rgba(0,0,0,0)",
        borderwidth = 0, font = list(size = 10)
      ),
      plot_bgcolor  = "white",
      paper_bgcolor = "white",
      margin        = list(l = 50, r = 50, t = 30, b = 50),
      font          = list(family = "Arial, sans-serif", size = 11,
                           color = "rgb(80, 80, 80)")
    )
}


# ---------------------------------------------------------------------------
# create_flat_map_visualization
# ---------------------------------------------------------------------------
create_flat_map_visualization <- function(df,
                                          agg_col          = "AidData_Record_ID",
                                          agg_func         = "count",
                                          value_label      = "Projects",
                                          country_col      = "Country_of_Activity",
                                          color_scale      = "Greens",
                                          zmax             = NULL,
                                          use_percentiles  = FALSE,
                                          format_fn        = NULL,
                                          outlier_color    = NULL,
                                          outlier_countries = NULL) {

  # Aggregate by country
  country_agg <- df |>
    group_by(Country = .data[[country_col]]) |>
    summarise(
      Value = switch(agg_func,
        "count"  = n(),
        "nunique" = n_distinct(.data[[agg_col]]),
        "sum"    = sum(.data[[agg_col]], na.rm = TRUE),
        "mean"   = mean(.data[[agg_col]], na.rm = TRUE),
        "median" = median(.data[[agg_col]], na.rm = TRUE),
        stop(paste("Unknown agg_func:", agg_func))
      )
    )

  # Exclude outlier countries from main choropleth
  if (!is.null(outlier_countries)) {
    main_agg <- country_agg |> filter(!Country %in% names(outlier_countries))
  } else {
    main_agg <- country_agg
  }

  # Default format function: currency with B/M units
  if (is.null(format_fn)) {
    format_fn <- function(v) {
      if (v >= 1e9)      sprintf("$%.2fB", v / 1e9)
      else if (v >= 1e6) sprintf("$%.2fM", v / 1e6)
      else               sprintf("$%.2f", v)
    }
  }

  main_agg <- main_agg |>
    mutate(fmt = sapply(Value, format_fn))

  .colorbar <- list(
    len = 0.8, thickness = 15,
    tickfont = list(size = 10),
    y = 0.5, yanchor = "middle",
    x = 1.0, xanchor = "left"
  )

  # Build choropleth
  if (use_percentiles) {
    boundaries <- quantile(main_agg$Value, probs = seq(0, 1, by = 0.1), na.rm = TRUE)
    main_agg <- main_agg |>
      mutate(
        Decile = as.numeric(cut(Value,
                                breaks = unique(boundaries),
                                labels = FALSE,
                                include.lowest = TRUE)) - 1
      )

    yl_to_pu <- list(
      list(0.0,  "rgb(255, 253, 208)"),
      list(0.11, "rgb(255, 247, 190)"),
      list(0.22, "rgb(255, 237, 170)"),
      list(0.33, "rgb(255, 223, 160)"),
      list(0.44, "rgb(255, 205, 180)"),
      list(0.56, "rgb(240, 190, 210)"),
      list(0.67, "rgb(220, 190, 230)"),
      list(0.78, "rgb(200, 180, 220)"),
      list(0.89, "rgb(180, 160, 210)"),
      list(1.0,  "rgb(160, 140, 190)")
    )

    fig <- plot_ly(
      main_agg,
      type          = "choropleth",
      locations     = ~Country,
      locationmode  = "country names",
      z             = ~Decile,
      colorscale    = yl_to_pu,
      zmin          = -0.5, zmax = 9.5,
      customdata    = ~fmt,
      hovertemplate = paste0("<b>%{location}</b><br>", value_label,
                             ": %{customdata}<extra></extra>"),
      colorbar      = .colorbar,
      showscale     = TRUE
    )
  } else {
    fig <- plot_ly(
      main_agg,
      type          = "choropleth",
      locations     = ~Country,
      locationmode  = "country names",
      z             = ~Value,
      colorscale    = color_scale,
      zmin          = 0,
      zmax          = if (!is.null(zmax)) zmax else max(main_agg$Value, na.rm = TRUE),
      customdata    = ~fmt,
      hovertemplate = paste0("<b>%{location}</b><br>", value_label,
                             ": %{customdata}<extra></extra>"),
      colorbar      = .colorbar,
      showscale     = TRUE
    )
  }

  fig <- fig |>
    layout(
      geo          = .geo_layout,
      autosize     = TRUE,
      height       = 500,
      showlegend   = FALSE,
      margin       = list(l = 0, r = 100, t = 10, b = 10),
      paper_bgcolor = "rgba(255, 255, 255, 0)",
      plot_bgcolor  = "rgba(255, 255, 255, 0)"
    )

  # Add outlier countries as separate solid-color traces
  oc <- if (!is.null(outlier_color)) outlier_color else "rgb(0, 35, 14)"
  if (!is.null(outlier_countries)) {
    for (cname in names(outlier_countries)) {
      rows <- country_agg |> filter(Country == cname)
      if (nrow(rows) > 0) {
        val_str <- format_fn(rows$Value[1])
        fig <- fig |>
          add_trace(
            type          = "choropleth",
            locations     = cname,
            locationmode  = "country names",
            z             = 1,
            colorscale    = list(list(0, oc), list(1, oc)),
            showscale     = FALSE,
            showlegend    = FALSE,
            hovertemplate = paste0("<b>", cname, "</b><br>",
                                   value_label, ": ", val_str, "<br>",
                                   "<i>Outlier \u2014 exceeds color scale</i><extra></extra>")
          )
      }
    }
  }

  fig
}



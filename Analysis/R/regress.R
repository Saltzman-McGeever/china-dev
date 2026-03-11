library(plotly)

regress <- function(model, y_value, x_value, label = "") {
  reg_data <- model[, c(x_value, y_value)]
  reg_data <- reg_data[complete.cases(reg_data), ]

  formula <- as.formula(paste0("`", y_value, "` ~ `", x_value, "`"))
  fit      <- lm(formula, data = reg_data)
  s        <- summary(fit)

  # Print simplified output (mirrors statsmodels summary table 1)
  print(s$coefficients)
  cat(sprintf("\nR\u00b2: %.4f\n",     s$r.squared))
  cat(sprintf("Adj. R\u00b2: %.4f\n", s$adj.r.squared))
  cat(sprintf("N: %d\n\n",            nrow(reg_data)))

  # Forest plot with 95% CI
  ci  <- confint(fit)
  est <- coef(fit)[x_value]
  lo  <- ci[x_value, 1]
  hi  <- ci[x_value, 2]

  fig <- plot_ly() |>
    add_markers(
      x      = est,
      y      = x_value,
      error_x = list(
        type      = "data",
        symmetric = FALSE,
        array     = hi - est,
        arrayminus = est - lo,
        color     = "steelblue",
        thickness = 2,
        width     = 5
      ),
      marker    = list(size = 8, color = "steelblue"),
      showlegend = FALSE
    ) |>
    layout(
      title  = list(text = paste0("Regress ", y_value, " on ", x_value)),
      xaxis  = list(title = "Coefficient Estimate (95% CI)"),
      yaxis  = list(title = ""),
      shapes = list(list(
        type = "line",
        x0 = 0, x1 = 0,
        y0 = 0, y1 = 1, yref = "paper",
        line = list(color = "red", dash = "dash", width = 1)
      )),
      plot_bgcolor  = "white",
      paper_bgcolor = "white",
      showlegend    = FALSE
    )

  print(fig)
  invisible(fit)
}

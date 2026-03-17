library(ggplot2)
library(dplyr)
library(knitr)
library(kableExtra)

source(here::here("analysis", "R", "style.R"))

# ============================================================================
# MODEL FITTING
# ============================================================================

fit_model <- function(lhs, rhs, data, weights_var = NULL) {
  f      <- as.formula(paste0("`", lhs, "` ~ ", paste0("`", rhs, "`", collapse = " + ")))
  needed <- unique(c(all.vars(f), weights_var))
  d      <- data |> select(any_of(needed)) |> drop_na()

  if (nrow(d) < length(rhs) + 2) return(NULL)

  m <- if (!is.null(weights_var)) {
    lm(f, data = d, weights = d[[weights_var]])
  } else {
    lm(f, data = d)
  }

  list(
    model = m,
    vcov  = vcov(m),
    nobs  = nrow(d)
  )
}

# ============================================================================
# COEFFICIENT EXTRACTION
# ============================================================================

extract_forest_data <- function(fit, focal_vars, coef_rename = NULL) {
  if (is.null(fit)) return(NULL)

  m         <- fit$model
  v         <- fit$vcov
  available <- intersect(focal_vars, names(coef(m)))
  if (length(available) == 0) return(NULL)

  est  <- coef(m)[available]
  se   <- sqrt(diag(v)[available])
  df   <- fit$model$df.residual
  crit <- qt(0.975, df = df)
  pval <- 2 * pt(abs(est / se), df = df, lower.tail = FALSE)

  labels <- if (!is.null(coef_rename)) {
    ifelse(available %in% names(coef_rename), coef_rename[available], available)
  } else {
    available
  }

  data.frame(
    variable  = available,
    label     = labels,
    estimate  = unname(est),
    ci_lower  = unname(est - crit * se),
    ci_upper  = unname(est + crit * se),
    se        = unname(se),
    pval      = unname(pval),
    row.names = NULL
  )
}

# ============================================================================
# HELPERS
# ============================================================================

fmt_coef <- function(x) {
  abs_x <- abs(x)
  sign  <- ifelse(x < 0, "-", "")
  dplyr::case_when(
    abs_x >= 1e12 ~ paste0(sign, round(abs_x / 1e12, 1), "T"),
    abs_x >= 1e9  ~ paste0(sign, round(abs_x / 1e9,  1), "B"),
    abs_x >= 1e6  ~ paste0(sign, round(abs_x / 1e6,  1), "M"),
    abs_x >= 1e3  ~ paste0(sign, round(abs_x / 1e3,  1), "K"),
    TRUE          ~ paste0(sign, signif(abs_x, 3))
  )
}

# ============================================================================
# FOREST PLOT
# ============================================================================

plot_forest <- function(forest_data, title = NULL, subtitle = NULL) {
  if (is.null(forest_data) || nrow(forest_data) == 0) return(invisible(NULL))
  forest_data <- forest_data[!is.na(forest_data$ci_lower) & !is.na(forest_data$ci_upper), ]
  if (nrow(forest_data) == 0) return(invisible(NULL))

  forest_data$label <- factor(forest_data$label, levels = rev(forest_data$label))
  forest_data$sig_level <- dplyr::case_when(
    forest_data$pval < 0.001 ~ "p001",
    forest_data$pval < 0.01  ~ "p01",
    forest_data$pval < 0.05  ~ "p05",
    TRUE                      ~ "ns"
  )

  stars <- dplyr::case_when(
    forest_data$pval < 0.001 ~ "***",
    forest_data$pval < 0.01  ~ "**",
    forest_data$pval < 0.05  ~ "*",
    forest_data$pval < 0.1   ~ "+",
    TRUE                      ~ ""
  )

  sig_colors <- c(
    p001 = STYLE$red,
    p01  = STYLE$red_medium,
    p05  = STYLE$red_light,
    ns   = STYLE$grey_muted
  )
  dot_color <- sig_colors[forest_data$sig_level]

  single <- nrow(forest_data) == 1

  p <- ggplot(forest_data, aes(x = estimate, y = label, color = sig_level))

  if (single) {
    p <- p +
      geom_rect(
        aes(xmin = ci_lower, xmax = ci_upper, ymin = 0.72, ymax = 1.28),
        fill       = dot_color,
        alpha      = 0.12, color = NA, inherit.aes = FALSE,
        data       = forest_data
      )
  }

  p <- p +
    geom_vline(xintercept = 0, linetype = "dashed", color = STYLE$grid, linewidth = 0.6) +
    geom_errorbarh(
      aes(xmin = ci_lower, xmax = ci_upper),
      height    = if (single) 0.14 else 0.2,
      linewidth = if (single) 1.4  else 1.2,
      lineend   = "round"
    ) +
    geom_point(size = if (single) 4 else 3.5, shape = 16) +
    scale_color_manual(
      values = sig_colors,
      guide  = "none"
    ) +
    labs(title = title, subtitle = subtitle, x = "Coefficient Estimate (95% CI)", y = NULL) +
    theme_china() +
    theme(
      panel.grid.major.y = element_blank(),
      panel.grid.major.x = element_line(color = STYLE$grid, linewidth = 0.3),
      axis.text.y        = element_text(face = "bold", color = STYLE$text_dark,
                                        size = STYLE$base_size * 0.8)
    )

  nudge <- diff(range(c(forest_data$ci_lower, forest_data$ci_upper, 0))) * 0.04
  p <- p +
    annotate(
      "text",
      x      = forest_data$ci_upper + nudge,
      y      = as.numeric(forest_data$label),
      label  = stars,
      hjust  = 0, size = 4, fontface = "bold",
      color  = dot_color,
      family = STYLE$font
    ) +
    scale_x_continuous(expand = expansion(mult = c(0.05, 0.12)), labels = fmt_coef) +
    coord_cartesian(clip = "off")

  if (single) {
    p <- p +
      scale_y_discrete(expand = expansion(add = 0.6)) +
      theme(axis.text.y = element_blank(), axis.ticks.y = element_blank())
  }

  p
}

# ============================================================================
# MARGINAL EFFECTS PLOT
# ============================================================================

plot_marginal <- function(fit, y_value, x_value, sig_level = "ns") {
  sig_colors <- c(p001 = STYLE$red, p01 = STYLE$red_medium, p05 = STYLE$red_light, ns = STYLE$grey_muted)
  col <- unname(sig_colors[sig_level])
  if (is.null(fit) || length(x_value) != 1) return(invisible(NULL))

  m     <- fit$model
  d     <- model.frame(m)
  x_col <- x_value[1]

  if (!x_col %in% names(d)) return(invisible(NULL))

  is_binary <- length(unique(d[[x_col]])) <= 2

  if (is_binary) {
    grid <- data.frame(x = c(0, 1))
  } else {
    grid <- data.frame(x = seq(min(d[[x_col]]), max(d[[x_col]]), length.out = 200))
  }
  names(grid) <- x_col

  # Hold other covariates at their mean/mode
  other_vars <- setdiff(names(d), c(y_value, x_col))
  for (v in other_vars) {
    grid[[v]] <- if (is.numeric(d[[v]])) mean(d[[v]], na.rm = TRUE) else
      names(sort(table(d[[v]]), decreasing = TRUE))[1]
  }

  pred        <- predict(m, newdata = grid, interval = "confidence")
  grid$fit    <- pred[, "fit"]
  grid$lwr    <- pred[, "lwr"]
  grid$upr    <- pred[, "upr"]
  grid$x_plot <- grid[[x_col]]

  if (is_binary) {
    grid$label <- factor(
      ifelse(grid[[x_col]] == 1, "Yes", "No"),
      levels = c("No", "Yes")
    )
    p <- ggplot(grid, aes(x = fit, y = label)) +
      geom_rect(
        aes(xmin = lwr, xmax = upr,
            ymin = as.numeric(label) - 0.28,
            ymax = as.numeric(label) + 0.28),
        fill = col, alpha = 0.12, color = NA, inherit.aes = FALSE,
        data = grid
      ) +
      geom_errorbarh(
        aes(xmin = lwr, xmax = upr),
        height = 0.14, linewidth = 1.4, lineend = "round", color = col
      ) +
      geom_point(size = 4, shape = 16, color = col) +
      scale_x_continuous(labels = fmt_coef, expand = expansion(mult = c(0.05, 0.12))) +
      scale_y_discrete(expand = expansion(add = 0.6)) +
      labs(x = sprintf("Predicted %s (95%% CI)", y_value), y = NULL,
           subtitle = "Predicted value (95% CI)") +
      theme_china() +
      theme(
        panel.grid.major.y = element_blank(),
        panel.grid.major.x = element_line(color = STYLE$grid, linewidth = 0.3),
        axis.text.y        = element_text(face = "bold", color = STYLE$text_dark,
                                          size = STYLE$base_size * 0.8)
      ) +
      coord_cartesian(clip = "off")
  } else {
    p <- ggplot(grid, aes(x = x_plot, y = fit)) +
      geom_ribbon(aes(ymin = lwr, ymax = upr), fill = col, alpha = 0.15) +
      geom_line(color = col, linewidth = 1.2) +
      labs(x = x_col, y = y_value, subtitle = "Predicted value (95% CI)") +
      scale_y_continuous(labels = fmt_coef) +
      theme_china()
  }

  p
}

# ============================================================================
# FORMULA NOTATION
# ============================================================================

format_reg_formula <- function(y_value, x_value) {
  lhs <- sprintf("\\text{%s}_i", gsub("_", "\\\\_", y_value))

  rhs_parts <- sprintf(
    "\\beta_{%d}\\,\\text{%s}_i",
    seq_along(x_value),
    gsub("_", "\\\\_", x_value)
  )

  formula <- sprintf("$\\displaystyle %s = %s + \\varepsilon_i$", lhs, paste(rhs_parts, collapse = " + "))
  sprintf(
    "::: {style=\"overflow-x: auto; overflow-y: hidden; font-size: 1.01em;\"}\n%s\n:::",
    formula
  )
}

# ============================================================================
# TOP-LEVEL HELPER
# ============================================================================

format_codebook_table <- function(y_value, x_value, codebook, var_map = NULL) {
  vars        <- c(y_value, x_value)
  # Remap derived variables to their codebook source names for lookup
  lookup_vars <- ifelse(vars %in% names(var_map), var_map[vars], vars)

  lookup <- codebook[codebook$Field_Name %in% lookup_vars, c("Field_Name", "Description")]
  if (nrow(lookup) == 0) return(invisible(NULL))

  # Restore display names (derived names) while keeping source descriptions
  lookup$Field_Name <- vars[match(lookup$Field_Name, lookup_vars)]
  lookup$Role <- ifelse(lookup$Field_Name == y_value, "Outcome", "Predictor")
  lookup$Role <- factor(lookup$Role, levels = c("Outcome", "Predictor"))
  lookup      <- lookup[order(lookup$Role), c("Role", "Field_Name", "Description")]

  tbl <- knitr::kable(lookup, format = "html", col.names = c("Role", "Variable", "Description")) |>
    kableExtra::kable_styling(
      bootstrap_options = c("striped", "condensed"),
      full_width = TRUE, font_size = 12
    ) |>
    kableExtra::column_spec(1, bold = TRUE, width = "6em") |>
    kableExtra::column_spec(2, width = "14em") |>
    kableExtra::column_spec(3, color = STYLE$text_medium)

  cat(
    '<details><summary style="cursor:pointer;font-size:0.85em;color:', STYLE$text_medium,
    '">Variable definitions</summary>\n', tbl, '\n</details>\n\n',
    sep = ""
  )
}

regress <- function(data, y_value, x_value, codebook = NULL, var_map = NULL) {
  cat(format_reg_formula(y_value, x_value), "\n\n")

  if (!is.null(codebook)) format_codebook_table(y_value, x_value, codebook, var_map)

  fit <- fit_model(y_value, x_value, data)
  if (is.null(fit)) {
    message("Insufficient data to fit model.")
    return(invisible(NULL))
  }

  s        <- suppressWarnings(summary(fit$model))
  fd       <- extract_forest_data(fit, x_value)
  subtitle <- sprintf("N = %s | R\u00b2 = %.4f", format(fit$nobs, big.mark = ","), s$r.squared)
  sig_level <- if (!is.null(fd) && nrow(fd) == 1) {
    p <- fd$pval[1]
    dplyr::case_when(p < 0.001 ~ "p001", p < 0.01 ~ "p01", p < 0.05 ~ "p05", TRUE ~ "ns")
  } else "ns"
  p_forest  <- plot_forest(fd, subtitle = subtitle)
  p_mfx     <- plot_marginal(fit, y_value, x_value, sig_level = sig_level)

  if (!is.null(p_mfx)) {
    save_plot <- function(p, suffix, h = 3) {
      f <- knitr::fig_path(paste0(suffix, ".png"))
      dir.create(dirname(f), recursive = TRUE, showWarnings = FALSE)
      ggplot2::ggsave(f, p, width = 7, height = h, dpi = 150, bg = STYLE$background)
      f
    }
    f1 <- save_plot(p_forest, "forest")
    f2 <- save_plot(p_mfx,    "mfx")
    cat("::: {.panel-tabset}\n\n")
    cat("## Forest Plot\n\n")
    cat(sprintf("![](%s){width=100%%}\n\n", f1))
    cat("## Marginal Effects\n\n")
    cat(sprintf("![](%s){width=100%%}\n\n", f2))
    cat(":::\n\n")
  } else {
    print(p_forest)
  }

  invisible(fit)
}

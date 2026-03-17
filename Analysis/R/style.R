library(ggplot2)
library(showtext)

# Load Source Sans Pro from Google Fonts (fall back to system sans-serif if offline)
.font_loaded <- tryCatch({
  font_add_google("Source Sans Pro", "source_sans")
  showtext_auto()
  "source_sans"
}, error = function(e) "sans")

# ============================================================================
# STYLE GUIDE
#
# Red is the primary accent, evoking China and significance.
# All other content is grey-scale and minimal.
# ============================================================================

STYLE <- list(

  # --- Colors ---
  red          = "#C0392B",   # p < 0.001: full red
  red_medium   = "#D4736C",   # p < 0.01:  medium red
  red_light    = "#E8AEA9",   # p < 0.05:  light red
  grey_muted   = "#AAAAAA",   # Non-significant / secondary
  text_dark    = "#2E3440",   # Titles, axis labels
  text_medium  = "#4C566A",   # Subtitles, captions
  grid         = "#E0E0E0",   # Horizontal grid lines
  background   = "#F5F5F5",   # Plot and panel background

  # --- Typography ---
  font         = .font_loaded,
  base_size    = 14
)

# ============================================================================
# BASE THEME
# ============================================================================

theme_china <- function(base_size = STYLE$base_size) {
  theme_minimal(base_family = STYLE$font, base_size = base_size) +
    theme(
      # Titles
      plot.title        = element_text(
        face = "bold", size = base_size * 1.2, hjust = 0,
        color = STYLE$text_dark, margin = margin(b = 6)
      ),
      plot.subtitle     = element_text(
        size = base_size * 0.8, hjust = 0,
        color = STYLE$text_medium, margin = margin(b = 10)
      ),
      plot.caption      = element_text(
        size = base_size * 0.7, hjust = 0, color = STYLE$text_medium
      ),

      # Panel
      plot.background   = element_rect(fill = STYLE$background, color = NA),
      panel.background  = element_rect(fill = STYLE$background, color = NA),
      panel.grid.major.x = element_blank(),
      panel.grid.minor   = element_blank(),
      panel.grid.major.y = element_line(color = STYLE$grid, linewidth = 0.4),

      # Axes
      axis.text         = element_text(color = STYLE$text_medium, size = base_size * 0.8),
      axis.title        = element_text(color = STYLE$text_dark,   size = base_size * 0.85),
      axis.ticks        = element_blank(),

      # Legend
      legend.background = element_rect(fill = STYLE$background, color = NA),
      legend.key        = element_rect(fill = STYLE$background, color = NA),
      legend.text       = element_text(color = STYLE$text_medium, size = base_size * 0.8),
      legend.title      = element_text(color = STYLE$text_dark,   size = base_size * 0.85),

      plot.margin       = margin(20, 20, 20, 20)
    )
}

# ============================================================================
# ROUNDED RECTANGLE GEOM
# ============================================================================

GeomRrect <- ggplot2::ggproto("GeomRrect", ggplot2::GeomRect,
  draw_panel = function(self, data, panel_params, coord,
                        radius = grid::unit(4, "pt")) {
    coords <- coord$transform(data, panel_params)
    grid::roundrectGrob(
      x      = (coords$xmin + coords$xmax) / 2,
      y      = (coords$ymin + coords$ymax) / 2,
      width  = coords$xmax - coords$xmin,
      height = coords$ymax - coords$ymin,
      r      = radius,
      default.units = "npc",
      gp = grid::gpar(
        col  = coords$colour,
        fill = scales::alpha(coords$fill, coords$alpha),
        lwd  = coords$linewidth * ggplot2::.pt,
        lty  = coords$linetype
      )
    )
  }
)

geom_rrect <- function(mapping = NULL, data = NULL, stat = "identity",
                       position = "identity", radius = grid::unit(4, "pt"),
                       ..., na.rm = FALSE, show.legend = NA,
                       inherit.aes = TRUE) {
  ggplot2::layer(
    geom = GeomRrect, mapping = mapping, data = data, stat = stat,
    position = position, show.legend = show.legend, inherit.aes = inherit.aes,
    params = list(radius = radius, na.rm = na.rm, ...)
  )
}

# ============================================================================
# PLOTLY DEFAULTS (for plots.R)
# ============================================================================

PLOTLY_STYLE <- list(
  font_family   = "Source Sans Pro, Arial, sans-serif",
  font_color    = "#4C566A",
  font_size     = 11,
  bg_color      = "#F5F5F5",
  grid_color    = "#E0E0E0",
  primary_color = "rgb(192, 57, 43)",    # STYLE$red as rgb
  secondary_color = "rgb(170, 170, 170)" # STYLE$grey_muted as rgb
)

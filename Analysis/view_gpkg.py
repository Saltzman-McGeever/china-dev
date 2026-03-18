"""
Visualise aid_data_geospatial.gpkg for Africa in the browser.
Uses simplified polygons (tolerance=0.05°) for fast rendering.
"""
import webbrowser, tempfile, pathlib
import geopandas as gpd
import folium

GPKG = pathlib.Path(__file__).parents[1] / "datasets" / "aid_data_geospatial.gpkg"

AFRICA_ISO = {
    "DZA","AGO","BEN","BWA","BFA","BDI","CPV","CMR","CAF","TCD","COM","COD",
    "COG","CIV","DJI","EGY","GNQ","ERI","SWZ","ETH","GAB","GMB","GHA","GIN",
    "GNB","KEN","LSO","LBR","LBY","MDG","MWI","MLI","MRT","MUS","MAR","MOZ",
    "NAM","NER","NGA","RWA","STP","SEN","SLE","SOM","ZAF","SSD","SDN","TZA",
    "TGO","TUN","UGA","ZMB","ZWE",
}

print("Loading…")
gdf = gpd.read_file(GPKG)

africa = gdf[gdf["Recipient.ISO-3"].isin(AFRICA_ISO)].copy()
print(f"{len(africa):,} features for Africa")

# Top 5% by loan amount
amt_col = "Amount.(Constant.USD.2021)"
threshold = africa[amt_col].quantile(0.75)
africa = africa[africa[amt_col] >= threshold].copy()
print(f"{len(africa):,} features after top-5% filter (≥ ${threshold:,.0f})")

# Simplify geometry for fast rendering
africa["geometry"] = africa["geometry"].simplify(tolerance=0.01, preserve_topology=True)

m = folium.Map(location=[5, 20], zoom_start=3, tiles="CartoDB positron")

folium.GeoJson(
    africa,
    name="AidData projects",
    style_function=lambda _: {
        "fillColor": "#c0392b",
        "color": "#922b21",
        "weight": 0.5,
        "fillOpacity": 0.35,
    },
    tooltip=folium.GeoJsonTooltip(
        fields=["Title", "Recipient", "Sector.Name",
                "Amount.(Constant.USD.2021)", "Commitment.Year"],
        aliases=["Title", "Recipient", "Sector", "Amount (USD 2021)", "Year"],
        localize=True,
    ),
).add_to(m)

folium.LayerControl().add_to(m)

out = pathlib.Path(tempfile.mktemp(suffix=".html"))
m.save(str(out))
print(f"Saved → {out}")
webbrowser.open(out.as_uri())

import os
import geopandas as gpd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.feature import ShapelyFeature
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
from mpl_toolkits.axes_grid1.inset_locator import inset_axes


# =========================================================
# SETTINGS
# =========================================================

DATA_FOLDER = "data_files"
PROJECTION = "EPSG:32629"

files = {
    "outline": "NI_outline.shp",
    "towns": "Towns.shp",
    "water": "Water.shp",
    "rivers": "Rivers.shp",
    "counties": "Counties.shp"
}

county_colors = ['#003f5c', '#444e86', '#955196',
                 '#dd5182', '#ff6e54', '#ffa600']


# =========================================================
# LOAD DATA
# =========================================================

def load(path):
    return gpd.read_file(os.path.join(DATA_FOLDER, path)).to_crs(PROJECTION)


outline = load(files["outline"])
towns = load(files["towns"])
water = load(files["water"])
rivers = load(files["rivers"])
counties = load(files["counties"])


# =========================================================
# MAP SETUP
# =========================================================

crs = ccrs.UTM(29)

fig = plt.figure(figsize=(10, 10))
ax = plt.axes(projection=crs)


# =========================================================
# BACKGROUND (FIXED LOCATION)
# =========================================================

ax.add_feature(cfeature.OCEAN, facecolor="#cfe8ff", zorder=0)
ax.add_feature(cfeature.LAND, facecolor="#f2f2f2", zorder=0)
ax.add_feature(cfeature.COASTLINE, linewidth=0.5, zorder=1)
ax.add_feature(cfeature.BORDERS, linewidth=0.5, zorder=1)


# =========================================================
# EXTENT
# =========================================================

xmin, ymin, xmax, ymax = outline.total_bounds
ax.set_extent([xmin-5000, xmax+5000, ymin-5000, ymax+5000], crs=crs)


# =========================================================
# OUTLINE
# =========================================================

ax.add_feature(
    ShapelyFeature(outline.geometry, crs,
                   edgecolor="black",
                   facecolor="white",
                   linewidth=1,
                   zorder=2)
)


# =========================================================
# COUNTIES
# =========================================================

county_names = sorted(counties.CountyName.unique())

for i, name in enumerate(county_names):
    subset = counties[counties["CountyName"] == name]

    ax.add_feature(
        ShapelyFeature(subset.geometry, crs,
                       edgecolor="black",
                       facecolor=county_colors[i % len(county_colors)],
                       alpha=0.85,
                       linewidth=1,
                       zorder=3)
    )


# =========================================================
# WATER + RIVERS
# =========================================================

ax.add_feature(
    ShapelyFeature(water.geometry, crs,
                   edgecolor="mediumblue",
                   facecolor="mediumblue",
                   zorder=4)
)

ax.add_feature(
    ShapelyFeature(rivers.geometry, crs,
                   edgecolor="royalblue",
                   linewidth=0.5,
                   zorder=5)
)


# =========================================================
# TOWNS
# =========================================================

ax.plot(
    towns.geometry.x,
    towns.geometry.y,
    's',
    color='0.4',
    ms=5,
    transform=crs,
    zorder=6
)

for _, row in towns.iterrows():
    ax.text(
        row.geometry.x,
        row.geometry.y,
        row["TOWN_NAME"].title(),
        fontsize=7,
        fontweight='bold',
        bbox=dict(facecolor='white', alpha=0.6, edgecolor='none'),
        transform=crs,
        zorder=7
    )


# =========================================================
# SCALE BAR
# =========================================================

def scale_bar(ax, length=20):
    x0, x1, y0, y1 = ax.get_extent()

    sbx = x0 + (x1 - x0) * 0.92
    sby = y0 + (y1 - y0) * 0.95

    ax.plot([sbx, sbx - length * 1000],
            [sby, sby],
            color="black",
            linewidth=4,
            transform=crs)

    ax.text(sbx, sby - 2000, f"{length} km",
            transform=crs,
            ha="center", fontsize=8)


scale_bar(ax)


# =========================================================
# NORTH ARROW
# =========================================================

ax.annotate(
    "N",
    xy=(0.93, 0.15),
    xytext=(0.93, 0.15),
    xycoords="axes fraction",
    textcoords="axes fraction",
    ha="center",
    va="center",
    fontsize=14,
    fontweight="bold",
    arrowprops=dict(facecolor="black", width=4, headwidth=10)
)


# =========================================================
# LEGEND
# =========================================================

county_handles = [
    mpatches.Rectangle((0, 0), 1, 1,
                       facecolor=county_colors[i % len(county_colors)],
                       edgecolor="black")
    for i in range(len(county_names))
]

labels = [name.title() for name in county_names]

legend_handles = county_handles + [
    mpatches.Patch(color="mediumblue", label="Lakes"),
    mlines.Line2D([], [], color="royalblue", label="Rivers"),
    mlines.Line2D([], [], color="0.4", marker="s", linestyle="None", label="Towns")
]

labels += ["Lakes", "Rivers", "Towns"]

ax.legend(legend_handles, labels,
          loc="upper left",
          frameon=True,
          framealpha=1,
          title="Legend")


# =========================================================
# INSET MAP (FIXED)
# =========================================================

ax_inset = fig.add_axes(
    [0.05, 0.05, 0.25, 0.25],
    projection=ccrs.PlateCarree()
)

ax_inset.set_global()
ax_inset.add_feature(cfeature.COASTLINE, linewidth=0.5)
ax_inset.add_feature(cfeature.BORDERS, linewidth=0.5)

ax_inset.set_extent([-10, 2, 50, 60])
ax_inset.set_title("UK Context", fontsize=8)


# =========================================================
# TITLE + FOOTNOTE
# =========================================================

plt.title("Northern Ireland Physical & Administrative Map",
          fontsize=14, pad=15)

plt.figtext(
    0.5, 0.01,
    "Data source: OpenData NI | Projection: UTM Zone 29N",
    ha="center",
    fontsize=8
)


# =========================================================
# EXPORT
# =========================================================

plt.savefig("map.png", dpi=300, bbox_inches="tight")
plt.show()
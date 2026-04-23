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
# 1. USER SETTINGS (EDIT THIS SECTION ONLY)
# =========================================================

DATA_FOLDER = "data_files"

LAYER_FILES = {
    "outline": "NI_outline.shp",
    "towns": "Towns.shp",
    "water": "Water.shp",
    "rivers": "Rivers.shp",
    "admin": "Counties.shp"
}

ATTRIBUTE_FIELDS = {
    "town_name": "TOWN_NAME",
    "admin_name": "CountyName"
}

OUTPUT_FILE = "map.png"

PROJECTION = "EPSG:32629"   # UTM Zone 29N (Northern Ireland)

COUNTY_COLORS = [
    '#003f5c', '#444e86', '#955196',
    '#dd5182', '#ff6e54', '#ffa600'
]


# =========================================================
# 2. HELPER FUNCTIONS
# =========================================================

def load_data():
    layers = {}
    for key, file in LAYER_FILES.items():
        path = os.path.join(DATA_FOLDER, file)
        layers[key] = gpd.read_file(path).to_crs(PROJECTION)
    return layers


def add_north_arrow(ax, location=(0.93, 0.15)):
    ax.annotate(
        'N',
        xy=location,
        xytext=location,
        xycoords='axes fraction',
        textcoords='axes fraction',
        ha='center',
        va='center',
        fontsize=14,
        fontweight='bold',
        arrowprops=dict(facecolor='black', width=4, headwidth=10)
    )


def add_scale_bar(ax, length_km=20):
    x0, x1, y0, y1 = ax.get_extent()
    sbx = x0 + (x1 - x0) * 0.92
    sby = y0 + (y1 - y0) * 0.95

    ax.plot([sbx, sbx - length_km * 1000],
            [sby, sby],
            color='black',
            linewidth=4,
            transform=ccrs.UTM(29))

    ax.text(sbx, sby - 2000, f"{length_km} km",
            transform=ccrs.UTM(29),
            ha='center', fontsize=8)


def create_handles(labels, colors):
    return [
        mpatches.Rectangle((0, 0), 1, 1,
                           facecolor=colors[i % len(colors)],
                           edgecolor='black')
        for i in range(len(labels))
    ]


# =========================================================
# 3. LOAD DATA
# =========================================================

data = load_data()

outline = data["outline"]
towns = data["towns"]
water = data["water"]
rivers = data["rivers"]
admin = data["admin"]


# =========================================================
# 4. MAP SETUP
# =========================================================

crs = ccrs.UTM(29)

fig = plt.figure(figsize=(10, 10))
ax = plt.axes(projection=crs)


# Background
ax.add_feature(cfeature.OCEAN, facecolor='#cfe8ff', zorder=0)
ax.add_feature(cfeature.LAND, facecolor='#f2f2f2', zorder=0)
ax.add_feature(cfeature.COASTLINE, linewidth=0.5, zorder=1)


# Extent
xmin, ymin, xmax, ymax = outline.total_bounds
ax.set_extent([xmin-5000, xmax+5000, ymin-5000, ymax+5000], crs=crs)


# =========================================================
# 5. THEMATIC LAYERS
# =========================================================

# Outline
ax.add_feature(ShapelyFeature(outline.geometry, crs,
                              edgecolor='black',
                              facecolor='white',
                              linewidth=1,
                              zorder=2))


# Admin areas (e.g. counties)
admin_names = sorted(admin[ATTRIBUTE_FIELDS["admin_name"]].unique())

for i, name in enumerate(admin_names):
    subset = admin[admin[ATTRIBUTE_FIELDS["admin_name"]] == name]

    ax.add_feature(
        ShapelyFeature(subset.geometry, crs,
                       edgecolor='black',
                       facecolor=COUNTY_COLORS[i % len(COUNTY_COLORS)],
                       alpha=0.85,
                       linewidth=1,
                       zorder=3)
    )


# Water
ax.add_feature(ShapelyFeature(water.geometry, crs,
                              edgecolor='mediumblue',
                              facecolor='mediumblue',
                              zorder=4))


# Rivers
ax.add_feature(ShapelyFeature(rivers.geometry, crs,
                              edgecolor='royalblue',
                              linewidth=0.5,
                              zorder=5))


# Towns
ax.plot(
    towns.geometry.x,
    towns.geometry.y,
    's',
    color='0.4',
    ms=5,
    transform=crs,
    zorder=6
)


# Labels
for _, row in towns.iterrows():
    ax.text(
        row.geometry.x,
        row.geometry.y,
        row[ATTRIBUTE_FIELDS["town_name"]].title(),
        fontsize=7,
        fontweight='bold',
        bbox=dict(facecolor='white', alpha=0.6, edgecolor='none'),
        transform=crs,
        zorder=7
    )


# =========================================================
# 6. MAP ELEMENTS
# =========================================================

add_scale_bar(ax)
add_north_arrow(ax)

ax.set_title("GIS Map Output", fontsize=14, pad=15)


# Legend
handles = create_handles(admin_names, COUNTY_COLORS)
labels = [name.title() for name in admin_names]

handles += [
    mpatches.Patch(color='mediumblue', label='Lakes'),
    mlines.Line2D([], [], color='royalblue', label='Rivers'),
    mlines.Line2D([], [], color='0.4', marker='s', linestyle='None', label='Towns')
]

labels += ["Lakes", "Rivers", "Towns"]

ax.legend(handles, labels,
          loc='upper left',
          frameon=True,
          framealpha=1)


# =========================================================
# 7. INSET MAP (UK CONTEXT)
# =========================================================

ax_inset = inset_axes(ax,
                      width="30%",
                      height="30%",
                      loc="lower left",
                      axes_class=plt.Axes,
                      axes_kwargs=dict(projection=ccrs.PlateCarree()))

ax_inset.set_global()
ax_inset.add_feature(cfeature.COASTLINE, linewidth=0.5)
ax_inset.add_feature(cfeature.BORDERS, linewidth=0.5)
ax_inset.set_extent([-10, 2, 50, 60])
ax_inset.set_title("UK Context", fontsize=8)


# =========================================================
# 8. EXPORT
# =========================================================

plt.figtext(
    0.5, 0.01,
    "Data source: OpenData NI | Projection: UTM Zone 29N",
    ha='center',
    fontsize=8
)

plt.savefig(OUTPUT_FILE, dpi=300, bbox_inches='tight')
plt.show()
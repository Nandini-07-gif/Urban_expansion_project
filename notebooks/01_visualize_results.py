import rasterio
import matplotlib.pyplot as plt

years = [2015, 2020, 2025]

fig, axes = plt.subplots(1, 3, figsize=(18, 6))

for ax, year in zip(axes, years):

    file_path = f"data/urban_classification_{year}.tif"

    with rasterio.open(file_path) as src:
        image = src.read(1)

    ax.imshow(image, cmap="RdYlGn")
    ax.set_title(f"Urban Classification {year}")
    ax.axis("off")

plt.suptitle(
    "AI-Based Satellite Detection of Urban Expansion",
    fontsize=16
)

plt.tight_layout()

plt.savefig(
    "results/urban_classification_comparison.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()
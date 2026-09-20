import rasterio
import matplotlib.pyplot as plt

# Load 2015 classification
with rasterio.open("data/urban_classification_2015.tif") as src:
    classified2015 = src.read(1)
    transform = src.transform

# Load 2025 classification
with rasterio.open("data/urban_classification_2025.tif") as src:
    classified2025 = src.read(1)

# Urban expansion:
# 2015 = Non-Urban (0)
# 2025 = Urban (1)

urban_expansion = (
    (classified2015 == 0) &
    (classified2025 == 1)
)

# Create the figure
plt.figure(figsize=(10, 8))

plt.imshow(
    urban_expansion,
    cmap="YlOrBr"
)

plt.title(
    "Urban Expansion in Bangalore Urban District\n2015–2025",
    fontsize=16
)

plt.axis("off")

plt.tight_layout()

# Save result
plt.savefig(
    "results/urban_expansion_2015_2025.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()
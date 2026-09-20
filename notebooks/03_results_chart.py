import matplotlib.pyplot as plt

years = [2015, 2020, 2025]

urban_area = [
    1400.9514,
    1354.6360,
    1457.1187
]

plt.figure(figsize=(10, 6))

bars = plt.bar(
    years,
    urban_area
)

plt.title(
    "Random Forest–Classified Urban Area\nBangalore Urban District (2015–2025)",
    fontsize=15
)

plt.xlabel("Year")
plt.ylabel("Classified Urban Area (km²)")

plt.xticks(years)

# Add values above bars
for bar, value in zip(bars, urban_area):
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 15,
        f"{value:.1f} km²",
        ha="center"
    )

plt.tight_layout()

plt.savefig(
    "results/urban_area_2015_2025.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()
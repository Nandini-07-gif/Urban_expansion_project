import streamlit as st
import rasterio
import numpy as np
import pandas as pd
import plotly.express as px
from pathlib import Path


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Urban Expansion Monitor",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# PROJECT PATHS
# ============================================================

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"


# ============================================================
# PROJECT DATA
# ============================================================

YEARS = [2015, 2020, 2025]

# Earth Engine classified urban-area results
URBAN_AREA = {
    2015: 1400.9514267785637,
    2020: 1354.6360334354997,
    2025: 1457.1187413588416
}

# Validation results
VALIDATION = {
    2015: {
        "accuracy": 86.75,
        "kappa": 0.735
    },
    2020: {
        "accuracy": 84.91,
        "kappa": 0.698
    },
    2025: {
        "accuracy": 84.90,
        "kappa": 0.698
    }
}

TOTAL_AREA = 2187.3123452556

GROSS_EXPANSION = 271.240521769
GROSS_LOSS = 215.073207189
NET_CHANGE = 56.167314580


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background-color: #0b1220;
    }

    .block-container {
        max-width: 1400px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }

    /* HERO */

    .hero {
        padding: 2.5rem;
        border-radius: 22px;
        background: linear-gradient(
            135deg,
            #111827 0%,
            #172554 100%
        );
        border: 1px solid #263449;
        margin-bottom: 2rem;
    }

    .hero h1 {
        font-size: 2.8rem;
        margin-bottom: 0.5rem;
    }

    .hero p {
        color: #aab6c8;
        font-size: 1.05rem;
        margin-bottom: 0;
    }

    /* CARDS */

    .card {
        background: #111827;
        border: 1px solid #263449;
        border-radius: 16px;
        padding: 1.4rem;
        height: 100%;
        margin-bottom: 0.5rem;
    }

    .card-title {
        color: #94a3b8;
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }

    .card-value {
        font-size: 1.65rem;
        font-weight: 700;
        margin-top: 0.4rem;
    }

    .card-description {
        color: #64748b;
        font-size: 0.8rem;
        margin-top: 0.3rem;
    }

    /* SECTION */

    .section {
        font-size: 1.45rem;
        font-weight: 650;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }

    /* INFO BOX */

    .info {
        background: #111827;
        border-left: 4px solid #60a5fa;
        padding: 1rem 1.2rem;
        border-radius: 8px;
        margin: 1rem 0;
    }

    /* MAP LEGEND */

    .legend {
        display: flex;
        gap: 1.5rem;
        align-items: center;
        background: #111827;
        border: 1px solid #263449;
        padding: 0.8rem 1rem;
        border-radius: 10px;
        margin-top: 0.5rem;
        margin-bottom: 1rem;
    }

    .legend-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: #cbd5e1;
        font-size: 0.85rem;
    }

    .legend-box {
        width: 16px;
        height: 16px;
        border-radius: 4px;
        display: inline-block;
    }

    .urban {
        background: rgb(220, 80, 50);
    }

    .nonurban {
        background: rgb(70, 150, 90);
    }

    /* SMALL TEXT */

    .muted {
        color: #94a3b8;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# FUNCTIONS
# ============================================================

@st.cache_data
def load_raster(year):
    """
    Load the original 0/1 classification raster.

    0 = Non-Urban
    1 = Urban
    """

    path = DATA_DIR / f"urban_classification_{year}.tif"

    if not path.exists():
        st.error(
            f"Raster file not found: {path}"
        )
        st.stop()

    with rasterio.open(path) as src:
        image = src.read(1)

    return image


@st.cache_data
def load_classification(year):
    """
    Convert classification raster into RGB image
    for dashboard display.
    """

    image = load_raster(year)

    rgb = np.zeros(
        (image.shape[0], image.shape[1], 3),
        dtype=np.uint8
    )

    # Non-Urban
    rgb[image == 0] = [70, 150, 90]

    # Urban
    rgb[image == 1] = [220, 80, 50]

    # NoData / invalid pixels
    rgb[image < 0] = [0, 0, 0]

    return rgb


def calculate_area(image):
    """
    Calculate classified urban area from raster.

    Uses 30 m × 30 m pixels.
    """

    valid = image >= 0

    urban_pixels = np.sum(
        (image == 1) & valid
    )

    pixel_area_km2 = (
        30 * 30
    ) / 1_000_000

    return urban_pixels * pixel_area_km2


def calculate_change(image1, image2):
    """
    Calculate gross expansion and gross loss.

    Expansion:
        Non-Urban → Urban

    Loss:
        Urban → Non-Urban
    """

    valid = (
        (image1 >= 0)
        &
        (image2 >= 0)
    )

    expansion = np.sum(
        (image1 == 0)
        &
        (image2 == 1)
        &
        valid
    )

    loss = np.sum(
        (image1 == 1)
        &
        (image2 == 0)
        &
        valid
    )

    pixel_area_km2 = (
        30 * 30
    ) / 1_000_000

    expansion_area = (
        expansion * pixel_area_km2
    )

    loss_area = (
        loss * pixel_area_km2
    )

    return expansion_area, loss_area


def create_area_dataframe():
    """
    Create dataframe for urban-area charts.
    """

    return pd.DataFrame({
        "Year": YEARS,
        "Classified Urban Area (km²)": [
            URBAN_AREA[y]
            for y in YEARS
        ]
    })


def create_validation_dataframe():
    """
    Create dataframe for validation metrics.
    """

    return pd.DataFrame({
        "Year": YEARS,
        "Validation Accuracy (%)": [
            VALIDATION[y]["accuracy"]
            for y in YEARS
        ],
        "Kappa": [
            VALIDATION[y]["kappa"]
            for y in YEARS
        ]
    })


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## 🛰️ Urban Monitor")

    st.caption(
        "AI-Based Satellite Detection"
    )

    st.divider()

    page = st.radio(
        "Dashboard",
        [
            "Overview",
            "Explore Maps",
            "Compare Years",
            "Model Performance",
            "Methodology"
        ]
    )

    st.divider()

    st.markdown("### Study Area")

    st.write(
        "Bangalore Urban District"
    )

    st.markdown("### Satellite")

    st.write(
        "Landsat"
    )

    st.markdown("### Model")

    st.write(
        "Random Forest"
    )

    st.markdown("### Resolution")

    st.write(
        "30 m"
    )

    st.divider()

    st.caption(
        "2015 → 2020 → 2025"
    )


# ============================================================
# HERO
# ============================================================

st.markdown(
    """
    <div class="hero">

    <h1>🛰️ Urban Expansion Monitor</h1>

    <p>
    AI-Based Satellite Detection of Urban Expansion
    in Bangalore Urban District, Karnataka
    </p>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# OVERVIEW
# ============================================================

if page == "Overview":

    st.markdown(
        '<div class="section">📊 Project Overview</div>',
        unsafe_allow_html=True
    )

    st.write(
        """
        This dashboard presents the results of a supervised machine
        learning workflow using Landsat satellite imagery to classify
        areas as Urban or Non-Urban and examine changes across
        Bangalore Urban District between 2015 and 2025.
        """
    )

    # --------------------------------------------------------
    # KPI CARDS
    # --------------------------------------------------------

    c1, c2, c3, c4 = st.columns(4)

    metrics = [
        (
            "2015 Urban Area",
            "1,400.95 km²",
            "Random Forest classification"
        ),
        (
            "2020 Urban Area",
            "1,354.64 km²",
            "Random Forest classification"
        ),
        (
            "2025 Urban Area",
            "1,457.12 km²",
            "Random Forest classification"
        ),
        (
            "Net 2015–25 Change",
            "+56.17 km²",
            "Classified urban area"
        )
    ]

    for column, (title, value, description) in zip(
        [c1, c2, c3, c4],
        metrics
    ):

        with column:

            st.markdown(
                f"""
                <div class="card">

                <div class="card-title">
                {title}
                </div>

                <div class="card-value">
                {value}
                </div>

                <div class="card-description">
                {description}
                </div>

                </div>
                """,
                unsafe_allow_html=True
            )

    # --------------------------------------------------------
    # URBAN AREA TREND
    # --------------------------------------------------------

    st.markdown(
        '<div class="section">📈 Classified Urban Area Trend</div>',
        unsafe_allow_html=True
    )

    df = create_area_dataframe()

    fig = px.line(
        df,
        x="Year",
        y="Classified Urban Area (km²)",
        markers=True
    )

    fig.update_traces(
        line_width=4,
        marker_size=10,
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Urban Area: %{y:.2f} km²"
            "<extra></extra>"
        )
    )

    fig.update_layout(
        template="plotly_dark",
        height=430,
        hovermode="x unified",
        margin=dict(
            l=20,
            r=20,
            t=30,
            b=20
        ),
        xaxis=dict(
            tickmode="linear",
            dtick=5
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # --------------------------------------------------------
    # CHANGE SUMMARY
    # --------------------------------------------------------

    st.markdown(
        '<div class="section">🔎 2015–2025 Change Summary</div>',
        unsafe_allow_html=True
    )

    a, b, c = st.columns(3)

    with a:

        st.metric(
            "Gross Expansion",
            f"{GROSS_EXPANSION:.2f} km²",
            help="Non-Urban → Urban"
        )

    with b:

        st.metric(
            "Gross Urban → Non-Urban",
            f"{GROSS_LOSS:.2f} km²",
            help="Urban → Non-Urban"
        )

    with c:

        st.metric(
            "Net Classified Change",
            f"{NET_CHANGE:+.2f} km²"
        )

    st.info(
        """
        The classification identified approximately 271.24 km²
        of gross Non-Urban → Urban change between 2015 and 2025.
        After accounting for approximately 215.07 km² of
        Urban → Non-Urban change, the net classified urban-area
        change is approximately 56.17 km².
        """
    )

    st.caption(
        "Note: These values represent classified urban area, "
        "not independently verified built-up area."
    )


# ============================================================
# EXPLORE MAPS
# ============================================================

elif page == "Explore Maps":

    st.markdown(
        '<div class="section">🗺️ Explore Classification Maps</div>',
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # YEAR SELECTOR
    # --------------------------------------------------------

    selected_year = st.select_slider(
        "Select classification year",
        options=YEARS,
        value=2025
    )

    # Load original raster
    image = load_raster(
        selected_year
    )

    # Load RGB display image
    display_image = load_classification(
        selected_year
    )

    # --------------------------------------------------------
    # MAP
    # --------------------------------------------------------

    st.image(
        display_image,
        caption=(
            f"Random Forest Classification — "
            f"Bangalore Urban District — {selected_year}"
        ),
        use_container_width=True
    )

    # --------------------------------------------------------
    # LEGEND
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="legend">

            <div class="legend-item">
                <span class="legend-box urban"></span>
                Urban
            </div>

            <div class="legend-item">
                <span class="legend-box nonurban"></span>
                Non-Urban
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # YEAR STATISTICS
    # --------------------------------------------------------

    c1, c2, c3 = st.columns(3)

    with c1:

        st.metric(
            "Classification Year",
            selected_year
        )

    with c2:

        st.metric(
            "Classified Urban Area",
            f"{URBAN_AREA[selected_year]:.2f} km²"
        )

    with c3:

        percentage = (
            URBAN_AREA[selected_year]
            /
            TOTAL_AREA
        ) * 100

        st.metric(
            "Share of Study Area",
            f"{percentage:.2f}%"
        )

    # --------------------------------------------------------
    # CLASSIFIED AREA DETAIL
    # --------------------------------------------------------

    st.markdown(
        '<div class="section">📐 Classification Details</div>',
        unsafe_allow_html=True
    )

    nonurban_area = (
        TOTAL_AREA
        -
        URBAN_AREA[selected_year]
    )

    details = pd.DataFrame({
        "Class": [
            "Urban",
            "Non-Urban"
        ],
        "Area (km²)": [
            URBAN_AREA[selected_year],
            nonurban_area
        ],
        "Share (%)": [
            (
                URBAN_AREA[selected_year]
                /
                TOTAL_AREA
            ) * 100,

            (
                nonurban_area
                /
                TOTAL_AREA
            ) * 100
        ]
    })

    st.dataframe(
        details.style.format({
            "Area (km²)": "{:.2f}",
            "Share (%)": "{:.2f}%"
        }),
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        "Map values: 0 = Non-Urban, 1 = Urban."
    )


# ============================================================
# COMPARE YEARS
# ============================================================

elif page == "Compare Years":

    st.markdown(
        '<div class="section">🔄 Compare Two Years</div>',
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # YEAR SELECTORS
    # --------------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        year1 = st.selectbox(
            "Earlier year",
            YEARS,
            index=0
        )

    with col2:

        later_options = [
            year for year in YEARS
            if year > year1
        ]

        if later_options:

            default_index = (
                len(later_options) - 1
            )

            year2 = st.selectbox(
                "Later year",
                later_options,
                index=default_index
            )

        else:

            st.warning(
                "Select an earlier year."
            )

            st.stop()

    # --------------------------------------------------------
    # LOAD RASTERS
    # --------------------------------------------------------

    image1 = load_raster(
        year1
    )

    image2 = load_raster(
        year2
    )

    display1 = load_classification(
        year1
    )

    display2 = load_classification(
        year2
    )

    # --------------------------------------------------------
    # CHANGE CALCULATION
    # --------------------------------------------------------

    expansion, loss = calculate_change(
        image1,
        image2
    )

    net = (
        expansion
        -
        loss
    )

    # --------------------------------------------------------
    # METRICS
    # --------------------------------------------------------

    c1, c2, c3 = st.columns(3)

    with c1:

        st.metric(
            "Gross Expansion",
            f"{expansion:.2f} km²"
        )

    with c2:

        st.metric(
            "Gross Loss",
            f"{loss:.2f} km²"
        )

    with c3:

        st.metric(
            "Net Classified Change",
            f"{net:+.2f} km²"
        )

    # --------------------------------------------------------
    # AREA COMPARISON
    # --------------------------------------------------------

    st.markdown(
        '<div class="section">📊 Urban Area Comparison</div>',
        unsafe_allow_html=True
    )

    comparison_df = pd.DataFrame({
        "Year": [
            year1,
            year2
        ],
        "Classified Urban Area (km²)": [
            URBAN_AREA[year1],
            URBAN_AREA[year2]
        ]
    })

    fig = px.bar(
        comparison_df,
        x="Year",
        y="Classified Urban Area (km²)",
        text="Classified Urban Area (km²)"
    )

    fig.update_traces(
        texttemplate="%{text:.2f} km²",
        textposition="outside",
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Urban Area: %{y:.2f} km²"
            "<extra></extra>"
        )
    )

    fig.update_layout(
        template="plotly_dark",
        height=400,
        margin=dict(
            l=20,
            r=20,
            t=30,
            b=20
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # --------------------------------------------------------
    # SIDE-BY-SIDE MAPS
    # --------------------------------------------------------

    st.markdown(
        '<div class="section">🗺️ Classification Comparison</div>',
        unsafe_allow_html=True
    )

    left, right = st.columns(2)

    with left:

        st.image(
            display1,
            caption=f"Classification — {year1}",
            use_container_width=True
        )

    with right:

        st.image(
            display2,
            caption=f"Classification — {year2}",
            use_container_width=True
        )

    # --------------------------------------------------------
    # LEGEND
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="legend">

            <div class="legend-item">
                <span class="legend-box urban"></span>
                Urban
            </div>

            <div class="legend-item">
                <span class="legend-box nonurban"></span>
                Non-Urban
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # EXPLANATION
    # --------------------------------------------------------

    st.markdown(
        f"""
        <div class="info">

        <b>{year1} → {year2}</b>

        <br><br>

        <b>Gross expansion:</b>
        {expansion:.2f} km²

        <br>

        <b>Gross urban-to-non-urban change:</b>
        {loss:.2f} km²

        <br>

        <b>Net classified urban change:</b>
        {net:+.2f} km²

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# MODEL PERFORMANCE
# ============================================================

elif page == "Model Performance":

    st.markdown(
        '<div class="section">🤖 Random Forest Performance</div>',
        unsafe_allow_html=True
    )

    performance_df = create_validation_dataframe()

    # --------------------------------------------------------
    # KPI SUMMARY
    # --------------------------------------------------------

    avg_accuracy = (
        performance_df[
            "Validation Accuracy (%)"
        ].mean()
    )

    avg_kappa = (
        performance_df["Kappa"].mean()
    )

    c1, c2, c3 = st.columns(3)

    with c1:

        st.metric(
            "2015 Accuracy",
            "86.75%"
        )

    with c2:

        st.metric(
            "2025 Accuracy",
            "84.90%"
        )

    with c3:

        st.metric(
            "Mean Accuracy",
            f"{avg_accuracy:.2f}%"
        )

    # --------------------------------------------------------
    # ACCURACY CHART
    # --------------------------------------------------------

    st.markdown(
        '<div class="section">📊 Validation Accuracy</div>',
        unsafe_allow_html=True
    )

    fig = px.bar(
        performance_df,
        x="Year",
        y="Validation Accuracy (%)",
        text="Validation Accuracy (%)"
    )

    fig.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside",
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Accuracy: %{y:.2f}%"
            "<extra></extra>"
        )
    )

    fig.update_layout(
        template="plotly_dark",
        yaxis_range=[0, 100],
        height=430,
        margin=dict(
            l=20,
            r=20,
            t=30,
            b=20
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # --------------------------------------------------------
    # KAPPA CHART
    # --------------------------------------------------------

    st.markdown(
        '<div class="section">📐 Kappa by Year</div>',
        unsafe_allow_html=True
    )

    kappa_df = performance_df[
        ["Year", "Kappa"]
    ]

    fig2 = px.line(
        kappa_df,
        x="Year",
        y="Kappa",
        markers=True
    )

    fig2.update_traces(
        line_width=4,
        marker_size=10,
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Kappa: %{y:.3f}"
            "<extra></extra>"
        )
    )

    fig2.update_layout(
        template="plotly_dark",
        height=350,
        yaxis_range=[0, 1],
        margin=dict(
            l=20,
            r=20,
            t=30,
            b=20
        )
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

    # --------------------------------------------------------
    # TABLE
    # --------------------------------------------------------

    st.markdown(
        '<div class="section">📋 Validation Results</div>',
        unsafe_allow_html=True
    )

    st.dataframe(
        performance_df.style.format({
            "Validation Accuracy (%)": "{:.2f}",
            "Kappa": "{:.3f}"
        }),
        use_container_width=True,
        hide_index=True
    )

    # --------------------------------------------------------
    # LIMITATION
    # --------------------------------------------------------

    st.warning(
        """
        Validation uses an 80/20 pixel-level holdout from the
        training polygons. Because nearby pixels can be spatially
        correlated, these values may be optimistic compared with
        independent spatial validation.
        """
    )


# ============================================================
# METHODOLOGY
# ============================================================

elif page == "Methodology":

    st.markdown(
        '<div class="section">🔬 Methodology</div>',
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # WORKFLOW
    # --------------------------------------------------------

    steps = [
        (
            "01",
            "Landsat imagery",
            "Landsat Collection 2 Level-2 Surface Reflectance imagery."
        ),
        (
            "02",
            "Preprocessing",
            "Cloud and cloud-shadow masking followed by median compositing."
        ),
        (
            "03",
            "Feature engineering",
            "Spectral bands B2–B7 combined with NDVI and NDBI."
        ),
        (
            "04",
            "Machine learning",
            "Random Forest classification trained separately for each year."
        ),
        (
            "05",
            "Validation",
            "80/20 pixel-level holdout validation."
        ),
        (
            "06",
            "Change detection",
            "Classification outputs compared to identify spatial transitions."
        )
    ]

    for number, title, description in steps:

        st.markdown(
            f"""
            <div class="info">

            <b>{number} — {title}</b>

            <br>

            {description}

            </div>
            """,
            unsafe_allow_html=True
        )

    # --------------------------------------------------------
    # PROJECT PARAMETERS
    # --------------------------------------------------------

    st.markdown(
        '<div class="section">📌 Project Parameters</div>',
        unsafe_allow_html=True
    )

    parameters = pd.DataFrame({
        "Parameter": [
            "Study area",
            "Study period",
            "Satellite",
            "Classification",
            "Model",
            "Features",
            "Spatial resolution",
            "Training samples per year"
        ],
        "Value": [
            "Bangalore Urban District",
            "2015–2025",
            "Landsat",
            "Urban vs Non-Urban",
            "Random Forest",
            "B2–B7 + NDVI + NDBI",
            "30 m",
            "39,104 pixels"
        ]
    })

    st.dataframe(
        parameters,
        use_container_width=True,
        hide_index=True
    )

    # --------------------------------------------------------
    # STUDY AREA STATISTICS
    # --------------------------------------------------------

    st.markdown(
        '<div class="section">🌍 Study Area</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns(3)

    with c1:

        st.metric(
            "Study Area",
            f"{TOTAL_AREA:.2f} km²"
        )

    with c2:

        st.metric(
            "Training Polygons",
            "9"
        )

    with c3:

        st.metric(
            "Classes",
            "2"
        )

    # --------------------------------------------------------
    # LIMITATIONS
    # --------------------------------------------------------

    st.markdown(
        '<div class="section">⚠️ Limitations</div>',
        unsafe_allow_html=True
    )

    st.warning(
        """
        The binary Urban/Non-Urban classification can confuse
        spectrally similar surfaces such as bare soil and built-up
        land. Training polygons are limited, and validation is
        pixel-level rather than independent spatial validation.

        The 2015 and 2020 classifications use Landsat 8, while
        the 2025 composite combines Landsat 8 and Landsat 9.

        Therefore, classified urban-area estimates should be
        interpreted cautiously and should not automatically be
        treated as independently verified built-up-area estimates.
        """
    )

    # --------------------------------------------------------
    # INTERPRETATION
    # --------------------------------------------------------

    st.markdown(
        '<div class="section">💡 What the Project Measures</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="info">

        <b>The project is a classification and change-detection
        workflow.</b>

        <br><br>

        Satellite imagery is converted into spectral and vegetation/
        built-up features. A Random Forest model then classifies
        pixels as Urban or Non-Urban for each study year.

        <br><br>

        The resulting maps are compared to identify areas that
        changed from Non-Urban to Urban and from Urban to Non-Urban.

        <br><br>

        This means the project examines <b>observed classified
        changes</b> between 2015, 2020 and 2025 rather than
        predicting future urban growth.

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "AI-Based Satellite Detection of Urban Expansion • "
    "Bangalore Urban District • Landsat + Random Forest"
)
# 🛰️ AI-Based Satellite Detection of Urban Expansion

A machine-learning and remote-sensing project that uses Landsat satellite imagery to classify Urban and Non-Urban areas and examine classified urban-area changes in Bangalore Urban District, Karnataka, between 2015 and 2025.

---

## 📌 Project Overview

Urban areas change continuously as cities expand, redevelop, and change land use.

This project combines:

- 🛰️ Landsat satellite imagery
- 🌱 NDVI and NDBI
- 🤖 Random Forest machine learning
- 🗺️ Land-cover classification
- 📊 Area calculation
- 🔄 Change detection
- 💻 Interactive Streamlit visualization

The objective is to create a reproducible workflow for examining how areas classified as Urban and Non-Urban changed across three observation years:

**2015 → 2020 → 2025**

> This project performs historical classification and change detection. It does not predict future urban growth.

---

## 🎯 Research Question

**How can machine learning and Landsat satellite imagery be used to classify urban and non-urban areas and quantify classified urban-area change in Bengaluru, India, from 2015 to 2025?**

---

## 📍 Study Area

**Bangalore Urban District, Karnataka, India**

The study area corresponds to the **Bangalore Urban administrative district**.

- Approximate study area: **2,187.31 km²**
- Classification resolution: **30 m**
- Observation years: **2015, 2020, 2025**

---

## 🛰️ Data

### Satellite

**Landsat Collection 2 Level-2 Surface Reflectance**

The workflow uses:

- Landsat 8 for 2015
- Landsat 8 for 2020
- Landsat 8 + Landsat 9 for 2025

Cloud and cloud-shadow masking is applied before creating annual median composites.

---

## 🧠 Features

The Random Forest classifier uses:

### Spectral bands

- B2 — Blue
- B3 — Green
- B4 — Red
- B5 — Near Infrared
- B6 — SWIR 1
- B7 — SWIR 2

### Spectral indices

**NDVI — Normalized Difference Vegetation Index**

Used to provide information related to vegetation.

**NDBI — Normalized Difference Built-up Index**

Used to provide information related to built-up surfaces.

### Final feature set

**B2–B7 + NDVI + NDBI**

---

## 🤖 Machine Learning

A separate **Random Forest classifier** is trained for each study year.

### Classification classes

| Class | Meaning |
|---|---|
| 0 | Non-Urban |
| 1 | Urban |

Training samples were generated from manually defined training polygons.

The final training dataset contained:

**39,104 pixels per year**

with balanced Urban and Non-Urban samples.

---

## 🔬 Methodology

```text
Landsat Satellite Imagery
          ↓
Cloud / Cloud-Shadow Masking
          ↓
Annual Median Composite
          ↓
Feature Engineering
(B2–B7 + NDVI + NDBI)
          ↓
Training Samples
          ↓
Random Forest Classification
          ↓
Urban / Non-Urban Maps
          ↓
Validation
          ↓
Urban Area Calculation
          ↓
2015–2020–2025 Comparison
          ↓
Urban Change Detection
          ↓
Interactive Streamlit Dashboard
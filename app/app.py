
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
    initial_sidebar_state="expanded",
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RESULTS_DIR = BASE_DIR / "results"


# ============================================================
# PROJECT DATA — UNCHANGED
# ============================================================

URBAN_AREA = {
    2015: 1400.9514267785637,
    2020: 1354.6360334354997,
    2025: 1457.1187413588416,
}

VALIDATION = {
    2015: {
        "accuracy": 86.75,
        "kappa": 0.735,
    },
    2020: {
        "accuracy": 84.91,
        "kappa": 0.698,
    },
    2025: {
        "accuracy": 84.90,
        "kappa": 0.698,
    },
}

TOTAL_AREA = 2187.3123452556

GROSS_EXPANSION = 271.240521769
GROSS_LOSS = 215.073207189
NET_CHANGE = 56.167314580


# ============================================================
# GLOBAL + CINEMATIC CSS
# ============================================================

st.html(
    """
    <style>

    @import url(
        'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Orbitron:wght@400;500;600;700;800&display=swap'
    );


    /* ========================================================
       GLOBAL
    ======================================================== */

    .stApp {
        background:
            radial-gradient(
                ellipse at 15% 10%,
                rgba(15, 80, 125, .10),
                transparent 28%
            ),
            radial-gradient(
                ellipse at 90% 5%,
                rgba(0, 180, 255, .055),
                transparent 25%
            ),
            #010409;

        color: #dceef5;
    }

    .block-container {
        max-width: 1500px;
        padding-top: 1.2rem;
        padding-bottom: 3rem;
    }


    /* ========================================================
       SIDEBAR
    ======================================================== */

    section[data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                #020810 0%,
                #010409 100%
            );

        border-right:
            1px solid rgba(82,230,255,.10);
    }

    .sidebar-brand {
        font-family: 'Orbitron', sans-serif;
        font-size: 16px;
        font-weight: 700;
        letter-spacing: 2px;
        color: #eafaff;
    }

    .sidebar-sub {
        margin-top: 4px;

        font-family: 'Orbitron', sans-serif;

        font-size: 7px;

        letter-spacing: 2px;

        color: #456474;
    }

    .sidebar-status {
        margin-top: 24px;

        padding: 14px;

        border:
            1px solid rgba(82,230,255,.13);

        background:
            rgba(82,230,255,.025);

        border-radius: 8px;
    }

    .sidebar-status-label {
        font-family: 'Orbitron', sans-serif;

        font-size: 7px;

        letter-spacing: 2px;

        color: #4c6979;
    }

    .sidebar-status-value {
        margin-top: 6px;

        font-family: 'Orbitron', sans-serif;

        font-size: 9px;

        letter-spacing: 1px;

        color: #55e8ff;
    }


    /* ========================================================
       HERO
    ======================================================== */

    .space-hero {

        position: relative;

        min-height: 560px;

        overflow: hidden;

        border-radius: 26px;

        border:
            1px solid rgba(82,230,255,.22);

        background:

            radial-gradient(
                ellipse at 74% 42%,
                rgba(0,130,200,.16),
                transparent 27%
            ),

            radial-gradient(
                ellipse at 20% 80%,
                rgba(0,100,180,.055),
                transparent 28%
            ),

            radial-gradient(
                ellipse at 88% 80%,
                rgba(0,220,255,.07),
                transparent 30%
            ),

            linear-gradient(
                120deg,
                #010308 0%,
                #020914 48%,
                #010308 100%
            );

        box-shadow:

            0 45px 130px rgba(0,0,0,.72),

            inset 0 0 100px
            rgba(0,190,255,.025);
    }


    /* ========================================================
       NEBULA
    ======================================================== */

    .nebula-one {
        position: absolute;

        width: 600px;
        height: 300px;

        left: -130px;
        top: 150px;

        border-radius: 50%;

        background:
            radial-gradient(
                ellipse,
                rgba(30,110,190,.11),
                rgba(10,40,90,.045),
                transparent 70%
            );

        filter: blur(35px);

        animation:
            nebulaFloat 16s ease-in-out infinite alternate;

        pointer-events: none;
    }

    .nebula-two {
        position: absolute;

        width: 520px;
        height: 260px;

        right: 100px;
        top: -90px;

        border-radius: 50%;

        background:
            radial-gradient(
                ellipse,
                rgba(0,190,255,.08),
                transparent 68%
            );

        filter: blur(40px);

        animation:
            nebulaFloatTwo 20s ease-in-out infinite alternate;

        pointer-events: none;
    }

    @keyframes nebulaFloat {

        from {
            transform:
                translate3d(0,0,0)
                scale(1);
        }

        to {
            transform:
                translate3d(35px,-20px,0)
                scale(1.08);
        }

    }

    @keyframes nebulaFloatTwo {

        from {
            transform:
                translate3d(0,0,0)
                scale(1);
        }

        to {
            transform:
                translate3d(-30px,25px,0)
                scale(1.12);
        }

    }


    /* ========================================================
       STARFIELD — FAR STARS
    ======================================================== */

    .stars-far {
        position: absolute;

        inset: 0;

        opacity: .38;

        background-image:
            radial-gradient(
                circle,
                rgba(255,255,255,.8) 0 1px,
                transparent 1.5px
            );

        background-size:
            190px 190px;

        background-position:
            10px 20px;

        animation:
            starDriftFar 45s linear infinite;

        pointer-events: none;
    }


    /* ========================================================
       STARFIELD — MID STARS
    ======================================================== */

    .stars-mid {
        position: absolute;

        inset: -80px;

        opacity: .48;

        background-image:
            radial-gradient(
                circle,
                rgba(180,235,255,.9) 0 1.1px,
                transparent 1.8px
            );

        background-size:
            115px 115px;

        background-position:
            45px 75px;

        animation:
            starDriftMid 30s linear infinite;

        pointer-events: none;
    }


    /* ========================================================
       STARFIELD — NEAR STARS
    ======================================================== */

    .stars-near {
        position: absolute;

        inset: -120px;

        opacity: .35;

        background-image:
            radial-gradient(
                circle,
                rgba(255,255,255,1) 0 1.6px,
                transparent 2.5px
            );

        background-size:
            275px 275px;

        background-position:
            120px 30px;

        animation:
            starDriftNear 22s linear infinite;

        pointer-events: none;
    }


    @keyframes starDriftFar {

        from {
            transform:
                translate(0,0);
        }

        to {
            transform:
                translate(-35px,20px);
        }

    }

    @keyframes starDriftMid {

        from {
            transform:
                translate(0,0);
        }

        to {
            transform:
                translate(-60px,35px);
        }

    }

    @keyframes starDriftNear {

        from {
            transform:
                translate(0,0);
        }

        to {
            transform:
                translate(-90px,45px);
        }

    }


    /* ========================================================
       SHOOTING STAR
    ======================================================== */

    .shooting-star {
        position: absolute;

        width: 120px;
        height: 1px;

        top: 100px;
        left: 45%;

        background:
            linear-gradient(
                90deg,
                transparent,
                rgba(255,255,255,.75),
                transparent
            );

        transform:
            rotate(-25deg);

        opacity: 0;

        animation:
            shootingStar 9s linear infinite;

        z-index: 3;
    }

    @keyframes shootingStar {

        0%, 70% {
            opacity: 0;
            transform:
                translate(0,0)
                rotate(-25deg);
        }

        73% {
            opacity: 1;
        }

        80% {
            opacity: 0;
            transform:
                translate(250px,100px)
                rotate(-25deg);
        }

        100% {
            opacity: 0;
        }

    }


    /* ========================================================
       EARTH
    ======================================================== */

    .earth {

        position: absolute;

        width: 500px;
        height: 500px;

        right: -35px;
        top: 38px;

        border-radius: 50%;

        z-index: 6;

        background:

            /* illuminated cloud structures */

            radial-gradient(
                ellipse at 37% 27%,
                rgba(255,255,255,.17) 0 2%,
                transparent 7%
            ),

            radial-gradient(
                ellipse at 59% 36%,
                rgba(255,255,255,.11) 0 3%,
                transparent 8%
            ),

            radial-gradient(
                ellipse at 42% 61%,
                rgba(255,255,255,.08) 0 3%,
                transparent 9%
            ),

            /* land */

            radial-gradient(
                ellipse at 31% 38%,
                rgba(62,145,104,.78) 0 7%,
                transparent 8%
            ),

            radial-gradient(
                ellipse at 46% 47%,
                rgba(57,137,96,.70) 0 10%,
                transparent 11%
            ),

            radial-gradient(
                ellipse at 58% 31%,
                rgba(55,135,96,.67) 0 8%,
                transparent 9%
            ),

            radial-gradient(
                ellipse at 64% 55%,
                rgba(45,119,87,.67) 0 7%,
                transparent 8%
            ),

            radial-gradient(
                ellipse at 36% 68%,
                rgba(42,108,80,.58) 0 8%,
                transparent 9%
            ),

            /* ocean */

            radial-gradient(
                circle at 34% 29%,
                #2f7899 0%,
                #175570 22%,
                #0a354e 46%,
                #05243b 67%,
                #020c16 100%
            );

        box-shadow:

            0 0 0 4px
            rgba(90,225,255,.035),

            0 0 18px 6px
            rgba(75,220,255,.17),

            0 0 55px 16px
            rgba(28,178,235,.15),

            0 0 120px 32px
            rgba(15,105,165,.13),

            inset -100px -35px 125px
            rgba(0,0,0,.94),

            inset -25px 0 50px
            rgba(0,0,0,.35);

        animation:
            earthPulse 8s ease-in-out infinite alternate;
    }


    @keyframes earthPulse {

        from {
            box-shadow:
                0 0 0 4px rgba(90,225,255,.035),
                0 0 18px 6px rgba(75,220,255,.14),
                0 0 55px 16px rgba(28,178,235,.13),
                0 0 120px 32px rgba(15,105,165,.11),
                inset -100px -35px 125px rgba(0,0,0,.94);
        }

        to {
            box-shadow:
                0 0 0 5px rgba(90,225,255,.05),
                0 0 24px 8px rgba(75,220,255,.20),
                0 0 70px 20px rgba(28,178,235,.18),
                0 0 145px 38px rgba(15,105,165,.15),
                inset -100px -35px 125px rgba(0,0,0,.94);
        }

    }


    /* ========================================================
       ATMOSPHERIC RIM
    ======================================================== */

    .atmosphere {

        position: absolute;

        width: 525px;
        height: 525px;

        right: -47px;
        top: 25px;

        border-radius: 50%;

        z-index: 8;

        border:
            2px solid
            rgba(100,237,255,.25);

        box-shadow:

            0 0 13px
            rgba(91,231,255,.22),

            0 0 35px
            rgba(63,206,255,.13),

            0 0 75px
            rgba(63,206,255,.07);

        animation:
            atmospherePulse 5s ease-in-out infinite alternate;

        pointer-events: none;
    }

    @keyframes atmospherePulse {

        from {
            opacity: .65;
        }

        to {
            opacity: 1;
        }

    }


    /* ========================================================
       EARTH LAT/LONG GRID
    ======================================================== */

    .earth-grid {

        position: absolute;

        width: 500px;
        height: 500px;

        right: -35px;
        top: 38px;

        border-radius: 50%;

        z-index: 9;

        background:

            repeating-linear-gradient(
                90deg,
                transparent 0 55px,
                rgba(110,230,255,.065) 56px,
                transparent 57px
            ),

            repeating-linear-gradient(
                0deg,
                transparent 0 55px,
                rgba(110,230,255,.055) 56px,
                transparent 57px
            );

        opacity: .32;

        animation:
            gridRotate 40s linear infinite;

        pointer-events: none;
    }

    @keyframes gridRotate {

        from {
            transform:
                rotate(0deg)
                scale(1);
        }

        to {
            transform:
                rotate(3deg)
                scale(1.015);
        }

    }


    /* ========================================================
       ORBIT RINGS
    ======================================================== */

    .orbit {

        position: absolute;

        border-radius: 50%;

        z-index: 11;

        pointer-events: none;
    }

    .orbit-one {

        width: 700px;
        height: 245px;

        right: -150px;
        top: 155px;

        border:
            1px solid
            rgba(82,230,255,.31);

        transform:
            rotate(-22deg);

        animation:
            orbitGlow 5s ease-in-out infinite alternate;
    }

    .orbit-two {

        width: 640px;
        height: 205px;

        right: -120px;
        top: 165px;

        border:
            1px solid
            rgba(255,255,255,.11);

        transform:
            rotate(15deg);
    }

    .orbit-three {

        width: 570px;
        height: 315px;

        right: -75px;
        top: 90px;

        border:
            1px dashed
            rgba(82,230,255,.15);

        transform:
            rotate(38deg);
    }

    @keyframes orbitGlow {

        from {
            opacity: .55;
        }

        to {
            opacity: 1;
        }

    }


    /* ========================================================
       ORBITING ENERGY POINTS
    ======================================================== */

    .orbit-point {

        position: absolute;

        width: 8px;
        height: 8px;

        border-radius: 50%;

        background:
            #55e8ff;

        box-shadow:

            0 0 8px
            #55e8ff,

            0 0 23px
            rgba(82,230,255,.8);

        z-index: 17;

        animation:
            pointPulse 2s ease-in-out infinite alternate;
    }

    .point-one {
        right: 90px;
        top: 120px;
    }

    .point-two {
        right: 365px;
        top: 290px;

        width: 5px;
        height: 5px;

        animation-delay: .8s;
    }

    .point-three {
        right: 205px;
        top: 460px;

        width: 5px;
        height: 5px;

        animation-delay: 1.5s;
    }

    @keyframes pointPulse {

        from {
            transform: scale(.65);
            opacity: .45;
        }

        to {
            transform: scale(1.4);
            opacity: 1;
        }

    }


    /* ========================================================
       SATELLITE
    ======================================================== */

    .satellite {

        position: absolute;

        right: 280px;
        top: 60px;

        width: 95px;
        height: 55px;

        z-index: 25;

        transform:
            rotate(-18deg);

        animation:
            satelliteFloat 7s ease-in-out infinite;
    }

    @keyframes satelliteFloat {

        0%,100% {
            transform:
                rotate(-18deg)
                translateY(0);
        }

        50% {
            transform:
                rotate(-14deg)
                translateY(-8px);
        }

    }

    .sat-body {

        position: absolute;

        left: 35px;
        top: 17px;

        width: 27px;
        height: 20px;

        border-radius: 3px;

        background:
            linear-gradient(
                145deg,
                #d8e8ed,
                #586d77
            );

        border:
            1px solid
            rgba(160,242,255,.75);

        box-shadow:
            0 0 12px
            rgba(82,230,255,.45);
    }

    .sat-panel-left,
    .sat-panel-right {

        position: absolute;

        top: 15px;

        width: 29px;
        height: 24px;

        background:
            repeating-linear-gradient(
                90deg,
                #031a2b 0 4px,
                #0b5270 5px 7px
            );

        border:
            1px solid
            rgba(82,230,255,.62);

        box-shadow:
            inset 0 0 6px
            rgba(82,230,255,.12);
    }

    .sat-panel-left {
        left: 2px;
    }

    .sat-panel-right {
        right: 2px;
    }

    .sat-antenna {

        position: absolute;

        right: 29px;
        top: 2px;

        width: 14px;
        height: 14px;

        border:
            1px solid
            #8deeff;

        border-radius: 50%;

        box-shadow:
            0 0 10px
            rgba(82,230,255,.6);
    }

    .sat-antenna::after {

        content: "";

        position: absolute;

        width: 20px;
        height: 1px;

        left: -4px;
        top: 6px;

        background:
            #8deeff;

        opacity: .6;
    }

    .sat-beam {

        position: absolute;

        left: 49px;
        top: 34px;

        width: 1px;
        height: 150px;

        background:
            linear-gradient(
                180deg,
                rgba(82,230,255,.5),
                rgba(82,230,255,.12),
                transparent
            );

        transform:
            rotate(17deg);

        transform-origin:
            top;

        filter:
            drop-shadow(
                0 0 5px
                rgba(82,230,255,.5)
            );
    }


    /* ========================================================
       SCANNING ARC
    ======================================================== */

    .scan-arc {

        position: absolute;

        width: 450px;
        height: 450px;

        right: -15px;
        top: 62px;

        border-radius: 50%;

        border-right:
            2px solid
            rgba(82,230,255,.18);

        border-top:
            2px solid
            rgba(82,230,255,.08);

        z-index: 14;

        transform:
            rotate(-28deg);

        animation:
            scanRotate 8s ease-in-out infinite alternate;
    }

    @keyframes scanRotate {

        from {
            transform:
                rotate(-32deg);
        }

        to {
            transform:
                rotate(-18deg);
        }

    }


    .scan-line {

        position: absolute;

        right: 15px;
        top: 275px;

        width: 440px;
        height: 2px;

        background:
            linear-gradient(
                90deg,
                transparent,
                rgba(82,230,255,.05),
                rgba(82,230,255,.5),
                rgba(82,230,255,.05),
                transparent
            );

        z-index: 15;

        transform:
            rotate(-27deg);

        animation:
            scanPulse 3.5s ease-in-out infinite;
    }

    @keyframes scanPulse {

        0%,100% {
            opacity: .25;
        }

        50% {
            opacity: 1;
        }

    }


    /* ========================================================
       TARGET RETICLE
    ======================================================== */

    .reticle {

        position: absolute;

        right: 150px;
        top: 270px;

        width: 105px;
        height: 105px;

        z-index: 20;

        border:
            1px solid
            rgba(82,230,255,.18);

        border-radius: 50%;

        box-shadow:
            0 0 28px
            rgba(82,230,255,.04);

        animation:
            reticlePulse 3s ease-in-out infinite;
    }

    .reticle::before {

        content: "";

        position: absolute;

        left: 50%;
        top: -18px;

        width: 1px;
        height: 140px;

        background:
            rgba(82,230,255,.13);
    }

    .reticle::after {

        content: "";

        position: absolute;

        left: -18px;
        top: 50%;

        width: 140px;
        height: 1px;

        background:
            rgba(82,230,255,.13);
    }

    .reticle-dot {

        position: absolute;

        left: 50%;
        top: 50%;

        width: 6px;
        height: 6px;

        transform:
            translate(-50%,-50%);

        border-radius: 50%;

        background:
            #55e8ff;

        box-shadow:
            0 0 12px
            #55e8ff,

            0 0 28px
            rgba(82,230,255,.7);
    }

    @keyframes reticlePulse {

        0%,100% {
            opacity: .45;
            transform: scale(.96);
        }

        50% {
            opacity: 1;
            transform: scale(1);
        }

    }


    /* ========================================================
       MAIN HERO CONTENT
    ======================================================== */

    .hero-content {

        position: relative;

        z-index: 40;

        width: 59%;

        padding:
            70px 0 0 60px;
    }

    .mission-tag {

        display: inline-block;

        padding:
            9px 15px;

        border:
            1px solid
            rgba(82,230,255,.32);

        background:
            rgba(82,230,255,.035);

        color:
            #55e8ff;

        border-radius:
            4px;

        font-family:
            'Orbitron',
            sans-serif;

        font-size:
            8px;

        letter-spacing:
            2.5px;

        box-shadow:
            0 0 25px
            rgba(82,230,255,.035);
    }


    .hero-title {

        margin:
            24px 0 16px;

        font-family:
            'Orbitron',
            sans-serif;

        font-size:
            clamp(40px,5vw,70px);

        line-height:
            .92;

        letter-spacing:
            -3px;

        color:
            #f2fbff;

        text-shadow:
            0 0 28px
            rgba(82,230,255,.08);
    }

    .hero-title .cyan {

        color:
            #55e8ff;

        text-shadow:
            0 0 28px
            rgba(82,230,255,.28);
    }


    .hero-subtitle {

        max-width:
            580px;

        color:
            #8aa8b8;

        font-size:
            13px;

        line-height:
            1.8;
    }


    /* ========================================================
       HUD BOXES
    ======================================================== */

    .hud-row {

        display:
            flex;

        gap:
            8px;

        flex-wrap:
            wrap;

        margin-top:
            28px;
    }

    .hud-box {

        min-width:
            125px;

        padding:
            10px 13px;

        border:
            1px solid
            rgba(82,230,255,.12);

        background:
            rgba(2,12,20,.72);

        border-radius:
            5px;

        backdrop-filter:
            blur(5px);
    }

    .hud-label {

        color:
            #456778;

        font-family:
            'Orbitron',
            sans-serif;

        font-size:
            6px;

        letter-spacing:
            1.7px;
    }

    .hud-value {

        margin-top:
            5px;

        color:
            #cdebf4;

        font-family:
            'Orbitron',
            sans-serif;

        font-size:
            8px;

        letter-spacing:
            .7px;
    }


    /* ========================================================
       TELEMETRY
    ======================================================== */

    .telemetry {

        position:
            absolute;

        left:
            60px;

        bottom:
            38px;

        z-index:
            40;

        width:
            420px;

        padding:
            13px 16px;

        border-left:
            2px solid
            rgba(82,230,255,.34);

        background:
            linear-gradient(
                90deg,
                rgba(3,18,28,.74),
                transparent
            );

        color:
            rgba(130,181,199,.43);

        font-family:
            'Orbitron',
            sans-serif;

        font-size:
            6px;

        line-height:
            2.15;

        letter-spacing:
            1.4px;

        animation:
            telemetryFlicker 6s ease-in-out infinite;
    }

    @keyframes telemetryFlicker {

        0%,94%,100% {
            opacity: .72;
        }

        96% {
            opacity: .35;
        }

        98% {
            opacity: .9;
        }

    }


    /* ========================================================
       CORNERS
    ======================================================== */

    .hero-corner-left {

        position:
            absolute;

        left:
            24px;

        top:
            21px;

        z-index:
            50;

        color:
            rgba(82,230,255,.25);

        font-family:
            'Orbitron',
            sans-serif;

        font-size:
            7px;

        letter-spacing:
            2px;
    }

    .hero-corner-right {

        position:
            absolute;

        right:
            24px;

        bottom:
            21px;

        z-index:
            50;

        color:
            rgba(82,230,255,.27);

        font-family:
            'Orbitron',
            sans-serif;

        font-size:
            7px;

        letter-spacing:
            1.5px;
    }


    /* ========================================================
       SECTION DESIGN
    ======================================================== */

    .section-kicker {

        margin-top:
            30px;

        margin-bottom:
            6px;

        color:
            #55e8ff;

        font-family:
            'Orbitron',
            sans-serif;

        font-size:
            8px;

        letter-spacing:
            2.5px;
    }

    .section-title {

        margin-bottom:
            20px;

        color:
            #eafaff;

        font-family:
            'Orbitron',
            sans-serif;

        font-size:
            22px;

        letter-spacing:
            -.5px;
    }


    /* ========================================================
       CARDS
    ======================================================== */

    .metric-card {

        padding:
            21px;

        min-height:
            110px;

        border:
            1px solid
            rgba(82,230,255,.09);

        border-radius:
            11px;

        background:
            linear-gradient(
                145deg,
                rgba(10,27,39,.75),
                rgba(3,9,15,.78)
            );
    }

    .metric-label {

        color:
            #527487;

        font-family:
            'Orbitron',
            sans-serif;

        font-size:
            7px;

        letter-spacing:
            1.8px;
    }

    .metric-value {

        margin-top:
            8px;

        color:
            #eafaff;

        font-family:
            'Orbitron',
            sans-serif;

        font-size:
            24px;

        font-weight:
            600;
    }

    .metric-note {

        margin-top:
            5px;

        color:
            #4b6878;

        font-size:
            10px;
    }


    .info-panel {

        padding:
            24px;

        border:
            1px solid
            rgba(82,230,255,.09);

        border-radius:
            11px;

        background:
            rgba(5,15,23,.70);
    }

    .info-panel h3 {

        margin-top:
            0;

        color:
            #eafaff;

        font-family:
            'Orbitron',
            sans-serif;

        font-size:
            12px;

        letter-spacing:
            .8px;
    }

    .info-panel p {

        color:
            #7895a5;

        font-size:
            13px;

        line-height:
            1.7;
    }


    /* ========================================================
       FOOTER
    ======================================================== */

    .footer {

        margin-top:
            50px;

        padding-top:
            20px;

        border-top:
            1px solid
            rgba(82,230,255,.07);

        color:
            #385361;

        font-family:
            'Orbitron',
            sans-serif;

        font-size:
            7px;

        letter-spacing:
            1.6px;

        text-align:
            center;
    }

    </style>
    """
)


# ============================================================
# HERO HTML
# ============================================================

st.html(
    """
    <div class="space-hero">


        <!-- STAR SYSTEM -->

        <div class="stars-far"></div>

        <div class="stars-mid"></div>

        <div class="stars-near"></div>

        <div class="shooting-star"></div>


        <!-- NEBULA -->

        <div class="nebula-one"></div>

        <div class="nebula-two"></div>


        <!-- EARTH -->

        <div class="earth"></div>

        <div class="atmosphere"></div>

        <div class="earth-grid"></div>


        <!-- ORBITS -->

        <div class="orbit orbit-one"></div>

        <div class="orbit orbit-two"></div>

        <div class="orbit orbit-three"></div>


        <!-- ORBITAL POINTS -->

        <div class="orbit-point point-one"></div>

        <div class="orbit-point point-two"></div>

        <div class="orbit-point point-three"></div>


        <!-- SATELLITE -->

        <div class="satellite">

            <div class="sat-panel-left"></div>

            <div class="sat-body"></div>

            <div class="sat-panel-right"></div>

            <div class="sat-antenna"></div>

            <div class="sat-beam"></div>

        </div>


        <!-- SCANNING SYSTEM -->

        <div class="scan-arc"></div>

        <div class="scan-line"></div>


        <!-- TARGETING -->

        <div class="reticle">

            <div class="reticle-dot"></div>

        </div>


        <!-- HUD CORNER -->

        <div class="hero-corner-left">
            UEM-01 // EARTH OBSERVATION SYSTEM
        </div>


        <!-- MAIN TITLE -->

        <div class="hero-content">

            <div class="mission-tag">
                🛰️ EARTH OBSERVATION MISSION // UEM-01
            </div>


            <div class="hero-title">

                URBAN<br>

                <span class="cyan">
                    EXPANSION
                </span><br>

                MONITOR

            </div>


            <div class="hero-subtitle">

                AI-based satellite analysis of urban expansion
                across Bengaluru using Landsat Earth observation
                data and Random Forest classification.

            </div>


            <!-- HUD INFORMATION -->

            <div class="hud-row">


                <div class="hud-box">

                    <div class="hud-label">
                        TARGET REGION
                    </div>

                    <div class="hud-value">
                        BENGALURU / INDIA
                    </div>

                </div>


                <div class="hud-box">

                    <div class="hud-label">
                        SENSOR
                    </div>

                    <div class="hud-value">
                        LANDSAT 8 / 9
                    </div>

                </div>


                <div class="hud-box">

                    <div class="hud-label">
                        TEMPORAL WINDOW
                    </div>

                    <div class="hud-value">
                        2015 — 2025
                    </div>

                </div>


                <div class="hud-box">

                    <div class="hud-label">
                        CLASSIFIER
                    </div>

                    <div class="hud-value">
                        RANDOM FOREST
                    </div>

                </div>

            </div>

        </div>


        <!-- TELEMETRY -->

        <div class="telemetry">

            UEM-01 / ORBITAL TELEMETRY<br>

            LAT 12.9716° N
            &nbsp;&nbsp;
            LON 77.5946° E<br>

            ALT 705 KM
            &nbsp;&nbsp;
            ORBIT PASS 04<br>

            OBSERVATION MODE // MULTISPECTRAL<br>

            RESOLUTION // 30 METERS<br>

            DATA STREAM // NOMINAL<br>

            TARGET LOCK // BENGALURU URBAN

        </div>


        <!-- BOTTOM HUD -->

        <div class="hero-corner-right">

            ◉ SENSOR NOMINAL
            &nbsp;&nbsp;//&nbsp;&nbsp;

            ◉ DATA STREAM ACTIVE
            &nbsp;&nbsp;//&nbsp;&nbsp;

            UEM-01

        </div>


    </div>
    """
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.html(
        """
        <div class="sidebar-brand">
            UEM-01
        </div>

        <div class="sidebar-sub">
            MISSION CONTROL
        </div>

        <div class="sidebar-status">

            <div class="sidebar-status-label">
                SYSTEM STATUS
            </div>

            <div class="sidebar-status-value">
                ● OPERATIONAL
            </div>

        </div>
        """
    )


    page = st.radio(
        "MISSION MODULES",
        [
            "Mission Overview",
            "Explore Maps",
            "Compare Years",
            "Model Performance",
            "Methodology",
        ],
    )


    st.html(
        """
        <div style="
            margin-top:30px;
            color:#3c5968;
            font-family:Orbitron,sans-serif;
            font-size:7px;
            line-height:2.2;
            letter-spacing:1.3px;
        ">

            DATA SOURCE<br>
            USGS / LANDSAT<br><br>

            GEO PLATFORM<br>
            GOOGLE EARTH ENGINE<br><br>

            ML ENGINE<br>
            RANDOM FOREST<br><br>

            STUDY REGION<br>
            BENGALURU URBAN

        </div>
        """
    )


# ============================================================
# DATA FUNCTIONS — UNCHANGED
# ============================================================

def load_raster(year):

    path = DATA_DIR / f"urban_classification_{year}.tif"

    if not path.exists():
        return None, None, None

    with rasterio.open(path) as src:

        image = src.read(1)
        transform = src.transform
        crs = src.crs

    return image, transform, crs


def load_classification(year):

    image, transform, crs = load_raster(year)

    if image is None:
        return None

    return image


def calculate_area(image):

    if image is None:
        return 0

    urban_pixels = np.sum(image == 1)

    pixel_area_km2 = (30 * 30) / 1_000_000

    return urban_pixels * pixel_area_km2


def calculate_change(image1, image2):

    if image1 is None or image2 is None:
        return 0

    return calculate_area(image2) - calculate_area(image1)


def create_area_dataframe():

    return pd.DataFrame(
        {
            "Year": list(URBAN_AREA.keys()),
            "Urban Area (km²)": list(URBAN_AREA.values()),
        }
    )


def create_validation_dataframe():

    rows = []

    for year, values in VALIDATION.items():

        rows.append(
            {
                "Year": year,
                "Accuracy (%)": values["accuracy"],
                "Kappa": values["kappa"],
            }
        )

    return pd.DataFrame(rows)


# ============================================================
# MISSION OVERVIEW
# ============================================================

if page == "Mission Overview":

    st.html(
        """
        <div class="section-kicker">
            MISSION BRIEF
        </div>

        <div class="section-title">
            Bengaluru Urban Expansion Monitoring
        </div>
        """
    )


    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.html(
            """
            <div class="metric-card">

                <div class="metric-label">
                    STUDY AREA
                </div>

                <div class="metric-value">
                    2,187 km²
                </div>

                <div class="metric-note">
                    Bengaluru Urban region
                </div>

            </div>
            """
        )


    with col2:

        st.html(
            """
            <div class="metric-card">

                <div class="metric-label">
                    TIME WINDOW
                </div>

                <div class="metric-value">
                    10 YEARS
                </div>

                <div class="metric-note">
                    2015 → 2025
                </div>

            </div>
            """
        )


    with col3:

        st.html(
            """
            <div class="metric-card">

                <div class="metric-label">
                    NET CHANGE
                </div>

                <div class="metric-value">
                    +56.17 km²
                </div>

                <div class="metric-note">
                    2015 → 2025
                </div>

            </div>
            """
        )


    with col4:

        st.html(
            """
            <div class="metric-card">

                <div class="metric-label">
                    CLASSIFIER
                </div>

                <div class="metric-value">
                    RF-100
                </div>

                <div class="metric-note">
                    Random Forest trees
                </div>

            </div>
            """
        )


    st.html(
        """
        <div class="section-kicker">
            MISSION OBJECTIVE
        </div>
        """
    )


    col1, col2 = st.columns([1.3, 1])


    with col1:

        st.html(
            """
            <div class="info-panel">

                <h3>
                    What is this mission measuring?
                </h3>

                <p>
                    This project uses satellite imagery to identify
                    urban and non-urban areas across Bengaluru and
                    compare how the classified urban footprint changes
                    between 2015, 2020 and 2025.
                </p>

                <p>
                    Landsat spectral bands are combined with NDVI and
                    NDBI features and classified using a Random Forest
                    machine-learning model.
                </p>

            </div>
            """
        )


    with col2:

        st.html(
            """
            <div class="info-panel">

                <h3>
                    Observation Timeline
                </h3>

                <p>
                    <b>2015</b> — Initial baseline
                </p>

                <p>
                    <b>2020</b> — Mid-period observation
                </p>

                <p>
                    <b>2025</b> — Latest observation
                </p>

            </div>
            """
        )


    st.html(
        """
        <div class="section-kicker">
            URBAN AREA THROUGH TIME
        </div>

        <div class="section-title">
            Classified Urban Footprint
        </div>
        """
    )


    df_area = create_area_dataframe()


    fig = px.line(
        df_area,
        x="Year",
        y="Urban Area (km²)",
        markers=True,
    )


    fig.update_layout(
        template="plotly_dark",
        height=420,
        margin=dict(
            l=10,
            r=10,
            t=30,
            b=10,
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            color="#8da8b7"
        ),
    )


    fig.update_traces(
        line_width=3,
        marker_size=9,
    )


    st.plotly_chart(
        fig,
        width="stretch"
    )


# ============================================================
# EXPLORE MAPS
# ============================================================

elif page == "Explore Maps":

    st.html(
        """
        <div class="section-kicker">
            EARTH OBSERVATION
        </div>

        <div class="section-title">
            Classified Satellite Maps
        </div>
        """
    )


    year = st.selectbox(
        "SELECT OBSERVATION YEAR",
        [2015, 2020, 2025],
    )


    image, transform, crs = load_raster(year)


    if image is None:

        st.error(
            f"Classification raster for {year} was not found."
        )

    else:

        rgb = np.zeros(
            (
                image.shape[0],
                image.shape[1],
                3
            ),
            dtype=np.uint8
        )


        valid = np.isin(
            image,
            [0, 1]
        )


        rgb[
            (image == 0) & valid
        ] = [
            7,
            20,
            31
        ]


        rgb[
            (image == 1) & valid
        ] = [
            45,
            220,
            255
        ]


        rgb[
            ~valid
        ] = [
            0,
            0,
            0
        ]


        st.image(
            rgb,
            caption=f"Urban Classification Map — {year}",
            width="stretch",
        )


        urban_pixels = int(
            np.sum(image == 1)
        )

        total_pixels = int(
            image.size
        )


        urban_percent = (
            urban_pixels /
            total_pixels *
            100
            if total_pixels
            else 0
        )


        col1, col2, col3, col4 = st.columns(4)


        with col1:

            st.metric(
                "Urban Pixels",
                f"{urban_pixels:,}",
            )


        with col2:

            st.metric(
                "Total Pixels",
                f"{total_pixels:,}",
            )


        with col3:

            st.metric(
                "Urban Coverage",
                f"{urban_percent:.2f}%",
            )


        with col4:

            st.metric(
                "Raster Size",
                f"{image.shape[1]} × {image.shape[0]}",
            )


        st.caption(
            f"Coordinate Reference System: {crs}"
        )


# ============================================================
# COMPARE YEARS
# ============================================================

elif page == "Compare Years":

    st.html(
        """
        <div class="section-kicker">
            TEMPORAL ANALYSIS
        </div>

        <div class="section-title">
            Urban Expansion Across Observation Years
        </div>
        """
    )


    df = create_area_dataframe()


    fig = px.bar(
        df,
        x="Year",
        y="Urban Area (km²)",
        text="Urban Area (km²)",
    )


    fig.update_layout(
        template="plotly_dark",
        height=430,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            color="#8da8b7"
        ),
        margin=dict(
            l=10,
            r=10,
            t=30,
            b=10,
        ),
    )


    fig.update_traces(
        texttemplate="%{text:.1f}",
        textposition="outside",
    )


    st.plotly_chart(
        fig,
        width="stretch"
    )


    col1, col2, col3 = st.columns(3)


    with col1:

        st.html(
            f"""
            <div class="metric-card">

                <div class="metric-label">
                    GROSS EXPANSION
                </div>

                <div class="metric-value">
                    {GROSS_EXPANSION:.2f}
                </div>

                <div class="metric-note">
                    km² classified as newly urban
                </div>

            </div>
            """
        )


    with col2:

        st.html(
            f"""
            <div class="metric-card">

                <div class="metric-label">
                    GROSS LOSS
                </div>

                <div class="metric-value">
                    {GROSS_LOSS:.2f}
                </div>

                <div class="metric-note">
                    km² classified as urban → non-urban
                </div>

            </div>
            """
        )


    with col3:

        st.html(
            f"""
            <div class="metric-card">

                <div class="metric-label">
                    NET CHANGE
                </div>

                <div class="metric-value">
                    +{NET_CHANGE:.2f}
                </div>

                <div class="metric-note">
                    km² net change, 2015 → 2025
                </div>

            </div>
            """
        )


    st.html(
        """
        <div class="section-kicker">
            CHANGE INTERPRETATION
        </div>
        """
    )


    st.info(
        "The 2015–2025 comparison shows a net increase in "
        "classified urban area. Gross expansion and gross loss "
        "are reported separately because land-cover transitions "
        "can occur in both directions."
    )


# ============================================================
# MODEL PERFORMANCE
# ============================================================

elif page == "Model Performance":

    st.html(
        """
        <div class="section-kicker">
            MACHINE LEARNING TELEMETRY
        </div>

        <div class="section-title">
            Random Forest Validation
        </div>
        """
    )


    validation_df = create_validation_dataframe()


    col1, col2, col3 = st.columns(3)


    for col, year in zip(
        [col1, col2, col3],
        [2015, 2020, 2025]
    ):

        with col:

            st.html(
                f"""
                <div class="metric-card">

                    <div class="metric-label">
                        {year} MODEL
                    </div>

                    <div class="metric-value">
                        {VALIDATION[year]["accuracy"]:.2f}%
                    </div>

                    <div class="metric-note">
                        Overall validation accuracy
                    </div>

                    <div style="
                        margin-top:15px;
                        color:#58788c;
                        font-family:Orbitron,sans-serif;
                        font-size:8px;
                        letter-spacing:1px;
                    ">

                        KAPPA

                        <span style="
                            color:#dcecf3;
                        ">
                            {VALIDATION[year]["kappa"]:.3f}
                        </span>

                    </div>

                </div>
                """
            )


    st.html(
        """
        <div class="section-kicker">
            PERFORMANCE TREND
        </div>

        <div class="section-title">
            Accuracy by Observation Year
        </div>
        """
    )


    fig = px.line(
        validation_df,
        x="Year",
        y="Accuracy (%)",
        markers=True,
    )


    fig.update_layout(
        template="plotly_dark",
        height=400,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            color="#8da8b7"
        ),
        margin=dict(
            l=10,
            r=10,
            t=30,
            b=10,
        ),
        yaxis=dict(
            range=[75,95]
        ),
    )


    fig.update_traces(
        line_width=3,
        marker_size=9,
    )


    st.plotly_chart(
        fig,
        width="stretch"
    )


    st.html(
        """
        <div class="info-panel">

            <h3>
                Validation Note
            </h3>

            <p>
                The reported validation values come from an
                80/20 random hold-out split of the sampled training
                pixels. This is internal validation rather than
                independent spatial validation.
            </p>

        </div>
        """
    )


# ============================================================
# METHODOLOGY
# ============================================================

elif page == "Methodology":

    st.html(
        """
        <div class="section-kicker">
            MISSION ARCHITECTURE
        </div>

        <div class="section-title">
            How the System Works
        </div>
        """
    )


    steps = [

        (
            "01",
            "SATELLITE DATA",
            "Landsat 8 and Landsat 9 surface-reflectance imagery "
            "for 2015, 2020 and 2025."
        ),

        (
            "02",
            "PREPROCESSING",
            "Cloud masking using the Landsat QA_PIXEL quality band "
            "and reflectance scaling."
        ),

        (
            "03",
            "FEATURE ENGINEERING",
            "Spectral bands are combined with NDVI and NDBI to "
            "capture vegetation and built-up characteristics."
        ),

        (
            "04",
            "TRAINING DATA",
            "Manually defined urban and non-urban polygons are "
            "sampled at 30-m resolution."
        ),

        (
            "05",
            "RANDOM FOREST",
            "Separate 100-tree Random Forest classifiers are trained "
            "for each observation year."
        ),

        (
            "06",
            "VALIDATION",
            "An 80/20 random hold-out is used to calculate accuracy "
            "and Cohen's kappa."
        ),

        (
            "07",
            "URBAN AREA",
            "Pixels classified as urban are converted into area "
            "using 30-m Landsat pixel dimensions."
        ),

        (
            "08",
            "CHANGE DETECTION",
            "2015 and 2025 classifications are compared to identify "
            "gross expansion, gross loss and net change."
        ),

    ]


    for number, title, description in steps:

        col1, col2 = st.columns(
            [1,8]
        )


        with col1:

            st.html(
                f"""
                <div style="
                    font-family:Orbitron,sans-serif;
                    color:#55e8ff;
                    font-size:11px;
                    padding-top:6px;
                    letter-spacing:1px;
                ">
                    {number}
                </div>
                """
            )


        with col2:

            st.html(
                f"""
                <div class="info-panel"
                     style="margin-bottom:12px;">

                    <h3>
                        {title}
                    </h3>

                    <p>
                        {description}
                    </p>

                </div>
                """
            )


    st.html(
        """
        <div class="section-kicker">
            TECHNOLOGY STACK
        </div>

        <div class="section-title">
            Mission Components
        </div>
        """
    )


    col1, col2, col3, col4 = st.columns(4)


    technologies = [

        (
            "EARTH OBSERVATION",
            "Landsat"
        ),

        (
            "GEO PLATFORM",
            "Google Earth Engine"
        ),

        (
            "ML MODEL",
            "Random Forest"
        ),

        (
            "ANALYTICS",
            "Python"
        ),

    ]


    for col, (label, value) in zip(
        [col1,col2,col3,col4],
        technologies
    ):

        with col:

            st.html(
                f"""
                <div class="metric-card">

                    <div class="metric-label">
                        {label}
                    </div>

                    <div style="
                        margin-top:10px;
                        color:#eafaff;
                        font-family:Orbitron,sans-serif;
                        font-size:13px;
                    ">
                        {value}
                    </div>

                </div>
                """
            )


# ============================================================
# FOOTER
# ============================================================

st.html(
    """
    <div class="footer">

        UEM-01 //
        URBAN EXPANSION MONITOR //
        EARTH OBSERVATION × MACHINE LEARNING //
        BENGALURU, INDIA //
        2015—2025

    </div>
    """
)


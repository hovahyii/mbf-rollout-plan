# Mobifone Regional Rollout Dashboard - User Guide (v1.0.0)

Welcome to the **Mobifone Rollout Dashboard**. This tool is designed to provide real-time spatial monitoring of site delivery, planning, and cluster management for North, Middle, and South regions.

---

## 1. Key Features

### 🗺️ Interactive Map
- **Marker Clustering**: 10,000+ sites are clustered for optimal performance. Zoom in to see individual sites.
- **Site Information**: Hover or click any site to view a detailed information card including:
  - **PO & Region**
  - **Existing eNodeB ID** (Formatted as clean integers)
  - **Location**: Province, District, and precise Lat/Long.
  - **Scenario & Site Type**: (e.g., Macro, IBC, CRAN).
  - **Timeline**: The scheduled rollout week (Delivery plan W).
  - **VIP Status**: High-priority sites (SVIP, VVIP, VIP) are highlighted with a gold border and larger radius.

### 🔍 Advanced Filtering (2-Column Grid)
The sidebar includes a compact filter grid to narrow down your view:
- **Region**: Filter by North, Ha Noi, Middle, or South.
- **Site Status**:
  - **On-Air (Green)**: Site is active, data pulled from `On Air Progress Tracker.xlsx`.
  - **RFI Ready (Blue)**: Site has a `Site configure Lock Date`.
  - **Pending (Grey)**: No approval/lock date and not on-air.
- **Week Filter**: Filter by specific rollout weeks (W1, W2, etc.).
- **RAT Filter**: Filter sites by **4G**, **5G**, or both. On-Air status for specific RATs is pulled from the progress tracker.
- **Site Type**: Filter by physical deployment type (Macro, IBC, etc.).
- **VIP Filter**: Isolate high-priority sites (SVIP, VVIP, VIP).

### 📏 Engineering Tools
- **Distance Ruler (Pencil Icon)**: Click the pencil to activate. Click two points on the map to measure the exact distance (meters/kilometers) between them. Right-click to clear.
- **Dark Mode (Moon Icon)**: Toggle between high-visibility light mode and premium dark mode.
- **Reset View**: Quickly zoom out to see the full country view.

### 💠 Official Regional Polygons
The dashed lines on the map represent the **Official Planning Clusters** loaded from the regional Shapefiles. This helps engineering teams prevent **Scattered Insertion (插花)** by ensuring sites are deployed within their planned boundaries.

---

## 2. Maintenance & Data Updates

The dashboard is built as a static application for high performance. To update the data and view locally:

1.  **Update Source Files**: Save your latest `MBF RAN Project - Phase 1 PO - Master Site List - *.xlsx` and `On Air Progress Tracker.xlsx` in the root folder: `E:\MBF Rollout Dashboard\`.
2.  **Generate Data**: Open a terminal in `E:\MBF Rollout Dashboard` and run:
    ```bash
    python generate_rollout_data.py
    ```
    This script will:
    - Extract **On-Air** statuses from the tracking sheet.
    - Separate **Ha Noi** sites from the **North** region.
    - Clean all `nan` and `None` values and generate a fresh `rollout_data.js`.

3.  **Run Localhost Server**: To view the dashboard locally, start a Python HTTP server in the same directory:
    ```bash
    python -m http.server 8000
    ```
    Then, open your web browser and go to: `http://localhost:8000`

4.  **Push to GitHub** (If deploying online):
    ```bash
    git add .
    git commit -m "Update site data"
    git push
    ```
    *Vercel will automatically detect the push and update the live website.*

---

## 3. Troubleshooting
- **Stuck at Loading**: If the loading screen doesn't disappear, ensure `rollout_data.js` exists and is valid. You can also click the "Click here if stuck" button.
- **404 on Vercel**: Ensure the main file is named `index.html`.
- **Missing Polygons**: Ensure the Shapefiles are located in their respective `Region` folders.

---

**Primary Contact**: [hovahyii@mbf.vn](mailto:60086951@mbf.vn)
**Version**: 1.0.0

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
- **Region**: Filter by North, Middle, or South.
- **Site Status**:
  - **Ready (Green)**: `Site configure Lock Date` is present.
  - **Approved (Blue)**: `RF Approved` or `CDD Approved` is present.
  - **Pending (Grey)**: No approval/lock date yet.
- **Week Filter**: Filter by specific rollout weeks (W1, W2, etc.).
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

The dashboard is built as a static application for high performance. To update the data:

1.  **Update Master Excel**: Save your latest site list in the root folder: `E:\MBF Rollout Dashboard\`.
2.  **Run Generator**: Open a terminal and run:
    ```bash
    python generate_rollout_data.py
    ```
    This script will:
    - Clean all `nan` and `None` values.
    - Remove decimal places from eNodeB IDs.
    - Load official polygons from the regional folders.
    - Generate a fresh `rollout_data.js`.
3.  **Push to GitHub**:
    ```bash
    git add .
    git commit -m "Update site data - [Date]"
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

# MBF Rollout Dashboard - Data Logic Definition

This document explains how the data is extracted from the source files and how statuses and connections are defined in the dashboard.

## Source File
The primary data source is the latest Rollout Plan Excel file:
`E:\MBF Rollout Dashboard\60086951_56A0US7_20260515222627.xlsm`
Sheet used: `Site Rollout Plan`

---

## 1. On-Air Status
The "On-Air" status determines if a site is fully operational (rendered as a **Green** dot).

*   **Column Range**: **IR to JA** (Excel columns 251 to 260).
*   **Specific Columns Used**:
    *   **253**: `On-Air 4G` -> `Actual End Date`
    *   **258**: `On-Air 5G` -> `Actual End Date`
*   **Logic**: If either of these columns contains a valid date (not empty or NaN), the site is marked as **On-Air**.

---

## 2. RFI / Ready Status
The "RFI Ready" status determines if a site is ready for installation or ready for On-Air but not yet fully operational (rendered as a **Blue** dot).

*   **Columns Used**:
    *   **326**: `Ready for OnAir` -> `Actual End Date` (from range **LM to LP** -> 324 to 327)
    *   **321**: `Ready For Installation` -> `Actual End Date` (from range **LH to LL** -> 319 to 323)
*   **Logic**: If the site is **not** On-Air, but **either** of these columns contains a valid date, the site is marked as **RFI Ready**.

*Note: If a site has neither On-Air nor RFI dates, it is marked as **Pending** (Grey dot).*

---

## 3. BBU Connection (CRAN Links)
The dashboard draws links between Remote Sites (CRAN-R) and their BBU Hosts (CRAN-M) to show resource sharing.

*   **Column Used**: Column **108** (`Main Site Name (BBU Location)`).
*   **Logic**:
    *   The script reads the BBU host name from column 108.
    *   It filters out invalid names (like `-`, `PROBLEM`, `NO EP data`).
    *   It looks up the coordinates for that BBU host using a global coordinate lookup (built from the Master Site List and the Rollout Plan).
*   **Display Logic**:
    *   To keep the map clean, lines are hidden by default.
    *   When you **hover** or **click** on a site:
        *   It draws the line to its BBU host (if it points to one).
        *   **AND** it searches for all other sites that use this site as a BBU and draws lines from them to this site.
    *   This allows you to see the full "star" cluster of connections by clicking on either the remote site or the host site.

---

## Coordinate Resolution
To ensure lines connect accurately:
1.  Coordinates are primarily loaded from the **Master Site List** (`MBF RAN Project - Phase 1 PO - Master Site List - 20260506.xlsx`).
2.  If a site is missing from the Master List, it falls back to the coordinates provided in the **Rollout Plan** (Columns 99 and 106).

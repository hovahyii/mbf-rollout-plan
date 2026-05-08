This dashboard is designed to monitor the **MBF RAN Project - Phase 1** rollout progress across North, Middle, and South regions, with a specific focus on preventing **"插花" (Scattered Insertion)**.

### What is "插花"?
In telecom engineering, **"插花"** refers to scattered, mixed, or non-continuous deployment (deploying "here and there" like flower arrangement). This dashboard uses **Polygon Clustering** to visualize site density and ensure deployment remains continuous and efficient.

## 1. How to Update Data

Whenever the **Master Site List** Excel file is updated, follow these steps to refresh the dashboard:

1.  Ensure the new Excel file is saved in the directory: `E:\MBF Rollout Dashboard\`
    - *Note: The script automatically picks up the latest file starting with "MBF RAN Project - Phase 1 PO - Master Site List -".*
2.  Run the data generation script:
    - Open a terminal/command prompt.
    - Run: `python "E:\MBF Rollout Dashboard\generate_rollout_data.py"`
3.  The script will process the Excel file and update `rollout_data.js`.
4.  **Refresh your browser** (or press `Ctrl + F5`) to see the new data.

---

## 2. Status Definitions

The dashboard categorizes sites into three statuses based on specific columns in the Excel sheets:

### ✅ READY (Green)
- **Definition**: The site is technically finalized and ready for the rollout phase.
- **Requirement**: The column **`Site configure Lock Date`** must contain a valid date/value.

### 🔵 APPROVED / NOT READY (Blue)
- **Definition**: The site design has been approved, but it is not yet locked for configuration.
- **Requirement**: The **`Site configure Lock Date`** is empty, BUT either **`RF Approved`** or **`CDD Approved`** columns contain a valid date/value.

### ⚪ PENDING (Grey)
- **Definition**: The site is still in the planning or early design phase.
- **Requirement**: All three columns (**`Site configure Lock Date`**, **`RF Approved`**, and **`CDD Approved`**) are empty or "None".

---

## 3. Visualization Key

- **Zone Colors (Borders)**:
  - **North**: Mobifone Blue
  - **Middle**: Mobifone Yellow
  - **South**: Mobifone Red
- **VIP Highlight**: VIP sites have a **larger radius** and a **thick gold border** for immediate identification.
- **Clusters**: The blue polygons on the map represent "Clusters" of sites. This helps you monitor **Scattered Insertion (插花)** patterns.

---

## 4. Troubleshooting

- **Stuck at Loading**: If the dashboard stays on the "Loading" screen, ensure `rollout_data.js` exists in the same folder. You can also click the "Click here if stuck" link to force the dashboard to open.
- **Nothing on Map**: Check if your Excel file has valid Latitude/Longitude coordinates. The script skips any sites with invalid or missing coordinates.

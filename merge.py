import os

with open('old_index.html', 'r', encoding='utf-8') as f:
    old_content = f.read()

with open('index.html', 'r', encoding='utf-8') as f:
    new_content = f.read()

# Extract new CSS (everything between <style> and </style>)
import re
new_style = re.search(r'<style>(.*?)</style>', new_content, re.DOTALL).group(1)

# Extract new body UI (everything between <body> and <div id="map">)
new_body_top = re.search(r'(<div id="loadingOverlay".*?)<div id="map">', new_content, re.DOTALL).group(1)

# Extract new map DOM (everything inside <div id="map"> up to scripts)
new_map_dom = re.search(r'(<div id="map">.*?</div>)\s*<script', new_content, re.DOTALL).group(1)

# Get old scripts
old_scripts = re.search(r'(<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js">.*</body>)', old_content, re.DOTALL).group(1)

# Modify old JS to match new floating card structure
old_scripts = old_scripts.replace("document.getElementById('cardStatus').textContent = clean(s.status);", "document.getElementById('cardStatusBadge').textContent = clean(s.status);")
old_scripts = old_scripts.replace("document.getElementById('cardStatus').style.color =", "document.getElementById('cardStatusBadge').style.color =")
old_scripts = old_scripts.replace("document.getElementById('cardRfi').textContent = clean(s.rfi_date);", "document.getElementById('cardRfi').textContent = clean(s.rfi_date);")
old_scripts = old_scripts.replace("document.getElementById('cardOnAir').textContent = clean(s.on_air_date);", "document.getElementById('cardOnAir').textContent = clean(s.on_air_date);")

# Wait, we need to ensure the JS map initialization correctly connects the DOM
# E.g. toggleTheme vs toggleDarkMode. New UI uses toggleTheme(). Old UI uses toggleDarkMode().
# Let's just rename toggleTheme in HTML to toggleDarkMode.
new_map_dom = new_map_dom.replace('toggleTheme()', 'L.DomEvent.stopPropagation(event); toggleDarkMode()')
new_map_dom = new_map_dom.replace('toggleMeasureTool()', 'L.DomEvent.stopPropagation(event); toggleMeasureTool()')
new_map_dom = new_map_dom.replace('resetView()', 'L.DomEvent.stopPropagation(event); resetMap()')

final_html = f"""<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mobifone Rollout Dashboard - Analytics Map</title>
    
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.css" />
    <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.Default.css" />

    <style>
{new_style}
        /* Leaflet overrides for dark mode */
        .leaflet-container {{ background: var(--bg-body) !important; font-family: 'Inter', sans-serif; }}
        .leaflet-tooltip {{ background: var(--bg-panel); color: var(--text-main); border: 1px solid var(--border-glass); backdrop-filter: blur(10px); box-shadow: 0 4px 10px rgba(0,0,0,0.3); }}
        .leaflet-tooltip-top:before {{ border-top-color: var(--bg-panel); }}
        
        /* Modals (copied from old_index.html) */
        .modal-overlay {{ position: fixed; inset: 0; background: rgba(0,0,0,0.4); backdrop-filter: blur(8px); display: none; align-items: center; justify-content: center; z-index: 10000; }}
        .modal-content {{ background: var(--bg-panel); color: var(--text-main); width: 400px; padding: 32px; border-radius: 24px; box-shadow: 0 20px 50px rgba(0,0,0,0.2); position: relative; border: 1px solid var(--border-glass); }}
    </style>
</head>
<body class="dark">
{new_body_top}
    <!-- Include Modals from old index -->
    <div id="contributorsModal" class="modal-overlay" onclick="closeModal()">
        <div class="modal-content" onclick="event.stopPropagation()">
            <div style="font-size: 22px; font-weight: 800; color: var(--mbf-blue); margin-bottom: 20px; font-family: 'Outfit';">Contributors</div>
            <div style="font-size: 10px; font-weight: 800; color: var(--text-dim); text-transform: uppercase;">Creator</div><div style="font-size: 15px; font-weight: 600; margin-bottom: 12px;">Jehovah Yii Zui Hon (60086951)</div>
            <div style="font-size: 10px; font-weight: 800; color: var(--text-dim); text-transform: uppercase;">Advisors</div>
            <div style="font-size: 15px; font-weight: 600; margin-bottom: 4px;">Li Wei (00909100)</div>
            <div style="font-size: 15px; font-weight: 600; margin-bottom: 12px;">Wang Haipeng (00508684)</div>
            <div style="margin: 20px 0; border-top: 1px solid rgba(0,0,0,0.05);"></div>
            <div style="font-size: 10px; font-weight: 800; color: var(--mbf-red); text-transform: uppercase;">Special Thanks</div>
            <div style="font-size: 10px; font-weight: 800; color: var(--text-dim);">North Polygon</div><div style="font-size: 13px; font-weight: 600; margin-bottom: 8px;">Cao Siqi (00840317)</div>
            <div style="font-size: 10px; font-weight: 800; color: var(--text-dim);">Middle Polygon</div><div style="font-size: 13px; font-weight: 600;">Nguyen Duc Trung (60079749)</div>
        </div>
    </div>

    <div id="whatsNewModal" class="modal-overlay" onclick="closeWhatsNewModal()">
        <div class="modal-content" onclick="event.stopPropagation()">
            <div style="font-size: 22px; font-weight: 800; color: var(--mbf-blue); margin-bottom: 20px; font-family: 'Outfit';">What's New in V2.0.0</div>
            <ul style="font-size: 13px; font-weight: 500; line-height: 1.6; padding-left: 20px; margin-bottom: 24px; color: var(--text-dim);">
                <li><strong>Sleek Glassmorphism UI:</strong> Enjoy the modernized dark mode dashboard inspired by Mapcn analytics.</li>
                <li><strong>Stable Leaflet Engine:</strong> Reverted back to the highly stable Canvas renderer to prevent WebGL compatibility issues.</li>
            </ul>
            <button onclick="closeWhatsNewModal()" style="width: 100%; padding: 12px; border-radius: 12px; background: var(--mbf-blue); color: white; font-weight: 800; border: none; cursor: pointer;">AWESOME!</button>
        </div>
    </div>

{new_map_dom}

{old_scripts}
</html>
"""

# Post processing JS bugs from string replace:
final_html = final_html.replace('document.getElementById(\'cardCoords\').textContent = `${s.lat.toFixed(5)}, ${s.lon.toFixed(5)}`;', 'document.getElementById(\'cardCoords\').textContent = `${parseFloat(s.lat).toFixed(5)}, ${parseFloat(s.lon).toFixed(5)}`;')

# Restore the footer link to modals
final_html = final_html.replace('<p class="footer-text" style="margin-top: 8px;"><a class="footer-link">Version 2.0.0 (WebGL)</a></p>', 
'''<p class="footer-text" style="margin-top: 8px;"><a class="footer-link">Version 2.0.1 (Leaflet)</a></p>
            <p class="footer-text" style="margin-top: 4px;"><a onclick="openWhatsNewModal()" class="footer-link" style="color: var(--mbf-blue); font-weight: 800;">🚀 What's New</a></p>
            <p class="footer-text" style="margin-top: 4px;"><a onclick="openModal()" class="footer-link" style="color: var(--mbf-red); font-weight: 800;">★ Special Thanks</a></p>''')

# We need to make sure toggleDarkMode correctly toggles the HTML class 'dark' so the CSS works
final_html = final_html.replace('''        function toggleDarkMode() {
            document.body.classList.toggle('dark-mode');
            const isDark = document.body.classList.contains('dark-mode');''', 
'''        function toggleDarkMode() {
            document.documentElement.classList.toggle('dark');
            const isDark = document.documentElement.classList.contains('dark');''')

# Fix body class initialization in old script if present
final_html = final_html.replace('<body class="dark-mode">', '<body class="dark">')
final_html = final_html.replace('document.body.classList.contains(\'dark-mode\')', 'document.documentElement.classList.contains(\'dark\')')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(final_html)

print("Merged successfully!")

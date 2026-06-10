import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

old_move = "function onMeasureMove(e) { if (currentPoints.length !== 1) return; const start = currentPoints[0], current = e.latlng; if (currentLinePreview) map.removeLayer(currentLinePreview); currentLinePreview = L.polyline([start, current], { color: '#0054A6', weight: 1.5, dashArray: '5, 10' }).addTo(map); const dist = start.distanceTo(current); const distText = dist > 1000 ? (dist/1000).toFixed(2) + ' km' : Math.round(dist) + ' m'; if (currentTooltipPreview) map.removeLayer(currentTooltipPreview); currentTooltipPreview = L.tooltip({ permanent: true, className: 'measure-tooltip' }).setLatLng(current).setContent(distText).addTo(map); }"

new_move = '''function onMeasureMove(e) { 
    if (currentPoints.length !== 1) return; 
    const start = currentPoints[0], current = e.latlng; 
    if (currentLinePreview) map.removeLayer(currentLinePreview); 
    currentLinePreview = L.polyline([start, current], { color: '#0054A6', weight: 1.5, dashArray: '5, 10' }).addTo(map); 
    const dist = start.distanceTo(current); 
    const distText = dist > 1000 ? (dist/1000).toFixed(2) + ' km' : Math.round(dist) + ' m'; 
    let bearing = turf.bearing(turf.point([start.lng, start.lat]), turf.point([current.lng, current.lat]));
    if (bearing < 0) bearing += 360;
    const content = distText + ' | Az: ' + Math.round(bearing) + '&deg;';
    if (currentTooltipPreview) map.removeLayer(currentTooltipPreview); 
    currentTooltipPreview = L.tooltip({ permanent: true, className: 'measure-tooltip' }).setLatLng(current).setContent(content).addTo(map); 
}'''

old_finish = "function finishLine(start, end, startDot) { const layers = [startDot]; const endDot = L.circleMarker(end, { radius: 4, color: '#000', fillColor: '#fff', fillOpacity: 1 }).addTo(map); const line = L.polyline([start, end], { weight: 3, color: '#0054A6' }).addTo(map); const dist = start.distanceTo(end), distText = dist > 1000 ? (dist/1000).toFixed(2) + ' km' : Math.round(dist) + ' m'; const label = L.tooltip({ permanent: true, className: 'measure-tooltip' }).setLatLng(L.latLngBounds([start, end]).getCenter()).setContent(distText).addTo(map); layers.push(endDot, line, label); completedMeasurements.push(layers); }"

new_finish = '''function finishLine(start, end, startDot) { 
    const layers = [startDot]; 
    const endDot = L.circleMarker(end, { radius: 4, color: '#000', fillColor: '#fff', fillOpacity: 1 }).addTo(map); 
    const line = L.polyline([start, end], { weight: 3, color: '#0054A6' }).addTo(map); 
    const dist = start.distanceTo(end);
    const distText = dist > 1000 ? (dist/1000).toFixed(2) + ' km' : Math.round(dist) + ' m'; 
    let bearing = turf.bearing(turf.point([start.lng, start.lat]), turf.point([end.lng, end.lat]));
    if (bearing < 0) bearing += 360;
    const content = distText + ' | Az: ' + Math.round(bearing) + '&deg;';
    const label = L.tooltip({ permanent: true, className: 'measure-tooltip' }).setLatLng(L.latLngBounds([start, end]).getCenter()).setContent(content).addTo(map); 
    layers.push(endDot, line, label); 
    completedMeasurements.push(layers); 
}'''

# Due to newline differences, we use re.sub for safety, removing all space formatting differences.
def normalize(s): return re.sub(r'\s+', r'\\s+', re.escape(s))

content = re.sub(normalize(old_move), new_move, content)
content = re.sub(normalize(old_finish), new_finish, content)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated measuring tool")

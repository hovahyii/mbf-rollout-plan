const fs = require('fs');

const rolloutData = [
  {
    "region": "North",
    "po": "PO1.3",
    "site_name": "BCN_BBE_BA_BE",
    "province": "Thai Nguyen",
    "district": "Ba Be",
    "enodeb_id": "872000",
    "lat": 22.411895,
    "lon": 105.6277,
    "vip": "NO"
  }
];

let allData = rolloutData;
let sitesGeoJSON = { type: 'FeatureCollection', features: [] };

try {
            sitesGeoJSON.features = allData
                .filter(s => !isNaN(parseFloat(s.lon)) && !isNaN(parseFloat(s.lat)))
                .map((s, idx) => ({
                    type: 'Feature',
                    id: idx, // numerical ID required for feature state
                    geometry: { type: 'Point', coordinates: [parseFloat(s.lon), parseFloat(s.lat)] },
                    properties: {
                        ...s,
                        is_vip_bool: s.is_vip ? true : false,
                        site_id_upper: s.enodeb_id ? s.enodeb_id.toUpperCase() : '',
                        site_name_upper: s.site_name ? s.site_name.toUpperCase() : ''
                    }
                }));

console.log("GeoJSON built successfully, len:", sitesGeoJSON.features.length);
} catch (e) {
  console.error("GeoJSON mapping error:", e);
}

let region = 'All', status = 'All', week = 'All', type = 'All', vip = 'All', rat = 'All';

            let total = 0, ready = 0;
            try {
            sitesGeoJSON.features.forEach(f => {
                const s = f.properties;
                const match = (region === 'All' || s.region === region) &&
                              (status === 'All' || s.status === status) &&
                              (week === 'All' || s.timeline === week) &&
                              (type === 'All' || s.site_type === type) &&
                              (vip === 'All' || s.vip === vip) &&
                              (rat === 'All' || (s.rat && s.rat.includes(rat)));
                if (match) {
                    total++;
                    if (s.status === 'On-Air') ready++;
                }
            });
            console.log("Stats total:", total);
            } catch (e) { console.error("Filter error:", e); }

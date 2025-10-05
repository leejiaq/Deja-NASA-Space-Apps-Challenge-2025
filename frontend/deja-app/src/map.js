const params = new URLSearchParams(document.location.search);

const lat = parseFloat(params.get("lat"));
const lon = parseFloat(params.get("lon"));

var map = L.map('map').setView([lat, lon], 13);

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);

var marker = L.marker([lat, lon]).addTo(map);

var circle = L.circle([lat, lon], {
    color: 'red',
    fillColor: '#f03',
    fillOpacity: 0.5,
    radius: 500
}).addTo(map);

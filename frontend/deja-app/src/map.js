const params = new URLSearchParams(document.location.search);

const lat = parseFloat(params.get("lat"));
const lon = parseFloat(params.get("lon"));

var map = L.map('map').setView([lat, lon], 13);

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);

var marker = L.marker([lat, lon]).addTo(map);

const data = {
	L0: parseFloat(params.get("estimated_maximum_diameter")),
	Ui: 2000.0,
	v0: parseFloat(params.get("estimated_maximum_diameter")) / 3.6, // convert to m/s
	T: 90.0,
	Uj: 5515.3,
};

fetch("http://localhost:8000/impact", {
	method: "POST",
	headers: {
		"Content-Type": "application/json"
	},
	body: JSON.stringify(data)
}).then(res => res.json()).then(result => {
	console.log(result);
})

var circle = L.circle([lat, lon], {
    color: 'red',
    fillColor: '#f03',
    fillOpacity: 0.5,
    radius: 500
}).addTo(map);

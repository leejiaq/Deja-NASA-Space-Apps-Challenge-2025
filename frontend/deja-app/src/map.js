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
	v0: parseFloat(params.get("relative_velocity")) / 3.6, // convert to m/s
	T: parseFloat(params.get("angle")),
	Uj: 5515.3,
};

fetch("http://localhost:8000/impact", {
	method: "POST",
	headers: {
		"Content-Type": "application/json"
	},
	body: JSON.stringify(data)
}).then(res => res.json()).then(result => {
	impact = result;
	console.log(impact.crater_diamater)
	var circle = L.circle([lat, lon], {
		color: 'red',
		fillColor: '#f03',
		fillOpacity: 0.5,
		radius: impact.crater_diamater / 2,
	}).addTo(map);

	document.getElementById("name").innerHTML = params.get("name")

	document.getElementById("diameter").innerHTML = formatNum(parseFloat(params.get("estimated_maximum_diameter"))) + "&nbsp;m"
	document.getElementById("velocity").innerHTML = formatNum(data.v0) + "&nbsp;m⁄s"
	document.getElementById("angle").innerHTML = formatNum(parseFloat(params.get("angle"))) + "°"
	
	document.getElementById("energy").innerHTML = formatNum(impact.E0 / 10**12) + "&nbsp;TJ"
	document.getElementById("tnt").innerHTML = formatNum(impact.E0 / (4.184*10**15)) + "&nbsp;megatons"
	document.getElementById("hiroshima").innerHTML = formatNum(impact.E0 / (15*(4.184*10**15))) + "&nbsp;hiroshima bombs"

	document.getElementById("craterdia").innerHTML = formatNum(impact.crater_diamater) + "&nbsp;m"
	document.getElementById("craterdep").innerHTML = formatNum(impact.crater_depth) + "&nbsp;m"
	
	fetch(`https://lobster-app-bhpix.ondigitalocean.app/?lat=${params.get("lat")}&lng=${params.get("lon")}&radii=${Math.round(impact.crater_diamater / 2)}`)
		.then((response) => response.json()).then(result => {
			console.log(result)
			document.getElementById("population").innerHTML = formatNum(parseFloat(result.populations[0]));
		})
})

function formatNum(n) {
	return n.toLocaleString('en-US', {minimumFractionDigits: 0, maximumFractionDigits: 2});
}

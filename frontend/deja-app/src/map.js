const params = new URLSearchParams(document.location.search);

const lat = parseFloat(params.get("lat"));
const lon = parseFloat(params.get("lon"));

var map = L.map('map').setView([lat, lon], 13);

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);

const data = {
	L0: parseFloat(params.get("estimated_maximum_diameter")),
	Ui: 2000.0,
	v0: parseFloat(params.get("relative_velocity")) / 3.6, // convert to m/s
	T: parseFloat(params.get("angle")),
	Uj: 5515.3,
};

fetch("https://dejaapi.altafcreator.com/impact", {
	method: "POST",
	headers: {
		"Content-Type": "application/json"
	},
	body: JSON.stringify(data)
}).then(res => res.json()).then(result => {
	impact = result;
	console.log(impact)

	document.getElementById("name").innerHTML = params.get("name")

	document.getElementById("diameter").innerHTML = formatNum(parseFloat(params.get("estimated_maximum_diameter"))) + "&nbsp;m"
	document.getElementById("velocity").innerHTML = formatNum(data.v0) + "&nbsp;m⁄s"
	document.getElementById("angle").innerHTML = formatNum(parseFloat(params.get("angle"))) + "°"
	
	document.getElementById("energy").innerHTML = formatNum(impact.E0 / 10**12) + "&nbsp;TJ"
	document.getElementById("tnt").innerHTML = formatNum(impact.E0 / (4.184*10**15)) + "&nbsp;megatons"
	document.getElementById("hiroshima").innerHTML = formatNum(impact.E0 / (15*(4.184*10**15))) + "&nbsp;hiroshima bombs"

	if (!impact.crater_diamater) {
		console.log(document.getElementById("noeff"))
		document.getElementById("noeff").style.display = "block";
		document.getElementById("eff").style.display = "none";
	} else {
		var marker = L.marker([lat, lon]).addTo(map);

		var circle = L.circle([lat, lon], {
			color: 'red',
			fillColor: '#f03',
			fillOpacity: 0.5,
			radius: impact.crater_diamater / 2,
		}).addTo(map);

		document.getElementById("energyim").innerHTML = formatNum(impact.E_ground / 10**12) + "&nbsp;TJ"
		document.getElementById("tntim").innerHTML = formatNum(impact.E_ground / (4.184*10**15)) + "&nbsp;megatons"
		document.getElementById("hiroshimaim").innerHTML = formatNum(impact.E_ground / (15*(4.184*10**15))) + "&nbsp;hiroshima bombs"
		document.getElementById("energyair").innerHTML = formatNum(impact.E_air / 10**12) + "&nbsp;TJ"
	
		document.getElementById("craterdia").innerHTML = formatNum(impact.crater_diamater) + "&nbsp;m"
		document.getElementById("craterdep").innerHTML = formatNum(impact.crater_depth) + "&nbsp;m"
	
		document.getElementById("thermal").innerHTML = formatNum(parseFloat(impact.r_effects["1"].thermal_exposure) / 10**6) + "&nbspMJ⁄m²";
		document.getElementById("mmi").innerHTML = impact.r_effects["1"].effective_mmi;
		document.getElementById("wind").innerHTML = formatNum(parseFloat(impact.r_effects["1"].peak_wind_vel)) + "&nbspm⁄s";
		document.getElementById("blast").innerHTML = formatNum(parseFloat(impact.r_effects["1"].surface_blast) / 10**6) + "&nbspMPa";
		
		fetch(`https://lobster-app-bhpix.ondigitalocean.app/?lat=${params.get("lat")}&lng=${params.get("lon")}&radii=${Math.round(impact.crater_diamater / 2)}`)
			.then((response) => response.json()).then(result => {
				console.log(result)
				document.getElementById("population").innerHTML = formatNum(parseFloat(result.populations[0]));
			})
	}
  
	document.getElementById("chat1").classList.add("opacity-100");
	document.getElementById("chat2").classList.add("opacity-100");
	document.getElementById("gobtn").classList.add("opacity-100");
})

function formatNum(n) {
	return n.toLocaleString('en-US', {minimumFractionDigits: 0, maximumFractionDigits: 2});
}

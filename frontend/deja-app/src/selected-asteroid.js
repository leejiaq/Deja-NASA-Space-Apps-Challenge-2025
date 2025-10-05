selectedAsteroid = document.getElementById("selected-asteroid");
const params = new URLSearchParams(document.location.search);
let name = params.get("name");
let closeApproachDate = params.get("close_approach_date");
let estimatedMaximumDiameter = params.get("estimated_maximum_diameter");
let relativeVelocity = params.get("relative_velocity");
let distanceFromEarth = params.get("distance_from_earth");

selectedAsteroid.innerHTML = `
        <div
          class="grid lg:grid-cols-2 gap-5 rounded-4xl lg:h-full w-full duration-200 px-10 mt-10"
        >
          <!-- image -->
          <div class="lg:flex flex-col justify-center items-center relative -z-10 h-4/5 hidden"
            ><img src="/public/meteor.png" alt="" style="scale: ${
              estimatedMaximumDiameter / 500
            } ${estimatedMaximumDiameter / 500}" /><p
              class="absolute bottom-0 left-0 text-slate-200/40"
              >*Not the actual asteroid.<br />**Image is scaled to estimated maximum
              diameter of the asteroid and small asteroid can appear to be near invisible. <br />
              ***Data from NASA Open APIs.</p
            ></div
          >

          <!-- description and call to action -->
          <div class="flex flex-col justify-center z-100 bg-slate-50/10 backdrop-blur-3xl p-10 rounded-r-3xl rounded-tl-3xl border-l border-b border-white hover:bg-slate-50/0 duration-500 lg:h-4/5 py-4"
            id="right-grid"><h3 class="text-3xl"
              ><span id="asteroid-name">${name}</span></h3
            >
            <p class="mt-6 leading-8">
              Close approach date:
              <span id="asteroid-close-date" class="font-bold"
                >${closeApproachDate}</span
              >
              <br />
              Estimated maximum diameter:
              <span id="asteroid-diameter" class="font-bold"
                >${estimatedMaximumDiameter}</span
              >
              m
              <br />
              Relative velocity:
              <span id="asteroid-velocity" class="font-bold"
                >${relativeVelocity}</span
              >
              km/h
              <br />
              Distance from earth:
              <span id="asteroid-distance" class="font-bold"
                >${distanceFromEarth}</span
              >
              Astronomical units
              <br />
              Potential hazardous asteroid:
              <span id="asteroid-harzard" class="font-bold">No</span>
            </p>
          </div>
        </div>
        
        `;
asteroidNamu = document.getElementById("asteroid-namu");
asteroidNamu.innerHTML = name;
document.getElementById(
  "asteroid-img"
).innerHTML = `<div class="flex flex-col justify-center items-center -z-10 h-[30%]"
            ><img src="/public/meteor.png" alt="" style="height:30vh; width:auto;" /><p
              class="text-slate-200/40"
              >*Not the actual asteroid.<br />**Image is scaled to estimated maximum
              diameter of the asteroid and small asteroid can appear to be near invisible. <br />
              ***Data from NASA Open APIs.</p
            ></div
          >`;

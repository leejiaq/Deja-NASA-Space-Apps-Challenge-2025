const now = new Date();
let day = now.getDate();
let month = now.getMonth();
const year = now.getFullYear();
if (day < 10) {
  day = "0" + day;
}
if (month + 1 < 10) {
  month = "0" + month;
} else {
  month = month + 1;
}

const wrapper = document.getElementById("carousel-wrapper");
let fetchData;
fetch(
  `https://api.nasa.gov/neo/rest/v1/feed?start_date=${year}-${month}-${day}&end_date=${year}-${month}-${day}&api_key=6bGt7Gk2DeCotzxiiIhLDF8MhN8QmiCcSB5aMsNV`
)
  .then((response) => {
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json(); // Or .text(), .blob(), etc.
  })
  .then((data) => {
    fetchData = data;
    console.log(data);
  })
  .catch((error) => {
    console.error("There was a problem with the fetch operation:", error);
  })
  .then(() => {
    for (let i = 0; i < 10; i++) {
      wrapper.innerHTML += `
        <div
          class="carousel-cell mt-10 grid bg-[#ffffff10] grid-cols-2 gap-5 p-10 rounded-4xl border-b border-[#d1d1d1] h-[600px] backdrop-blur-sm w-full hover:scale-[1.05_1.05] duration-200"
        >
          <!-- image -->
          <div class="flex flex-col justify-center items-center relative -z-10"
            ><img src="meteor.png" alt="" style="scale: ${
              fetchData.near_earth_objects[`${year}-${month}-${day}`][i]
                .estimated_diameter.meters.estimated_diameter_max / 500
            } ${
        fetchData.near_earth_objects[`${year}-${month}-${day}`][i]
          .estimated_diameter.meters.estimated_diameter_max / 500
      }" /><p
              class="absolute bottom-0 left-0 text-slate-200/40"
              >*Not the actual asteroid.<br />**Image is scaled to estimated maximum
              diameter of the asteroid and small asteroid can appear to be near invisible. <br />
              ***Data from NASA Open APIs.</p
            ></div
          >

          <!-- description and call to action -->
          <div class="flex flex-col justify-center z-100 bg-slate-50/10 backdrop-blur-3xl p-10 rounded-r-3xl rounded-tl-3xl border-l border-b border-white hover:bg-slate-50/0 duration-500"
            id="right-grid"><h3 class="text-3xl"
              ><span id="asteroid-name">${
                fetchData.near_earth_objects[`${year}-${month}-${day}`][i].name
              }</span></h3
            >
            <p class="mt-6 leading-8">
              Close approach date:
              <span id="asteroid-close-date" class="font-bold"
                >${
                  fetchData.near_earth_objects[`${year}-${month}-${day}`][i]
                    .close_approach_data[0].close_approach_date
                }</span
              >
              <br />
              Estimated maximum diameter:
              <span id="asteroid-diameter" class="font-bold"
                >${fetchData.near_earth_objects[`${year}-${month}-${day}`][
                  i
                ].estimated_diameter.meters.estimated_diameter_max.toFixed(
                  2
                )}</span
              >
              m
              <br />
              Relative velocity:
              <span id="asteroid-velocity" class="font-bold"
                >${Number(
                  fetchData.near_earth_objects[`${year}-${month}-${day}`][i]
                    .close_approach_data[0].relative_velocity
                    .kilometers_per_hour
                ).toFixed(2)}</span
              >
              km/h
              <br />
              Distance from earth:
              <span id="asteroid-distance" class="font-bold"
                >${Number(
                  fetchData.near_earth_objects[`${year}-${month}-${day}`][i]
                    .close_approach_data[0].miss_distance.astronomical
                ).toFixed(2)}</span
              >
              Astronomical units
              <br />
              Potential hazardous asteroid:
              <span id="asteroid-harzard" class="font-bold">${
                fetchData.near_earth_objects[`${year}-${month}-${day}`][i]
                  .close_approach_data[0].is_potentially_hazardous_asteroid
                  ? "Yes"
                  : "No"
              }</span>
            </p>
            <a
              href="/post-sel.html?id=${i}&date=${year}-${month}-${day}&name=${
        fetchData.near_earth_objects[`${year}-${month}-${day}`][i].name
      }&close_approach_date=${
        fetchData.near_earth_objects[`${year}-${month}-${day}`][i]
          .close_approach_data[0].close_approach_date
      }&estimated_maximum_diameter=${fetchData.near_earth_objects[
        `${year}-${month}-${day}`
      ][i].estimated_diameter.meters.estimated_diameter_max.toFixed(
        2
      )}&relative_velocity=${Number(
        fetchData.near_earth_objects[`${year}-${month}-${day}`][i]
          .close_approach_data[0].relative_velocity.kilometers_per_hour
      ).toFixed(2)}&distance_from_earth=${Number(
        fetchData.near_earth_objects[`${year}-${month}-${day}`][i]
          .close_approach_data[0].miss_distance.astronomical
      ).toFixed(2)}#sel-wrapper"
              id="asteroid-call"
              class="mt-10 px-8 py-4 bg-slate-50 text-slate-800 rounded-4xl hover:scale-110 duration-200"
              >Select this asteroid</a
            >
          </div>
        </div>
        
        `;
    }
  });

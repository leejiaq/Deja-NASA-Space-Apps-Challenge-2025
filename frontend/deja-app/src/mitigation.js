const hero = document.getElementById("hero-wrapper");
const slide2 = document.getElementById("stephen");
const slide3 = document.getElementById("do-nothing");

// slide2.style.display = "none";

function change(slidebefore, slideafter) {
  console.log(slideafter);
  document.getElementById(slidebefore).style.display = "none";
  document.getElementById(slideafter).style.display = "block";
}

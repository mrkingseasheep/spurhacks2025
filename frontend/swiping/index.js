const sitePic = document.getElementById("sitePic");
const nextBtn = document.getElementById("nextBtn");
const prevBtn = document.getElementById("prevBtn");

var camp_id = "xxx";
var img_path = "/path/to/nowhere";
var privacy = "privacy";

nextBtn.addEventListener("click", () => {
    sitePic.classList.add("flyRight");
    fetch("http://localhost:5000/api/items")
        .then((response) => response.json())
        .then((data) => {
            camp_id = data["_id"];
            img_path = data["Campsite Photo"];
            privacy = data["Privacy"];
            console.log(data["Privacy"]);
        });
});

prevBtn.addEventListener("click", () => {
    sitePic.classList.add("flyLeft");
});

sitePic.addEventListener("animationend", () => {
    sitePic.classList.remove("flyRight");
    sitePic.classList.remove("flyLeft");
});

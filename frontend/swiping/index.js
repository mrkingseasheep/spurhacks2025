const sitePic = document.getElementById("sitePic");
const nextBtn = document.getElementById("nextBtn");
const prevBtn = document.getElementById("prevBtn");

let newImagePath;

function newSitePath() {
    // return "../../img/lake1.png";
    return "../../img/weedtree.jpg";
}

let cur_id = "xxx";
let user_response = {
    title: "title",
    description: "description",
    _id: cur_id,
    liked: true,
};

nextBtn.addEventListener("click", () => {
    fetch(`http://localhost:5000/api/items`)
        .then((response) => response.json())
        .then((data) => {
            console.log(data["Privacy"]);
        });
});

prevBtn.addEventListener("click", () => {
    sitePic.classList.add("flyLeft");
    console.log("flying left");
});

sitePic.addEventListener("animationend", () => {
    sitePic.classList.remove("flyRight");
    sitePic.classList.remove("flyLeft");
    newImagePath = newSitePath();
    sitePic.style.backgroundImage = `url(${newImagePath})`;
    console.log("flying right, weetree");
});

document.addEventListener("DOMContentLoaded", () => {
    fetch("/api/items")
        .then((response) => response.json())
        .then((data) => {
            console.log(data.get("Service Type"));
        });
});

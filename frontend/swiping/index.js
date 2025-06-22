const sitePic = document.getElementById("sitePic");
const nextBtn = document.getElementById("nextBtn");
const prevBtn = document.getElementById("prevBtn");

function newSitePath() {
    // return "../../img/lake1.png";
    return "../../img/weedtree.jpg";
}

nextBtn.addEventListener("click", () => {
    sitePic.classList.add("flyRight");
});

prevBtn.addEventListener("click", () => {
    sitePic.classList.add("flyLeft");
    console.log("flying left");
});

sitePic.addEventListener("animationend", () => {
    sitePic.classList.remove("flyRight");
    sitePic.classList.remove("flyLeft");
    let newImagePath = newSitePath();
    sitePic.style.backgroundImage = `url(${newImagePath})`;
    console.log("flying right, weetree");
});

document.addEventListener("DOMContentLoaded", () => {
    fetch("/api/items");
});

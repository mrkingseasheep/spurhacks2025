const sitePic = document.getElementById("sitePic");
const nextBtn = document.getElementById("nextBtn");
const prevBtn = document.getElementById("prevBtn");

nextBtn.addEventListener("click", () => {
    sitePic.classList.remove("flyLeft");
    if (sitePic.classList.contains("flyRight")) {
        sitePic.classList.remove("flyRight");
        console.log("removing animation");
    } else {
        sitePic.classList.add("flyRight");
        console.log("started animation");
    }
});

prevBtn.addEventListener("click", () => {
    sitePic.classList.remove("flyRight");
    if (sitePic.classList.contains("flyLeft")) {
        sitePic.classList.remove("flyLeft");
        console.log("removing animation");
    } else {
        sitePic.classList.add("flyLeft");
        console.log("started animation");
    }
});

function nextSite() {
    sitePic.style.backgroundImage = 'url("../../img/lake1.png")';
}

function prevSite() {
    sitePic.style.backgroundImage = 'url("../../img/weedtree.jpg")';
}

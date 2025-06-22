const sitePic = document.getElementById("sitePic");
const picture = document.getElementById("picture");
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
    // user_response["liked"] = true;
    // sitePic.classList.add("flyRight");
    // console.log();
    // fetch("http://localhost:5000/api/add_item", {
    //     method: "POST",
    //     headers: {
    //         "Content-Type": "application/json",
    //     },
    //     body: JSON.stringify(user_response),
    // })
    //     .then((response) => response.json()) // 4️⃣ Wait for the server’s response, then parse it as JSON
    //     .then((data) => {
    //         if (data.error) {
    //             console.error("Error:", data.error); // 5️⃣ If server sent an error, log it
    //         } else {
    //             console.log("Success:", data.message, "New ID:", data.id); // 6️⃣ Otherwise, log success message and inserted item ID
    //         }
    //     })
    //     .catch((err) => {
    //         console.error("Fetch error:", err); // 7️⃣ If something went wrong with the request itself (like network error), catch it here
    //     });
    //
    fetch(`http://localhost:5000/api/items`)
        .then((response) => response.json())
        .then(delay(2000))
        .then((data) => {
            console.log(data);
            console.log(data["Campsite Photo"]);
            // sitePic.style.backgroundImage = `url(${data["Campsite Photo"]})`;
            newImagePath = data["Campsite Photo"];
            cur_id = data["_id"];
            // picture.src = data["Campsite Photo"];
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

// document.addEventListener("DOMContentLoaded", () => {
//     fetch("/api/items")
//         .then((response) => response.json())
//         .then((data) => {
//             console.log(data.get("Service Type"));
//         });
// });

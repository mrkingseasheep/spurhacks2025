const sitePic = document.getElementById("sitePic");
const prevBtn = document.getElementById("prevBtn");
const nextBtn = document.getElementById("nextBtn");
const infoHeader = document.getElementById("location");
const infoBox = document.getElementById("useful-info");

// variables for the image overlay
var camp_id = "xxx";
var img_path = "/path/to/nowhere";
var privacy = "privacy";

// ------------------------------------------------
// -HARDWARE STUFF---------------------------------
// ------------------------------------------------

// Add a temporary connect button to start the serial connection
const connectBtn = document.createElement("button");
connectBtn.textContent = "Connect to Arduino";
connectBtn.style.position = "fixed";
connectBtn.style.top = "10px";
connectBtn.style.right = "10px";
document.body.appendChild(connectBtn);

// Prevent over-triggering
let lastTriggerTime = 0;
const DEBOUNCE = 500;

function handleJoystick(x) {
    const now = Date.now();
    if (now - lastTriggerTime < DEBOUNCE) return;

    if (x < 300) {
        sitePic.classList.remove("flyLeft");
        void sitePic.offsetWidth;
        sitePic.classList.add("flyLeft");
        // console.log("flyLeft");
        lastTriggerTime = now;
    } else if (x > 700) {
        sitePic.classList.remove("flyRight");
        void sitePic.offsetWidth;
        sitePic.classList.add("flyRight");
        // console.log("flyRight");
        lastTriggerTime = now;
    }
}

// Serial connection
connectBtn.addEventListener("click", async () => {

    try {
        const port = await navigator.serial.requestPort();
        await port.open({ baudRate: 9600 });
        connectBtn.style.display = "none";


        const decoder = new TextDecoderStream();
        port.readable.pipeTo(decoder.writable);
        const input = decoder.readable
            .pipeThrough(
                new TransformStream({
                    start() {
                        this.buffer = "";
                    },
                    transform(chunk, controller) {
                        this.buffer += chunk;
                        const lines = this.buffer.split("\n");
                        this.buffer = lines.pop();
                        lines.forEach((line) =>
                            controller.enqueue(line.trim()),
                        );
                    },
                    flush(controller) {
                        if (this.buffer) controller.enqueue(this.buffer.trim());
                    },
                }),
            )
            .getReader();

        while (true) {
            const { value, done } = await input.read();
            if (done) break;
            if (value) {
                const parts = value.split(",").map(Number);
                if (parts.length === 2 && parts.every((n) => !isNaN(n))) {
                    const [x, y] = parts;
                    handleJoystick(x); // 👈 only care about X for left/right
                }
            }
        }
    } catch (err) {
        console.error("Serial error:", err);
    }
});

// Button fallbacks

prevBtn.addEventListener("click", () => {
    sitePic.classList.remove("flyLeft");
    sitePic.classList.add("flyLeft");
});

nextBtn.addEventListener("click", () => {
    sitePic.classList.remove("flyRight");
    void sitePic.offsetWidth;
    sitePic.classList.add("flyRight");
    fetch("http://localhost:5000/api/items")
        .then((response) => response.json())
        .then((data) => {
            camp_id = data["_id"];
            img_path = "../." + data["Campsite Photo"];
            privacy = data["Privacy"];
            infoBox.textContent =
                data["Service Type"] + " " + data["Adjacent to"];
            infoHeader.textContent =
                data["Provincial Park"] + " " + data["Campsite number"];
            sitePic.style.backgroundImage = `url(${img_path})`;
            console.log(data["Privacy"]);
        });
});

sitePic.addEventListener("animationend", () => {
    sitePic.classList.remove("flyRight");
    sitePic.classList.remove("flyLeft");
    //     sitePic.style.backgroundImage = `url('../../img/weedtree.jpg')`;
});

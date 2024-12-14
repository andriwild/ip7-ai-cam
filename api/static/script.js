console.log('script.js loaded');
console.log("Server runs on:" ,window.SERVER_URL);

const BASE_URL = window.SERVER_URL;

const cameraElement     = document.getElementById("cameraSelect");
const resolutionElement = document.getElementById("resolutionSelect");
const modelElement      = document.getElementById("modelSelect");
const confidenceElement = document.getElementById("confidenceInput");
const tempElement       = document.getElementById("temp");
const cpuElement        = document.getElementById("cpu");
const storageElement    = document.getElementById("storage");

const sendSetting = (json, endpoint) => {
    fetch(`${BASE_URL}${endpoint}`, {
        method: 'POST',
        mode: 'no-cors',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(json)
    }).then(response => {
        console.log(response);
     });
};

const fetchSetting = (endpoint, applyFn) => {
    fetch(`${BASE_URL}${endpoint}`)
        .then(response => response.json())
        .then(data => {
            applyFn(data);
        });
};


fetchSetting(
    "cameras", (
    data => data.forEach(cam => {
            cameraElement.innerHTML += `<option value="${cam}">${cam}</option>`;
        })
    )
)

fetchSetting(
    "confidence", (
    data => confidenceElement.value = data["confidence"]
    )
)

const updateMetaData = () => {
    fetchSetting(
        "meta", (
            data => {
                tempElement.innerText    = data["temp"]
                cpuElement.innerText     = data["cpu"]
                storageElement.innerText = data["storage"]
            }
        )
    )
};
updateMetaData();


document.getElementById("cameraSelectBtn").onclick = () => 
    sendSetting({ camera: cameraElement.value }, "camera");

document.getElementById("resolutionSelectBtn").onclick = () => 
    sendSetting({ resolution: resolutionElement.value }, "resolution");

document.getElementById("modelSelectBtn").onclick = () => 
    sendSetting({ model: modelElement.value }, "model");

document.getElementById("confidenceInputBtn").onclick = () => 
    sendSetting({ confidence: confidenceElement.value }, "confidence");

document.getElementById("metadataBtn").onclick = updateMetaData;

document.getElementById("roiSaveBtn").onclick = () => 
    sendSetting({ 
        roi: { 
            x: roiXSpan.textContent, 
            y: roiYSpan.textContent, 
            w: roiWSpan.textContent, 
            h: roiHSpan.textContent 
        } 
    }, "roi");

document.getElementById("roiResetBtn").onclick = () => sendSetting({ roi: "" }, "roi");

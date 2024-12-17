console.log('script.js loaded');
console.log("Server runs on:" ,window.SERVER_URL);

const BASE_URL = window.SERVER_URL;

const sourceElement     = document.getElementById("sourceSelect");
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
    "sources", (
    data => data.forEach(source => {
            sourceElement.innerHTML += `<option value="${source}">${source}</option>`;
        })
    )
)

fetchSetting(
    "models", (
    data => data.forEach(model => {
            modelElement.innerHTML += `<option value="${model}">${model}</option>`;
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


document.getElementById("sourceSelectBtn").onclick = () => 
    sendSetting({ source: sourceElement.value }, "source");

document.getElementById("resolutionSelectBtn").onclick = () => 
    sendSetting({ resolution: resolutionElement.value }, "resolution");

document.getElementById("modelSelectBtn").onclick = () => {
    var values = Array.from(modelElement.selectedOptions).map(({ value }) => value);
    sendSetting({ models: values }, "models");
}

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

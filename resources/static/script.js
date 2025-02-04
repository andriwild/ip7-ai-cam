console.log('script.js loaded');

import { sendSource, sendSinks, sendOperation } from './helper.js';

const sourceElement    = document.getElementById("sourceSelect");
const sinkElement      = document.getElementById("sinkSelect");
const operationElement = document.getElementById("operationSelect");

const fetchSetting = (endpoint, applyFn) => {
    fetch(`/${endpoint}`)
        .then(response => response.json())
        .then(data => {
            applyFn(data);
        });
};


fetchSetting(
    "config", (
    data => {
            data.sources.forEach(source => { 
                sourceElement.innerHTML += `<option value="${source.name}">${source.name}</option>`; 
            });
            data.sinks.forEach(sink => { 
                sinkElement.innerHTML += `<option value="${sink.name}">${sink.name}</option>`; 
            });
            data.operation.forEach(operation => { 
                operationElement.innerHTML += `<option value="${operation.name}">${operation.name}</option>`; 
            });
        })
    )


fetch("/source", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({ source: "default" }),
})
  .then((res) => res.json())
  .then((data) => console.log(data))
  .catch((err) => console.error(err));


document.getElementById("operationSelectBtn").onclick = () => 
    sendOperation(operationElement.value);

document.getElementById("sourceSelectBtn").onclick = () => 
    sendSource(sourceElement.value);

document.getElementById("sinkSelectBtn").onclick = () => {
    let options = sinkElement.selectedOptions;
    let values = Array.from(options).map(({ value }) => value);
    sendSinks(values);
};


// document.getElementById("confidenceInputBtn").onclick = () => 
//     sendSetting({ confidence: confidenceElement.value }, "confidence");

// document.getElementById("metadataBtn").onclick = updateMetaData;

// document.getElementById("roiSaveBtn").onclick = () => 
//     sendSetting({ 
//         roi: { 
//             x: roiXSpan.textContent, 
//             y: roiYSpan.textContent, 
//             w: roiWSpan.textContent, 
//             h: roiHSpan.textContent 
//         } 
//     }, "roi");

// document.getElementById("roiResetBtn").onclick = () => sendSetting({ roi: "" }, "roi");

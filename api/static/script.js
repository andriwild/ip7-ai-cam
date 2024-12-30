console.log('script.js loaded');

import { sendSource, sendSinks } from './helper.js';

const sourceElement = document.getElementById("sourceSelect");
const sinkElement   = document.getElementById("sinkSelect");

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

// fetchSetting(
//     "models", (
//     data => data.forEach(model => {
//             modelElement.innerHTML += `<option value="${model}">${model}</option>`;
//         })
//     )
// )

document.getElementById("sourceSelectBtn").onclick = () => 
    sendSource(sourceElement.value);

document.getElementById("sinkSelectBtn").onclick = () => 
    sendSinks(sinkElement.value);


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

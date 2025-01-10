console.log('script.js loaded');

import { sendSource, sendSinks, sendPipe } from './helper.js';

const sourceElement = document.getElementById("sourceSelect");
const sinkElement   = document.getElementById("sinkSelect");
const pipeElement   = document.getElementById("pipeSelect");

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
            data.pipes.forEach(pipe => { 
                pipeElement.innerHTML += `<option value="${pipe.name}">${pipe.name}</option>`; 
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


document.getElementById("pipeSelectBtn").onclick = () => 
    sendPipe(pipeElement.value);

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

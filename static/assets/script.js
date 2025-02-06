console.log('script.js loaded');

const sourceElement    = document.getElementById("sourceSelect");
const sinkElement      = document.getElementById("sinkSelect");
const operationElement = document.getElementById("operationSelect");


/**
 * Sends a POST request to /operation with { operation: opVal }
 * @param {string} opVal - The new operation value
 * @returns {Promise<Object>} - Resolves with JSON response
 */
async function sendOperation(opVal) {
  return fetch("/operation", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ operation: opVal}),
  })
    .then((res) => {
      if (!res.ok) {
        throw new Error(`sendSource failed with status ${res.status}`);
      }
      return res.json();
    });
}

/**
 * Sends a POST request to /source with { source: sourceVal }
 * @param {string} sourceVal - The new source value
 * @returns {Promise<Object>} - Resolves with JSON response
 */
async function sendSource(sourceVal) {
  return fetch("/source", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ source: sourceVal }),
  })
    .then((res) => {
      if (!res.ok) {
        throw new Error(`sendSource failed with status ${res.status}`);
      }
      return res.json();
    });
}

/**
 * Sends a POST request to /sinks with { sinks: sinksVal }
 * @param {Array|string} sinksVal - The new sinks value (Array or string)
 * @returns {Promise<Object>} - Resolves with JSON response
 */
async function sendSinks(sinksVal) {
  return fetch("/sinks", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ sinks: sinksVal }),
  })
    .then((res) => {
      if (!res.ok) {
        throw new Error(`sendSinks failed with status ${res.status}`);
      }
      return res.json();
    });
}

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
            data.operations.forEach(operation => { 
                operationElement.innerHTML += `<option value="${operation.name}">${operation.name}</option>`; 
            });
        })
    )


document.getElementById("operationSelectBtn").onclick = () =>
    sendOperation(operationElement.value);

document.getElementById("sourceSelectBtn").onclick = () => 
    sendSource(sourceElement.value);

document.getElementById("sinkSelectBtn").onclick = () => {
    let options = sinkElement.selectedOptions;
    let values = Array.from(options).map(({ value }) => value);
    sendSinks(values);
};

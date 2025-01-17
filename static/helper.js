
/**
 * Sends a POST request to /pipe with { pipe: pipeVal }
 * @param {string} pipeVal - The new pipe value
 * @returns {Promise<Object>} - Resolves with JSON response
 */
export function sendPipe(pipeVal) {
  return fetch("/pipe", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ pipe: pipeVal }),
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
export function sendSource(sourceVal) {
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
export function sendSinks(sinksVal) {
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

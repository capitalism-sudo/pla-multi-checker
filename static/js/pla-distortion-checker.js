const resultTemplate = document.querySelector("[data-pla-results-template]");
const resultsArea = document.getElementById("distortionResults");

loadPreferences();
setupPreferenceSaving();

// Save and load user preferences
function loadPreferences() {
  document.getElementById("mapSelect").value =
    localStorage.getItem("mapSelect") ?? "obsidianfieldlands";
  document.getElementById("rolls").value = readIntFromStorage("rolls", 1);
  document.getElementById("distortionAlphaFilter").checked =
    readBoolFromStorage("distortionAlphaFilter", false);
  document.getElementById("distortionShinyFilter").checked =
    readBoolFromStorage("distortionShinyFilter", false);
}

function setupPreferenceSaving() {
  document
    .getElementById("mapSelect")
    .addEventListener("change", (e) =>
      localStorage.setItem("mapSelect", e.target.value)
    );
  document
    .getElementById("rolls")
    .addEventListener("change", (e) =>
      saveIntToStorage("rolls", e.target.value)
    );
  document
    .getElementById("distortionAlphaFilter")
    .addEventListener("change", (e) =>
      saveBoolToStorage("distortionAlphaFilter", e.target.checked)
    );
  document
    .getElementById("distortionShinyFilter")
    .addEventListener("change", (e) =>
      saveBoolToStorage("distortionShinyFilter", e.target.checked)
    );
}

function saveIntToStorage(id, value) {
  localStorage.setItem(id, value);
}

function readIntFromStorage(id, defaultValue) {
  value = localStorage.getItem(id);
  return value ? parseInt(value) : defaultValue;
}

function saveBoolToStorage(id, value) {
  localStorage.setItem(id, value ? 1 : 0);
}

function readBoolFromStorage(id, defaultValue) {
  value = localStorage.getItem(id);
  return value ? parseInt(value) == 1 : defaultValue;
}

function getOptions() {
  let mapSelect = document.getElementById("mapSelect").value;
  let rolls = document.getElementById("rolls").value;
  let distortionAlphaFilter = document.getElementById(
    "distortionAlphaFilter"
  ).checked;
  let distortionShinyFilter = document.getElementById(
    "distortionShinyFilter"
  ).checked;

  return { mapSelect, rolls, distortionAlphaFilter, distortionShinyFilter };
}

function checkDistortions() {
  let options = getOptions();

  fetch("/read-distortions", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(options),
  })
    .then((response) => response.json())
    .then((results) => showResults(results))
    .catch((error) => showError(error));
}

function showResults({ results }) {
  resultsArea.innerHTML = "";
  console.log(results);

  results.forEach((result, index) => {
    if (!result.spawn) {
      return;
    }

    const resultContainer = resultTemplate.content.cloneNode(true);
    resultContainer.querySelector("[data-pla-results-species]").innerText =
      result.species;
    resultContainer.querySelector("[data-pla-results-location]").innerText =
      result.distortion_name;
    resultContainer.querySelector("[data-pla-results-shiny]").innerText =
      result.shiny;
    resultContainer.querySelector("[data-pla-results-alpha]").innerText =
      result.alpha;
    resultContainer.querySelector("[data-pla-results-nature]").innerText =
      result.nature;
    resultContainer.querySelector("[data-pla-results-gender]").innerText =
      result.gender;
    resultContainer.querySelector("[data-pla-results-ec]").innerText =
      result.ec;
    resultContainer.querySelector("[data-pla-results-pid]").innerText =
      result.pid;
    resultContainer.querySelector("[data-pla-results-ivs-hp]").innerText =
      result.ivs[0];
    resultContainer.querySelector("[data-pla-results-ivs-att]").innerText =
      result.ivs[1];
    resultContainer.querySelector("[data-pla-results-ivs-def]").innerText =
      result.ivs[2];
    resultContainer.querySelector("[data-pla-results-ivs-spa]").innerText =
      result.ivs[3];
    resultContainer.querySelector("[data-pla-results-ivs-spd]").innerText =
      result.ivs[4];
    resultContainer.querySelector("[data-pla-results-ivs-spe]").innerText =
      result.ivs[5];

    resultsArea.appendChild(resultContainer);
  });
}

function showError(error) {
  console.log(error);
  let resultsArea = document.getElementById("distortionResults");
  resultsArea.textContent = "Error" + JSON.stringify(error, null, 2);
}

function createDistortion() {
  fetch("/create-distortion", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });
}

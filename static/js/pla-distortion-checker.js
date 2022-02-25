const resultTemplate = document.querySelector("[data-pla-results-template]");
const resultsArea = document.getElementById("distortionResults");

// options
const mapSelect = document.getElementById("mapSelect");
const rollsInput = document.getElementById("rolls");

// filters
const distShinyOrAlphaCheckbox = document.getElementById(
  "distortionShinyOrAlphaFilter"
);
const distShinyCheckbox = document.getElementById("distortionShinyFilter");
const distAlphaCheckbox = document.getElementById("distortionAlphaFilter");

loadPreferences();
setupPreferenceSaving();

const results = [];

// Save and load user preferences
function loadPreferences() {
  mapSelect.value = localStorage.getItem("mapSelect") ?? "obsidianfieldlands";
  rollsInput.value = readIntFromStorage("rolls", 1);
  distAlphaCheckbox.checked = readBoolFromStorage(
    "distortionAlphaFilter",
    false
  );
  distShinyCheckbox.checked = readBoolFromStorage(
    "distortionShinyFilter",
    false
  );
  distShinyOrAlphaCheckbox.checked = readBoolFromStorage(
    "distortionShinyOrAlphaFilter",
    false
  );
  validateFilters();
}

function setupPreferenceSaving() {
  mapSelect.addEventListener("change", (e) =>
    localStorage.setItem("mapSelect", e.target.value)
  );
  rollsInput.addEventListener("change", (e) =>
    saveIntToStorage("rolls", e.target.value)
  );
  distAlphaCheckbox.addEventListener("change", (e) =>
    saveBoolToStorage("distortionAlphaFilter", e.target.checked)
  );
  distShinyCheckbox.addEventListener("change", (e) =>
    saveBoolToStorage("distortionShinyFilter", e.target.checked)
  );
  distShinyOrAlphaCheckbox.addEventListener("change", (e) =>
    saveBoolToStorage("distortionShinyOrAlpaFilter", e.target.checked)
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

function validateFilters() {
  let shinyOrAlphaFilter = distShinyOrAlphaCheckbox.checked;
  let shinyFilter = distShinyCheckbox.checked;
  let alphaFilter = distAlphaCheckbox.checked;

  if (shinyOrAlphaFilter) {
    shinyFilter = false;
    alphaFilter = false;
  }

  if (shinyFilter || alphaFilter) {
    shinyOrAlphaFilter = false;
  }

  distShinyOrAlphaCheckbox.checked = shinyOrAlphaFilter;
  distShinyCheckbox.checked = shinyFilter;
  distAlphaCheckbox.checked = alphaFilter;
}

function filter(result, shinyOrAlphaFilter, shinyFilter, alphaFilter) {
  if (shinyOrAlphaFilter && !(result.shiny || result.alpha)) {
    return false;
  }

  if (shinyFilter && !result.shiny) {
    return false;
  }

  if (alphaFilter && !result.alpha) {
    return false;
  }

  return true;
}

function getOptions() {
  return {
    map_name: mapSelect.value,
    rolls: parseInt(rollsInput.value),
  };
}

function checkDistortions() {
  const options = getOptions();
  showFetchingResults();

  fetch("/read-distortions", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(options),
  })
    .then((response) => response.json())
    .then((res) => showResults(res))
    .catch((error) => showError(error));
}

function showFetchingResults() {
  results.length = 0;
  resultsArea.innerHTML = "";
  resultsArea.innerText = "Searching distortion results";
}

const showResults = ({ distortion_spawns }) => {
  distortion_spawns.forEach((pokemon) => {
    if (pokemon.spawn) {
      results.push(pokemon);
    }
  });
  showFilteredResults();
};

const showFilteredResults = () => {
  validateFilters();

  let shinyOrAlphaFilter = distShinyOrAlphaCheckbox.checked;
  let shinyFilter = distShinyCheckbox.checked;
  let alphaFilter = distAlphaCheckbox.checked;

  resultsArea.innerHTML = "";

  filteredResults = results.filter(
    (result) =>
      result.spawn &&
      filter(result, shinyOrAlphaFilter, shinyFilter, alphaFilter)
  );

  if (filteredResults.length > 0) {
    filteredResults.forEach((result) => {
      const resultContainer = resultTemplate.content.cloneNode(true);
      resultContainer.querySelector("[data-pla-results-species]").innerText =
        result.species;
      resultContainer.querySelector("[data-pla-results-location]").innerText =
        result.distortion_name;

      let resultShiny = resultContainer.querySelector(
        "[data-pla-results-shiny]"
      );
      resultShiny.innerText = result.shiny;
      resultShiny.classList.toggle("pla-result-true", result.shiny);
      resultShiny.classList.toggle("pla-result-false", !result.shiny);

      let resultAlpha = resultContainer.querySelector(
        "[data-pla-results-alpha]"
      );
      resultAlpha.innerText = result.alpha;
      resultAlpha.classList.toggle("pla-result-true", result.alpha);
      resultAlpha.classList.toggle("pla-result-false", !result.alpha);

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
  } else {
    resultsArea.innerText = "No results found";
  }
};

function showError(error) {
  console.log(error);
  resultsArea.textContent = "Error" + JSON.stringify(error, null, 2);
}

function createDistortion() {
  fetch("/create-distortion", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });
}

import {
  DEFAULT_MAP,
  MESSAGE_ERROR,
  MESSAGE_INFO,
  showMessage,
  showModalMessage,
  clearMessages,
  clearModalMessages,
  showNoResultsFound,
  saveIntToStorage,
  readIntFromStorage,
  saveBoolToStorage,
  readBoolFromStorage,
  setupExpandables,
  showPokemonInformation,
} from "./modules/common.mjs";

const resultTemplate = document.querySelector("[data-pla-results-template]");
const resultsArea = document.querySelector("[data-pla-results]");
const mapLocationsArea = document.querySelector("[data-pla-info-locations]");
const mapSpawnsArea = document.querySelector("[data-pla-info-spawns]");
const spinnerTemplate = document.querySelector("[data-pla-spinner]");

const resultsSection = document.querySelector(".pla-section-results");

// options
const mapSelect = document.getElementById("mapSelect");
const rollsInput = document.getElementById("rolls");

mapSelect.addEventListener("change", setMap);

// filters
const distShinyOrAlphaCheckbox = document.getElementById(
  "distortionShinyOrAlphaFilter"
);
const distShinyCheckbox = document.getElementById("distortionShinyFilter");
const distAlphaCheckbox = document.getElementById("distortionAlphaFilter");

distShinyOrAlphaCheckbox.addEventListener("change", setFilter);
distShinyCheckbox.addEventListener("change", setFilter);
distAlphaCheckbox.addEventListener("change", setFilter);

// actions
const checkDistortionsButton = document.getElementById(
  "pla-button-check-distortions"
);
const createDistortionsButton = document.getElementById(
  "pla-button-create-distortion"
);

checkDistortionsButton.addEventListener("click", checkDistortions);
createDistortionsButton.addEventListener("click", createDistortion);

loadPreferences();
setupPreferenceSaving();
setMap();

const results = [];

// Save and load user preferences
function loadPreferences() {
  mapSelect.value = localStorage.getItem("mapSelect") ?? DEFAULT_MAP;
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

function setFilter(event) {
  if (event.target.checked) {
    if (event.target == distShinyOrAlphaCheckbox) {
      distShinyCheckbox.checked = false;
      distAlphaCheckbox.checked = false;
    }
    if (event.target == distShinyCheckbox) {
      distShinyOrAlphaCheckbox.checked = false;
    }
    if (event.target == distAlphaCheckbox) {
      distShinyOrAlphaCheckbox.checked = false;
    }
  }

  showFilteredResults();
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

function setMap() {
  fetch("/map-info", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ map_name: mapSelect.value }),
  })
    .then((response) => response.json())
    .then((res) => showMapInfo(res))
    .catch((error) => showMessage(MESSAGE_ERROR, error));
}

function showMapInfo({ locations, spawns }) {
  mapLocationsArea.innerHTML = "";
  mapSpawnsArea.innerHTML = "";

  locations.forEach((loc) => {
    let locListItem = document.createElement("li");
    locListItem.innerText = loc;
    mapLocationsArea.appendChild(locListItem);
  });

  spawns.forEach((spawn) => {
    let spawnItem = document.createElement("li");
    spawnItem.innerText = spawn;
    mapSpawnsArea.appendChild(spawnItem);
  });
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
    .catch((error) => showMessage(MESSAGE_ERROR, error));
}

function showFetchingResults() {
  results.length = 0;
  resultsArea.innerHTML = "";
  const spinner = spinnerTemplate.content.cloneNode(true);
  resultsArea.appendChild(spinner);
  resultsSection.classList.toggle("pla-loading", true);
}

const showResults = ({ distortion_spawns }) => {
  distortion_spawns.forEach((pokemon) => {
    if (pokemon.spawn) {
      results.push(pokemon);
    }
  });
  showFilteredResults();
};

function showFilteredResults() {
  validateFilters();

  let shinyOrAlphaFilter = distShinyOrAlphaCheckbox.checked;
  let shinyFilter = distShinyCheckbox.checked;
  let alphaFilter = distAlphaCheckbox.checked;

  resultsArea.innerHTML = "";
  resultsSection.classList.toggle("pla-loading", false);

  const filteredResults = results.filter(
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
      resultContainer.querySelector("[data-pla-results-seed]").innerText =
        result.generator_seed.toString(16);
      resultContainer.querySelector("[data-pla-results-ec]").innerText =
        result.ec.toString(16);
      resultContainer.querySelector("[data-pla-results-pid]").innerText =
        result.pid.toString(16);
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

      showPokemonInformation(resultContainer, result);

      resultsArea.appendChild(resultContainer);
    });
  } else {
    showNoResultsFound();
  }
}

function createDistortion() {
  clearMessages();
  fetch("/create-distortion", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  })
    .then((response) => response.json())
    .then((res) =>
      setTimeout((res) => {
        // The distortion creation method already has some delay
        // We delay showing the distortion creation even more to allow the game to update
        showMessage(MESSAGE_INFO, "Successfully tried to create distortion");
      }, 1500)
    )
    .catch((error) => showMessage(MESSAGE_ERROR, error));
}

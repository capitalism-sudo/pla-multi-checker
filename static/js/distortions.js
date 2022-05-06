import {
  DEFAULT_MAP,
  MESSAGE_ERROR,
  MESSAGE_INFO,
  showMessage,
  clearMessages,
  doSearch,
  showNoResultsFound,
  saveBoolToStorage,
  readBoolFromStorage,
  showPokemonIVs,
  showPokemonInformation,
  showPokemonHiddenInformation,
  replaceWithSpinnerUntilRestore,
  initializeApp,
} from "./modules/common.mjs";

const resultTemplate = document.querySelector("[data-pla-results-template]");
const resultsArea = document.querySelector("[data-pla-results]");
const mapLocationsArea = document.querySelector("[data-pla-info-locations]");
const mapSpawnsArea = document.querySelector("[data-pla-info-spawns]");

// options
const mapSelect = document.getElementById("mapSelect");

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

initializeApp("distortions");
loadPreferences();
setupPreferenceSaving();
setMap();

const results = [];

// Save and load user preferences
function loadPreferences() {
  mapSelect.value = localStorage.getItem("mapSelect") ?? DEFAULT_MAP;
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
  };
}

function setMap() {
  fetch("/api/read-distortion-map-info", {
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
    locListItem.textContent = loc;
    mapLocationsArea.appendChild(locListItem);
  });

  spawns.forEach((spawn) => {
    let spawnItem = document.createElement("li");
    spawnItem.textContent = spawn;
    mapSpawnsArea.appendChild(spawnItem);
  });
}

function checkDistortions() {
  doSearch(
    "/api/read-distortions",
    results,
    getOptions(),
    showFilteredResults,
    checkDistortionsButton
  );
}

function showFilteredResults() {
  validateFilters();

  let shinyOrAlphaFilter = distShinyOrAlphaCheckbox.checked;
  let shinyFilter = distShinyCheckbox.checked;
  let alphaFilter = distAlphaCheckbox.checked;

  const filteredResults = results.filter((result) =>
    filter(result, shinyOrAlphaFilter, shinyFilter, alphaFilter)
  );

  if (filteredResults.length > 0) {
    resultsArea.innerHTML = "";
    filteredResults.forEach((result) => showResult(result));
  } else {
    showNoResultsFound();
  }
}

function showResult(result) {
  const resultContainer = resultTemplate.content.cloneNode(true);

  resultContainer.querySelector("[data-pla-results-location]").textContent =
    result.distortion_name;

  showPokemonInformation(resultContainer, result);
  showPokemonHiddenInformation(resultContainer, result);
  showPokemonIVs(resultContainer, result);

  resultsArea.appendChild(resultContainer);
}

function createDistortion() {
  const restoreButton = replaceWithSpinnerUntilRestore(createDistortionsButton);

  clearMessages();
  fetch("/api/create-distortion", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  })
    .then((response) => response.json())
    .then(() =>
      setTimeout(() => {
        // The distortion creation method already has some delay
        // We delay showing the distortion creation even more to allow the game to update
        showMessage(MESSAGE_INFO, "Successfully tried to create distortion");
        restoreButton();
      }, 1500)
    )
    .catch((error) => showMessage(MESSAGE_ERROR, error));
}

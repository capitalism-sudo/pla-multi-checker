import {
  doSearch,
  showNoResultsFound,
  saveBoolToStorage,
  readBoolFromStorage,
  showPokemonIVs,
  showPokemonInformation,
  showPokemonHiddenInformation,
  initializeApp,
} from "./modules/common.mjs";

const resultTemplate = document.querySelector("[data-pla-results-template]");
const resultsArea = document.querySelector("[data-pla-results]");

// options
const maxDepth = document.getElementById("maxDepth");
const maxAlive = document.getElementById("maxAlive");
const groupID = document.getElementById("groupID");
const nightCheck = document.getElementById("nightToggle");

// filters
const distShinyOrAlphaCheckbox = document.getElementById(
  "mmoShinyOrAlphaFilter"
);
const distShinyCheckbox = document.getElementById("mmoShinyFilter");
const distAlphaCheckbox = document.getElementById("mmoAlphaFilter");
const mmoSpeciesText = document.getElementById("mmoSpeciesFilter");

distShinyOrAlphaCheckbox.addEventListener("change", setFilter);
distShinyCheckbox.addEventListener("change", setFilter);
distAlphaCheckbox.addEventListener("change", setFilter);
mmoSpeciesText.addEventListener("input", setFilter);

// actions
const checkMultiButton = document.getElementById("pla-button-checkmulti");
checkMultiButton.addEventListener("click", checkMulti);

initializeApp("multis");
loadPreferences();
setupPreferenceSaving();

const results = [];

// Save and load user preferences
function loadPreferences() {
  maxDepth.value = localStorage.getItem("maxDepth") ?? "0";
  distAlphaCheckbox.checked = readBoolFromStorage("mmoAlphaFilter", false);
  distShinyCheckbox.checked = readBoolFromStorage("mmoShinyFilter", false);
  nightCheck.checked = readBoolFromStorage("nightToggle");
  distShinyOrAlphaCheckbox.checked = readBoolFromStorage(
    "mmoShinyOrAlphaFilter",
    false
  );
  validateFilters();
}

function setupPreferenceSaving() {
  maxDepth.addEventListener("change", (e) =>
    localStorage.setItem("maxDepth", e.target.value)
  );
  distAlphaCheckbox.addEventListener("change", (e) =>
    saveBoolToStorage("mmoAlphaFilter", e.target.checked)
  );
  distShinyCheckbox.addEventListener("change", (e) =>
    saveBoolToStorage("mmoShinyFilter", e.target.checked)
  );
  distShinyOrAlphaCheckbox.addEventListener("change", (e) =>
    saveBoolToStorage("mmoShinyOrAlpaFilter", e.target.checked)
  );
  nightCheck.addEventListener("change", (e) =>
    saveBoolToStorage("nightCheck", e.target.checked)
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

function filter(
  result,
  shinyOrAlphaFilter,
  shinyFilter,
  alphaFilter,
  speciesFilter
) {
  if (shinyOrAlphaFilter && !(result.shiny || result.alpha)) {
    return false;
  }

  if (shinyFilter && !result.shiny) {
    return false;
  }

  if (alphaFilter && !result.alpha) {
    return false;
  }

  if (
    speciesFilter.length != 0 &&
    !result.species.toLowerCase().includes(speciesFilter.toLowerCase())
  ) {
    return false;
  }

  return true;
}

function getOptions() {
  return {
    maxdepth: parseInt(maxDepth.value),
    group_id: parseInt(groupID.value),
    maxalive: parseInt(maxAlive.value),
    isnight: nightCheck.checked,
    //	inmap: inmapCheck.checked
  };
}

function checkMulti() {
  doSearch(
    "/api/check-multi-spawn",
    results,
    getOptions(),
    showFilteredResults,
    checkMultiButton
  );
}

function showFilteredResults() {
  validateFilters();

  let shinyOrAlphaFilter = distShinyOrAlphaCheckbox.checked;
  let shinyFilter = distShinyCheckbox.checked;
  let alphaFilter = distAlphaCheckbox.checked;
  let speciesFilter = mmoSpeciesText.value;

  const filteredResults = results.filter((result) =>
    filter(result, shinyOrAlphaFilter, shinyFilter, alphaFilter, speciesFilter)
  );

  if (filteredResults.length > 0) {
    resultsArea.innerHTML =
      "<section><h3>D = Despawn. Despawn Multiple Pokemon by either Multibattles (for aggressive) or Scaring (for skittish) pokemon.</h3></section>";
    filteredResults.forEach((result) => showResult(result));
  } else {
    showNoResultsFound();
  }
}

function showResult(result) {
  const resultContainer = resultTemplate.content.cloneNode(true);

  const advances = result.path.length;
  let pathdisplay = "Path To Target: &nbsp;";

  pathdisplay +=
    advances == 0
      ? "<input type='checkbox'>&nbsp; Initial Spawn"
      : result.path
          .map((step) => `<input type='checkbox'>&nbsp;D${step}`)
          .join(" &emsp;");

  resultContainer.querySelector("[data-pla-results-location]").innerHTML =
    pathdisplay;
  resultContainer.querySelector("[data-pla-results-adv]").textContent =
    advances;

  showPokemonInformation(resultContainer, result);
  showPokemonHiddenInformation(resultContainer, result);
  showPokemonIVs(resultContainer, result);

  resultsArea.appendChild(resultContainer);
}

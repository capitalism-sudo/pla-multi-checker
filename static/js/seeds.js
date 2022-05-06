import {
  doSearch,
  showNoResultsFound,
  saveIntToStorage,
  readIntFromStorage,
  saveBoolToStorage,
  readBoolFromStorage,
  showPokemonIVs,
  showPokemonInformation,
  initializeApp,
} from "./modules/common.mjs";

const resultTemplate = document.querySelector("[data-pla-results-template]");
const resultsArea = document.querySelector("[data-pla-results]");

// options
const inputSeed = document.getElementById("inputseed");
const frSpawns = document.getElementById("frspawns");
const brSpawns = document.getElementById("brspawns");
const bonusCheckbox = document.getElementById("bonus");
const frEncounter = document.querySelector("#frpokemon");
const brEncounter = document.querySelector("#brpokemon");

// filters
const distShinyOrAlphaCheckbox = document.getElementById(
  "mmoShinyOrAlphaFilter"
);
const distShinyCheckbox = document.getElementById("mmoShinyFilter");
const distAlphaCheckbox = document.getElementById("mmoAlphaFilter");
const distDefaultCheckbox = document.getElementById("mmoDefaultRouteFilter");
const distMultiCheckbox = document.getElementById("mmoMultiFilter");

distShinyOrAlphaCheckbox.addEventListener("change", setFilter);
distShinyCheckbox.addEventListener("change", setFilter);
distAlphaCheckbox.addEventListener("change", setFilter);
distDefaultCheckbox.addEventListener("change", setFilter);
distMultiCheckbox.addEventListener("change", setFilter);

const checkMMOsButton = document.getElementById("pla-button-checkmmos");
checkMMOsButton.addEventListener("click", checkMMOs);

initializeApp("seeds");
loadPreferences();
setupPreferenceSaving();

const results = [];

// Save and load user preferences
function loadPreferences() {
  distAlphaCheckbox.checked = readBoolFromStorage("mmoAlphaFilter", false);
  distShinyCheckbox.checked = readBoolFromStorage("mmoShinyFilter", false);
  distShinyOrAlphaCheckbox.checked = readBoolFromStorage(
    "mmoShinyOrAlphaFilter",
    false
  );
  distDefaultCheckbox.checked = readBoolFromStorage(
    "mmoDefaultRouteFilter",
    false
  );
  frSpawns.value = readIntFromStorage("frspawns", 1);
  brSpawns.value = readIntFromStorage("brspawns", 1);
  bonusCheckbox.checked = readBoolFromStorage("bonus", false);
  validateFilters();
}

function setupPreferenceSaving() {
  distAlphaCheckbox.addEventListener("change", (e) =>
    saveBoolToStorage("mmoAlphaFilter", e.target.checked)
  );
  distShinyCheckbox.addEventListener("change", (e) =>
    saveBoolToStorage("mmoShinyFilter", e.target.checked)
  );
  distShinyOrAlphaCheckbox.addEventListener("change", (e) =>
    saveBoolToStorage("mmoShinyOrAlpaFilter", e.target.checked)
  );
  frSpawns.addEventListener("change", (e) =>
    saveIntToStorage("frspawns", e.target.value)
  );
  brSpawns.addEventListener("change", (e) =>
    saveIntToStorage("brspawns", e.target.value)
  );
  bonusCheckbox.addEventListener("change", (e) =>
    saveBoolToStorage("bonus", e.target.checked)
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
  defaultFilter,
  multiFilter
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

  if (defaultFilter && !result.defaultroute) {
    return false;
  }

  if (multiFilter && !result.multi) {
    return false;
  }

  return true;
}

function getOptions() {
  return {
    seed: inputSeed.value,
    frspawns: parseInt(frSpawns.value),
    brspawns: parseInt(brSpawns.value),
    isbonus: bonusCheckbox.checked,
    frencounter: frEncounter.value,
    brencounter: brEncounter.value,
    //	inmap: inmapCheck.checked
  };
}

function checkMMOs() {
  doSearch(
    "/api/check-mmoseed",
    results,
    getOptions(),
    showFilteredResults,
    checkMMOsButton
  );
}

function showFilteredResults() {
  validateFilters();

  let shinyOrAlphaFilter = distShinyOrAlphaCheckbox.checked;
  let shinyFilter = distShinyCheckbox.checked;
  let alphaFilter = distAlphaCheckbox.checked;
  let defaultFilter = distDefaultCheckbox.checked;
  let multiFilter = distMultiCheckbox.checked;

  const filteredResults = results.filter((result) =>
    filter(
      result,
      shinyOrAlphaFilter,
      shinyFilter,
      alphaFilter,
      defaultFilter,
      multiFilter
    )
  );

  if (filteredResults.length > 0) {
    resultsArea.innerHTML =
      "<h3><section class='pla-section-results' flow>D = Despawn. Despawn Multiple Pokemon by either Multibattles (for aggressive) or Scaring (for skittish) pokemon.</section></h3>";
    filteredResults.forEach((result) => showResult(result));
  } else {
    showNoResultsFound();
  }
}

function showResult(result) {
  const resultContainer = resultTemplate.content.cloneNode(true);

  let indexprefix = "";
  let chainprefix = "";
  if (result.chains.length == 0) {
    indexprefix = "Single Shiny Path: <br>" + result.index;
    chainprefix = "No Additional Shinies On Path";
  } else {
    indexprefix =
      "Multiple Shiny Path (Complete for more than one Shiny):  <br>" +
      result.index;
    chainprefix = "<br>" + result.chains;
    result.multi = true;
  }
  resultContainer.querySelector("[data-pla-results-location]").innerHTML =
    indexprefix;
  resultContainer.querySelector("[data-pla-info-chains]").innerHTML =
    chainprefix;

  showPokemonInformation(resultContainer, result);
  showPokemonIVs(resultContainer, result);

  resultsArea.appendChild(resultContainer);
}

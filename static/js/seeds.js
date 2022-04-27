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
const spinnerTemplate = document.querySelector("[data-pla-spinner]");

const resultsSection = document.querySelector(".pla-section-results");

// options
const inputSeed = document.getElementById("inputseed");
const rollsInput = document.getElementById("rolls");
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

loadPreferences();
setupPreferenceSaving();

const results = [];

// Save and load user preferences
function loadPreferences() {
  rollsInput.value = readIntFromStorage("rolls", 1);
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
  rollsInput.addEventListener("change", (e) =>
    saveIntToStorage("rolls", e.target.value)
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
    rolls: parseInt(rollsInput.value),
    frspawns: parseInt(frSpawns.value),
    brspawns: parseInt(brSpawns.value),
    isbonus: bonusCheckbox.checked,
    frencounter: frEncounter.value,
    brencounter: brEncounter.value,
    //	inmap: inmapCheck.checked
  };
}

function checkMMOs() {
  const options = getOptions();
  showFetchingResults();

  fetch("/check-mmoseed", {
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

function showResults({ mmo_spawns }) {
  for (const [key, value] of Object.entries(mmo_spawns)) {
    for (const [z, vall] of Object.entries(value)) {
      if (vall.spawn) {
        results.push(vall);
      }
      for (const [x, pokemon] of Object.entries(vall)) {
        if (pokemon.spawn) {
          results.push(pokemon);
        } else if (x.includes("Bonus")) {
          for (const [b, bonus] of Object.entries(pokemon)) {
            if (bonus.spawn) {
              results.push(bonus);
            }
          }
        }
      }
    }
  }
  showFilteredResults();
}

function showFilteredResults() {
  validateFilters();

  let shinyOrAlphaFilter = distShinyOrAlphaCheckbox.checked;
  let shinyFilter = distShinyCheckbox.checked;
  let alphaFilter = distAlphaCheckbox.checked;
  let defaultFilter = distDefaultCheckbox.checked;
  let multiFilter = distMultiCheckbox.checked;

  resultsArea.innerHTML = "";
  resultsSection.classList.toggle("pla-loading", false);

  const filteredResults = results.filter(
    (result) =>
      result.spawn &&
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
    filteredResults.forEach((result) => {
      let sprite = document.createElement("img");
      sprite.src = "static/img/sprite/" + result.sprite;

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

      const resultContainer = resultTemplate.content.cloneNode(true);
      resultContainer.querySelector(".pla-results-sprite").appendChild(sprite);
      resultContainer.querySelector("[data-pla-results-species]").innerText =
        result.species;
      resultContainer.querySelector("[data-pla-results-location]").innerHTML =
        indexprefix;

      let resultShiny = resultContainer.querySelector(
        "[data-pla-results-shiny]"
      );
      let sparkle = "";
      let sparklesprite = document.createElement("img");
      sparklesprite.className = "pla-results-sparklesprite";
      sparklesprite.src =
        "data:image/svg+xml;charset=utf8,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%3E%3C/svg%3E";
      sparklesprite.height = "10";
      sparklesprite.width = "10";
      sparklesprite.style.cssText = "pull-left;display:inline-block;";
      if (result.shiny && result.square) {
        sparklesprite.src = "static/img/square.png";
        sparkle = "Square Shiny!";
      } else if (result.shiny) {
        sparklesprite.src = "static/img/shiny.png";
        sparkle = "Shiny!";
      } else {
        sparkle = "Not Shiny";
      }
      resultContainer
        .querySelector("[data-pla-results-shinysprite]")
        .appendChild(sparklesprite);
      resultShiny.innerHTML = sparkle;
      resultShiny.classList.toggle("pla-result-true", result.shiny);
      resultShiny.classList.toggle("pla-result-false", !result.shiny);

      let resultAlpha = resultContainer.querySelector(
        "[data-pla-results-alpha]"
      );
      let bigmon = "";
      if (result.alpha) {
        bigmon = "Alpha!";
      } else {
        bigmon = "Not Alpha";
      }
      resultAlpha.innerText = bigmon;
      resultAlpha.classList.toggle("pla-result-true", result.alpha);
      resultAlpha.classList.toggle("pla-result-false", !result.alpha);

      resultContainer.querySelector("[data-pla-info-chains]").innerHTML =
        chainprefix;
      resultContainer.querySelector("[data-pla-results-nature]").innerText =
        result.nature;
      resultContainer.querySelector("[data-pla-results-gender]").innerHTML =
        result.gender;
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

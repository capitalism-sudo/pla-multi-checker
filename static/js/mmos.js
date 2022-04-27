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
// const inmapCheck = document.getElementById("inmapcheck");

// filters
const distShinyOrAlphaCheckbox = document.getElementById(
  "mmoShinyOrAlphaFilter"
);
const distShinyCheckbox = document.getElementById("mmoShinyFilter");
const distAlphaCheckbox = document.getElementById("mmoAlphaFilter");
const mmoSpeciesText = document.getElementById("mmoSpeciesFilter");
const distDefaultCheckbox = document.getElementById("mmoDefaultRouteFilter");
const distMultiCheckbox = document.getElementById("mmoMultiFilter");

distShinyOrAlphaCheckbox.addEventListener("change", setFilter);
distShinyCheckbox.addEventListener("change", setFilter);
distAlphaCheckbox.addEventListener("change", setFilter);
mmoSpeciesText.addEventListener("input", setFilter);
distDefaultCheckbox.addEventListener("change", setFilter);
distMultiCheckbox.addEventListener("change", setFilter);

// actions
const checkOneMapButton = document.getElementById("pla-button-checkonemap");
const checkMMOsButton = document.getElementById("pla-button-checkmmos");
const checkNormalsButton = document.getElementById("pla-button-checknormals");
const checkMapsButton = document.getElementById("pla-button-checkmaps");

checkOneMapButton.addEventListener("click", checkOneMap);
checkMMOsButton.addEventListener("click", checkMMOs);
checkNormalsButton.addEventListener("click", checkNormals);
checkMapsButton.addEventListener("click", readMaps);

loadPreferences();
setupPreferenceSaving();
readMaps();

const results = [];

// Save and load user preferences
function loadPreferences() {
  mapSelect.value = localStorage.getItem("mmo-mapSelect") ?? "0";
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
  validateFilters();
}

function setupPreferenceSaving() {
  mapSelect.addEventListener("change", (e) =>
    localStorage.setItem("mmo-mapSelect", e.target.value)
  );
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
  speciesFilter,
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

  if (
    speciesFilter.value.length != 0 &&
    !result.species.toLowerCase().includes(speciesFilter.value.toLowerCase())
  ) {
    return false;
  }

  if (multiFilter && !result.multi) {
    return false;
  }

  return true;
}

function getOptions() {
  return {
    mapname: parseInt(mapSelect.value),
    rolls: parseInt(rollsInput.value),
    //	inmap: inmapCheck.checked
  };
}

function readMaps() {
  fetch("/read-maps", {
    method: "GET",
  })
    .then((response) => response.json())
    .then((res) => showMaps(res))
    .catch((error) => showMessage(MESSAGE_ERROR, error));
}

function showMaps({ maps, outbreaks }) {
  mapLocationsArea.innerHTML = "";
  mapSpawnsArea.innerHTML = "";

  maps.forEach((location, index) => {
    if (location != "None") {
      let locListItem = document.createElement("li");
      locListItem.textContent = `${index} - ${location}`;
      mapLocationsArea.appendChild(locListItem);
    }
  });

  outbreaks.forEach((pokemon) => {
    let spawnItem = document.createElement("li");
    spawnItem.textContent = pokemon;
    mapSpawnsArea.appendChild(spawnItem);
  });
}

function convertCoords(coordinates) {
  return [coordinates[2] * -0.5, coordinates[0] * 0.5];
}

function checkMMOs() {
  const options = getOptions();
  showFetchingResults();

  fetch("/read-mmos", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(options),
  })
    .then((response) => response.json())
    .then((res) => showResults(res))
    .catch((error) => showMessage(MESSAGE_ERROR, error));
}

function checkNormals() {
  const options = getOptions();
  showFetchingResults();

  fetch("/read-normals", {
    method: "POST",
    headers: { "Content-type": "application/json" },
    body: JSON.stringify(options),
  })
    .then((response) => response.json())
    .then((res) => showNormalResults(res))
    .catch((error) => showMessage(MESSAGE_ERROR, error));
}

function checkOneMap() {
  const options = getOptions();
  showFetchingResults();

  fetch("/read-one-map", {
    method: "POST",
    headers: { "Content-type": "application/json" },
    body: JSON.stringify(options),
  })
    .then((response) => response.json())
    .then((res) => showMapResults(res))
    .catch((error) => showMessage(MESSAGE_ERROR, error));
}

function teleportToSpawn(coords) {
  fetch("/api/teleport-to-spawn", {
    method: "POST",
    headers: { "Content-type": "application/json" },
    body: JSON.stringify({
      coords: coords,
    }),
  });
}

function showFetchingResults() {
  results.length = 0;
  resultsArea.innerHTML = "";
  const spinner = spinnerTemplate.content.cloneNode(true);
  resultsArea.appendChild(spinner);
  resultsSection.classList.toggle("pla-loading", true);
}

const showNormalResults = ({ normal_spawns }) => {
  console.log(normal_spawns);
  for (const [key, value] of Object.entries(normal_spawns)) {
    for (const [x, pokemon] of Object.entries(value)) {
      console.log(x);
      if (pokemon.spawn) {
        results.push(pokemon);
      }
    }
  }
  showFilteredResults();
};

const showMapResults = ({ mmo_spawn }) => {
  for (const [key, value] of Object.entries(mmo_spawn)) {
    for (const [x, pokemon] of Object.entries(value)) {
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
  showFilteredResults();
};

function showResults({ mmo_spawns }) {
  for (const [key, value] of Object.entries(mmo_spawns)) {
    for (const [z, vall] of Object.entries(value)) {
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
  let speciesFilter = mmoSpeciesText;
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
        speciesFilter,
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
        indexprefix = "Single Shiny Path: <p>" + result.index;
        chainprefix = "No Additional Shinies On Path";
      } else {
        indexprefix =
          "Multiple Shiny Path (Complete for more than one Shiny): <p>" +
          result.index;
        chainprefix = result.chains;
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
      sparklesprite.style.cssText =
        "pull-left;display:inline-block;margin-left:0px;";
      if (result.shiny && result.square) {
        sparkle = "Square Shiny!";
        sparklesprite.src = "static/img/square.png";
      } else if (result.shiny) {
        sparklesprite.src = "static/img/shiny.png";
        sparkle = "Shiny!";
      } else {
        sparkle = "Not Shiny";
      }
      resultContainer
        .querySelector("[data-pla-results-shinysprite]")
        .appendChild(sparklesprite);
      resultShiny.innerText = sparkle;
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

      resultContainer.querySelector("[data-pla-results-group]").innerText =
        result.group;
      resultContainer.querySelector("[data-pla-results-numspawns]").innerText =
        result.numspawns;
      resultContainer.querySelector("[data-pla-results-mapname]").innerText =
        result.mapname;
      resultContainer.querySelector("[data-pla-results-nature]").innerText =
        result.nature;
      var coll = document.getElementsByClassName("collapsible");
      var c;

      for (c = 0; c < coll.length; c++) {
        coll[c].addEventListener("click", function () {
          this.classList.toggle("active");
          var content = this.nextElementSibling;
          if (content.style.maxHeight) {
            content.style.maxHeight = null;
          } else {
            content.style.maxHeight = content.scrollHeight + "px";
          }
        });
      }
      resultContainer.querySelector("[data-pla-info-chains]").innerHTML =
        chainprefix;
      resultContainer.querySelector("[data-pla-results-dupes]").innerText =
        result.dupes;
      resultContainer.querySelector("[data-pla-results-gender]").innerHTML =
        result.gender;
      resultContainer.querySelector("[data-pla-results-seed]").innerText =
        result.generator_seed;
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

      let button = document.createElement("button");
      button.innerText = "Teleport to Spawn";
      button.classList.add("pla-button", "pla-button-action");
      button.addEventListener("click", () => teleportToSpawn(result.coords));

      resultContainer
        .querySelector(".pla-results-teleport")
        .appendChild(button);

      resultsArea.appendChild(resultContainer);
    });
  } else {
    showNoResultsFound();
  }
}

import {
  MESSAGE_ERROR,
  showMessage,
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
const mapLocationsArea = document.querySelector("[data-pla-info-locations]");
const mapSpawnsArea = document.querySelector("[data-pla-info-spawns]");

// options
const mapSelect = document.getElementById("mapSelect");
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
const checkOutbreaksButton = document.getElementById(
  "pla-button-checkoutbreaks"
);
const checkMapsButton = document.getElementById("pla-button-checkmaps");

checkOneMapButton.addEventListener("click", checkOneMap);
checkMMOsButton.addEventListener("click", checkMMOs);
checkOutbreaksButton.addEventListener("click", checkOutbreaks);
checkMapsButton.addEventListener("click", readMaps);

initializeApp("mmos");
loadPreferences();
setupPreferenceSaving();
readMaps();

const results = [];

// Save and load user preferences
function loadPreferences() {
  mapSelect.value = localStorage.getItem("mmo-mapSelect") ?? "0";
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
    speciesFilter.length != 0 &&
    !result.species.toLowerCase().includes(speciesFilter.toLowerCase())
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
    //	inmap: inmapCheck.checked
  };
}

function readMaps() {
  fetch("/api/read-mmo-map-info", {
    method: "GET",
  })
    .then((response) => response.json())
    .then((res) => showMaps(res))
    .catch((error) => {
      console.log(error);
      showMessage(
        MESSAGE_ERROR,
        "There was an error loading MMO information. Try restarting the program and clicking 'Refresh Maps'"
      );

      checkOneMapButton.disabled = true;
      checkMMOsButton.disabled = true;
      checkOutbreaksButton.disabled = true;
    });
}

function showMaps({ maps, outbreaks }) {
  mapSelect.innerHTML = "";
  mapLocationsArea.innerHTML = "";
  mapSpawnsArea.innerHTML = "";

  let validMaps = 0;
  maps.forEach((location, index) => {
    if (location != null) {
      validMaps++;

      let mapSelectItem = document.createElement("option");
      mapSelectItem.textContent = location;
      mapSelectItem.value = index;
      mapSelect.append(mapSelectItem);

      let locListItem = document.createElement("li");
      locListItem.textContent = `${index} - ${location}`;
      mapLocationsArea.appendChild(locListItem);
    }
  });

  if (validMaps == 0) {
    let mapSelectItem = document.createElement("option");
    mapSelectItem.textContent = "No MMOs";
    mapSelectItem.value = "-1";
    mapSelect.append(mapSelectItem);

    let locListItem = document.createElement("li");
    locListItem.textContent = "No MMOs Active";
    mapLocationsArea.appendChild(locListItem);

    checkOneMapButton.disabled = true;
    checkMMOsButton.disabled = true;
  } else {
    checkOneMapButton.disabled = false;
    checkMMOsButton.disabled = false;
  }

  if (outbreaks.length == 0) {
    const el = document.createElement("li");
    el.textContent = "None";
    mapSpawnsArea.appendChild(el);
    checkOutbreaksButton.disabled = true;
  } else {
    checkOutbreaksButton.disabled = false;
  }

  outbreaks.forEach((pokemon) => {
    let spawnItem = document.createElement("li");
    spawnItem.textContent = pokemon;
    mapSpawnsArea.appendChild(spawnItem);
  });
}

function checkMMOs() {
  doSearch(
    "/api/read-mmos",
    results,
    getOptions(),
    showFilteredResults,
    checkMMOsButton
  );
}

function checkOneMap() {
  doSearch(
    "/api/read-mmos-one-map",
    results,
    getOptions(),
    showFilteredResults,
    checkOneMapButton
  );
}

function checkOutbreaks() {
  doSearch(
    "/api/read-outbreaks",
    results,
    getOptions(),
    showFilteredResults,
    checkOutbreaksButton
  );
}

function showFilteredResults() {
  validateFilters();

  let shinyOrAlphaFilter = distShinyOrAlphaCheckbox.checked;
  let shinyFilter = distShinyCheckbox.checked;
  let alphaFilter = distAlphaCheckbox.checked;
  let speciesFilter = mmoSpeciesText.value;
  let defaultFilter = distDefaultCheckbox.checked;
  let multiFilter = distMultiCheckbox.checked;

  const filteredResults = results.filter((result) =>
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
      "<section><h3>D = Despawn. Despawn Multiple Pokemon by either Multibattles (for aggressive) or Scaring (for skittish) pokemon.</h3></section>";
    filteredResults.forEach((result) => showResult(result));
  } else {
    showNoResultsFound();
  }
}

function showResult(result) {
  const resultContainer = resultTemplate.content.cloneNode(true);

  let indexprefix = "";
  let chainprefix = "N/A";

  const isMMO = result.hasOwnProperty("chains");
  if (isMMO) {
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

    var coll = resultContainer.querySelectorAll(".collapsible");
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
  } else {
    // To show path for normal outbreaks
    indexprefix = result.index;
  }
  resultContainer.querySelector("[data-pla-info-chains]").innerHTML =
    chainprefix;
  resultContainer.querySelector("[data-pla-results-dupes]").innerText = isMMO
    ? result.dupes
    : "N/A";

  resultContainer.querySelector("[data-pla-results-location]").innerHTML =
    indexprefix;

  resultContainer.querySelector("[data-pla-results-group]").innerText =
    result.group;
  resultContainer.querySelector("[data-pla-results-numspawns]").innerText =
    result.numspawns;
  resultContainer.querySelector("[data-pla-results-mapname]").innerText =
    result.mapname;

  showPokemonInformation(resultContainer, result);
  showPokemonHiddenInformation(resultContainer, result);
  showPokemonIVs(resultContainer, result);

  let button = document.createElement("button");
  button.innerText = "Teleport to Spawn";
  button.classList.add("pla-button", "pla-button-action");
  button.addEventListener("click", () => teleportToSpawn(result.coords));

  resultContainer.querySelector(".pla-results-teleport").appendChild(button);

  resultsArea.appendChild(resultContainer);
}

function convertCoords(coordinates) {
  return [coordinates[2] * -0.5, coordinates[0] * 0.5];
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

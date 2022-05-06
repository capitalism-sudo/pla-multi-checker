import {
  doSearch,
  showNoResultsFound,
  saveIntToStorage,
  readIntFromStorage,
  saveBoolToStorage,
  readBoolFromStorage,
  setupExpandables,
  showPokemonIVs,
  showPokemonInformation,
  showPokemonGender,
  initializeApp,
} from "./modules/common.mjs";

const resultTemplate = document.querySelector("[data-pla-results-template]");
const resultsArea = document.querySelector("[data-pla-results]");
const mapSpawnsArea = document.querySelector("[data-pla-info-spawner]");

// options
const inputSeed = document.getElementById("inputseed");
const rollsInput = document.getElementById("rolls");
const staticAlpha = document.getElementById("staticalpha");
const genderCheckbox = document.getElementById("gendercheck");
const dayNight = document.getElementById("daynightcheck");
const mapName = document.getElementById("speciesmap");
const speciesName = document.getElementById("speciesnames");
const spawnerID = document.getElementById("spawnernames");

// filters
const genderFilter = document.getElementById("gender");

genderFilter.addEventListener("change", setFilter);
spawnerID.addEventListener("change", setSpawners);
dayNight.addEventListener("change", setSpawners);

const checkAlphaAdvButton = document.getElementById("pla-button-checkalphaadv");
checkAlphaAdvButton.addEventListener("click", checkAlphaAdv);

initializeApp("spawns");
loadPreferences();
setupPreferenceSaving();
setupExpandables();

const results = [];

// Save and load user preferences
function loadPreferences() {
  rollsInput.value = readIntFromStorage("rolls", 1);
  genderFilter.value = readIntFromStorage("gender", 1);
  genderCheckbox.checked = readBoolFromStorage("gendercheck", false);
}

function setupPreferenceSaving() {
  rollsInput.addEventListener("change", (e) =>
    saveIntToStorage("rolls", e.target.value)
  );
  genderFilter.addEventListener("change", (e) =>
    saveIntToStorage("gender", e.target.value)
  );
  genderCheckbox.addEventListener("change", (e) =>
    saveBoolToStorage("gendercheck", e.target.checked)
  );
}

function setFilter(event) {
  showFilteredResults();
}

function setSpawners(event) {
  mapSpawnsArea.innerHTML = "";
  $.getJSON("static/resources/" + mapName.value + ".json", function (data) {
    $.each(data, function (key, value) {
      if (key == spawnerID.value) {
        console.log(key);
        var time = false;
        let cycle = dayNight.checked;
        if (cycle) time = true;
        var breakloop = false;
        $.each(value, function (timeweather, species) {
          if (
            time &&
            (timeweather.includes("Any Time") ||
              timeweather.includes("Night")) &&
            !breakloop
          ) {
            breakloop = true;
            $.each(species, function (pokemon, slot) {
              let locListItem = document.createElement("li");
              locListItem.textContent = pokemon;
              mapSpawnsArea.appendChild(locListItem);
            });
          } else if (
            !time &&
            (timeweather.includes("Any Time") || timeweather.includes("Day")) &&
            !breakloop
          ) {
            console.log(timeweather);
            console.log(species);
            breakloop = true;
            $.each(species, function (pokemon, slot) {
              console.log(pokemon);
              console.log(slot);
              let locListItem = document.createElement("li");
              locListItem.textContent = pokemon;
              console.log("loclistitem innertext");
              console.log(locListItem.innerText);
              mapSpawnsArea.appendChild(locListItem);
            });
          }
        });
      }
    });
  });
}

function getOptions() {
  return {
    seed: inputSeed.value,
    rolls: parseInt(rollsInput.value),
    isalpha: staticAlpha.checked,
    setgender: genderCheckbox.checked,
    filter: {
      species: speciesName.value,
      mapname: mapName.value,
      spawner: spawnerID.value,
      daynight: dayNight.checked,
    },
  };
}

function checkAlphaAdv() {
  doSearch("/api/check-alphaseed", results, getOptions(), showFilteredResults);
}

function showFilteredResults() {
  if (results.length > 0) {
    resultsArea.innerHTML = "";
    results.forEach((result) => showResult(result));
  } else {
    showNoResultsFound();
  }
}

function showResult(result) {
  const resultContainer = resultTemplate.content.cloneNode(true);

  resultContainer.querySelector("[data-pla-results-adv]").innerText =
    result.adv;

  showPokemonInformation(resultContainer, result);
  showPokemonIVs(resultContainer, result);

  // Overwrite Gender Display
  let genderValue = genderFilter.value;
  let resultGender = "GENDERLESS";
  if (result.gender < genderValue) {
    resultGender = "FEMALE";
  } else if (genderValue != -1) {
    resultGender = "MALE";
  }
  showPokemonGender(resultContainer, resultGender);

  resultsArea.appendChild(resultContainer);
}

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
  const options = getOptions();
  showFetchingResults();

  fetch("/check-alphaseed", {
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

function showResults({ alpha_spawns }) {
  if (alpha_spawns.spawn) {
    results.push(alpha_spawns);
  }
  showFilteredResults();
}

function showFilteredResults() {
  resultsArea.innerHTML = "";
  resultsSection.classList.toggle("pla-loading", false);

  if (results.length > 0) {
    results.forEach((result) => {
      console.log(results);

      const resultContainer = resultTemplate.content.cloneNode(true);

      let sprite = document.createElement("img");
      sprite.src = "static/img/sprite/" + result.sprite;

      resultContainer.querySelector(".pla-results-sprite").appendChild(sprite);
      resultContainer.querySelector("[data-pla-results-species]").innerText =
        result.species;

      let resultGender = "Genderless";

      if (result.gender < parseInt(genderFilter.value)) {
        resultGender = "Female";
      } else if (parseInt(genderFilter.value) != -1) {
        resultGender = "Male";
      }

      resultContainer.querySelector("[data-pla-results-adv]").innerText =
        result.adv;
      resultContainer.querySelector("[data-pla-results-nature]").innerText =
        result.nature;
      resultContainer.querySelector("[data-pla-results-gender]").innerText =
        resultGender;
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

import {
  DEFAULT_MAP,
  MESSAGE_ERROR,
  MESSAGE_INFO,
  showMessage,
  showModalMessage,
  clearMessages,
  clearModalMessages,
  doSearch,
  showNoResultsFound,
  saveIntToStorage,
  readIntFromStorage,
  saveBoolToStorage,
  readBoolFromStorage,
  setupExpandables,
  showPokemonIVs,
  showPokemonInformation,
  showPokemonHiddenInformation,
  initializeApp,
} from "./modules/common.mjs";

const resultTemplate = document.querySelector("[data-pla-results-template]");
const resultsArea = document.querySelector("[data-pla-results]");

// options
const inputS0 = document.getElementById("inputs0");
const inputS1 = document.getElementById("inputs1");
const inputS2 = document.getElementById("inputs2");
const inputS3 = document.getElementById("inputs3");
const advances = document.getElementById("advances");
const gameVer = document.getElementById("version");
const storyFlag = document.getElementById("storyflags");
const roomID = document.getElementById("roomid");
const diglettMode = document.getElementById("diglett");

// filters
/*const distShinyOrAlphaCheckbox = document.getElementById(
  "mmoShinyOrAlphaFilter"
);*/
const distShinyCheckbox = document.getElementById("mmoShinyFilter");
//const distAlphaCheckbox = document.getElementById("mmoAlphaFilter");
const mmoSpeciesText = document.getElementById("mmoSpeciesFilter");

//distShinyOrAlphaCheckbox.addEventListener("change", setFilter);
distShinyCheckbox.addEventListener("change", setFilter);
//distAlphaCheckbox.addEventListener("change", setFilter);
mmoSpeciesText.addEventListener("input", setFilter);

// actions
const checkUGButton = document.getElementById("pla-button-checkug");
checkUGButton.addEventListener("click", checkUnderground);

loadPreferences();
setupPreferenceSaving();
setupExpandables();
//setupTabs();

const results = [];

// Setup tabs

// Save and load user preferences
function loadPreferences() {
  /*maxDepth.value = localStorage.getItem("maxDepth") ?? "0";
  distAlphaCheckbox.checked = readBoolFromStorage("mmoAlphaFilter", false);
  distShinyCheckbox.checked = readBoolFromStorage("mmoShinyFilter", false);
  nightCheck.checked = readBoolFromStorage("nightToggle");
  distShinyOrAlphaCheckbox.checked = readBoolFromStorage(
    "mmoShinyOrAlphaFilter",
    false
  );
  validateFilters();*/
}

function setupPreferenceSaving() {
  /*maxDepth.addEventListener("change", (e) =>
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
  );*/
}

/*function setupTabs() {
  document.querySelectorAll(".tablinks").forEach((element) => {
    element.addEventListener("click", (event) =>
      openTab(event, element.dataset.plaTabFor)
    );
  });
}

function openTab(evt, tabName) {
  let i, tabcontent, tablinks;

  tabcontent = document.getElementsByClassName("tabcontent");
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }

  tablinks = document.getElementsByClassName("tablinks");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].className = tablinks[i].className.replace(" active", "");
  }

  document.getElementById(tabName).style.display = "block";
  evt.currentTarget.className += " active";
}*/

function setFilter(event) {
  if (event.target.checked) {
    /*if (event.target == distShinyOrAlphaCheckbox) {
      distShinyCheckbox.checked = false;
      distAlphaCheckbox.checked = false;
    }*/
    if (event.target == distShinyCheckbox) {
      //distShinyOrAlphaCheckbox.checked = false;
    }
    /*if (event.target == distAlphaCheckbox) {
      distShinyOrAlphaCheckbox.checked = false;
    }*/
  }

  showFilteredResults();
}

function validateFilters() {
  /*let shinyOrAlphaFilter = distShinyOrAlphaCheckbox.checked;
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
  distAlphaCheckbox.checked = alphaFilter;*/
}

function filter(
  result,
  shinyFilter,
  speciesFilter
) {
  /*if (shinyOrAlphaFilter && !(result.shiny || result.alpha)) {
    return false;
  }*/

  if (shinyFilter && !result.shiny) {
    return false;
  }

  /*if (alphaFilter && !result.alpha) {
    return false;
  }*/

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
    s0: inputS0.value,
	s1: inputS1.value,
	s2: inputS2.value,
	s3: inputS3.value,
    advances: parseInt(advances.value),
    story: parseInt(storyFlag.value),
    version: parseInt(gameVer.value),
    diglett: diglettMode.checked,
	room: parseInt(roomID.value),
    //	inmap: inmapCheck.checked
  };
}

function checkUnderground() {
  doSearch(
    "/api/check-underground",
    results,
    getOptions(),
    showFilteredResults,
    checkUGButton
  );
}

function showFilteredResults() {
  //validateFilters();
  
  console.log(results);

  //let shinyOrAlphaFilter = distShinyOrAlphaCheckbox.checked;
  let shinyFilter = distShinyCheckbox.checked;
  //let alphaFilter = distAlphaCheckbox.checked;
  let speciesFilter = mmoSpeciesText.value;
  //let defaultFilter = distDefaultCheckbox.checked;
  //let multiFilter = distMultiCheckbox.checked;

  const filteredResults = results.filter((result) =>
    filter(
      result,
      shinyFilter,
      speciesFilter
    )
  );

  console.log("Filtered Results:");
  console.log(filteredResults);
  
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
  
  let sprite = document.createElement("img");
  sprite.src = "static/img/spritebig/" + result.sprite;
  resultContainer.querySelector(".pla-results-sprite").appendChild(sprite);
  
  resultContainer.querySelector("[data-pla-results-species]").innerHTML =
    result.species;

  resultContainer.querySelector("[data-pla-results-advances]").textContent =
	result.advances;
  resultContainer.querySelector("[data-pla-results-shine]").textContent =
	result.shiny;
  resultContainer.querySelector("[data-pla-results-spawn]").textContent =
	result.spawn;
	
  resultContainer.querySelector("[data-pla-results-shiny]").innerHTML =
    result.shiny;
  resultContainer.querySelector("[data-pla-results-adv]").textContent =
    result.advances;
  resultContainer.querySelector("[data-pla-results-nature]").textContent =
    result.nature;
  resultContainer.querySelector("[data-pla-results-gender]").textContent =
    result.gender;
  resultContainer.querySelector("[data-pla-results-ability]").textContent =
    result.ability;
  resultContainer.querySelector("[data-pla-results-egg]").textContent =
    result.eggmove;
  /*resultContainer.querySelector("[data-pla-results-ec]").textContent =
    result.ec;
  resultContainer.querySelector("[data-pla-results-pid]").textContent =
    result.pid;*/

  //showPokemonInformation(resultContainer, result);
  showPokemonIVs(resultContainer, result);
  showPokemonHiddenInformation(resultContainer, result);

  resultsArea.appendChild(resultContainer);
}
  

/*function checkUnderground() {
	
	const options = getOptions()
	
	fetch("/api/check-underground", {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify(options),
	})
	  .then((response) => response.json())
	  .then((res) => showFilteredResults(res))
	  .catch((error) => {});
}

function showFilteredResults(results) {
  /*validateFilters();

  let shinyOrAlphaFilter = distShinyOrAlphaCheckbox.checked;
  let shinyFilter = distShinyCheckbox.checked;
  let alphaFilter = distAlphaCheckbox.checked;
  let speciesFilter = mmoSpeciesText.value;

  const filteredResults = results.filter((result) =>
    filter(result, shinyOrAlphaFilter, shinyFilter, alphaFilter, speciesFilter)
  );

	console.log(results);
    resultsArea.innerHTML =
      "<section><h3>D = Despawn. Despawn Multiple Pokemon by either Multibattles (for aggressive) or Scaring (for skittish) pokemon.</h3></section>";
    //filteredResults.forEach((result) => showResult(result));
	for (const [key,value] of Object.entries(results)) {
		console.log(key);
		console.log(value);
		for (const [k,v] of Object.entries(value)) {
			console.log(k);
			console.log(v);
			v.forEach((result) => showResult(result));
		}
	}
}

function showResult(result) {
	console.log(result)
  if (distShinyCheckbox.checked && result.shiny) {
  const resultContainer = resultTemplate.content.cloneNode(true);
  
  let sprite = document.createElement("img");
  sprite.src = "static/img/spritebig/" + result.sprite;
  resultContainer.querySelector(".pla-results-sprite").appendChild(sprite);
  
  resultContainer.querySelector("[data-pla-results-species]").innerHTML =
    result.species;

  resultContainer.querySelector("[data-pla-results-advances]").textContent =
	result.advances;
  resultContainer.querySelector("[data-pla-results-shine]").textContent =
	result.shiny;
	
  resultContainer.querySelector("[data-pla-results-shiny]").innerHTML =
    result.shiny;
  resultContainer.querySelector("[data-pla-results-adv]").textContent =
    result.advances;
  resultContainer.querySelector("[data-pla-results-nature]").textContent =
    result.nature;
  resultContainer.querySelector("[data-pla-results-gender]").textContent =
    result.gender;
  resultContainer.querySelector("[data-pla-results-ability]").textContent =
    result.ability;
  resultContainer.querySelector("[data-pla-results-egg]").textContent =
    result.eggmove;
  /*resultContainer.querySelector("[data-pla-results-ec]").textContent =
    result.ec;
  resultContainer.querySelector("[data-pla-results-pid]").textContent =
    result.pid;

  //showPokemonInformation(resultContainer, result);
  showPokemonIVs(resultContainer, result);
  showPokemonHiddenInformation(resultContainer, result);

  resultsArea.appendChild(resultContainer);
  }
  else if (!distShinyCheckbox.checked) {
	  const resultContainer = resultTemplate.content.cloneNode(true);
  
  let sprite = document.createElement("img");
  sprite.src = "static/img/spritebig/" + result.sprite;
  resultContainer.querySelector(".pla-results-sprite").appendChild(sprite);
  
  resultContainer.querySelector("[data-pla-results-species]").innerHTML =
    result.species;

  resultContainer.querySelector("[data-pla-results-advances]").textContent =
	result.advances;
  resultContainer.querySelector("[data-pla-results-shine]").textContent =
	result.shiny;
  resultContainer.querySelector("[data-pla-results-spawn]").textContent =
	result.spawn;
	
  resultContainer.querySelector("[data-pla-results-shiny]").innerHTML =
    result.shiny;
  resultContainer.querySelector("[data-pla-results-adv]").textContent =
    result.advances;
  resultContainer.querySelector("[data-pla-results-nature]").textContent =
    result.nature;
  resultContainer.querySelector("[data-pla-results-gender]").textContent =
    result.gender;
  resultContainer.querySelector("[data-pla-results-ability]").textContent =
    result.ability;
  resultContainer.querySelector("[data-pla-results-egg]").textContent =
    result.eggmove;
  /*resultContainer.querySelector("[data-pla-results-ec]").textContent =
    result.ec;
  resultContainer.querySelector("[data-pla-results-pid]").textContent =
    result.pid;

  //showPokemonInformation(resultContainer, result);
  showPokemonIVs(resultContainer, result);
  showPokemonHiddenInformation(resultContainer, result);

  resultsArea.appendChild(resultContainer);
  }
}*/

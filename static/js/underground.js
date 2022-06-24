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
  setupIVBox,
  getSelectValues,
} from "./modules/common.mjs";

const resultTemplate = document.querySelector("[data-pla-results-template]");
const wrapperTemplate = document.querySelector("[data-swsh-results-template]");
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
const minAdv = document.getElementById("minadvances");
const Delay = document.getElementById("delay");

//IVs

const minHP = document.getElementById("minhp");
const minATK = document.getElementById("minatk");
const minDEF = document.getElementById("mindef");
const minSPA = document.getElementById("minspa");
const minSPD = document.getElementById("minspd");
const minSPE = document.getElementById("minspe");

const maxHP = document.getElementById("maxhp");
const maxATK = document.getElementById("maxatk");
const maxDEF = document.getElementById("maxdef");
const maxSPA = document.getElementById("maxspa");
const maxSPD = document.getElementById("maxspd");
const maxSPE = document.getElementById("maxspe");

// filters
const distSelectFilter = document.getElementById("selectfilter");
const natureSelect = document.getElementById("naturefilter");
/*const distShinyOrAlphaCheckbox = document.getElementById(
  "mmoShinyOrAlphaFilter"
);*/
const distShinyCheckbox = document.getElementById("mmoShinyFilter");
//const distAlphaCheckbox = document.getElementById("mmoAlphaFilter");
const mmoSpeciesText = document.getElementById("mmoSpeciesFilter");
const advanceText = document.getElementById("advanceFilter");
const genderSelect = document.getElementById("genderfilter");

distShinyCheckbox.addEventListener("change", setFilter);
mmoSpeciesText.addEventListener("input", setFilter);
advanceText.addEventListener("input", setFilter);
genderSelect.addEventListener("change", setFilter);

// actions
const checkUGButton = document.getElementById("pla-button-checkug");
checkUGButton.addEventListener("click", checkUnderground);
//const checkUGButtonTest = document.getElementById("pla-button-checkug-test");
//checkUGButtonTest.addEventListener("click", checkUndergroundTest);

loadPreferences();
setupPreferenceSaving();
setupExpandables();
//setupTabs();
setupIVBox();

const results = [];

// Setup tabs

// Save and load user preferences
function loadPreferences() {
  distShinyCheckbox.checked = readBoolFromStorage("mmoShinyFilter", false);
  advances.value = 10000;
  minAdv.value = 0;
  storyFlag.value = localStorage.getItem("storyflags") ?? "6";
  gameVer.value = localStorage.getItem("version") ?? "1";
  
  minAdv.value = 0;
  minHP.value = 0;
  minATK.value = 0;
  minDEF.value = 0;
  minSPA.value = 0;
  minSPD.value = 0;
  minSPE.value = 0;
  
  maxHP.value = 31;
  maxATK.value = 31;
  maxDEF.value = 31;
  maxSPA.value = 31;
  maxSPD.value = 31;
  maxSPE.value = 31;
  
  natureSelect.value = "any";
  genderSelect.value = 50;
  Delay.value = 20;
}

function setupPreferenceSaving() {
  advances.addEventListener("change", (e) =>
    localStorage.setItem("advances", e.target.value)
  );
  minAdv.addEventListener("change", (e) =>
    localStorage.setItem("minadvances", e.target.value)
  );
  distShinyCheckbox.addEventListener("change", (e) =>
    saveBoolToStorage("mmoShinyFilter", e.target.checked)
  );
  storyFlag.addEventListener("change", (e) =>
    localStorage.setItem("storyflags", e.target.value)
  );
  gameVer.addEventListener("change", (e) =>
	localStorage.setItem("version", e.target.value)
  );
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

$(function() {
	$(".chosen-select").chosen({
		no_results_text: "Oops, nothing found!",
		inherit_select_classes: true
	});
	
	$('#naturefilter').chosen().change(setFilter);
	
	$('#slotfilter').chosen().change(setFilter);
});

function setFilter(event) {
  if (event.target.checked) {
    if (event.target == distShinyCheckbox) {
      //distShinyOrAlphaCheckbox.checked = false;
    }
  }

  showFilteredResults();
}

function validateFilters() {
}

function filter(
  result,
  shinyFilter,
  speciesFilter,
  advanceFilter,
  natureFilter,
  genderFilter,
) {

  console.log("advancefilter");
  console.log(advanceFilter);
  
  if (shinyFilter && !result.shiny) {
    return false;
  }

  if (
    speciesFilter.length != 0 &&
    !result.species.toLowerCase().includes(speciesFilter.toLowerCase())
  ) {
    return false;
  }
  
  if (
	advanceFilter.length != 0 &&
	result.advances != parseInt(advanceFilter)
  ) {
	  return false;
  }
  
  if (
		!natureFilter.includes("any") &&
		!natureFilter.includes(result.nature.toLowerCase())
		) {
			return false;
		}
		
  if (
		genderFilter != 50
	) {
		console.log("Filter is not any, checking:");
		if (
		genderFilter == 0 &&
		!(result.gender == 0)
		){
			console.log("Gender Result not male, male filter selected");
		return false;
		}
		else if ( genderFilter == 1 && !(result.gender == 1)) {
			console.log("Gender Result not female, female filter selected");
			return false;
		}
		else if ( genderFilter == 2 && !(result.gender == 2)) {
			return false;
		}
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
	filter: distSelectFilter.value,
	minadv: parseInt(minAdv.value),
	ivs: {
		minivs: [minHP.value, minATK.value, minDEF.value, minSPA.value, minSPD.value, minSPE.value],
		maxivs: [maxHP.value, maxATK.value, maxDEF.value, maxSPA.value, maxSPD.value, maxSPE.value],
	},
	delay: parseInt(Delay.value),
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

function checkUndergroundTest() {
  doSearch(
    "/api/check-underground-test",
    results,
    getOptions(),
    showFilteredResultsTest,
    checkUGButton
  );
}

function showFilteredResults() {
  //validateFilters();
  
  //let shinyOrAlphaFilter = distShinyOrAlphaCheckbox.checked;
  let shinyFilter = distShinyCheckbox.checked;
  //let alphaFilter = distAlphaCheckbox.checked;
  let speciesFilter = mmoSpeciesText.value;
  //let defaultFilter = distDefaultCheckbox.checked;
  //let multiFilter = distMultiCheckbox.checked;
  let advanceFilter = advanceText.value;
  let natureFilter = getSelectValues(natureSelect);
  let genderFilter = parseInt(genderSelect.value);

  const filteredResults = results.filter((result) =>
    filter(
      result,
      shinyFilter,
      speciesFilter,
	  advanceFilter,
	  natureFilter,
	  genderFilter
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

  resultContainer.querySelector("[data-pla-results-spawn]").textContent =
	result.spawn;
	
  let resultShiny = resultContainer.querySelector("[data-pla-results-shiny]");
  let sparkle = "";
  let sparklesprite = document.createElement("img");
  sparklesprite.className = "pla-results-sparklesprite";
  sparklesprite.src =
    "data:image/svg+xml;charset=utf8,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%3E%3C/svg%3E";
  sparklesprite.height = "10";
  sparklesprite.width = "10";
  sparklesprite.style.cssText =
    "pull-left;display:inline-block;margin-left:0px;";
	
  if (result.shiny) {
    sparklesprite.src = "static/img/shiny.png";
    sparkle = "Shiny!";
  } else {
    sparkle = "Not Shiny";
  }
  resultContainer
    .querySelector("[data-pla-results-shinysprite]")
    .appendChild(sparklesprite);
  resultShiny.textContent = sparkle;
  resultShiny.classList.toggle("pla-result-true", result.shiny);
  resultShiny.classList.toggle("pla-result-false", !result.shiny);

  resultContainer.querySelector("[data-pla-results-adv]").textContent =
    result.advances;
  resultContainer.querySelector("[data-pla-results-nature]").textContent =
    result.nature;
	
  let gender = 'male';
  if (result.gender == 1){
	  gender = 'female';
  }
  else if (result.gender == 2){
	  gender = 'genderless';
  }
  
  const genderStrings = {
  male: "Male <i class='fa-solid fa-mars' style='color:blue'/>",
  female: "Female <i class='fa-solid fa-venus' style='color:pink'/>",
  genderless: "Genderless <i class='fa-solid fa-genderless'/>",
  };

  resultContainer.querySelector("[data-pla-results-gender]").innerHTML =
    genderStrings[gender];

  resultContainer.querySelector("[data-pla-results-ability]").textContent =
    result.ability;
  resultContainer.querySelector("[data-pla-results-egg]").textContent =
    result.eggmove;
	
  showPokemonIVs(resultContainer, result);
  showPokemonHiddenInformation(resultContainer, result);

  resultsArea.appendChild(resultContainer);
}


function showFilteredResultsTest() {
  /*//validateFilters();
  
  //let shinyOrAlphaFilter = distShinyOrAlphaCheckbox.checked;
  let shinyFilter = distShinyCheckbox.checked;
  //let alphaFilter = distAlphaCheckbox.checked;
  let speciesFilter = mmoSpeciesText.value;
  //let defaultFilter = distDefaultCheckbox.checked;
  //let multiFilter = distMultiCheckbox.checked;
  let advanceFilter = advanceText.value;
  let natureFilter = getSelectValues(natureSelect);
  let genderFilter = parseInt(genderSelect.value);

  const filteredResults = results.filter((result) =>
    filter(
      result,
      shinyFilter,
      speciesFilter,
	  advanceFilter,
	  natureFilter,
	  genderFilter
    )
  );

  console.log("Filtered Results:");
  console.log(filteredResults);*/
  
  const filteredResults = results;
  
  if (filteredResults.length > 0) {
    resultsArea.innerHTML =
      "<section><h3>D = Despawn. Despawn Multiple Pokemon by either Multibattles (for aggressive) or Scaring (for skittish) pokemon.</h3></section>";
    filteredResults.forEach((result) => showResultTest(result));
  } else {
    showNoResultsFound();
  }
}

function showResultTest(results) {
  const wrapperContainer = wrapperTemplate.content.cloneNode(true);
  
  wrapperContainer.querySelector("[data-swsh-results-adv]").textContent =
	results[0].advances;
  
  const check = wrapperContainer.querySelector("[data-inner-results-template]");
  setupExpandables();
  	
  results.forEach((result) => {

	  const resultContainer = check.content.cloneNode(true);

	  
	  let sprite = document.createElement("img");
	  sprite.src = "static/img/spritebig/" + result.sprite;
	  resultContainer.querySelector(".pla-results-sprite").appendChild(sprite);
	  
	  resultContainer.querySelector("[data-pla-results-species]").innerHTML =
		result.species;

	  resultContainer.querySelector("[data-pla-results-spawn]").textContent =
		result.spawn;
		
	  let resultShiny = resultContainer.querySelector("[data-pla-results-shiny]");
	  let sparkle = "";
	  let sparklesprite = document.createElement("img");
	  sparklesprite.className = "pla-results-sparklesprite";
	  sparklesprite.src =
		"data:image/svg+xml;charset=utf8,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%3E%3C/svg%3E";
	  sparklesprite.height = "10";
	  sparklesprite.width = "10";
	  sparklesprite.style.cssText =
		"pull-left;display:inline-block;margin-left:0px;";
		
	  if (result.shiny) {
		sparklesprite.src = "static/img/shiny.png";
		sparkle = "Shiny!";
	  } else {
		sparkle = "Not Shiny";
	  }
	  resultContainer
		.querySelector("[data-pla-results-shinysprite]")
		.appendChild(sparklesprite);
	  resultShiny.textContent = sparkle;
	  resultShiny.classList.toggle("pla-result-true", result.shiny);
	  resultShiny.classList.toggle("pla-result-false", !result.shiny);

	  resultContainer.querySelector("[data-pla-results-adv]").textContent =
		result.advances;
	  resultContainer.querySelector("[data-pla-results-nature]").textContent =
		result.nature;
		
	  let gender = 'male';
	  if (result.gender == 1){
		  gender = 'female';
	  }
	  else if (result.gender == 2){
		  gender = 'genderless';
	  }
	  
	  const genderStrings = {
	  male: "Male <i class='fa-solid fa-mars' style='color:blue'/>",
	  female: "Female <i class='fa-solid fa-venus' style='color:pink'/>",
	  genderless: "Genderless <i class='fa-solid fa-genderless'/>",
	  };

	 const wtf = wrapperContainer.firstElementChild
	 console.log(wtf);
	 const help = wtf.firstElementChild
	 	 console.log("help", help);

	  resultContainer.querySelector("[data-pla-results-gender]").innerHTML =
		genderStrings[gender];

	  resultContainer.querySelector("[data-pla-results-ability]").textContent =
		result.ability;
	  resultContainer.querySelector("[data-pla-results-egg]").textContent =
		result.eggmove;
		
	  showPokemonIVs(resultContainer, result);
	  showPokemonHiddenInformation(resultContainer, result);
	  
	  wrapperContainer.insertBefore(resultContainer, help)
	  //wrapperContainer.append(resultContainer);
	  
  });
  resultsArea.appendChild(wrapperContainer);
  setupExpandables();
}
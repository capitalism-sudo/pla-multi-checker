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
  setivVal,
} from "./modules/common.mjs";

const resultTemplate = document.querySelector("[data-pla-results-template]");
const resultsArea = document.querySelector("[data-pla-results]");

// options
const inputS0 = document.getElementById("inputs0");
const inputS1 = document.getElementById("inputs1");
const inputS2 = document.getElementById("inputs2");
const inputS3 = document.getElementById("inputs3");
const advances = document.getElementById("advances");
const minAdv = document.getElementById("minadvances");
const delay = document.getElementById("delay");
const setIVs = document.getElementById("3iv");
const fixedGender = document.getElementById("fixedgender");

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
const distShinyCheckbox = document.getElementById("mmoShinyFilter");
const natureSelect = document.getElementById("naturefilter");
const genderRatio = document.getElementById("genderratio");
const slotSelect = document.getElementById("slotfilter");

distShinyCheckbox.addEventListener("change", setFilter);
//natureSelect.addEventListener("change", setFilter);
genderRatio.addEventListener("change", setFilter);

// actions
const checkWildButton = document.getElementById("pla-button-checkwild");
checkWildButton.addEventListener("click", checkWild);

loadPreferences();
setupPreferenceSaving();
setupExpandables();
//setupTabs();
setupIVBox();

const results = [];

// Setup tabs

// Save and load user preferences

$(function() {
	$(".chosen-select").chosen({
		no_results_text: "Oops, nothing found!",
		inherit_select_classes: true
	});
	
	$('#naturefilter').chosen().change(setFilter);
	
	$('#slotfilter').chosen().change(setFilter);
});

function loadPreferences() {
  distShinyCheckbox.checked = readBoolFromStorage("mmoShinyFilter", false);
  advances.value = 10000;
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
  
  delay.value = 1;
  
  natureSelect.value = "any";
  slotSelect.value = "any";
  
}

function setupPreferenceSaving() {
  distShinyCheckbox.addEventListener("change", (e) =>
    saveBoolToStorage("mmoShinyFilter", e.target.checked)
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

function setFilter(event) {
  if (event.target.checked) {
  }

  showFilteredResults();
}

function validateFilters() {
}

function filter(
  result,
  shinyFilter,
  natureFilter,
  slotFilter,
) {

  
  if (shinyFilter && !result.shiny) {
    return false;
  }

  /*if (
    speciesFilter.length != 0 &&
    !result.species.toLowerCase().includes(speciesFilter.toLowerCase())
  ) {
    return false;
  }*/
  
	if (
		!natureFilter.includes("any") &&
		!natureFilter.includes(result.nature.toLowerCase())
		) {
			return false;
		}

	if (
		!slotFilter.includes("any") &&
		!slotFilter.includes(result.slot.toString())
		) {
			return false;
		}
  
  /*if (
	advanceFilter.length != 0 &&
	result.advances != parseInt(advanceFilter)
  ) {
	  return false;
  }*/

  return true;
}

function getSelectValues(select) {
	var res = []
	var options = select && select.options;
	var opt;
	
	for (var i=0, iLen=options.length; i<iLen; i++) {
		opt = options[i];
		
		if (opt.selected) {
			res.push(opt.value || opt.text);
		}
	}
	
	return res;
}

function getOptions() {
  return {
    s0: inputS0.value,
	s1: inputS1.value,
	s2: inputS2.value,
	s3: inputS3.value,
	fixed_ivs: setIVs.checked,
	set_gender: fixedGender.checked,
	filter: {
		maxadv: parseInt(advances.value),
		minadv: parseInt(minAdv.value),
		minivs: [minHP.value, minATK.value, minDEF.value, minSPA.value, minSPD.value, minSPE.value],
		maxivs: [maxHP.value, maxATK.value, maxDEF.value, maxSPA.value, maxSPD.value, maxSPE.value],
	},
	species: 0,
	command: distSelectFilter.value,
	delay: parseInt(delay.value),
  };
}

function checkWild() {
  doSearch(
    "/api/check-bdsp-wild",
    results,
    getOptions(),
    showFilteredResults,
    checkWildButton
  );
}

function showFilteredResults() {
  //validateFilters();
  
  let shinyFilter = distShinyCheckbox.checked;
  let natureFilter = getSelectValues(natureSelect);
  let slotFilter = getSelectValues(slotSelect);
  
  console.log(slotFilter);

  const filteredResults = results.filter((result) =>
    filter(
      result,
      shinyFilter,
      natureFilter,
	  slotFilter
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
	
  if (result.shiny && result.square) {
	sparklesprite.src = "static/img/square.png";
	sparkle = "Square Shiny!";
  }
  else if (result.shiny) {
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
  
  let totalAdvance = result.adv;

  resultContainer.querySelector("[data-pla-results-adv]").textContent =
    totalAdvance;
  resultContainer.querySelector("[data-pla-results-slot]").textContent =
	result.slot;
  resultContainer.querySelector("[data-pla-results-nature]").textContent =
    result.nature;
	
  let gender = 'male';
  
  if (
	fixedGender.checked &&
	result.gender == -1
	){
		if (parseInt(genderRatio.value) == 0){
			gender = 'male';
		}
		else if (parseInt(genderRatio.value) == 254){
			gender = 'female';
		}
		else {
			gender = 'genderless';
		}
	}
  else if (
	result.gender < parseInt(genderRatio.value)
	){
		gender = 'female';
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
	
  showPokemonIVs(resultContainer, result);
  showPokemonHiddenInformation(resultContainer, result);

  resultsArea.appendChild(resultContainer);
}

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
  getSelectValues,
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
const mMethod = document.getElementById("masuda");
const shinyCharm = document.getElementById("shinycharm");
const ovalCharm = document.getElementById("ovalcharm");
const TID = document.getElementById("tid");
const SID = document.getElementById("sid");

//Parent Options

const compatibility = document.getElementById("compat");
const aNature = document.getElementById("a_nature");
const bNature = document.getElementById("b_nature");
const aDitto = document.getElementById("a_ditto");
const bDitto = document.getElementById("b_ditto");
const aItem = document.getElementById("a_item");
const bItem = document.getElementById("b_item");
const genderRatio = document.getElementById("genderratio");

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

const a_HP = document.getElementById("a_hp");
const a_ATK = document.getElementById("a_atk");
const a_DEF = document.getElementById("a_def");
const a_SPA = document.getElementById("a_spa");
const a_SPD = document.getElementById("a_spd");
const a_SPE = document.getElementById("a_spe");

const b_HP = document.getElementById("b_hp");
const b_ATK = document.getElementById("b_atk");
const b_DEF = document.getElementById("b_def");
const b_SPA = document.getElementById("b_spa");
const b_SPD = document.getElementById("b_spd");
const b_SPE = document.getElementById("b_spe");

// filters
const distSelectFilter = document.getElementById("selectfilter");
const distShinyCheckbox = document.getElementById("mmoShinyFilter");
const natureSelect = document.getElementById("naturefilter");
//const genderRatio = document.getElementById("genderratio");

distShinyCheckbox.addEventListener("change", setFilter);
natureSelect.addEventListener("change", setFilter);
//genderRatio.addEventListener("change", setFilter);

// actions
const checkEggButton = document.getElementById("pla-button-checkegg");
checkEggButton.addEventListener("click", checkEgg);

loadPreferences();
setupPreferenceSaving();
setupExpandables();
setupTabs();
setupIVBox();
document.getElementById("defaultOpen").click();


const results = [];

// Setup tabs

$(function() {
	$(".chosen-select").chosen({
		no_results_text: "Oops, nothing found!",
		inherit_select_classes: true
	});
	
	$(".chosen-select-single").chosen({
		width: "75%",
		inherit_select_classes: true
	});
	
	$('#naturefilter').chosen().change(setFilter);
	
	$('#slotfilter').chosen().change(setFilter);
});

// Save and load user preferences
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
  
  delay.value = 0;
  
  natureSelect.value = "any";
  
}

function setupPreferenceSaving() {
  distShinyCheckbox.addEventListener("change", (e) =>
    saveBoolToStorage("mmoShinyFilter", e.target.checked)
  );
}

function setupTabs() {
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
}

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
  
  /*if (
	advanceFilter.length != 0 &&
	result.advances != parseInt(advanceFilter)
  ) {
	  return false;
  }*/

  return true;
}

function getOptions() {
  return {
    s0: inputS0.value,
	s1: inputS1.value,
	s2: inputS2.value,
	s3: inputS3.value,
	filter: {
		maxadv: parseInt(advances.value),
		minadv: parseInt(minAdv.value),
		minivs: [minHP.value, minATK.value, minDEF.value, minSPA.value, minSPD.value, minSPE.value],
		maxivs: [maxHP.value, maxATK.value, maxDEF.value, maxSPA.value, maxSPD.value, maxSPE.value],
	},
	daycare: {
		oval_charm: ovalCharm.checked,
		shiny_charm: shinyCharm.checked,
		tid: parseInt(TID.value),
		sid: parseInt(SID.value),
		compatibility: parseInt(compatibility.value),
		a_ivs: [parseInt(a_HP.value), parseInt(a_ATK.value), parseInt(a_DEF.value), parseInt(a_SPA.value), parseInt(a_SPD.value), parseInt(a_SPE.value)],
		b_ivs: [parseInt(b_HP.value), parseInt(b_ATK.value), parseInt(b_DEF.value), parseInt(b_SPA.value), parseInt(b_SPD.value), parseInt(b_SPE.value)],
		a_item: parseInt(aItem.value),
		b_item: parseInt(bItem.value),
		masuda: mMethod.checked,
		nido_volbeat: false,
		a_nature: aNature.value,
		b_nature: bNature.value,
		a_ability: 0,
		b_ability: 1,
		a_ditto: aDitto.checked,
		b_ditto: bDitto.checked,
		gender_ratio: parseInt(genderRatio.value),
	},
	species: 0,
	command: distSelectFilter.value,
	delay: parseInt(delay.value),
  };
}

function checkEgg() {
  doSearch(
    "/api/check-bdsp-egg",
    results,
    getOptions(),
    showFilteredResults,
    checkEggButton
  );
}

function showFilteredResults() {
  //validateFilters();
  
  let shinyFilter = distShinyCheckbox.checked;
  let natureFilter = getSelectValues(natureSelect);

  const filteredResults = results.filter((result) =>
    filter(
      result,
      shinyFilter,
      natureFilter
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
  resultContainer.querySelector("[data-pla-results-eseed]").textContent =
    result.seed.toString(16).toUpperCase();
  resultContainer.querySelector("[data-pla-results-nature]").textContent =
    result.nature;
	
  let gender = 'male';
  
  if (result.gender == 2) {
	  gender = 'genderless';
  }
  else if (result.gender == 1) {
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

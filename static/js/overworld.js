import {
  doSearchSWSH,
  DEFAULT_MAP,
  MESSAGE_ERROR,
  MESSAGE_INFO,
  showMessage,
  showModalMessage,
  clearMessages,
  clearModalMessages,
  doSearch,
  showNoResultsFoundSWSH,
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
const resultsArea = document.querySelector("[data-swsh-results]");

// options
const seed0 = document.getElementById("inputseed0");
const seed1 = document.getElementById("inputseed1");
const trainerID = document.getElementById("tid");
const secretID = document.getElementById("sid");
const minAdv = document.getElementById("initadv");
const maxAdv = document.getElementById("finaladv");
const shinyCharm = document.getElementById("shiny_charm");
const markCharm = document.getElementById("mark_charm");
const cuteCharm = document.getElementById("cute_charm");

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

//filters

const brillFilter = document.getElementById("brillfilter");
const shinyFilter = document.getElementById("shinyfilter");
const natureSelect = document.getElementById("naturefilter");
const genderSelect = document.getElementById("genderfilter");
const markSelect = document.getElementById("markfilter");


//pokemon parsing
const gameVer = document.getElementById("version");
const encType = document.getElementById("type");
const encLoc = document.getElementById("location");
const encWeather = document.getElementById("weather");
const encSpecies = document.getElementById("species");
const weatherActive = document.getElementById("weatheractive");
const KOs = document.getElementById("kos");
const minSlot = document.getElementById("minslot");
const maxSlot = document.getElementById("maxslot");
const minLevel = document.getElementById("minlevel");
const maxLevel = document.getElementById("maxlevel");
const emCount = document.getElementById("emcount");
const heldItem = document.getElementById("helditem");
const flawlessIVs = document.getElementById("flawlessivs");
const shinyLock = document.getElementById("shinylock");
const setGender = document.getElementById("setgender");


encType.addEventListener("change", populateLocation);
encLoc.addEventListener("change", populateWeather);
encWeather.addEventListener("change", populateSpecies);
encSpecies.addEventListener("change", populateOptions);

//seedfinder options
const motionsUpdate = document.getElementById("seedupdate");
const startingAdvance = document.getElementById("startingadvance");
const maxAdvance = document.getElementById("maxadvance");


const addMotion0Button = document.getElementById("addmotion0");
addMotion0Button.addEventListener("click", addMotionPhys);
const addMotion1Button = document.getElementById("addmotion1");
addMotion1Button.addEventListener("click", addMotionSpec);

const motions = document.getElementById("motions");
motions.addEventListener("change", updateCount);
motions.addEventListener("keyup", updateCount);

const findSeed = document.getElementById("findseed");
findSeed.addEventListener("click", findSWSHSeed);

const updateSeed = document.getElementById("updateseed");
updateSeed.addEventListener("click", UpdateSeed);

const updateState = document.getElementById("updatesidebarstate");
updateState.addEventListener("click", UpdateSidebar);

const updateInit = document.getElementById("updatewithstate");
updateInit.addEventListener("click", UpdateState);

const checkOwButton = document.getElementById("swsh-button-checkow");
checkOwButton.addEventListener("click", checkOverworld);

natureSelect.addEventListener("change", setFilter);
genderSelect.addEventListener("change", setFilter);

loadPreferences();
setupPreferenceSaving();
setupExpandables();
setupTabs();
setupTabsRes();
populateLocation();
setupIVBox();
document.getElementById("defaultOpen").click();
document.getElementById("defaultresOpen").click();

const results = [];
var staticenc = false;
var fishing = false;
var Hidden = false;
const personalityMarks = ["Rowdy","AbsentMinded","Jittery","Excited","Charismatic","Calmness","Intense","ZonedOut","Joyful","Angry","Smiley","Teary","Upbeat","Peeved","Intellectual","Ferocious","Crafty","Scowling","Kindly","Flustered","PumpedUp","ZeroEnergy","Prideful","Unsure","Humble","Thorny","Vigor","Slump"]

$(function() {
	$(".chosen-select").chosen({
		no_results_text: "Oops, nothing found!",
		inherit_select_classes: true
	});
	
	$('#naturefilter').chosen().change(setFilter);
	
	$('#slotfilter').chosen().change(setFilter);
	
	$('#markfilter').chosen().change(setFilter);
});

// Save and load user preferences
function loadPreferences() {
	minAdv.value = 0;
	maxAdv.value = 10000;
	KOs.value = 0;
	minSlot.value = 0;
	maxSlot.value = 99;
	minLevel.value = 1;
	maxLevel.value = 99;
	flawlessIVs.value = 0;
	emCount.value = 0;
	
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
  
  shinyCharm.checked = readBoolFromStorage("shiny_charm", false);
  markCharm.checked = readBoolFromStorage("mark_charm", false);
  gameVer.value = localStorage.getItem("version") ?? "Sword";
  trainerID.value = localStorage.getItem("tid") ?? 0;
  secretID.value = localStorage.getItem("sid") ?? 0;
  natureSelect.value = "any";
  genderSelect.value = 50;
  markSelect.value = "any";
  
  shinyFilter.value = localStorage.getItem("shinyfilter") ?? "None";
}

function setupPreferenceSaving() {
	shinyCharm.addEventListener("change", (e) =>
    saveBoolToStorage("shiny_charm", e.target.checked)
  );
  markCharm.addEventListener("change", (e) =>
    saveBoolToStorage("mark_charm", e.target.checked)
  );
  gameVer.addEventListener("change", (e) =>
    localStorage.setItem("version", e.target.value)
  );
  trainerID.addEventListener("change", (e) =>
    localStorage.setItem("tid", e.target.value)
  );
  secretID.addEventListener("change", (e) =>
	localStorage.setItem("sid", e.target.value)
  );
  shinyFilter.addEventListener("change", (e) =>
	localStorage.setItem("shinyfilter", e.target.value)
  );
}

function setupTabs() {
  document.querySelectorAll(".tablinks").forEach((element) => {
    element.addEventListener("click", (event) =>
      openTab(event, element.dataset.swshTabFor)
    );
  });
}

function setupTabsRes() {
  document.querySelectorAll(".reslinks").forEach((element) => {
    element.addEventListener("click", (event) =>
      openTabRes(event, element.dataset.plaTabFor)
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

function openTabRes(evt, tabName) {
  let i, tabcontent, tablinks;

  tabcontent = document.getElementsByClassName("tabcontentres");
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }

  tablinks = document.getElementsByClassName("reslinks");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].className = tablinks[i].className.replace(" active", "");
  }

  document.getElementById(tabName).style.display = "block";
  evt.currentTarget.className += " active";
}

function stringToBits(string) {
	let bits = [];
	let i = 0;
	for (i=0; i < string.length; i++) {
		bits.push(parseInt(string[i]));
	}
	return bits;
}

function setFilter(event) {
  showFilteredResults();
}

function filter(
  result,
  natureFilter,
  genderFilter,
  markFilter
) {
	
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
		parseInt(genderFilter) == 0 &&
		!(result.gender == 0)
		){
			console.log("Gender Result not male, male filter selected");
		return false;
		}
		else if ( parseInt(genderFilter) == 1 && !(result.gender == 1)) {
			console.log("Gender Result not female, female filter selected");
			return false;
		}
	}
		
	if (markFilter.includes("AnyMark")){
		personalityMarks.forEach((mark) => {
			markFilter.push(mark);
		});
		markFilter.push("Weather");
		markFilter.push("Time");
		markFilter.push("Uncommon");
		markFilter.push("Rare");
		markFilter.push("Fishing");
	}
	else if (markFilter.includes("AnyPersonality")){
		personalityMarks.forEach((mark) => {
			markFilter.push(mark);
		});
	}
	
	console.log("Filtering: Markfilter:", markFilter);
	if (
		!markFilter.includes("any") &&
		!markFilter.includes(result.mark)
		) {
			return false;
		}

  return true;
}

function addMotionPhys() {
	addMotion("0");
}

function addMotionSpec() {
	addMotion("1");
}

function addMotion(val) {
	if (document.getElementById("motions").value.length < 128) {
		document.getElementById("motions").value += val;
		updateCount();
	}
}

function updateCount() {
	document.getElementById("count").innerText = ("000"+document.getElementById("motions").value.length.toString(10)).slice(-3);
}

function UpdateSidebar() {
	
	document.getElementById("inputseed0").value = document.querySelector("[data-updated-s0]").innerText;
	document.getElementById("inputseed1").value = document.querySelector("[data-updated-s1]").innerText;
	
}

function UpdateState() {
	
	document.getElementById("inputseed0").value = document.getElementById("data-s0").value;
	document.getElementById("inputseed1").value = document.getElementById("data-s1").value;
	
}

function getOptions() {
  return {
    s0: seed0.value,
    s1: seed1.value,
	initadv: parseInt(minAdv.value),
	maxadv: parseInt(maxAdv.value),
	options: {
		tid: trainerID.value,
		sid: secretID.value,
		shiny_charm: shinyCharm.checked,
		mark_charm: markCharm.checked,
		weather_active: weatherActive.checked,
		is_fishing: fishing,
		is_static: staticenc,
		is_shiny_locked: shinyLock.checked,
		flawless_ivs: flawlessIVs.value,
		forced_ability: 0,
		diff_held_item: heldItem.checked,
		egg_move_count: emCount.value,
		min_level: minLevel.value,
		max_level: maxLevel.value,
		kos: KOs.value,
		cute_charm: cuteCharm.value,
		set_gender: false,
		is_hidden: Hidden,
	},
    filter: {
		slot_min: parseInt(minSlot.value),
		slot_max: parseInt(maxSlot.value),
		shiny_filter: shinyFilter.value,
		brilliant: brillFilter.checked,
		minivs: [parseInt(minHP.value), parseInt(minATK.value), parseInt(minDEF.value), parseInt(minSPA.value), parseInt(minSPD.value), parseInt(minSPE.value)],
		maxivs: [parseInt(maxHP.value), parseInt(maxATK.value), parseInt(maxDEF.value), parseInt(maxSPA.value), parseInt(maxSPD.value), parseInt(maxSPE.value)],
    },
	info: {
		version: gameVer.value,
		type: encType.value,
		loc: encLoc.value,
		weather: encWeather.value,
		species: encSpecies.value,
	}
  };
}

function getSeedOptions() {
	return {
		motions: stringToBits(motions.value),
	};
}

function getSeedUpdateOptions() {
	return {
		s0: document.getElementById("data-s0").value,
		s1: document.getElementById("data-s1").value,
		motions: motionsUpdate.value,
		min: parseInt(startingAdvance.value),
		max: parseInt(maxAdvance.value),
	};
}

function populateLocation() {
	
	var options = { type: encType.value, version: gameVer.value }
	fetch("/api/pop-location", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(options),
  })
    .then((response) => response.json())
    .then((res) => {
		console.log(res)
		var html_code = '';
		var weather_code = '<option value="">Select Weather</option>';
		var species_code = '<option value="">Select Species</option>';
		html_code += '<option value="">Select Location:</option>';
		res.results.forEach((loc) => {
			html_code += '<option value="' + loc + '">' + loc + '</option>';
		});
		encLoc.innerHTML = html_code;
		encWeather.innerHTML = weather_code;
		encSpecies.innerHTML = species_code;
		
		if (encType.value == "Static"){
			staticenc = true;
			Hidden = false;
		}
		else if (encType.value == "Hidden"){
			Hidden = true;
			staticenc = false;
		}
		else {
			Hidden = false;
			staticenc = false;
		}
	})
}

function populateWeather() {
	var options = { type: encType.value, loc: encLoc.value, version: gameVer.value }
	fetch("/api/pop-weather", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(options),
  })
    .then((response) => response.json())
    .then((res) => {
		var html_code = '';
		var species_code = '<option value="">Select Species</option>';
		html_code += '<option value="">Select Weather:</option>';
		res.results.forEach((wea) => {
			html_code += '<option value="' + wea + '">' + wea + '</option>';
		});
		encWeather.innerHTML = html_code;
		encSpecies.innerHTML = species_code;
		
	})
}

function populateSpecies() {
	var options = { type: encType.value, loc: encLoc.value, weather: encWeather.value, version: gameVer.value }
	fetch("/api/pop-species", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(options),
  })
    .then((response) => response.json())
    .then((res) => {
		var html_code = '';
		html_code += '<option value="">Select Species:</option>';
		res.results.forEach((loc) => {
			html_code += '<option value="' + loc + '">' + loc + '</option>';
		});
		encSpecies.innerHTML = html_code;
		
		if (!["Any Weather","Fishing","Shaking Trees"].includes(encWeather.value)){
			weatherActive.checked = true;
		}
		
		if (["Normal Weather", "Normal"].includes(encWeather.value)){
			weatherActive.checked = false;
		}
		
		if (encWeather.value == "Fishing"){
			fishing = true;
		}
		else {
			fishing = false;
		}
	})
}


function populateOptions() {
	var options = { type: encType.value, loc: encLoc.value, weather: encWeather.value, version: gameVer.value, species: encSpecies.value }
	fetch("/api/pop-options", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(options),
  })
    .then((response) => response.json())
    .then((res) => {
		console.log(res);
		minSlot.value = res.results.minslot;
		maxSlot.value = res.results.maxslot;
		minLevel.value = res.results.minlevel;
		maxLevel.value = res.results.maxlevel;
		emCount.value = res.results.eggmove;
		heldItem.checked = res.results.helditem;
		flawlessIVs.value = res.results.ivs;
		shinyLock.checked = res.results.shinylock;
	})
}

function checkOverworld() {
  doSearchSWSH("/api/check-overworld", results, getOptions(), showFilteredResults, checkOwButton);
}

function findSWSHSeed() {
	
	const options = getSeedOptions();
	
	fetch("/api/find-swsh-seed", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(options),
  })
    .then((response) => response.json())
    .then((res) => showSeedInfo(res))
}

function UpdateSeed() {
	
	const options = getSeedUpdateOptions();
	
	fetch("/api/update-swsh-seed", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(options),
  })
    .then((response) => response.json())
    .then((res) => showSeedUpdateInfo(res))
    .catch((error) => {});
}

function showFilteredResults() {
  let natureFilter = getSelectValues(natureSelect);
  let genderfilter = genderSelect.value;
  let markFilter = getSelectValues(markSelect);
  
  console.log("NatureFilter:", natureFilter);
  console.log("MarkFilter:", markFilter);

  const filteredResults = results.filter((result) =>
    filter(
      result,
      natureFilter,
	  genderfilter,
	  markFilter
    )
  );

  console.log("Filtered Results:");
  console.log(filteredResults);
  
  if (filteredResults.length > 0) {
    resultsArea.innerHTML =
      "<section><h3>D = Despawn. Despawn Multiple Pokemon by either Multibattles (for aggressive) or Scaring (for skittish) pokemon.</h3></section>";
    filteredResults.forEach((result) => showResult(result));
  } else {
    showNoResultsFoundSWSH();
  }
}


function showResult(result) {
  const resultContainer = resultTemplate.content.cloneNode(true);
  
  let sprite = document.createElement("img");
  sprite.src = "static/img/spritebig/" + result.sprite;
  resultContainer.querySelector(".pla-results-sprite").appendChild(sprite);
  
  resultContainer.querySelector("[data-pla-results-species]").innerHTML =
    result.species;
	
  resultContainer.querySelector("[data-pla-results-mark]").textContent =
	result.mark;

  let brilliant = "";
  if(result.brilliant){
	  brilliant = "Brilliant!"
  }
  else{
	  brilliant = "Not Brilliant";
  }
  let resultBrilliant = resultContainer.querySelector("[data-pla-results-brill]");
  
  resultBrilliant.textContent = brilliant;
  resultBrilliant.classList.toggle("pla-result-true", result.brilliant);
  resultBrilliant.classList.toggle("pla-result-false", !result.brilliant);
	
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
	
  if (result.square) {
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


function showSeedInfo(result) {
	
	console.log(result);
	console.log(result.results.s0);
	console.log(result.results.s1);
	console.log(result.results.s0.toUpperCase());
	
	//document.getElementById("s0").innerText = result.s0.toUpperCase();
	//document.getElementById("s1").innerText = result.s1.toUpperCase();
	
	document.getElementById("data-s0").value =
	result.results.s0;
	document.getElementById("data-s1").value =
	result.results.s1;

}

function showSeedUpdateInfo(result) {
	
	console.log(result);
	
	document.querySelector("[data-seed-count]").innerText =
	 result.results.count;
	document.querySelector("[data-seed-adv]").innerText =
	 result.results.adv;
	document.querySelector("[data-updated-s0]").innerText =
	 result.results.s0.toUpperCase();
	document.querySelector("[data-updated-s1]").innerText =
	 result.results.s1.toUpperCase();
}
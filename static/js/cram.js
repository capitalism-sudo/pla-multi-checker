import {
  doSearchSWSH,
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

const resultTemplate = document.querySelector("[data-swsh-results-cram-template]");
const resultsArea = document.querySelector("[data-swsh-results]");
const resultTemplateLotto = document.querySelector("[data-swsh-results-lotto-template]");

// options
const seed0 = document.getElementById("inputseed0");
const seed1 = document.getElementById("inputseed1");
const npcCount = document.getElementById("npccount");
const distSportorSafari = document.getElementById("sportorsafari");
const distBonusCount = document.getElementById("bonuscount");
const trainerID = document.getElementById("tid");
const motionsUpdate = document.getElementById("seedupdate");
const startingAdvance = document.getElementById("startingadvance");
const maxAdvance = document.getElementById("maxadvance");


const checkCramButton = document.getElementById("swsh-button-checkcram");
checkCramButton.addEventListener("click", checkCram);
const checkLottery = document.getElementById("swsh-button-checklotto");
checkLottery.addEventListener("click", checkLotto);

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

loadPreferences();
setupPreferenceSaving();
setupExpandables();
setupTabs();
setupTabsRes();
document.getElementById("defaultOpen").click();
document.getElementById("defaultresOpen").click();

const results = [];

// Save and load user preferences
function loadPreferences() {
}

function setupPreferenceSaving() {

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
	npc_count: parseInt(npcCount.value),
	ids: trainerID.value,
    filter: {
		isSafariSport: distSportorSafari.checked,
		isBonusCount: distBonusCount.checked,
    },
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

function checkCram() {
  doSearchSWSH("/api/check-cramomatic", results, getOptions(), showFilteredResults, checkCramButton);
}

function checkLotto() {
	doSearchSWSH("/api/check-lotto", results, getOptions(), showFilteredResultsLotto, checkLottery);
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
    .catch((error) => {});
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
  if (results.length > 0) {
    resultsArea.innerHTML = "";
    results.forEach((result) => showResult(result));
  } else {
    showNoResultsFound();
  }
}

function showFilteredResultsLotto() {
  if (results.length > 0) {
    resultsArea.innerHTML = "";
    results.forEach((result) => showResultLotto(result));
  } else {
    showNoResultsFound();
  }
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
	
function showResult(result) {
  const resultContainer = resultTemplate.content.cloneNode(true);

  resultContainer.querySelector("[data-swsh-results-adv]").innerText =
    result.adv;
  resultContainer.querySelector("[data-swsh-results-issportsafari]").innerText =
    result.sportsafari;
  resultContainer.querySelector("[data-swsh-results-isbonuscount]").innerText =
    result.bonus;
  resultContainer.querySelector("[data-swsh-results-menuadv]").innerText =
    result.menu_adv;

  resultsArea.appendChild(resultContainer);
}

function showResultLotto(result) {
  const resultContainer = resultTemplateLotto.content.cloneNode(true);

  resultContainer.querySelector("[data-swsh-results-adv]").innerText =
    result.adv;
  resultContainer.querySelector("[data-swsh-results-menuadv]").innerText =
    result.menu_adv;
  resultContainer.querySelector("[data-swsh-results-lotto]").innerText =
    result.lotto;

  resultsArea.appendChild(resultContainer);
}
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

import {
	Xorshift
} from "./xorshift.js";

const resultTemplate = document.querySelector("[data-pla-results-template]");
const resultsArea = document.querySelector("[data-pla-results]");

// options
const inputS0 = document.getElementById("inputs0");
const inputS1 = document.getElementById("inputs1");
const inputS2 = document.getElementById("inputs2");
const inputS3 = document.getElementById("inputs3");
const advances = document.getElementById("advances");
const minAdv = document.getElementById("minadvances");
const tidFilter = document.getElementById("tidfilter");

//timer options
const timeS0 = document.getElementById("time-s0");
const timeS1 = document.getElementById("time-s1");
const timeStamp = document.getElementById("ts");
const tarAdv = document.getElementById("tadv");
const timeAdv = document.getElementById("time-adv");
const currTime = document.getElementById("time-curr");
const tuNA = document.getElementById("tuna");
const tuTA = document.getElementById("tuta");

// actions
const checkTidButton = document.getElementById("pla-button-checktid");
checkTidButton.addEventListener("click", checkTid);
const checkTimeButton = document.getElementById("pla-button-starttime");
checkTimeButton.addEventListener("click", generate);
tarAdv.addEventListener("change", updateTarget);


loadPreferences();
setupPreferenceSaving();
setupExpandables();
setupTabs();
document.getElementById("defaultOpen").click();

const results = [];

// Setup tabs

// Save and load user preferences
function loadPreferences() {
  advances.value = 1000;
  minAdv.value = 0;
}

function setupPreferenceSaving() {
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


let t0,t1,interval,rng,ts,tts,curr,timeAdvances

function updateCurrent() {
	curr = Date.now()/1000;
	
	while (curr >= ts) {
		ts += rng.rangeF(100,370)/30 - 0.048;
		timeAdvances += 1;
	}
	timeAdv.innerText = timeAdvances;
	currTime.innerText = Math.round(curr*100)/100;
	tuNA.innerText = Math.round((ts-curr)*100)/100;
	tuTA.innerText = Math.round((tts-curr)*100)/100;
}

function updateTarget() {
	
	tts = parseFloat(timeStamp.value);
	let target = parseInt(tarAdv.value);
	let trng = new Xorshift(t0 >> 32n, t0 & 0xFFFFFFFFn, t1 >> 32n, t1 & 0xFFFFFFFFn);
	for (let i = 1; i < target; i++) {
		tts += trng.rangeF(100,370)/30 - 0.048;
	}
}

function generate() {
	if (interval) {
		clearInterval(interval);
	}
	
	t0 = BigInt('0x'+timeS0.value);
	t1 = BigInt('0x'+timeS1.value);
	rng = new Xorshift(t0 >> 32n, t0 & 0xFFFFFFFFn, t1 >> 32n, t1 & 0xFFFFFFFFn);
	ts = parseFloat(timeStamp.value);
	timeAdvances = 0;
	updateTarget();
	interval = setInterval(updateCurrent,100);
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
) {

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
		tid: false,
		sid: false,
		g8tid: true,
	},
	ids: tidFilter.value,
  };
}

function checkTid() {
  doSearch(
    "/api/check-bdsp-tid",
    results,
    getOptions(),
    showFilteredResults,
    checkTidButton
  );
}

function showFilteredResults() {
  //validateFilters();
  
  const filteredResults = results.filter((result) =>
    filter(
      result,
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
  
  let totalAdvance = result.adv;

  resultContainer.querySelector("[data-pla-results-adv]").textContent =
    totalAdvance;

  resultContainer.querySelector("[data-pla-results-tid]").textContent =
	result.tid;
	
  resultContainer.querySelector("[data-pla-results-sid]").textContent =
	result.sid;
	
  resultContainer.querySelector("[data-pla-results-g8tid]").textContent =
	result.g8tid;
	
  resultContainer.querySelector("[data-pla-results-tsv]").textContent =
	result.tsv;

  resultsArea.appendChild(resultContainer);
}

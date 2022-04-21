const resultTemplate = document.querySelector("[data-pla-results-template]");
const resultsArea = document.querySelector("[data-pla-results]");
const mapLocationsArea = document.querySelector("[data-pla-info-locations]");
const mapSpawnsArea = document.querySelector("[data-pla-info-spawns]");
const spinnerTemplate = document.querySelector("[data-pla-spinner]");

const resultsSection = document.querySelector(".pla-section-results");
const resultsSprite = document.querySelector(".pla-results-sprite");

const teleportButton = document.querySelector(".pla-results-teleport");

// options
const inputSeed = document.getElementById("inputseed");
const maxDepth = document.getElementById("maxDepth");
const rollsInput = document.getElementById("rolls");
const inmapCheck = document.getElementById("inmapcheck");
const maxAlive = document.getElementById("maxAlive");
const groupID = document.getElementById("groupID");

// filters
const distShinyOrAlphaCheckbox = document.getElementById(
  "mmoShinyOrAlphaFilter"
);
const distShinyCheckbox = document.getElementById("mmoShinyFilter");
const distAlphaCheckbox = document.getElementById("mmoAlphaFilter");
const mmoSpeciesText = document.getElementById("mmoSpeciesFilter");
const distDefaultCheckbox = document.getElementById("mmoDefaultRouteFilter");
const distMultiCheckbox = document.getElementById("mmoMultiFilter");

distShinyOrAlphaCheckbox.onchange = setFilter;
distShinyCheckbox.onchange = setFilter;
distAlphaCheckbox.onchange = setFilter;
mmoSpeciesText.oninput = setFilter;

loadPreferences();
setupPreferenceSaving();
document.getElementById("defaultOpen").click()

const results = [];

// Save and load user preferences
function loadPreferences() {
  maxDepth.value = localStorage.getItem("maxDepth") ?? "0";
  rollsInput.value = readIntFromStorage("rolls", 1);
  distAlphaCheckbox.checked = readBoolFromStorage(
    "mmoAlphaFilter",
    false
  );
  distShinyCheckbox.checked = readBoolFromStorage(
    "mmoShinyFilter",
    false
  );
  distShinyOrAlphaCheckbox.checked = readBoolFromStorage(
    "mmoShinyOrAlphaFilter",
    false
  );
  validateFilters();
}

function setupPreferenceSaving() {
  maxDepth.addEventListener("change", (e) =>
    localStorage.setItem("maxDepth", e.target.value)
  );
  rollsInput.addEventListener("change", (e) =>
    saveIntToStorage("rolls", e.target.value)
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

function updatevalue() {
	console.log(mmoSpeciesText.value);
	setFilter;
}

function saveIntToStorage(id, value) {
  localStorage.setItem(id, value);
}

function readIntFromStorage(id, defaultValue) {
  value = localStorage.getItem(id);
  return value ? parseInt(value) : defaultValue;
}

function saveBoolToStorage(id, value) {
  localStorage.setItem(id, value ? 1 : 0);
}

function readBoolFromStorage(id, defaultValue) {
  value = localStorage.getItem(id);
  return value ? parseInt(value) == 1 : defaultValue;
}

function openTab(evt, tabName) {
	var i, tabcontent, tablinks;
	
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

function filter(result, shinyOrAlphaFilter, shinyFilter, alphaFilter, SpeciesFilter) {
  if (shinyOrAlphaFilter && !(result.shiny || result.alpha)) {
    return false;
  }

  if (shinyFilter && !result.shiny) {
    return false;
  }

  if (alphaFilter && !result.alpha) {
    return false;
  }
  
  
  if (SpeciesFilter.value.length != 0 && !result.species.toLowerCase().includes(SpeciesFilter.value.toLowerCase())){
	  return false;
  }
  

  return true;
}

function getOptions() {
  return {
	seed: inputSeed.value,
	maxdepth: parseInt(maxDepth.value),
    rolls: parseInt(rollsInput.value),
	group_id: parseInt(groupID.value),
	maxalive: parseInt(maxAlive.value)
//	inmap: inmapCheck.checked
  };
}

function checkmultiseed() {
  const options = getOptions();
  showFetchingResults();

  fetch("/check-multi-seed", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(options),
  })
    .then((response) => response.json())
    .then((res) => showResults(res))
    .catch((error) => showError(error));
}


function showFetchingResults() {
  results.length = 0;
  resultsArea.innerHTML = "";
  const spinner = spinnerTemplate.content.cloneNode(true);
  resultsArea.appendChild(spinner);
  resultsSection.classList.toggle("pla-loading", true);
}


const showResults = ({ multi_spawns }) => {
  for (const [key, value] of Object.entries(multi_spawns)) {
	  if(value.spawn) {
				  results.push(value);
	  }
  };
  showFilteredResults();
};


const showFilteredResults = () => {
  validateFilters();

  let shinyOrAlphaFilter = distShinyOrAlphaCheckbox.checked;
  let shinyFilter = distShinyCheckbox.checked;
  let alphaFilter = distAlphaCheckbox.checked;
  let SpeciesFilter = mmoSpeciesFilter;

  resultsArea.innerHTML = "";
  resultsSection.classList.toggle("pla-loading", false);

  filteredResults = results.filter(
    (result) =>
      result.spawn &&
      filter(result, shinyOrAlphaFilter, shinyFilter, alphaFilter, SpeciesFilter)
  );

  if (filteredResults.length > 0) {
	  resultsArea.innerHTML = "<h3><section class='pla-section-results' flow>D = Despawn. Despawn Multiple Pokemon by either Multibattles (for aggressive) or Scaring (for skittish) pokemon.</section></h3>";
    filteredResults.forEach((result) => {
	 
	  let sprite = document.createElement('img');
	  sprite.src = "static/img/sprite/"+result.sprite;
	  
	  let pathdisplay = "Path To Target: &nbsp;";
	  console.log(result.path);
	  if (result.path.toString().includes("Initial")) {
		  pathdisplay += "<input type='checkbox'>&nbsp;"+result.path;
	  }
	  else{
	  Array.from(result.path).forEach((step) => {
		  pathdisplay += "<input type='checkbox'>&nbsp;D"+ step +"</input> &emsp;";
	  });
	  }
	  
      const resultContainer = resultTemplate.content.cloneNode(true);
	  resultContainer.querySelector('.pla-results-sprite').appendChild(sprite);
      resultContainer.querySelector("[data-pla-results-species]").innerText =
        result.species;
      resultContainer.querySelector("[data-pla-results-location]").innerHTML =
        pathdisplay;

      let resultShiny = resultContainer.querySelector(
        "[data-pla-results-shiny]"
      );
	  let sparkle = "";
	  let sparklesprite = document.createElement('img');
	  sparklesprite.className = "pla-results-sparklesprite";
	  sparklesprite.src = "data:image/svg+xml;charset=utf8,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%3E%3C/svg%3E";
	  sparklesprite.height = "10";
	  sparklesprite.width = "10";
	  sparklesprite.style.cssText = "pull-left;display:inline-block;margin-left:0px;";
      if (result.shiny && result.square){
          sparkle = "Square Shiny!"
		  sparklesprite.src = "static/img/square.png";
      }
      else if (result.shiny){
		  sparklesprite.src = "static/img/shiny.png";
          sparkle = "Shiny!"
      }
	  else {
		  sparkle = "Not Shiny"
	  }
	  resultContainer.querySelector("[data-pla-results-shinysprite]").appendChild(sparklesprite);
      resultShiny.innerText = sparkle;
      resultShiny.classList.toggle("pla-result-true", result.shiny);
      resultShiny.classList.toggle("pla-result-false", !result.shiny);

      let resultAlpha = resultContainer.querySelector(
        "[data-pla-results-alpha]"
      );
	  let bigmon = "";
      if (result.alpha) {
          bigmon = "Alpha!";
      }
      else {
          bigmon = "Not Alpha";
      }
	  
	  
      resultAlpha.innerText = bigmon;
      resultAlpha.classList.toggle("pla-result-true", result.alpha);
      resultAlpha.classList.toggle("pla-result-false", !result.alpha);
	  
	  resultContainer.querySelector("[data-pla-results-adv]").innerText =
		result.adv;

      resultContainer.querySelector("[data-pla-results-nature]").innerText =
        result.nature;
		
      resultContainer.querySelector("[data-pla-results-gender]").innerHTML =
        result.gender;
      resultContainer.querySelector("[data-pla-results-ec]").innerText =
        result.ec;
      resultContainer.querySelector("[data-pla-results-pid]").innerText =
        result.pid;
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
		
	  switch (result.nature){
        case "Lonely":
          resultContainer.querySelector("[data-pla-results-ivs-att]").classList.add('pla-iv-minus');
          resultContainer.querySelector("[data-pla-results-ivs-def]").classList.add('pla-iv-plus');
          break;
        case "Adamant":
          resultContainer.querySelector("[data-pla-results-ivs-att]").classList.add('pla-iv-minus');
          resultContainer.querySelector("[data-pla-results-ivs-spa]").classList.add('pla-iv-plus');
          break;
        case "Naughty":
          resultContainer.querySelector("[data-pla-results-ivs-att]").classList.add('pla-iv-minus');
          resultContainer.querySelector("[data-pla-results-ivs-spd]").classList.add('pla-iv-plus');
          break;
        case "Brave":
          resultContainer.querySelector("[data-pla-results-ivs-att]").classList.add('pla-iv-minus');
          resultContainer.querySelector("[data-pla-results-ivs-spe]").classList.add('pla-iv-plus');
          break;
        case "Bold":
          resultContainer.querySelector("[data-pla-results-ivs-def]").classList.add('pla-iv-minus');
          resultContainer.querySelector("[data-pla-results-ivs-att]").classList.add('pla-iv-plus');
          break;
        case "Impish":
          resultContainer.querySelector("[data-pla-results-ivs-def]").classList.add('pla-iv-minus');
          resultContainer.querySelector("[data-pla-results-ivs-spa]").classList.add('pla-iv-plus');
          break;
        case "Lax":
          resultContainer.querySelector("[data-pla-results-ivs-def]").classList.add('pla-iv-minus');
          resultContainer.querySelector("[data-pla-results-ivs-spd]").classList.add('pla-iv-plus');
          break;
        case "Relaxed":
          resultContainer.querySelector("[data-pla-results-ivs-def]").classList.add('pla-iv-minus');
          resultContainer.querySelector("[data-pla-results-ivs-spe]").classList.add('pla-iv-plus');
          break;
        case "Modest":
          resultContainer.querySelector("[data-pla-results-ivs-spa]").classList.add('pla-iv-minus');
          resultContainer.querySelector("[data-pla-results-ivs-att]").classList.add('pla-iv-plus');
          break;
        case "Mild":
          resultContainer.querySelector("[data-pla-results-ivs-spa]").classList.add('pla-iv-minus');
          resultContainer.querySelector("[data-pla-results-ivs-def]").classList.add('pla-iv-plus');
          break;
        case "Rash":
          resultContainer.querySelector("[data-pla-results-ivs-spa]").classList.add('pla-iv-minus');
          resultContainer.querySelector("[data-pla-results-ivs-spd]").classList.add('pla-iv-plus');
          break;
        case "Quiet":
          resultContainer.querySelector("[data-pla-results-ivs-spa]").classList.add('pla-iv-minus');
          resultContainer.querySelector("[data-pla-results-ivs-spe]").classList.add('pla-iv-plus');
          break;
        case "Calm":
          resultContainer.querySelector("[data-pla-results-ivs-spd]").classList.add('pla-iv-minus');
          resultContainer.querySelector("[data-pla-results-ivs-att]").classList.add('pla-iv-plus');
          break;
        case "Gentle":
          resultContainer.querySelector("[data-pla-results-ivs-spd]").classList.add('pla-iv-minus');
          resultContainer.querySelector("[data-pla-results-ivs-def]").classList.add('pla-iv-plus');
          break;
        case "Careful":
          resultContainer.querySelector("[data-pla-results-ivs-spa]").classList.add('pla-iv-minus');
          resultContainer.querySelector("[data-pla-results-ivs-spd]").classList.add('pla-iv-plus');
          break;
        case "Sassy":
          resultContainer.querySelector("[data-pla-results-ivs-spd]").classList.add('pla-iv-minus');
          resultContainer.querySelector("[data-pla-results-ivs-spe]").classList.add('pla-iv-plus');
          break;
        case "Timid":
          resultContainer.querySelector("[data-pla-results-ivs-spe]").classList.add('pla-iv-minus');
          resultContainer.querySelector("[data-pla-results-ivs-att]").classList.add('pla-iv-plus');
          break;
        case "Hasty":
          resultContainer.querySelector("[data-pla-results-ivs-spe]").classList.add('pla-iv-minus');
          resultContainer.querySelector("[data-pla-results-ivs-def]").classList.add('pla-iv-plus');
          break;
        case "Jolly":
          resultContainer.querySelector("[data-pla-results-ivs-spe]").classList.add('pla-iv-minus');
          resultContainer.querySelector("[data-pla-results-ivs-spa]").classList.add('pla-iv-plus');
          break;
        case "Naive":
          resultContainer.querySelector("[data-pla-results-ivs-spe]").classList.add('pla-iv-minus');
          resultContainer.querySelector("[data-pla-results-ivs-spd]").classList.add('pla-iv-plus');
          break;
      }
		
	  
      resultsArea.appendChild(resultContainer);
	
    });
	
  } else {
    resultsArea.innerText = "No results found";
  }
};


function showError(error) {
  console.log(error);
  resultsArea.textContent = "Error" + JSON.stringify(error, null, 2);
}


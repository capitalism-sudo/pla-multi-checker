var script = document.createElement('script');
script.src = '../static/js/jquery.min.js';
script.type = 'text/javascript';
document.getElementsByTagName('head')[0].appendChild(script);

const resultTemplate = document.querySelector("[data-pla-results-template]");
const resultsArea = document.querySelector("[data-pla-results]");
const mapLocationsArea = document.querySelector("[data-pla-info-locations]");
const spinnerTemplate = document.querySelector("[data-pla-spinner]");

const resultsSection = document.querySelector(".pla-section-results");
const resultsSprite = document.querySelector(".pla-results-sprite");
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

genderFilter.onchange = setFilter;
spawnerID.onchange = setSpawners;
dayNight.onchange = setSpawners;

loadPreferences();
setupPreferenceSaving();

const results = [];


const coll = document.getElementsByClassName("expandable-control");

for (let c = 0; c < coll.length; c++){
	  coll[c].addEventListener("click", function() {
      this.classList.toggle("expanded");
      var content = this.nextElementSibling;

      if (content.style.maxHeight) {
        content.classList.toggle("expanded", false);
        content.style.maxHeight = null;
      }
      else {
        content.classList.toggle("expanded", true);
        content.style.maxHeight = content.scrollHeight + "px";
      }
    });
}

// Save and load user preferences
function loadPreferences() {
  rollsInput.value = readIntFromStorage("rolls", 1);
  genderFilter.value = readIntFromStorage("gender", 1);
  genderCheckbox.checked = readBoolFromStorage(
	"gendercheck",
	false
  );
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

function setFilter(event) {
	showFilteredResults();
}

function setSpawners(event) {
	mapSpawnsArea.innerHTML = "";
	$.getJSON('static/resources/' + mapName.value + '.json', function(data) {
		$.each(data, function(key,value) {
			if (key == spawnerID.value) {
				console.log(key)
				var time = false;
				let cycle = dayNight.checked;
				if (cycle)
					time = true;
				var breakloop = false;
				$.each(value, function(timeweather, species) {
					if ((time) && ((timeweather.includes("Any Time")) || (timeweather.includes("Night"))) && !(breakloop)){
						breakloop = true;
						$.each(species, function(pokemon, slot) {
							let locListItem = document.createElement("ul");
							locListItem.innerText = pokemon;
							mapSpawnsArea.appendChild(locListItem);
						});
					}
					else if (!(time) && ((timeweather.includes("Any Time")) || (timeweather.includes("Day"))) && !(breakloop)) {
						console.log(timeweather)
						console.log(species)
						breakloop = true;
						$.each(species, function(pokemon, slot) {
							console.log(pokemon)
							console.log(slot)
							let locListItem = document.createElement("ul");
							locListItem.innerText = pokemon;
							console.log("loclistitem innertext")
							console.log(locListItem.innerText)
							mapSpawnsArea.appendChild(locListItem);
						});
					}
				});
			}
		});
	});		
}

function readBoolFromStorage(id, defaultValue) {
  value = localStorage.getItem(id);
  return value ? parseInt(value) == 1 : defaultValue;
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
			daynight: dayNight.checked
	}
  };
}

function checkalphaadv() {
  const options = getOptions();
  showFetchingResults();

  fetch("/check-alphaseed", {
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


const showResults = ({ alpha_spawns }) => {
  if(alpha_spawns.spawn) {
	  results.push(alpha_spawns)
  };
  showFilteredResults();
};


const showFilteredResults = () => {

  resultsArea.innerHTML = "";
  resultsSection.classList.toggle("pla-loading", false);
  
  if(results.length > 0) {
	results.forEach((result) => {
	  console.log(results);
	  
      const resultContainer = resultTemplate.content.cloneNode(true);
	  
	  let sprite = document.createElement('img');
	  sprite.src = "static/img/sprite/"+result.sprite;
	  
	  resultContainer.querySelector('.pla-results-sprite').appendChild(sprite);
      resultContainer.querySelector("[data-pla-results-species]").innerText =
        result.species;
	  
	  let resultGender = "Genderless";
	  
	  if (result.gender < parseInt(genderFilter.value)) {
		  resultGender = "Female";
	  }
	  else if (parseInt(genderFilter.value) != -1) {
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
          resultContainer.querySelector("[data-pla-results-ivs-spd]").classList.add('pla-iv-minus');
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


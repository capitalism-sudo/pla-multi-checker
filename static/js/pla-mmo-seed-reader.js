const resultTemplate = document.querySelector("[data-pla-results-template]");
const resultsArea = document.querySelector("[data-pla-results]");
const mapLocationsArea = document.querySelector("[data-pla-info-locations]");
const mapSpawnsArea = document.querySelector("[data-pla-info-spawns]");
const spinnerTemplate = document.querySelector("[data-pla-spinner]");

const resultsSection = document.querySelector(".pla-section-results");
const resultsSprite = document.querySelector(".pla-results-sprite");
const resultsSparklesprite = document.querySelector(".pla-results-sparklesprite");

const teleportButton = document.querySelector(".pla-results-teleport");

// options
const inputSeed = document.getElementById("inputseed");
const rollsInput = document.getElementById("rolls");
const frSpawns = document.getElementById("frspawns");
const brSpawns = document.getElementById("brspawns");
const bonusCheckbox = document.getElementById("bonus");
const frEncounter = document.querySelector("#frpokemon");
const brEncounter = document.querySelector("#brpokemon");

// filters
const distShinyOrAlphaCheckbox = document.getElementById(
  "mmoShinyOrAlphaFilter"
);
const distShinyCheckbox = document.getElementById("mmoShinyFilter");
const distAlphaCheckbox = document.getElementById("mmoAlphaFilter");
const distDefaultCheckbox = document.getElementById("mmoDefaultRouteFilter");
const distMultiCheckbox = document.getElementById("mmoMultiFilter");

distShinyOrAlphaCheckbox.onchange = setFilter;
distShinyCheckbox.onchange = setFilter;
distAlphaCheckbox.onchange = setFilter;
distDefaultCheckbox.onchange = setFilter;
distMultiCheckbox.onchange = setFilter;

loadPreferences();
setupPreferenceSaving();

const results = [];

// Save and load user preferences
function loadPreferences() {
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
  distDefaultCheckbox.checked = readBoolFromStorage(
    "mmoDefaultRouteFilter",
	false
  );
  frSpawns.value = readIntFromStorage("frspawns", 1);
  brSpawns.value = readIntFromStorage("brspawns", 1);
  bonusCheckbox.checked = readBoolFromStorage(
    "bonus",
	false
  );
  validateFilters();
}

function setupPreferenceSaving() {
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
  frSpawns.addEventListener("change", (e) =>
	saveIntToStorage("frspawns", e.target.value)
  );
  brSpawns.addEventListener("change", (e) =>
	saveIntToStorage("brspawns", e.target.value)
  );
  bonusCheckbox.addEventListener("change", (e) =>
	saveBoolToStorage("bonus", e.target.checked)
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

function filter(result, shinyOrAlphaFilter, shinyFilter, alphaFilter, defaultFilter, multiFilter) {
  if (shinyOrAlphaFilter && !(result.shiny || result.alpha)) {
    return false;
  }

  if (shinyFilter && !result.shiny) {
    return false;
  }

  if (alphaFilter && !result.alpha) {
    return false;
  }

  if (defaultFilter && !result.defaultroute) {
	  return false;
  }
  
  if (multiFilter && !result.multi) {
	  return false;
  }

  return true;
}

function getOptions() {
  return {
	seed: inputSeed.value,
    rolls: parseInt(rollsInput.value),
	frspawns: parseInt(frSpawns.value),
	brspawns: parseInt(brSpawns.value),
	isbonus: bonusCheckbox.checked,
	frencounter: frEncounter.value,
	brencounter: brEncounter.value,
//	inmap: inmapCheck.checked
  };
}

function setMap() {
  const options = { map_name: mapSelect.value };

  fetch("/read-maps", {
	 method: "GET"
	})
	  .then((response) => response.json())
	  .then((res) => showMaps(res))
	  .catch((error) => showError(error));
}

function convertCoords(coordinates) {
            return [coordinates[2] * -0.5, coordinates[0] * 0.5];
}

function showMapInfo({ locations, spawns }) {
  mapLocationsArea.innerHTML = "";
  mapSpawnsArea.innerHTML = "";

  locations.forEach((loc) => {
    let locListItem = document.createElement("li");
    locListItem.innerText = loc;
    mapLocationsArea.appendChild(locListItem);
  });

  const spawnList = document.createElement("ul");
  spawns.forEach((spawn) => {
    let spawnItem = document.createElement("li");
    spawnItem.innerText = spawn;
    mapSpawnsArea.appendChild(spawnItem);
  });
}

function checkmmos() {
  const options = getOptions();
  showFetchingResults();

  fetch("/check-mmoseed", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(options),
  })
    .then((response) => response.json())
    .then((res) => showResults(res))
    .catch((error) => showError(error));
}

function checkmaps(){
	fetch("/read-maps", {
	 method: "GET"
	})
	  .then((response) => response.json())
	  .then((res) => showMaps(res))
	  .catch((error) => showError(error));
}

function checknormals(){
	const options = getOptions();
	showFetchingResults();

	fetch("/read-normals", {
		method: "POST",
		headers: { "Content-type": "application/json" },
		body: JSON.stringify(options),
	})
	  .then((response) => response.json())
	  .then((res) => showNormalResults(res))
	  .catch((error) => showError(error));
}

function checkonemap(){
	const options = getOptions();
	showFetchingResults();

	fetch("/read-one-map", {
		method: "POST",
		headers: { "Content-type": "application/json" },
		body: JSON.stringify(options),
	})
	  .then((response) => response.json())
	  .then((res) => showMapResults(res))
	  .catch((error) => showError(error));
}

function teleportToSpawn(coords) {

	var xhr = new XMLHttpRequest();
	xhr.open("POST", "/teleport-to-spawn", true);
	xhr.setRequestHeader('Content-Type', 'application/json');
	xhr.send(JSON.stringify({
		coords: coords
	}));
}

function showFetchingResults() {
  results.length = 0;
  resultsArea.innerHTML = "";
  const spinner = spinnerTemplate.content.cloneNode(true);
  resultsArea.appendChild(spinner);
  resultsSection.classList.toggle("pla-loading", true);
}

const showMaps = ({maps,outbreaks}) => {
  mapLocationsArea.innerHTML = "";
  mapSpawnsArea.innerHTML = "";
	maps.forEach((location, index) => {
		if (location != "None") {
			let locListItem = document.createElement("ul");
			locListItem.innerText = index + " - " + location;
			mapLocationsArea.appendChild(locListItem);
		}
	});

	outbreaks.forEach((pokemon) => {
		let spawnItem = document.createElement("ul");
		spawnItem.innerText = pokemon;
		mapSpawnsArea.appendChild(spawnItem);
	});
}


const showNormalResults = ({normal_spawns}) => {
	console.log(normal_spawns)
	for (const [key,value] of Object.entries(normal_spawns)) {
		for (const [x, pokemon] of Object.entries(value)) {
			console.log(x)
			if(pokemon.spawn) {
				results.push(pokemon);
			}
		}
	};
	showFilteredResults();
};

const showMapResults = ({mmo_spawn}) => {
	for (const [key,value] of Object.entries(mmo_spawn)) {
		for (const [x, pokemon] of Object.entries(value)) {
			if(pokemon.spawn) {
				results.push(pokemon);
			}
			else if (x.includes("Bonus")) {
				for (const [b, bonus] of Object.entries(pokemon)) {
					if(bonus.spawn) {
						results.push(bonus);
					}
				}
			}
		}
	};
	showFilteredResults();
};

const showResults = ({ mmo_spawns }) => {
  for (const [key, value] of Object.entries(mmo_spawns)) {
	  for (const [z, vall] of Object.entries(value)) {
		  if(vall.spawn) {
			  results.push(vall)
		  }
		  for (const[x, pokemon] of Object.entries(vall)) {
			  if(pokemon.spawn) {
				  results.push(pokemon);
			  }
			  else if (x.includes("Bonus")) {
				  for (const[b, bonus] of Object.entries(pokemon)) {
					  if(bonus.spawn) {
						  results.push(bonus);
					  }
				  }
			  }
		  }
	  }
  };
  showFilteredResults();
};


const showFilteredResults = () => {
  validateFilters();

  let shinyOrAlphaFilter = distShinyOrAlphaCheckbox.checked;
  let shinyFilter = distShinyCheckbox.checked;
  let alphaFilter = distAlphaCheckbox.checked;
  let defaultFilter = distDefaultCheckbox.checked;
  let multiFilter = distMultiCheckbox.checked;

  resultsArea.innerHTML = "";
  resultsSection.classList.toggle("pla-loading", false);

  filteredResults = results.filter(
    (result) =>
      result.spawn &&
      filter(result, shinyOrAlphaFilter, shinyFilter, alphaFilter, defaultFilter, multiFilter)
  );

  if (filteredResults.length > 0) {
	resultsArea.innerHTML = "<h3><section class='pla-section-results' flow>D = Despawn. Despawn Multiple Pokemon by either Multibattles (for aggressive) or Scaring (for skittish) pokemon.</section></h3>";  
    filteredResults.forEach((result) => {
	  let sprite = document.createElement('img');
	  sprite.src = "static/img/sprite/"+result.sprite;
	  
	  let indexprefix = ""
	  let chainprefix = ""
	  if (result.chains.length == 0) {
		  indexprefix = "Single Shiny Path: <br>" + result.index;
		  chainprefix = "No Additional Shinies On Path";
	  }
	  else {
		  indexprefix = "Multiple Shiny Path (Complete for more than one Shiny):  <br>" + result.index;
		  chainprefix = "<br>" + result.chains
		  result.multi = true;
	  }

      const resultContainer = resultTemplate.content.cloneNode(true);
	  resultContainer.querySelector('.pla-results-sprite').appendChild(sprite);
      resultContainer.querySelector("[data-pla-results-species]").innerText =
        result.species;
      resultContainer.querySelector("[data-pla-results-location]").innerHTML =
        indexprefix;

      let resultShiny = resultContainer.querySelector(
        "[data-pla-results-shiny]"
      );
      let sparkle = "";
	  let sparklesprite = document.createElement('img');
	  sparklesprite.className = "pla-results-sparklesprite";
	  sparklesprite.src = "data:image/svg+xml;charset=utf8,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%3E%3C/svg%3E";
	  sparklesprite.height = "10";
	  sparklesprite.width = "10";
	  sparklesprite.style.cssText = "pull-left;display:inline-block;";
      if (result.shiny && result.square) {
		  sparklesprite.src = "static/img/square.png";
          sparkle = "Square Shiny!"
      }
	  else if (result.shiny) {
		  sparklesprite.src = "static/img/shiny.png";
		  sparkle = "Shiny!"
	  }
      else {
          sparkle = "Not Shiny"
      }
	  resultContainer.querySelector("[data-pla-results-shinysprite]").appendChild(sparklesprite);
      resultShiny.innerHTML = sparkle;
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

	  resultContainer.querySelector("[data-pla-info-chains]").innerHTML =
		chainprefix;
      resultContainer.querySelector("[data-pla-results-nature]").innerText =
        result.nature;
      resultContainer.querySelector("[data-pla-results-gender]").innerHTML =
        result.gender;
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


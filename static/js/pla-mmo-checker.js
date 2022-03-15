const resultTemplate = document.querySelector("[data-pla-results-template]");
const resultsArea = document.querySelector("[data-pla-results]");
const mapLocationsArea = document.querySelector("[data-pla-info-locations]");
const mapSpawnsArea = document.querySelector("[data-pla-info-spawns]");
const spinnerTemplate = document.querySelector("[data-pla-spinner]");

const resultsSection = document.querySelector(".pla-section-results");

const teleportButton = document.querySelector(".pla-results-teleport");

// options
const mapSelect = document.getElementById("mapSelect");
const rollsInput = document.getElementById("rolls");

mapSelect.onchange = setMap;

// filters
const distShinyOrAlphaCheckbox = document.getElementById(
  "mmoShinyOrAlphaFilter"
);
const distShinyCheckbox = document.getElementById("mmoShinyFilter");
const distAlphaCheckbox = document.getElementById("mmoAlphaFilter");
const mmoSpeciesText = document.getElementById("mmoSpeciesFilter");

distShinyOrAlphaCheckbox.onchange = setFilter;
distShinyCheckbox.onchange = setFilter;
distAlphaCheckbox.onchange = setFilter;
mmoSpeciesText.oninput = setFilter;

loadPreferences();
setupPreferenceSaving();
setMap();

const results = [];

// Save and load user preferences
function loadPreferences() {
  mapSelect.value = localStorage.getItem("mapSelect") ?? "0";
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
  mapSelect.addEventListener("change", (e) =>
    localStorage.setItem("mapSelect", e.target.value)
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
	mapname: parseInt(mapSelect.value),
    rolls: parseInt(rollsInput.value),
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

  fetch("/read-mmos", {
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
	console.log(coords)
	
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
	console.log(mmo_spawn)
	for (const [key,value] of Object.entries(mmo_spawn)) {
		for (const [x, pokemon] of Object.entries(value)) {
			console.log(x)
			if(pokemon.spawn) {
				results.push(pokemon);
			}
			else if (x.includes("Bonus")) {
				for (const [b, bonus] of Object.entries(pokemon)) {
					console.log(b,bonus)
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
  console.log(mmo_spawns)
  for (const [key, value] of Object.entries(mmo_spawns)) {
	  for (const [z, vall] of Object.entries(value)) {
		  for (const[x, pokemon] of Object.entries(vall)) {
			  console.log(x)
			  if(pokemon.spawn) {
				  results.push(pokemon);
			  }
			  else if (x.includes("Bonus")) {
				  for (const[b, bonus] of Object.entries(pokemon)) {
					  console.log(b, bonus)
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
  let SpeciesFilter = mmoSpeciesFilter;

  resultsArea.innerHTML = "";
  resultsSection.classList.toggle("pla-loading", false);

  filteredResults = results.filter(
    (result) =>
      result.spawn &&
      filter(result, shinyOrAlphaFilter, shinyFilter, alphaFilter, SpeciesFilter)
  );

  if (filteredResults.length > 0) {
    filteredResults.forEach((result) => {
      const resultContainer = resultTemplate.content.cloneNode(true);
      resultContainer.querySelector("[data-pla-results-species]").innerText =
        result.species;
      resultContainer.querySelector("[data-pla-results-location]").innerText =
        result.index;

      let resultShiny = resultContainer.querySelector(
        "[data-pla-results-shiny]"
      );
      resultShiny.innerText = result.shiny;
      resultShiny.classList.toggle("pla-result-true", result.shiny);
      resultShiny.classList.toggle("pla-result-false", !result.shiny);

      let resultAlpha = resultContainer.querySelector(
        "[data-pla-results-alpha]"
      );
      resultAlpha.innerText = result.alpha;
      resultAlpha.classList.toggle("pla-result-true", result.alpha);
      resultAlpha.classList.toggle("pla-result-false", !result.alpha);

	  resultContainer.querySelector("[data-pla-results-group]").innerText =
	    result.group;
	  resultContainer.querySelector("[data-pla-results-mapname]").innerText =
	    result.mapname;
      resultContainer.querySelector("[data-pla-results-nature]").innerText =
        result.nature;
      resultContainer.querySelector("[data-pla-results-gender]").innerText =
        result.gender;
      resultContainer.querySelector("[data-pla-results-seed]").innerText =
        result.generator_seed.toString(16);
      resultContainer.querySelector("[data-pla-results-ec]").innerText =
        result.ec.toString(16);
      resultContainer.querySelector("[data-pla-results-pid]").innerText =
        result.pid.toString(16);
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
		
		
	  let button = document.createElement("button");
	  button.innerText = "Teleport to Spawn";
	  button.classList.add("pla-teleport-button");
	  button.onclick = () => teleportToSpawn(result.coords);

      resultContainer.querySelector('.pla-results-teleport').appendChild(button);
	  
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


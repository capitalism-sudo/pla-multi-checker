// Maps
export const DEFAULT_MAP = "obsidianfieldlands";

// Messages
export const MESSAGE_INFO = "info";
export const MESSAGE_ERROR = "error";

// Preference Data Version
export const PREFERENCES_VERSION = 1;

// Page initialisation
export function initializeApp(page) {
  checkPreferencesVersion();

  if (page !== "settings") {
    checkForResearch();
  }
}

// Preferences versioning - allows us to clear local storage if a breaking upgrade has happened
function checkPreferencesVersion() {
  let prefsVersion = readIntFromStorage("pla-prefs-version", -1);

  if (prefsVersion < PREFERENCES_VERSION) {
    // save the research string
    const researchString = localStorage.getItem("pla-research");

    localStorage.clear();
    saveIntToStorage("pla-prefs-version", PREFERENCES_VERSION);

    if (researchString) {
      localStorage.setItem("pla-research", researchString);
    }

    showMessage(
      MESSAGE_INFO,
      "PLA Multi Checker was recently updated, and we had to clear your old preferences to be compatible with the new version - don't worry, your research levels are still saved."
    );
  }
}

function checkForResearch() {
  // save the research string
  const researchString = localStorage.getItem("pla-research");

  if (!researchString) {
    showMessage(
      MESSAGE_INFO,
      "It looks like you haven't set the Pokédex research levels you've reached in the game. We need this information to work out your shiny odds. Please go to the 'Settings' page to fill it in. You don't have to fill in everything, but the more detail you give the more accurate your results will be."
    );
    return false;
  }
}

// Messages
export function showMessage(type, message) {
  const messages = document.querySelector("[data-pla-messages]");
  if (!messages) {
    console.log(
      `There was a message of type (${type}) but nowhere to show it. The message was: ${message}`
    );
    return;
  }

  messages.innerHTML = "";
  const messageElement = document.createElement("div");
  messageElement.classList.add("pla-message", `pla-message-${type}`);
  messageElement.textContent = message;
  messages.appendChild(messageElement);
}

export function showModalMessage(type, message) {
  const modalMessages = document.querySelector("[data-pla-modal-messages]");

  if (!modalMessages) {
    console.log(
      `There was a message of type (${type}) for a modal but nowhere to show it. The message was: ${message}`
    );
    return;
  }

  modalMessages.innerHTML = "";
  const messageElement = document.createElement("div");
  messageElement.classList.add("pla-message", `pla-message-${type}`);
  messageElement.textContent = message;
  modalMessages.appendChild(messageElement);
}

export function clearMessages() {
  const messages = document.querySelector("[data-pla-messages]");
  if (messages) messages.innerHTML = "";
}

export function clearModalMessages() {
  const modalMessages = document.querySelector("[data-pla-modal-messages]");
  if (modalMessages) modalMessages.innerHTML = "";
}

// Results Lifecycle
// This is the big function - basically a metafunction that takes other functions
// It abstracts a lot of common functionality for any search that will return an array of results to be shown on the page
// This way a lot of state for eg. spinners is all managed in a single function
export function doSearch(
  apiRoute,
  results,
  options,
  displayFunction,
  activationButton = null
) {
  const researchString = localStorage.getItem("pla-research");

  if (!researchString) {
    showMessage(
      MESSAGE_ERROR,
      "You haven't set the Pokedex research levels you've reached. This information is needed to work out your shiny odds. Please go to the 'Settings' page and fill in this information."
    );
    return false;
  }

  options["research"] = JSON.parse(researchString);

  // if that's all valid, set the page state to fetching results
  results.length = 0;
  showFetchingResults();

  let restoreButton = null;
  // if the activation button was provided, disable it to prevent hammering the api
  if (activationButton) {
    restoreButton = disableUntilRestore(activationButton);
  }

  // and do the fetch
  fetch(apiRoute, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(options),
  })
    .then((response) => response.json())
    .then((res) => {
      results.length = 0;

      // shows an error if one has been returned
      if (res.hasOwnProperty("error")) {
        showMessage(MESSAGE_ERROR, res.error);
      } else if (res.hasOwnProperty("results")) {
        console.log(res);
        results.push(...res.results);
      }

      setFetchingComplete();
      if (restoreButton) restoreButton();
      displayFunction();
    })
    .catch((error) => {
      if (restoreButton) restoreButton();
      showResultsError(error);
    });

  return true;
}

function showFetchingResults() {
  clearMessages();

  const spinnerTemplate = document.querySelector("[data-pla-spinner]");
  const spinner = spinnerTemplate.content.cloneNode(true);

  const resultsSection = document.querySelector(".pla-section-results");
  if (resultsSection) resultsSection.classList.toggle("pla-loading", true);

  const resultsArea = document.querySelector("[data-pla-results]");
  if (resultsArea) {
    resultsArea.innerHTML = "";
    resultsArea.appendChild(spinner);
  }
}

function setFetchingComplete() {
  const resultsSection = document.querySelector(".pla-section-results");
  if (resultsSection) resultsSection.classList.toggle("pla-loading", false);

  const resultsAreaSpinner = document.querySelector(
    "[data-pla-results] .pla-spinner"
  );

  if (resultsAreaSpinner) {
    resultsAreaSpinner.remove();
  }
}

function showResultsError(error) {
  setFetchingComplete();
  showMessage(MESSAGE_ERROR, error ?? "An error has occured");
  console.log(error);
}

export function showNoResultsFound() {
  const resultsArea = document.querySelector("[data-pla-results]");
  if (resultsArea) {
    resultsArea.innerHTML = "";
    const message = document.createElement("p");
    message.classList.add("pla-results-message");
    message.textContent = "No results found";
    resultsArea.appendChild(message);
  }
}

// Preference Saving / Loading
export function saveIntToStorage(id, value) {
  localStorage.setItem(id, value);
}

export function readIntFromStorage(id, defaultValue) {
  let value = localStorage.getItem(id);
  return value ? parseInt(value) : defaultValue;
}

export function saveBoolToStorage(id, value) {
  localStorage.setItem(id, value ? 1 : 0);
}

export function readBoolFromStorage(id, defaultValue) {
  let value = localStorage.getItem(id);
  return value ? parseInt(value) == 1 : defaultValue;
}

// Expandable Sections
export function setupExpandables() {
  const coll = document.getElementsByClassName("expandable-control");

  for (let c = 0; c < coll.length; c++) {
    coll[c].addEventListener("click", function () {
      this.classList.toggle("expanded");
      var content = this.nextElementSibling;

      if (content.style.maxHeight) {
        content.classList.toggle("expanded", false);
        content.style.maxHeight = null;
      } else {
        content.classList.toggle("expanded", true);
        content.style.maxHeight = content.scrollHeight + "px";
      }
    });
  }
}

//  Common Pokemon Result Display Fuctions
const natureIVs = {
  Lonely: ["[data-pla-results-ivs-att]", "[data-pla-results-ivs-def]"],
  Adamant: ["[data-pla-results-ivs-att]", "[data-pla-results-ivs-spa]"],
  Naughty: ["[data-pla-results-ivs-att]", "[data-pla-results-ivs-spd]"],
  Brave: ["[data-pla-results-ivs-att]", "[data-pla-results-ivs-spe]"],
  Bold: ["[data-pla-results-ivs-def]", "[data-pla-results-ivs-att]"],
  Impish: ["[data-pla-results-ivs-def]", "[data-pla-results-ivs-spa]"],
  Lax: ["[data-pla-results-ivs-def]", "[data-pla-results-ivs-spd]"],
  Relaxed: ["[data-pla-results-ivs-def]", "[data-pla-results-ivs-spe]"],
  Modest: ["[data-pla-results-ivs-spa]", "[data-pla-results-ivs-att]"],
  Mild: ["[data-pla-results-ivs-spa]", "[data-pla-results-ivs-def]"],
  Rash: ["[data-pla-results-ivs-spa]", "[data-pla-results-ivs-spd]"],
  Quiet: ["[data-pla-results-ivs-spa]", "[data-pla-results-ivs-spe]"],
  Calm: ["[data-pla-results-ivs-spd]", "[data-pla-results-ivs-att]"],
  Gentle: ["[data-pla-results-ivs-spd]", "[data-pla-results-ivs-def]"],
  Careful: ["[data-pla-results-ivs-spd]", "[data-pla-results-ivs-spa]"],
  Sassy: ["[data-pla-results-ivs-spd]", "[data-pla-results-ivs-spe]"],
  Timid: ["[data-pla-results-ivs-spe]", "[data-pla-results-ivs-att]"],
  Hasty: ["[data-pla-results-ivs-spe]", "[data-pla-results-ivs-def]"],
  Jolly: ["[data-pla-results-ivs-spe]", "[data-pla-results-ivs-spa]"],
  Naive: ["[data-pla-results-ivs-spe]", "[data-pla-results-ivs-spd]"],
  Serious: [false, false],
  Hardy: [false, false],
  Bashful: [false, false],
  Quirky: [false, false],
  Docile: [false, false],
};

export function showPokemonIVs(resultContainer, result) {
  resultContainer.querySelector("[data-pla-results-ivs-hp]").textContent =
    result.ivs[0];
  resultContainer.querySelector("[data-pla-results-ivs-att]").textContent =
    result.ivs[1];
  resultContainer.querySelector("[data-pla-results-ivs-def]").textContent =
    result.ivs[2];
  resultContainer.querySelector("[data-pla-results-ivs-spa]").textContent =
    result.ivs[3];
  resultContainer.querySelector("[data-pla-results-ivs-spd]").textContent =
    result.ivs[4];
  resultContainer.querySelector("[data-pla-results-ivs-spe]").textContent =
    result.ivs[5];

  const [plusNature, minusNature] = natureIVs[result.nature];
  if (plusNature)
    resultContainer.querySelector(plusNature).classList.add("pla-iv-plus");
  if (minusNature)
    resultContainer.querySelector(minusNature).classList.add("pla-iv-minus");
}

const genderStrings = {
  male: "Male <i class='fa-solid fa-mars' style='color:blue'/>",
  female: "Female <i class='fa-solid fa-venus' style='color:pink'/>",
  genderless: "Genderless <i class='fa-solid fa-genderless'/>",
};

export function showPokemonGender(resultContainer, gender) {
  resultContainer.querySelector("[data-pla-results-gender]").innerHTML =
    genderStrings[gender];
}

export function showPokemonInformation(resultContainer, result) {
  let sprite = document.createElement("img");
  sprite.src = "static/img/sprite/" + result.sprite;
  resultContainer.querySelector(".pla-results-sprite").appendChild(sprite);

  resultContainer.querySelector("[data-pla-results-species]").textContent =
    result.alpha ? "Alpha " + result.species : result.species;
  resultContainer.querySelector("[data-pla-results-nature]").textContent =
    result.nature;
  resultContainer.querySelector("[data-pla-results-rolls]").textContent =
    result.rolls;

  resultContainer.querySelector("[data-pla-results-gender]").innerHTML =
    genderStrings[result.gender];

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
    sparkle = "Square Shiny!";
    sparklesprite.src = "static/img/square.png";
  } else if (result.shiny) {
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

  let resultAlpha = resultContainer.querySelector("[data-pla-results-alpha]");
  resultAlpha.textContent = result.alpha ? "Alpha!" : "Not Alpha";
  resultAlpha.classList.toggle("pla-result-true", result.alpha);
  resultAlpha.classList.toggle("pla-result-false", !result.alpha);
}

export function showPokemonHiddenInformation(resultContainer, result) {
  let el = null;

  el = resultContainer.querySelector("[data-pla-results-seed]");
  if (el) el.textContent = result.generator_seed.toString(16).toUpperCase();

  el = resultContainer.querySelector("[data-pla-results-ec]");
  if (el) el.textContent = result.ec.toString(16).toUpperCase();

  el = resultContainer.querySelector("[data-pla-results-pid]");
  if (el) el.textContent = result.pid.toString(16).toUpperCase();
}

// Buttons
// Replaces button text with a spinner and disables the button
// returns a function that will restore the button to its original state
// So no state has to be saved
export function replaceWithSpinnerUntilRestore(buttonElement) {
  const spinnerTemplate = document.querySelector("[data-pla-spinner]");
  const spinner = spinnerTemplate.content.cloneNode(true);
  spinner.firstElementChild.classList.add("small");

  const buttonText = buttonElement.textContent;
  buttonElement.textContent = "";
  buttonElement.appendChild(spinner);
  buttonElement.disabled = true;

  return () => {
    buttonElement.removeChild(buttonElement.firstElementChild);
    buttonElement.textContent = buttonText;
    buttonElement.disabled = false;
  };
}

// Replaces button text with a spinner and disables the button
// returns a function that will restore the button to its original state
// So no state has to be saved
export function disableUntilRestore(buttonElement) {
  buttonElement.disabled = true;

  return () => {
    buttonElement.disabled = false;
  };
}

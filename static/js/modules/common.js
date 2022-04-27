// Maps
export const DEFAULT_MAP = "obsidianfieldlands";

// Messages
export const MESSAGE_INFO = "info";
export const MESSAGE_ERROR = "error";

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
export function showNoResultsFound() {
  const resultsArea = document.querySelector("[data-pla-results]");
  const message = document.createElement("p");
  message.classList.add("pla-results-message");
  message.textContent = "No results found";
  resultsArea.appendChild(message);
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

export function showPokemonInformation(resultContainer, result) {
  const [plusNature, minusNature] = natureIVs[result.nature];
  if (plusNature)
    resultContainer.querySelector(plusNature).classList.add("pla-iv-plus");
  if (minusNature)
    resultContainer.querySelector(minusNature).classList.add("pla-iv-minus");
}

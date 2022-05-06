import {
  MESSAGE_ERROR,
  MESSAGE_INFO,
  showMessage,
  showModalMessage,
  clearModalMessages,
  initializeApp,
} from "./modules/common.mjs";

// valid PLA save file sizes
const VALID_FILESIZES = [0x136dde, 0x13ad06];

// references to page elements
const researchTable = document.querySelector(".pla-research-table");
const rowTemplate = document.querySelector("[data-pla-research-row-template]");
const shinyCharmCheckbox = document.getElementById("pla-research-shinycharm");
const filterInput = document.getElementById("pla-research-filter");
const modal = document.getElementById("pla-research-modal");
const fileUpload = document.getElementById("pla-research-selectsave");

// page state
let hisuidex = [];
const researchRows = new Map();
const researchRadios = new Map();

initializeApp("settings");
loadPreferences();
setupPreferenceSaving();
loadPokedex();

// Save and load user preferences
function loadPreferences() {
  // Here for future proofing - not currently used
}

function setupPreferenceSaving() {
  // Here for future proofing - not currently used
}

// This runs on page load and wires the javascript up to the page once the pokedex data has loaded
function loadPokedex() {
  fetch("/api/hisuidex")
    .then((response) => response.json())
    .then((res) => {
      hisuidex = res.hisuidex;

      initializePage();
    })
    .catch((error) => {
      showMessage(
        MESSAGE_ERROR,
        "There was an error connecting to the server, the program is not running properly"
      );
    });
}

// The function that actually wires up the page
function initializePage() {
  // create the table for for each pokemon in the hisui dex
  hisuidex.forEach((pokemon) => createPokemonRow(pokemon));
  researchTable.addEventListener("change", saveResearch);

  // the button that sets all research to base level
  document
    .getElementById("pla-research-set-base")
    .addEventListener("click", () => {
      for (const [_, radios] of researchRadios) {
        radios[0].checked = true;
        radios[1].checked = false;
        radios[2].checked = false;
      }
      saveResearch();
    });

  // the button that sets all research to level 10 (+1 roll)
  document
    .getElementById("pla-research-set-complete")
    .addEventListener("click", () => {
      for (const [_, radios] of researchRadios) {
        radios[0].checked = false;
        radios[1].checked = true;
        radios[2].checked = false;
      }
      saveResearch();
    });

  // the button that sets all research to perfect (+3 rolls)
  document
    .getElementById("pla-research-set-perfect")
    .addEventListener("click", () => {
      for (const [_, radios] of researchRadios) {
        radios[0].checked = false;
        radios[1].checked = false;
        radios[2].checked = true;
      }
      saveResearch();
    });

  // the input that filters the list of pokemon
  filterInput.addEventListener("input", (e) => {
    const filterText = e.target.value.toLowerCase();
    for (const [name, row] of researchRows) {
      row.classList.toggle(
        "hidden",
        !name.toLowerCase().startsWith(filterText)
      );
    }
  });

  shinyCharmCheckbox.addEventListener("change", saveResearch);

  document
    .getElementById("pla-research-modal-open")
    .addEventListener("click", () => {
      modal.showModal();
    });

  document
    .getElementById("pla-research-modal-close")
    .addEventListener("click", () => {
      fileUpload.value = null;
      closeModal();
    });

  fileUpload.addEventListener("change", (e) => {
    uploadSave(e.target.files);
  });

  loadResearch();
}

function createPokemonRow(pokemon) {
  const row = rowTemplate.content.cloneNode(true);
  row.querySelector(".pla-research-row-name").textContent = pokemon.species;
  row.querySelector(
    "[data-pla-research-row-img]"
  ).src = `/static/img/sprite/${pokemon.sprite}`;
  let radios = row.querySelectorAll(".pla-research-radio");

  radios[0].name = pokemon.id;
  radios[1].name = pokemon.id;
  radios[2].name = pokemon.id;

  // radios[0].addEventListener("change", saveResearch);
  // radios[1].addEventListener("change", saveResearch);
  // radios[2].addEventListener("change", saveResearch);

  researchRows.set(pokemon.species, row.querySelector(".pla-research-row"));
  researchRadios.set(pokemon.species, [radios[0], radios[1], radios[2]]);
  researchTable.appendChild(row);
}

// select a save file to upload, doing some basic checking
// to increase the odds that its a file that can be read properly
// then upload the file and either show error messages returned by the server
// or set the page state to the read research values
function uploadSave(files) {
  if (files.length != 1) {
    showModalMessage(MESSAGE_ERROR, "You need to select a file");
    return;
  }

  const [file] = files;

  if (file.name != "main") {
    showModalMessage(MESSAGE_ERROR, 'Your save file should be called "main"');
    return;
  }

  if (VALID_FILESIZES.indexOf(file.size) < 0) {
    showModalMessage(
      MESSAGE_ERROR,
      "The file you chose isn't the right size for a PLA save file"
    );
    return;
  }

  const formData = new FormData();
  formData.append("save", file);

  fetch("/api/read-research", {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((res) => {
      // there are two possible situations for errors to happen:
      // this is when everything was sent to the server properly, but it had
      // an error while reading the save data
      if (res.hasOwnProperty("error")) {
        showModalMessage(MESSAGE_ERROR, res.error);
      } else {
        setResearch(res);
        saveResearch();
        fileUpload.value = null;
        closeModal();
        showMessage(MESSAGE_INFO, "Research levels loaded from save");
      }
    })
    .catch((error) => {
      // this error state is when there is some kind of problem with the
      // request or the configuration of the server
      showModalMessage(MESSAGE_ERROR, error);
    });
}

// sets the research state
function setResearch(research) {
  shinyCharmCheckbox.checked = research["shinycharm"];

  Object.entries(research["rolls"]).forEach(([name, value]) => {
    setRadioValue(researchRadios.get(name), value);
  });
}

// loads the research state
function loadResearch() {
  const researchString = localStorage.getItem("pla-research");

  // if there is no previously saved research level data, create it
  if (researchString == null) {
    saveResearch();
  } else {
    setResearch(JSON.parse(researchString));
  }
}

// save the research object to local storage
// this always creates a new research object to ensure there is no mismatch
// between the page state and what is saved to storage
function saveResearch() {
  const research = {};
  research["shinycharm"] = shinyCharmCheckbox.checked;
  research["rolls"] = {};

  hisuidex.forEach((pokemon) => {
    research["rolls"][pokemon.species] = getRadioValue(
      researchRadios.get(pokemon.species)
    );
  });

  localStorage.setItem("pla-research", JSON.stringify(research));
}

function getRadioValue(radios) {
  for (const radio of radios) {
    if (radio.checked) {
      return parseInt(radio.value, 10);
    }
  }
  return 0;
}

function setRadioValue(radios, value) {
  for (const radio of radios) {
    radio.checked = parseInt(radio.value, 10) == value;
  }
}

// close the modal,
// clearing all errors or they will persist if the modal is reopened
function closeModal() {
  clearModalMessages();
  modal.close();
}

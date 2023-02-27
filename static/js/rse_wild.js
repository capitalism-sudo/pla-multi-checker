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
    getSelectValues,
    setupIVBox,
    setivVal,
  } from "./modules/common.mjs";
  
  const resultTemplate = document.querySelector("[data-pla-results-template]");
  const resultsArea = document.querySelector("[data-pla-results]");
  
  // options
  const seed = document.getElementById("seed");
  const trainerID = document.getElementById("tid");
  const secretID = document.getElementById("sid");
  const minAdv = document.getElementById("minadvances");
  const maxAdv = document.getElementById("advances");
  const Delay = document.getElementById("delay");
  const method = document.getElementById("method");
  const lead = document.getElementById("lead");
  const leadopt = document.getElementById("leadopt");
  
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
  
  const distSelectFilter = document.getElementById("selectfilter");
  const natureSelect = document.getElementById("naturefilter");
  const genderSelect = document.getElementById("genderfilter");
  const SlotSelect = document.getElementById("slotfilter");
  const distShinyCheckbox = document.getElementById("mmoShinyFilter");
  const ratio = document.getElementById("genderratio");
  
  
  //pokemon parsing
  const gameVer = document.getElementById("version");
  const encType = document.getElementById("type");
  const encLoc = document.getElementById("location");
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
  encLoc.addEventListener("change", populateSpecies);
  encSpecies.addEventListener("change", populateOptions);
  
  const checkOwButton = document.getElementById("pla-button-checkwild");
  checkOwButton.addEventListener("click", checkOverworld);
  
  natureSelect.addEventListener("change", setFilter);
  genderSelect.addEventListener("change", setFilter);
  distShinyCheckbox.addEventListener("change", setFilter);
  ratio.addEventListener("change", setFilter);

  lead.addEventListener("change", populateLeads);
  gameVer.addEventListener("change", populateGame)

  loadPreferences();
  setupPreferenceSaving();
  setupExpandables();
  setupTabs();
  setupTabsRes();
  populateLocation();
  setupIVBox();
  populateGame();
  populateLeads();
  
  const results = [];
  var Safari = false;
  var rock = false;

  var synclead = '<option value="Hardy">Hardy</option>'+
  '<option value="Lonely">Lonely</option>'+
  '<option value="Brave">Brave</option>'+
  '<option value="Adamant">Adamant</option>'+
  '<option value="Naughty">Naughty</option>'+
  '<option value="Bold">Bold</option>'+
  '<option value="Docile">Docile</option>'+
  '<option value="Relaxed">Relaxed</option>'+
  '<option value="Impish">Impish</option>'+
  '<option value="Lax">Lax</option>'+
  '<option value="Timid">Timid</option>'+
  '<option value="Hasty">Hasty</option>'+
  '<option value="Serious">Serious</option>'+
  '<option value="Jolly">Jolly</option>'+
  '<option value="Naive">Naive</option>'+
  '<option value="Modest">Modest</option>'+
  '<option value="Mild">Mild</option>'+
  '<option value="Quiet">Quiet</option>'+
  '<option value="Bashful">Bashful</option>'+
  '<option value="Rash">Rash</option>'+
  '<option value="Calm">Calm</option>'+
  '<option value="Gentle">Gentle</option>'+
  '<option value="Sassy">Sassy</option>'+
  '<option value="Careful">Careful</option>'+
  '<option value="Quirky">Quirky</option>'
  
  var cutelead = '<option value="31f">&#9794; Lead, 12.5% &#9792; Target</option>'+
  '<option value="31m">&#9792; Lead, 87.5% &#9794; Target</option>'+
  '<option value="63f">&#9794; Lead, 25% &#9792; Target</option>'+
  '<option value="63m">&#9792; Lead, 75% &#9794; Target</option>'+
  '<option value="127f">&#9794; Lead, 50% &#9792; Target</option>'+
  '<option value="127m">&#9792; Lead, 50% &#9794; Target</option>'+
  '<option value="191f">&#9794; Lead, 75% &#9792; Target</option>'+
  '<option value="191m">&#9792; Lead, 25% &#9794; Target</option>'+
  
  $(function() {
      $(".chosen-select").chosen({
          no_results_text: "Oops, nothing found!",
          inherit_select_classes: true
      });
      
      $('#naturefilter').chosen().change(setFilter);
      
      $('#slotfilter').chosen().change(setFilter);
      
  });
  
  // Save and load user preferences
  function loadPreferences() {
      minAdv.value = 0;
      maxAdv.value = 10000;
      
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
    
    gameVer.value = localStorage.getItem("version") ?? "e";
    trainerID.value = localStorage.getItem("tid") ?? 0;
    secretID.value = localStorage.getItem("sid") ?? 0;
    natureSelect.value = "any";
    genderSelect.value = 50;
    SlotSelect.value = "any";
    Delay.value = 0;
    seed.value = 0;
    
  }
  
  function setupPreferenceSaving() {
    gameVer.addEventListener("change", (e) =>
      localStorage.setItem("version", e.target.value)
    );
    trainerID.addEventListener("change", (e) =>
      localStorage.setItem("tid", e.target.value)
    );
    secretID.addEventListener("change", (e) =>
      localStorage.setItem("sid", e.target.value)
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
    slotFilter,
    shinyFilter
  ) {

    if (shinyFilter && !result.shiny) {
        return false;
      }
      
    if (
          !natureFilter.includes("any") &&
          !natureFilter.includes(result.nature.toLowerCase())
          ) {
              return false;
          }
    
    if (
          genderFilter != 50
      ) {
          let gr = parseInt(ratio.value);
          console.log("Filter is not any, checking:");
          if (
          genderFilter == 0 &&
          !(result.gender > gr)
          ){
              console.log("Gender Result not male, male filter selected");
          return false;
          }
          else if ( genderFilter == 1 && !(result.gender < gr)) {
              console.log("Gender Result not female, female filter selected");
              return false;
          }
      }
    /*  
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
    */
        if (
            !slotFilter.includes("any") &&
            !slotFilter.includes(result.slot.toString())
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
      seed: seed.value,
      delay: parseInt(Delay.value),
      tid: trainerID.value,
      sid: secretID.value,
      method: parseInt(method.value),
      lead: lead.value,
      syncnature: leadopt.value,
      filter: {
        minadv: parseInt(minAdv.value),
        maxadv: parseInt(maxAdv.value),
          minivs: [parseInt(minHP.value), parseInt(minATK.value), parseInt(minDEF.value), parseInt(minSPA.value), parseInt(minSPD.value), parseInt(minSPE.value)],
          maxivs: [parseInt(maxHP.value), parseInt(maxATK.value), parseInt(maxDEF.value), parseInt(maxSPA.value), parseInt(maxSPD.value), parseInt(maxSPE.value)],
      },
      info: {
          version: gameVer.value,
          type: encType.value,
          loc: encLoc.value,
          species: encSpecies.value,
      },
      safari:Safari,
      rock: rock,
      command: distSelectFilter.value,
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

  function populateGame(){
    if (gameVer.value != "e"){
        lead.value = "None";
        populateLeads();
        if (!lead.diabled){
            lead.disabled = true;
        }
        if ((gameVer.value == "fr") || (gameVer.value == "lg")){
            rock = true;
        }
        else{
            rock = false;
        }
    }
    else {
        if (lead.disabled){
            lead.disabled = false;
        }
        rock = false;
    }
    populateLocation();
  }
  
  function populateLocation() {
      
      var options = { type: encType.value, version: gameVer.value }
      fetch("/api/g3-pop-location", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(options),
    })
      .then((response) => response.json())
      .then((res) => {
          console.log(res)
          var html_code = '';
          var species_code = '<option value="">Select Species</option>';
          html_code += '<option value="MAP_ROUTE111">Select Location:</option>';
          res.results.forEach((loc) => {
              html_code += '<option value="' + loc.rawloc + '">' + loc.location + '</option>';
          });
          encLoc.innerHTML = html_code;
          encSpecies.innerHTML = species_code;
          
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
      var options = { type: encType.value, location: encLoc.value, version: gameVer.value }
      fetch("/api/g3-pop-species", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(options),
    })
      .then((response) => response.json())
      .then((res) => {
          var html_code = '';
          html_code += '<option value="">Select Species:</option>';
          res.results.forEach((loc) => {
              html_code += '<option value="' + loc.raws + '">' + loc.species + '</option>';
          });
          encSpecies.innerHTML = html_code;

          if (encLoc.value.includes("SAFARI"))
          {
            Safari = true;
          }
          else {
            Safari = false;
          }
      })
  }
  
  
  function populateOptions() {
      var options = { type: encType.value, location: encLoc.value, version: gameVer.value, species: encSpecies.value }
      fetch("/api/g3-autofill", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(options),
    })
      .then((response) => response.json())
      .then((res) => {
          /*
          res.results.forEach((slot) => {
            SlotSelect.value += slot.toString();
          });
        console.log(getSelectValues(SlotSelect))
        */
        var element = SlotSelect

        // Set Values
        var values = res.results;
        console.log("Values:", values);
        /*
        for (var i = 0; i < element.options.length; i++) {
            console.log("Element Value: ",element.options[i].value, "Eval: ",values.toString().indexOf(element.options[i].value));
            element.options[i].selected = values.toString().indexOf(element.options[i].value) >= 0;
        }*/
        for (var i=0; i < element.options.length; i++){
            element.options[i].selected = false;
        }

        for (var p = 0; p < values.length; p++){
            element.options[values[p]+1].selected = true;
        }

        console.log(element.selectedOptions)

        // Get Value
        var selectedItens = Array.from(element.selectedOptions).map(option => option.value);

        selectedItens.innerHTML = selectedItens;
        $('#slotfilter').trigger("chosen:updated");
        showFilteredResults();
      })
  }

  function populateLeads() {
    console.log("I'm in",lead.value)
    if (lead.value == "Synch"){
        console.log(synclead);
        leadopt.innerHTML = synclead;
        if (leadopt.disabled){
            leadopt.disabled = false;
        }
    }
    else if (lead.value == "None"){
        leadopt.innerHTML = '<option value="None">None</option>';
        if (!leadopt.disabled){
            leadopt.disabled = true;
        }
    }
    else{
        leadopt.innerHTML = cutelead;
        if (leadopt.disabled){
            leadopt.disabled = false;
        }
    }
    $('#leadopt').trigger("chosen:updated");
  }
  
  function checkOverworld() {
    doSearch("/api/g3-check-wilds", results, getOptions(), showFilteredResults, checkOwButton);
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
    let shinyFilter = distShinyCheckbox.checked;
    let slotFilter = getSelectValues(SlotSelect);
    let genderfilter = genderSelect.value;

    console.log("NatureFilter:", natureFilter);
    console.log("SlotFilter:", slotFilter);

    const filteredResults = results.filter((result) =>
      filter(
        result,
        natureFilter,
        genderfilter,
        slotFilter,
        shinyFilter
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
    
    
    let sprite = document.createElement("img");
    sprite.src = "static/img/spritebig/" + result.sprite;
    resultContainer.querySelector(".pla-results-sprite").appendChild(sprite);

    
    resultContainer.querySelector("[data-pla-results-species]").innerHTML =
     result.species;
      
      
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
      result.adv;
    resultContainer.querySelector("[data-pla-results-slot]").textContent =
      result.slot;
    resultContainer.querySelector("[data-pla-results-hptype]").textContent =
      result.hidden;
    resultContainer.querySelector("[data-pla-results-hppow]").textContent =
      result.power;
    resultContainer.querySelector("[data-pla-results-level]").textContent =
      result.level;
    resultContainer.querySelector("[data-pla-results-nature]").textContent =
      result.nature;
      
    let gender = 'male';
    if (result.gender < parseInt(ratio.value)){
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
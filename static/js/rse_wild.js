import {
    doSearch,
    showNoResultsFound,
    setupExpandables,
    showPokemonIVs,
    showPokemonHiddenInformation,
    getSelectValues,
    setupIVBox,
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
  const distShinyCheckbox = document.getElementById("mmoShinyFilter");  
  
  //pokemon parsing
  const gameVer = document.getElementById("version");
  const encType = document.getElementById("type");
  const encLoc = document.getElementById("location");
  const encSpecies = document.getElementById("species");
  
  
  encType.addEventListener("change", populateLocation);
  encLoc.addEventListener("change", populateSpecies);
  encSpecies.addEventListener("change", setFilter)
  
  const checkOwButton = document.getElementById("pla-button-checkwild");
  checkOwButton.addEventListener("click", checkOverworld);
  
  natureSelect.addEventListener("change", setFilter);
  genderSelect.addEventListener("change", setFilter);
  distShinyCheckbox.addEventListener("change", setFilter);

  lead.addEventListener("change", populateLeads);
  gameVer.addEventListener("change", populateGame)

  loadPreferences();
  setupPreferenceSaving();
  setupExpandables();
  populateLocation();
  setupIVBox();
  populateGame();
  populateLeads();
  
  const results = [];
  var Safari = false;
  var rock = false;

  var synclead = '<option value=0>Hardy</option>'+
  '<option value=1>Lonely</option>'+
  '<option value=2>Brave</option>'+
  '<option value=3>Adamant</option>'+
  '<option value=4>Naughty</option>'+
  '<option value=5>Bold</option>'+
  '<option value=6>Docile</option>'+
  '<option value=7>Relaxed</option>'+
  '<option value=8>Impish</option>'+
  '<option value=9>Lax</option>'+
  '<option value=10>Timid</option>'+
  '<option value=11>Hasty</option>'+
  '<option value=12>Serious</option>'+
  '<option value=13>Jolly</option>'+
  '<option value=14>Naive</option>'+
  '<option value=15>Modest</option>'+
  '<option value=16>Mild</option>'+
  '<option value=17>Quiet</option>'+
  '<option value=18>Bashful</option>'+
  '<option value=19>Rash</option>'+
  '<option value=20>Calm</option>'+
  '<option value=21>Gentle</option>'+
  '<option value=22>Sassy</option>'+
  '<option value=23>Careful</option>'+
  '<option value=24>Quirky</option>'
  
  var cutelead = '<option value=25>&#9794; Lead</option>'+
  '<option value=26>&#9792; Lead</option>'+
  
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
          console.log("Filter is not any, checking:");
          if (
          genderFilter == 0 &&
          !(result.gender == 0)
          ){
              console.log("Gender Result not male, male filter selected");
          return false;
          }
          else if ( genderFilter == 1 && !(result.gender == 1)) {
              console.log("Gender Result not female, female filter selected");
              return false;
          }
          else if ( genderFilter == 2 && !(result.gender == 2)) {
            console.log("Gender Result not genderless, genderless filter selected");
            return false;
          }
      }
        if (
            !(slotFilter == "any") &&
            !(slotFilter == result.species)
        ) {
            return false;
        }
    return true;
  }
  
  function getOptions() {
    return {
      seed: seed.value,
      delay: parseInt(Delay.value),
      tid: trainerID.value,
      sid: secretID.value,
      method: parseInt(method.value),
      lead: lead.value,
      syncnature: parseInt(leadopt.value),
      filter: {
        minadv: parseInt(minAdv.value),
        maxadv: parseInt(maxAdv.value),
          minivs: [parseInt(minHP.value), parseInt(minATK.value), parseInt(minDEF.value), parseInt(minSPA.value), parseInt(minSPD.value), parseInt(minSPE.value)],
          maxivs: [parseInt(maxHP.value), parseInt(maxATK.value), parseInt(maxDEF.value), parseInt(maxSPA.value), parseInt(maxSPD.value), parseInt(maxSPE.value)],
      },
      info: {
          version: parseInt(gameVer.value),
          type: parseInt(encType.value),
          loc: parseInt(encLoc.value),
          species: encSpecies.value,
      },
      safari:Safari,
      rock: rock,
      command: distSelectFilter.value,
    };
  }
  

  function populateGame(){
    if (gameVer.value != 2){
        lead.value = "None";
        populateLeads();
        if (!lead.diabled){
            lead.disabled = true;
        }
    }
    else {
        if (lead.disabled){
            lead.disabled = false;
        }
    }
    populateLocation();
  }
  
  function populateLocation() {
      
      var options = { type: encType.value, version: parseInt(gameVer.value) }
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
          html_code += '<option value=0>Select Location:</option>';
          res.results.forEach((loc) => {
              html_code += '<option value="' + loc.rawloc + '">' + loc.location + '</option>';
          });
          encLoc.innerHTML = html_code;
          encSpecies.innerHTML = species_code;
          
      })
  }
  
  function populateSpecies() {
      var options = { type: parseInt(encType.value), location: parseInt(encLoc.value), version: parseInt(gameVer.value) }
      fetch("/api/g3-pop-species", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(options),
    })
      .then((response) => response.json())
      .then((res) => {
          var html_code = '';
          html_code += '<option value="any">Any Species:</option>';
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
        leadopt.innerHTML = '<option value=255>None</option>';
        if (!leadopt.disabled){
            leadopt.disabled = true;
        }
    }
    else if ((lead.value == "Pressure") || (lead.value == "Hustle") || (lead.value == "Vital Spirit")){
      leadopt.innerHTML = '<option value=32>None</option>';
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
  
  function showFilteredResults() {
    let natureFilter = getSelectValues(natureSelect);
    let shinyFilter = distShinyCheckbox.checked;
    let slotFilter = encSpecies.value;
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
    resultContainer.querySelector("[data-pla-results-hptype]").textContent =
      result.hidden;
    resultContainer.querySelector("[data-pla-results-hppow]").textContent =
      result.power;
    resultContainer.querySelector("[data-pla-results-level]").textContent =
      result.level;
    resultContainer.querySelector("[data-pla-results-nature]").textContent =
      result.nature;
    
    let gender = "male"
    if (result.gender == 1){
      gender = "female"
    }
    else if (result.gender == 2)
    {
      gender = "genderless"
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
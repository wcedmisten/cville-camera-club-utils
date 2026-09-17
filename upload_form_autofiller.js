// ==UserScript==
// @name        Cville Camera Club Autofiller
// @namespace   Violentmonkey Scripts
// @icon
// @version     1.0.0
//
// @match       https://c-villecameraclub.org/admin/*
// @grant       none
//
// @author      William Edmisten
// @description A utility to help upload CCC results
// @require https://cdn.jsdelivr.net/npm/@violentmonkey/shortcut@1
// ==/UserScript==

  function handleRecords(records) {
    console.log(records);
    // handle first record

    var photographers = Array.from(document.getElementById("name1").options).map((name) => { return {name: name.outerText, value: name.value}})
    console.log({photographers})

    records.forEach((record, index) => {
      // set the score
      document.getElementById("award" + (index + 1).toString()).value=record.score;

      // set the category
      document.getElementById("contest" + (index + 1).toString()).value=record.category;

      // replace nicknames
      var photographerOfficialName = record.photographer.replace("Jon Snoddy", "Jonathan Snoddy").replace("James Demas", "Jim Demas")
        .replace("Michael Bachmann", "Mike Bachmann").replace("Thomas Loucks", "Tom Loucks").replace("Ken Webster", "Kenneth Webster")

      foundPhotographerFilter = photographers.filter((photographer) => photographer.name.toLowerCase() == photographerOfficialName.toLowerCase());

      if (foundPhotographerFilter.length === 0) {
        alert("Could not find match for: " + photographerOfficialName)
      } else {
        // set the photographer
        document.getElementById("name" + (index + 1).toString()).value=foundPhotographerFilter[0].value;
      }

      // set the title
      document.getElementById("title" + (index + 1).toString()).value=record.title;
    })
  }

  const textBox = document.createElement('textarea');

  // 2. Configure it as a text box
  textBox.type = 'text';
  textBox.placeholder = 'Type something here...';

  // 3. Find the container on your page and add the text box to it
  document.body.appendChild(textBox);

  // 1. Target the parent element
  // 2. Create the new button element
  const newButton = document.createElement('button');

  // 3. Configure properties and content
  newButton.textContent = 'Fill in fields!';
  newButton.id = 'dynamic-btn';
  newButton.className = 'btn-primary';

  // 4. Attach an event listener
  newButton.addEventListener('click', () => {
    jsonString = textBox.value
    const records = JSON.parse(jsonString);

    dateXPath = "/html/body/div[2]/form/select";
    var dateSelect = document.evaluate(dateXPath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
    // set the date to the most recent option
    dateSelect.value = dateSelect.options[1].value

    handleRecords(records);

  });

  // 5. Append the button to the container
  document.body.appendChild(newButton);

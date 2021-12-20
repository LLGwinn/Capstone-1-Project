/* 
*  Add autocomplete to city inputs on home page
*/

mapboxgl.accessToken = 'pk.eyJ1IjoibGd3aW5uIiwiYSI6ImNreDljMWNuNjJlb2oyb211N2NieDh0MHYifQ.Gwv6bcmeKcZx2lqNHOUbdw';

let currCity = '';
let currState = '';
let destCity = '';
let destState = '';

const currGeocoder = new MapboxGeocoder({
            accessToken: mapboxgl.accessToken,
            countries:'US',
            types: 'place',
            fuzzyMatch:false
});

const destGeocoder = new MapboxGeocoder({
    accessToken: mapboxgl.accessToken,
    countries:'US',
    types: 'place',
    fuzzyMatch:false
});

// add geocoder tool to div
currGeocoder.addTo('#curr-city-div'); 
let currInputElement = document.getElementsByTagName('input')[0];
currInputElement.placeholder = 'Current City';

destGeocoder.addTo('#dest-city-div')
let destInputElement = document.getElementsByTagName('input')[1];
destInputElement.placeholder = 'Destination City';


// Get the geocoder results container.
const currResults = document.getElementById('curr-result'); // the <pre> element
const destResults = document.getElementById('dest-result');

// Assign result to variables.
currGeocoder.on('result', (evt) => {
    let currCity = evt.result.text;
    let currState = evt.result.context[1]["text"];
    let currAbbr = evt.result.context[1]["short_code"];
    document.getElementById('curr-city').value = currCity;
    document.getElementById('curr-state').value = currState;
    document.getElementById('curr-abbr').value = currAbbr;

});

destGeocoder.on('result', (evt) => {
    let destCity = evt.result.text;
    let destState = evt.result.context[1]["text"];
    let destAbbr = evt.result.context[1]["short_code"];
    document.getElementById('dest-city').value = destCity;
    document.getElementById('dest-state').value = destState;
    document.getElementById('dest-abbr').value = destAbbr;
});


// Clear results container when search is cleared.
currGeocoder.on('clear', () => {
results.innerText = '';
});

destGeocoder.on('clear', () => {
    results.innerText = '';
    });
    

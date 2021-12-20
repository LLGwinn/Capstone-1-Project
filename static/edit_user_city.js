/* 
*  Add autocomplete to city input on edit page
*/

mapboxgl.accessToken = 'pk.eyJ1IjoibGd3aW5uIiwiYSI6ImNreDljMWNuNjJlb2oyb211N2NieDh0MHYifQ.Gwv6bcmeKcZx2lqNHOUbdw';

const userGeocoder = new MapboxGeocoder({
            accessToken: mapboxgl.accessToken,
            countries:'US',
            types: 'place',
            fuzzyMatch:false
});

// add geocoder tool to div
userGeocoder.addTo('#user-city-div'); 
let userInputElement = document.getElementsByTagName('input')[2];
userInputElement.placeholder = 'Home City';

$('.mapboxgl-ctrl-geocoder').innerWidth(500)

// Get the geocoder results container.
const userResults = document.getElementById('user-result'); // the <pre> element


// Assign result to variables.
userGeocoder.on('result', (evt) => {
    let userCity = evt.result.text;
    let userState = evt.result.context[1]["text"];
    let userAbbr = evt.result.context[1]["short_code"];
    document.getElementById('user-city').value = userCity;
    document.getElementById('user-state').value = userState;
    document.getElementById('user-abbr').value = userAbbr;

});

// Clear results container when search is cleared.
userGeocoder.on('clear', () => {
userResults.innerText = '';
});


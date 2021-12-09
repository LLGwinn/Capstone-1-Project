/** Get comparison cities from form and make AJAX call to server. */

async function processForm(evt) {
    evt.preventDefault();
    let curr_city = $('#curr-city').val();
    let dest_city = $('#dest-city').val();

    const cities = {"current":curr_city, "destination":dest_city};
    
    let response = await axios.post('/cities/compare', cities);

    const icon = response.data.curr_city['icon'];

    $('#compare-results').append(
        `<p>Current City: ${response.data.curr_city['city_name']}</p>
        <p>Population: ${response.data.curr_city['pop']}</p>
        <p>Weather: ${response.data.curr_city['weather']}</p>
        <img id="wicon" src="http://openweathermap.org/img/w/${icon}.png" alt="Weather icon">
        <p>Dest City: ${response.data.dest_city['city_name']}</p>
        <p>Population: ${response.data.dest_city['pop']}</p>`
    )
    // $('b').text(""); //clear previous error messages
    // handleResponse(response);
}

/** handleResponse: deal with response server */

// function handleResponse(resp) {
//     // if response shows errors   
//     // if (typeof resp.data['errors'] != 'undefined') {
//     //     let errResp = resp.data['errors']; // dict of error messages
//     //     for (const [key, value] of Object.entries(errResp)) {
//     //         if (value.length > 0){
//     //             let field = `#${key}-err`;
//     //             $(`${field}`).append(value);
//     //         }
//     //     }
//     // } else {
//         let curr_city = resp.data.curr_city;
//         let dest_city = resp.data.dest_city;

//         $('#compare-results')
//             .append(`<p>Current City: ${curr_city.city_name}</p>
//                     <p>Destination: ${dest_city.city_name}</p>`);
        
// }

$("#cities-form").on("submit", processForm);

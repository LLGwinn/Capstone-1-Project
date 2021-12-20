# Relocation Assistant

[https://relocation-assistant.herokuapp.com/](https://relocation-assistant.herokuapp.com/)

This app allows users to compare census data from two cities to help with making a decision on whether to relocate.

After entering the name of the two comparison cities, user will see side-by-side real-time data drawn directly from the external APIs listed below. They can then click on a link to receive some basic advice on whether a move to the destination city makes sense. The logic for the advice is basic for now, based strictly on average incomes and average home values for each area, just to demonstrate that this functionality exists.

Users can choose to create an account, which will allow them to save their favorite cities for later reference. Other than saving favorites, all other functionality is available to users with or without an account.


### External APIS:
[U.S. Census Bureau]
American Community Survey 5-Year Data (2009-2019) for population, income, home price, and age data.
[OpenWeather]
Weather conditions for any city.
[Mapbox]
Autocomplete for city search.

### Tech Stack:
- Python
- Flask
- Javascript
- SQLAlchemy
- HTML
- CSS

[U.S. Census Bureau]:<https://api.census.gov/data/2019/acs/acs5>
[OpenWeather]:<https://api.openweathermap.org/data/2.5/weather?q={city name}&appid={API key}>
[Mapbox]:<https://api.mapbox.com/>
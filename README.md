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

### History:
This project was created as part of Springboard's Software Engineering Bootcamp in December 2021. The requirement was simply to create a database-driven app that goes further than basic CRUD, and to deploy the app on Heroku. The inspiration for a relocation assistant app came from the many times I, family members, or friends have wondered if relocating would make sense. What's the average income for that city? What's the average home value? And so on.  The U.S. Census Bureau was my primary data source, and it was a challenge. The API is complicated, there are dozens, if not hundreds, of variables (data points) to wade through to find the ones you need, and the response objects are difficult to traverse. But there is a wealth of available information, so I know I'll use it again at some point.  OpenWeather's API was easy to use, and I love the ability to add the icon to show current weather conditions.  Finally, based on feedback from my Springboard mentor and others, I decided to add an autocomplete component to the city search boxes. The popular choice would be Google Places, but their free tier was not generous and required a credit card, so I went with Mapbox. The documentation for Mapbox seemed a little wonky to this beginner, and I found it fairly tricky to implement the autocomplete. Specifically, I found it difficult and cumbersome to customize the search box in any way. But it works well, and its limitations are almost certainly due to my novice status.  
### Future:
If I ever want to complete my Bootcamp, I need to move on from this project for now. But as time allows, I would like to implement the following additional improvements:  
- for logged in users, default the home city field to the user's home city
- on user info page, allow user to click on favorite city to display home city vs. favorite city stats
- add ability to email report/data to user's email address
- add more data points for comparing cities



[U.S. Census Bureau]:<https://api.census.gov/data/2019/acs/acs5>
[OpenWeather]:<https://api.openweathermap.org/data/2.5/weather?q={city name}&appid={API key}>
[Mapbox]:<https://api.mapbox.com/>
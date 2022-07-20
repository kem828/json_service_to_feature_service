# json_service_to_feature_service
<div id="top"></div>




<!-- ABOUT THE PROJECT -->
## About The Project


This is a simple script that pulls a single layer json service and creates\updates a hosted feature service
 (either on AGOL or enterprise ArcGIS Server)




<!-- GETTING STARTED -->
## Getting Started

Change the run.bat file to point to your ArcGIS Pro python environment

### Prerequisites


* ArcGIS Pro


### Installation

1. Open credentials.json
2. Set the portal location and username and password
   ```
   "arcgis_portal" : "https://www.arcgis.com",
   username" : "userNAME",
   password" : "P@$$w0Rd!",
   ```
3. Set url source of json service
   ```
   "json_source" : "https://theres.data.here.org/api/losangeles/business",
   
   ```
4. If lat\long fields exist in the api, set them`
   ```
    "latitude_field_name" : "lat",
    "longitude_field_name" : "lng",
   ```

5. If using geocoding service to plot points, set geocoding to yesm and fill geocoder list`
   ```
    "geocoding" : "yes",
       "geocoder_list" : [
      "sampleUrl1/GeocodeServer",
      "sampleUrl2/GeocodeServer",
      "sampleUrl3/GeocodeServer"
    ]
   ```
6. Set the name you would like the service to have on the portal`
   ```
   "new_service_name" : "Super Cool Data Set",
   ```


<p align="right">(<a href="#top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

Run the run.bat file to pull the json service and create and point feature service on the ArcGIS portal.

Retrieve the itemID from the new service and add it to the credentials.json file

run the run.bat again to update the portal service







<!-- CONTACT -->
## Contact

Keinan Marks -  keinan@keinanmarks.com

Project Link: [https://github.com/kem828/json_service_to_feature_service](https://github.com/kem828/json_service_to_feature_service)

<p align="right">(<a href="#top">back to top</a>)</p>



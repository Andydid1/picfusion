const api_key = "prj_test_sk_5f5044e2820fcada59f618bb74ba28a11900354a";
const geo_api = "https://api.radar.io/v1/geocode/forward";

exports.location = async (req, res) => {

  console.log("call to /location...");

  try {
    var location = req.query.location
    
    // Access api.radar.io for detailed geocoding information
    var api_params = {
      method: "GET",
      headers: {
        "Authorization": api_key
      }
    };
    console.log("Querying "+geo_api+"?query="+location);
    var api_response = await fetch(geo_api+"?query="+location, api_params);
    var json_response = await api_response.json()
    
    // Throw error if failed
    if (await json_response['meta']['code'] == 400) {
      throw new Error('Query Geocoding API failed!');
    } else {
      var address_info = json_response['addresses'][0];
      var latitude = address_info['latitude'];
      var longitude = address_info['longitude'];
    }

    res.json({
      "message": "success",
      "latitude": await latitude,
      "longitude": await longitude
    })

  }//try
  catch (err) {
    res.status(400).json({
      "message": err.message,
      "latitude": -1,
      "longitude": -1
    });
  }//catch

}//put
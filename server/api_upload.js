//
// app.post('/image/:userid', async (req, res) => {...});
//
// Uploads an image to the bucket and updates the database,
// returning the asset id assigned to this image.
//
const dbConnection = require('./database.js')
const { PutObjectCommand } = require('@aws-sdk/client-s3');
const { s3, s3_bucket_name, s3_region_name } = require('./aws.js');

const uuid = require('uuid');

const api_key = "prj_test_sk_5f5044e2820fcada59f618bb74ba28a11900354a";
const geo_api = "https://api.radar.io/v1/geocode/forward";

exports.post_image = async (req, res) => {

  console.log("call to /upload...");

  try {

    var data = req.body;  // data => JS object
    var userid = req.params.userid;
    var bytes = Buffer.from(data['data'], 'base64');
    var formatted_addr = data['formatted_addr'].replaceAll(/[^a-zA-Z0-9]/g, '+')
    var assetname = data['assetname'];
    

    // Check if userid exists
    var rds_response = new Promise((resolve, reject) => {

      var sql = `SELECT bucketfolder FROM users WHERE userid = ?;`;

      dbConnection.query(sql, [userid], (err, results, _) => {
        if (err) {
          reject(err);
          return;
        }

        resolve(results);
      });
    });

    // If user doesn't exist response with error
    bucketfolder_res = await rds_response;
    if (bucketfolder_res == null || bucketfolder_res.length == 0) {
      res.json({
        "message": "no such user..."
      });
      return;
    }
    
    // Build a new bucket_key for s3
    var bucket = bucketfolder_res[0]['bucketfolder']
    var new_key = uuid.v4() + '.jpg';
    var bucket_key = bucket + '/' + new_key

    // Access api.radar.io for detailed geocoding information
    var api_params = {
      method: "GET",
      headers: {
        "Authorization": api_key
      }
    };
    console.log("Querying "+geo_api+"?query="+formatted_addr);
    var api_response = await fetch(geo_api+"?query="+formatted_addr, api_params);
    var json_response = await api_response.json()
    
    // Use default as Northwestern University if error
    if (await json_response['meta']['code'] == 400) {
      formatted_addr = "633 Clark Street, Evanston, IL 60208 USA";
      var postal_code = "60208";
      var city = "Evanston";
      var state = "Illinois";
      var country = "United States";
      var latitude = 42.060132;
      var longitude = -87.678033;
    } else {
      var address_info = json_response['addresses'][0];
      formatted_addr = address_info['formattedAddress'];
      var postal_code = address_info['postalCode'];
      var city = address_info['city'];
      var state = address_info['state'];
      var country = address_info['country'];
      var latitude = address_info['latitude'];
      var longitude = address_info['longitude'];
    }
  
    // Update rds
    var rds_response = new Promise((resolve, reject) => {
      var sql = `BEGIN;
                  INSERT INTO assets (userid, assetname, bucketkey) 
                  VALUES (?, ?, ?); 
                  
                  INSERT INTO metadata (assetid, formatted_addr, postal_code, city, state, country, latitude, longitude) 
                    VALUES(LAST_INSERT_ID(),?,?,?,?,?,?,?);
                    
                  SELECT assetid FROM metadata WHERE metadata_id = LAST_INSERT_ID();
                  COMMIT;`;
      var sql_params = [userid, assetname, bucket_key,  formatted_addr,  postal_code,  city,  state,  country,  latitude,  longitude];
      dbConnection.query(sql, sql_params, (err, results, _) => {
        if (err) {
          reject(err);
          return;
        }

        resolve(results);
      });
    });

    // Upload to s3
    const command = new PutObjectCommand({
      Bucket: s3_bucket_name,
      Key: bucket_key,
      Body: bytes,
    });
    
    const s3_response = await s3.send(command);

    Promise.all([s3_response, rds_response]).then(results => {
      var s3_result = results[0];
      var rds_result = results[1];
      res.json({
        "message": "success"
      });
    })
  }//try
  catch (err) {
    res.status(400).json({
      "message": err.message
    });
  }//catch

}//post
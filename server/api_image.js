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

exports.post_image = async (req, res) => {

  console.log("call to /image...");

  try {

    var data = req.body;  // data => JS object
    var userid = req.params.userid;
    var bytes = Buffer.from(data['data'], 'base64');

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
        "message": "no such user...",
        "assetid": -1
      });
      return;
    }

    // Upload object if user exists
    var bucket = bucketfolder_res[0]['bucketfolder']
    var new_key = uuid.v4() + '.jpg';
    var bucket_key = bucket + '/' + new_key
    
    // Update rds
    var rds_response = new Promise((resolve, reject) => {
      var sql = `INSERT INTO assets (userid, assetname, bucketkey) VALUES (?, ?, ?); SELECT LAST_INSERT_ID() as new_id;`;

      dbConnection.query(sql, [userid, data['assetname'], bucket_key], (err, results, _) => {
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

      var new_id = rds_result[1][0]['new_id'];
      res.json({
        "message": "success",
        "assetid": new_id
      });
    })
  }//try
  catch (err) {
    res.status(400).json({
      "message": err.message,
      "assetid": -1
    });
  }//catch

}//post
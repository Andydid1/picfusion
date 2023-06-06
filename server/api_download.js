//
// app.get('/download/:assetid', async (req, res) => {...});
//
// downloads an asset from S3 bucket and sends it back to the
// client as a base64-encoded string.
//
const dbConnection = require('./database.js')
const { GetObjectCommand } = require('@aws-sdk/client-s3');
const { s3, s3_bucket_name, s3_region_name } = require('./aws.js');

exports.get_download = async (req, res) => {

  console.log("call to /download...");

  try {


    // throw new Error("TODO: /download/:assetid");

    //
    // TODO
    //
    // MySQL in JS:
    //   https://expressjs.com/en/guide/database-integration.html#mysql
    //   https://github.com/mysqljs/mysql
    // AWS:
    //   https://docs.aws.amazon.com/sdk-for-javascript/v3/developer-guide/javascript_s3_code_examples.html
    //   https://docs.aws.amazon.com/AWSJavaScriptSDK/v3/latest/clients/client-s3/classes/getobjectcommand.html
    //   https://docs.aws.amazon.com/AWSJavaScriptSDK/v3/latest/clients/client-s3/
    //
    assetid = req.params.assetid;
    var rds_response = new Promise((resolve, reject) => {
      var sql = "SELECT * FROM assets WHERE assetid = ?;";
      dbConnection.query(sql, [assetid], async (err, results, _) => {
        if (err) {
          reject(err);
          throw err;
        }
        resolve(results)
      });
    });
    metadata_lst = await rds_response;
    if (metadata_lst == null || metadata_lst.length == 0) {
      res.json({
        "message": "no such asset...",
        "user_id": -1,
        "asset_name": "?",
        "bucket_key": "?",
        "data": []
      })
      return;
    }
    user_id = metadata_lst[0]['userid'];
    assetname = metadata_lst[0]['assetname'];
    bucketkey = metadata_lst[0]['bucketkey'];

    var s3_params = {
      Bucket: s3_bucket_name,
      Key: bucketkey
    };
    var s3_command = new GetObjectCommand(s3_params);
    var s3_response = s3.send(s3_command);
    const data = await s3_response;

    res.json({
      "message": "success",
      "user_id": user_id,
      "asset_name": assetname,
      "bucket_key": bucketkey,
      "data": await data.Body.transformToString("base64")
    })

  }//try
  catch (err) {
    //
    // generally we end up here if we made a 
    // programming error, like undefined variable
    // or function:
    //
    res.status(400).json({
      "message": err.message,
      "user_id": -1,
      "asset_name": "?",
      "bucket_key": "?",
      "data": []
    });
  }//catch

}//get
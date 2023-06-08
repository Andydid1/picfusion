// SignIn or Register account
// 
//
const dbConnection = require('./database.js')

const uuid = require('uuid');

exports.post_signin = async (req, res) => {

  console.log("call to /signin...");

  try {

    var data = req.body;  // data => JS object

    var sql = "Select user_password, userid From users Where email = ?;";
    var params = [data.email];

    var rds_response = new Promise((resolve, reject) => {
      dbConnection.query(sql, params, (err, results, _) => {
        if (err) {
          reject(err);
          return;
        }
        resolve(results);
      });
    });
    results = await rds_response;
    
    if (results.length == 0) {
      res.status(202).json({
          "message": "no such user...",
          "userid": -1
        });
      return;
    }

    if (results.length == 1) {
      if (data.password == results[0].user_password) {
        res.status(201).json({
          "message": "Success!",
          "userid": results[0].userid
        });
      } else {
        res.status(203).json({
          "message": "wrong password...",
          "userid": -1
        });
      }
      return;
    }
  }//try
  catch (err) {
    res.status(400).json({
      "message": err.message,
      "userid": -1
    });
  }//catch

}//post


exports.post_register = async (req, res) => {

  console.log("call to /register...");

  try {

    var data = req.body;  // data => JS object

    var sql = "Select * From users Where email = ?;";
    var params = [data.email];

    var rds_response1 = new Promise((resolve, reject) => {
      dbConnection.query(sql, params, (err, results, _) => {
        if (err) {
          reject(err);
          return;
        }
        resolve(results);
      });
    });

    results1 = await rds_response1;
    
    if (results1.length != 0) {
      res.status(203).json({
          "message": "email used..."
        });
      return;
    }
 
    var bucketfolder = uuid.v4();
      // bucket_key = results[0].bucketfolder + "/" + name + ".jpg";
    
    insert_sql = "INSERT INTO users \
                  (email, username, bucketfolder, user_password) \
                  VALUES(?, ?, ?, ?);"
    insert_param = [data.email, data.username,
                    bucketfolder, data.password];

    dbConnection.query(insert_sql, insert_param, (err, result, _) => {
      res.json({
        "message": "success",
      });
    });
    return;
  }//try
  catch (err) {
    res.status(400).json({
      "message": err.message,
    });
  }//catch

}//post
//
// app.put('/user', async (req, res) => {...});
//
// Inserts a new user into the database, or if the
// user already exists (based on email) then the
// user's data is updated (name and bucket folder).
// Returns the user's userid in the database.
//
const uuid = require('uuid');
const dbConnection = require('./database.js')

exports.put_user = async (req, res) => {

  console.log("call to /user...");

  try {

    var data = req.body;  // data => JS object

    var email = data['email'];
    var lastname = data['lastname'];
    var firstname = data['firstname'];
    var bucketfolder = data['bucketfolder']

    // Check if the user exists in DB
    var rds_response = new Promise((resolve, reject) => {

      console.log("/user: calling RDS...");

      var sql = `SELECT userid FROM users WHERE email = ?;`;

      dbConnection.query(sql, [email], (err, results, _) => {
        if (err) {
          reject(err);
          return;
        }

        console.log("/user query done");
        resolve(results);
      });
    });

    // Insert if not exist, else update
    existing_user = await rds_response;
    console.log(existing_user)
    if (existing_user == null || existing_user.length == 0) {

      var new_id_response = new Promise((resolve, reject) => {

        var sql = `INSERT INTO users (lastname, firstname, email, bucketfolder) VALUES (?, ?, ?, ?); SELECT LAST_INSERT_ID() as new_id;`;

        dbConnection.query(sql, [lastname, firstname, email, bucketfolder], (err, results, _) => {
          if (err) {
            reject(err);
            return;
          }

          console.log("/user insert done");
          resolve(results);
        });
      });
      new_id = (await new_id_response)[1][0]['new_id'];
      // console.log(await new_id);
      res.json({
        "message": "inserted",
        "userid": new_id
      });


    } else {
      console.log("/user: user exists");
      user_id = (await existing_user)[0]['userid'];
      // console.log(await user_id);
      var update_response = new Promise((resolve, reject) => {

        var sql = `UPDATE users SET lastname = ?, firstname = ?, bucketfolder = ? WHERE userid = ?;`;

        dbConnection.query(sql, [lastname, firstname, bucketfolder, user_id], (err, results, _) => {
          if (err) {
            reject(err);
            return;
          }

          console.log("/user update done");
          resolve(results);
        });
      });
      
      // console.log(await new_id);
      res.json({
        "message": "updated",
        "userid": user_id
      });
    }

  }//try
  catch (err) {
    console.log(err.message);
    res.status(400).json({
      "message": "some sort of error message",
      "userid": -1
    });
  }//catch

}//put
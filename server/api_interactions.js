//
// app.post('/interactions', async (req, res) => {...});
//
// Records a like/dislike interaction for an asset by a user.
//
const dbConnection = require('./database.js')

exports.post_interaction = async (req, res) => {

  console.log("call to /interactions...");

  try {

    var data = req.body;  // data => JS object
    var user_id = data['user_id'];
    var assetid = data['assetid'];
    var interaction_type = data['interaction_type']; // 1 for like, 0 for dislike

    // Insert the interaction into the database
    var rds_response = new Promise((resolve, reject) => {

      var sql = `INSERT INTO interactions (user_id, assetid, interaction_type) VALUES (?, ?, ?);`;

      dbConnection.query(sql, [user_id, assetid, interaction_type], (err, results, _) => {
        if (err) {
          reject(err);
          return;
        }

        resolve(results);
      });
    });

    // If the interaction is successfully recorded, respond with success
    rds_response.then(results => {
      res.json({
        "message": "success"
      });
    }).catch(err => {
      res.status(400).json({
        "message": err.message
      });
    });

  } catch (err) {
    res.status(400).json({
      "message": err.message
    });
  }
}

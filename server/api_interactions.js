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
    var userid = data['userid'];
    var assetid = data['assetid'];
    var interaction_type = data['interaction_type']; // 1 for like, -1 for dislike

    // Insert the interaction into the database
    var rds_response = new Promise((resolve, reject) => {

      var sql = `INSERT INTO interactions (user_id, assetid, interaction_type) VALUES (?, ?, ?)
                 ON DUPLICATE KEY UPDATE interaction_type = ?;
                 SELECT COALESCE(SUM(interaction_type),0) AS like_count 
                  FROM interactions
                  WHERE assetid = ?;`;

      dbConnection.query(sql, [userid, assetid, interaction_type, interaction_type, assetid], (err, results, _) => {
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
        "message": "success",
        "like_count": results[1][0]['like_count']
      });
    }).catch(err => {
      res.status(400).json({
        "message": err.message,
        "like_count": -1
      });
    });

  } catch (err) {
    res.status(400).json({
      "message": err.message,
        "like_count": -1
    });
  }
}
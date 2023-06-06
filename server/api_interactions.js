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
    var assetid = data['assetid'];
    var interaction_type = data['interaction_type']; // 1 for like, -1 for dislike

    // Insert the interaction into the database
    var rds_response = new Promise((resolve, reject) => {

      var sql = `INSERT INTO interactions (assetid, interaction_type) VALUES (?, ?)
                 ON DUPLICATE KEY UPDATE interaction_type = interaction_type + VALUES(interaction_type);`;

      dbConnection.query(sql, [assetid, interaction_type], (err, results, _) => {
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

// Add this to your api_interactions.js file
exports.get_interaction = async (req, res) => {
  const assetid = req.params.assetid;

  // Query to fetch interaction data
  const query = `SELECT SUM(interaction_type) as interaction_type FROM interactions WHERE assetid = ?`;

  dbConnection.query(query, [assetid], (err, results) => {
    if (err) {
      res.status(400).json({
        "message": err.message
      });
      return;
    }

    // Send the interaction data back to the client
    res.json({
      "interaction_type": results[0].interaction_type
    });
  });
};

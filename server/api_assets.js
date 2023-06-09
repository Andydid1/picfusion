//
// app.get('/assets', async (req, res) => {...});
//
// Return all the assets from the database:
//
const dbConnection = require('./database.js')

exports.get_assets = async (req, res) => {

  console.log("call to /assets...");

  try {

    //
    // TODO: remember we did an example similar to this in class with
    // movielens database (lecture 05 on Thursday 04-13)
    //
    // MySQL in JS:
    //   https://expressjs.com/en/guide/database-integration.html#mysql
    //   https://github.com/mysqljs/mysql
    //
    var sql = `SELECT meta_info.assetid, IFNULL(like_count,0) as like_count, userid, 
              assetname, bucketkey, formatted_addr, postal_code, city, 
              state, country, latitude, longitude FROM
                  (SELECT assetid, COALESCE(SUM(interaction_type),0) AS like_count 
                  FROM interactions 
                  GROUP BY assetid) like_info 
              RIGHT OUTER JOIN
                  (SELECT assets.assetid AS assetid, userid, assetname, 
                  bucketkey, formatted_addr, postal_code, city, state, country, latitude, longitude 
                  FROM assets JOIN metadata ON assets.assetid = metadata.assetid) meta_info
              ON like_info.assetid = meta_info.assetid;`;
    dbConnection.query(sql, async (err, results, _) => {
      if (err) {
        throw err;
      }
      // console.log(results);
      res.json({
        "message": "success",
        "data": results
      });
    });

  }//try
  catch (err) {
    res.status(400).json({
      "message": err.message,
      "data": []
    });
  }//catch

}//get

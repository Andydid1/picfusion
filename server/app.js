//
// Express js (and node.js) web service that interacts with 
// AWS S3 and RDS to provide clients data for building a 
// simple photo application for photo storage and viewing.
//


const express = require('express');
const app = express();
const config = require('./config.js');

const dbConnection = require('./database.js')
const { HeadBucketCommand, ListObjectsV2Command } = require('@aws-sdk/client-s3');
const { s3, s3_bucket_name, s3_region_name } = require('./aws.js');
var startTime;

app.use(express.json({ strict: false, limit: "50mb" }));

app.listen(config.service_port, () => {
  startTime = Date.now();
  console.log('web service running...');
  //
  // Configure AWS to use our config file:
  //
  process.env.AWS_SHARED_CREDENTIALS_FILE = config.photoapp_config;
});

app.get('/', (req, res) => {

  var uptime = Math.round((Date.now() - startTime) / 1000);

  res.json({
    "status": "running",
    "uptime-in-secs": uptime,
    "dbConnection": dbConnection.state
  });
});

//
// service functions:
//
var stats = require('./api_stats.js');
var users = require('./api_users.js');
var assets = require('./api_assets.js');
var bucket = require('./api_bucket.js');
var download = require('./api_download.js');
var user = require('./api_user.js');
var upload = require('./api_upload.js');
var interactions = require('./api_interactions.js');

app.get('/stats', stats.get_stats);  //app.get('/stats', (req, res) => {...});
app.get('/users', users.get_users);  //app.get('/users', (req, res) => {...});
app.get('/assets', assets.get_assets);  //app.get('/assets', (req, res) => {...});
app.get('/bucket', bucket.get_bucket);  //app.get('/bucket?startafter=bucketkey', (req, res) => {...});
app.get('/download/:assetid', download.get_download); //app.get('/download/:assetid', (req, res) => {...});
app.put('/user', user.put_user);
app.post('/upload/:userid', upload.post_image);

// ...
app.post('/interactions', interactions.post_interaction);
app.get('/interactions/:assetid', interactions.get_interaction);

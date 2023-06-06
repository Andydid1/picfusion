USE picfusion;

DROP TABLE IF EXISTS assets;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS metadata;
DROP TABLE IF EXISTS interactions;

CREATE TABLE users
(
    userid       int not null AUTO_INCREMENT,
    email        varchar(128) not null,
    username     varchar(64) not null,
    bucketfolder varchar(48) not null,  -- random, unique name (UUID)
    user_password varchar(64) not null, 
    create_time	    TIMESTAMP   DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (userid),
    UNIQUE      (email),
    UNIQUE      (bucketfolder)
);

CREATE TABLE assets
(
    assetid      int not null AUTO_INCREMENT,
    userid       int not null,
    assetname    varchar(128) not null,  -- original name from user
    bucketkey    varchar(128) not null,  -- random, unique name in bucket
    create_time	    TIMESTAMP   DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (assetid),
    UNIQUE      (bucketkey)
);

CREATE TABLE metadata
(
	metadata_id	int not null AUTO_INCREMENT,
	assetid	int not null,
	formatted_addr	varchar(128),
	postal_code	int,
	city	varchar(32) ,
	state	varchar(32) ,
	country	varchar(32) ,
	latitude	float not null,
	longitude	float not null,
    PRIMARY KEY (metadata_id)
);

CREATE TABLE interactions
(
	user_id	int not null,
	assetid	int not null,
	interaction_type int not null
);
CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL
);

-- Running upgrade  -> 45373c8be8ec

CREATE TABLE account (
    id INTEGER NOT NULL AUTO_INCREMENT, 
    email NATIONAL VARCHAR(255) NOT NULL, 
    username NATIONAL VARCHAR(255), 
    `passwordHash` NATIONAL VARCHAR(255) NOT NULL, 
    PRIMARY KEY (id)
);

INSERT INTO alembic_version (version_num) VALUES ('45373c8be8ec');

-- Running upgrade 45373c8be8ec -> f4bc6c0c8bb

ALTER TABLE account RENAME TO user;

ALTER TABLE user MODIFY email VARCHAR(64) NOT NULL;

ALTER TABLE user MODIFY username VARCHAR(64) NOT NULL;

ALTER TABLE user CHANGE `passwordHash` password_hash VARCHAR(128) NULL;

CREATE UNIQUE INDEX uq_user_username ON user (username);

CREATE UNIQUE INDEX uq_user_email ON user (email);

UPDATE alembic_version SET version_num='f4bc6c0c8bb' WHERE alembic_version.version_num = '45373c8be8ec';

-- Running upgrade f4bc6c0c8bb -> 3486834a848e

ALTER TABLE user ADD COLUMN name VARCHAR(64);

ALTER TABLE user ADD COLUMN location VARCHAR(64);

ALTER TABLE user ADD COLUMN about_me TEXT;

ALTER TABLE user ADD COLUMN member_since DATETIME;

ALTER TABLE user ADD COLUMN last_seen DATETIME;

UPDATE alembic_version SET version_num='3486834a848e' WHERE alembic_version.version_num = 'f4bc6c0c8bb';

-- Running upgrade 3486834a848e -> b80a450b7b7

ALTER TABLE user ADD COLUMN avatar_hash VARCHAR(32);

UPDATE alembic_version SET version_num='b80a450b7b7' WHERE alembic_version.version_num = '3486834a848e';

-- Running upgrade b80a450b7b7 -> 6bd709eea9c

CREATE TABLE image (
    id INTEGER NOT NULL AUTO_INCREMENT, 
    image_name VARCHAR(64), 
    timestamp DATETIME, 
    user_id INTEGER, 
    PRIMARY KEY (id), 
    FOREIGN KEY(user_id) REFERENCES user (id)
);

CREATE INDEX ix_image_timestamp ON image (timestamp);

UPDATE alembic_version SET version_num='6bd709eea9c' WHERE alembic_version.version_num = 'b80a450b7b7';

-- Running upgrade 6bd709eea9c -> 1ac6ea08d878

ALTER TABLE image ADD COLUMN hashtags VARCHAR(64);

UPDATE alembic_version SET version_num='1ac6ea08d878' WHERE alembic_version.version_num = '6bd709eea9c';

-- Running upgrade 1ac6ea08d878 -> 3e5a001f617a

CREATE TABLE follows (
    follower_id INTEGER NOT NULL, 
    followed_id INTEGER NOT NULL, 
    timestamp DATETIME, 
    PRIMARY KEY (follower_id, followed_id), 
    FOREIGN KEY(followed_id) REFERENCES user (id), 
    FOREIGN KEY(follower_id) REFERENCES user (id)
);

UPDATE alembic_version SET version_num='3e5a001f617a' WHERE alembic_version.version_num = '1ac6ea08d878';


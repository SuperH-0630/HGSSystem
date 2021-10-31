DROP DATABASE IF EXISTS hgssystem;
CREATE DATABASE IF NOT EXISTS hgssystem;
USE hgssystem;

CREATE TABLE IF NOT EXISTS user -- 创建用户表
(
    ID         INT PRIMARY KEY AUTO_INCREMENT,
    UserID     char(34)    NOT NULL UNIQUE,
    Name       varchar(50) NOT NULL,
    IsManager  bit         NOT NULL DEFAULT 0,
    Phone      char(11)    NOT NULL,
    Score      INT         NOT NULL,
    Reputation INT         NOT NULL,
    CreateTime DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS garbage -- 创建普通垃圾表
(
    GarbageID   INT PRIMARY KEY AUTO_INCREMENT,
    CreateTime  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    Flat        TINYINT  NOT NULL DEFAULT 0,
    UserID      char(34),
    UseTime     DATETIME,
    GarbageType TINYBLOB,
    Location    VARCHAR(50),
    CheckResult BIT,
    CheckerID   char(34),
    FOREIGN KEY (UserID) REFERENCES user (UserID),
    FOREIGN KEY (CheckerID) REFERENCES user (UserID)
);

-- 创建视图

DROP VIEW IF EXISTS garbage_n;
CREATE VIEW garbage_n AS
SELECT GarbageID, CreateTime
FROM garbage
WHERE Flat = 0;

DROP VIEW IF EXISTS garbage_c;
CREATE VIEW garbage_c AS
SELECT GarbageID, CreateTime, UserID, UseTime, GarbageType, Location
FROM garbage
WHERE Flat = 1;

DROP VIEW IF EXISTS garbage_u;
CREATE VIEW garbage_u AS
SELECT GarbageID,
       CreateTime,
       UserID,
       UseTime,
       GarbageType,
       Location,
       CheckerID,
       CheckResult
FROM garbage
WHERE Flat = 2;

DROP VIEW IF EXISTS garbage_time;
CREATE VIEW garbage_time AS
SELECT GarbageID, UserID, UseTime
FROM garbage
WHERE Flat = 1
   OR Flat = 2;

DROP VIEW IF EXISTS garbage_user;
CREATE VIEW garbage_user AS
SELECT GarbageID          AS GarbageID,
       garbage.CreateTime AS CreateTime,
       garbage.UserID     AS UserID,
       user.Name          AS UserName,
       user.Phone         AS UserPhone,
       user.Score         AS UserScore,
       user.Reputation    AS UserReputation,
       UseTime            AS UseTime,
       GarbageType        AS GarbageType,
       Location           AS Location,
       CheckResult        AS CheckResult,
       CheckerID          AS CheckerID
FROM garbage
         LEFT JOIN user on garbage.UserID = user.UserID;

DROP VIEW IF EXISTS garbage_checker;
CREATE VIEW garbage_checker AS
SELECT GarbageID          AS GarbageID,
       garbage.CreateTime AS CreateTime,
       garbage.UserID     AS UserID,
       UseTime            AS UseTime,
       GarbageType        AS GarbageType,
       Location           AS Location,
       CheckResult        AS CheckResult,
       CheckerID          AS CheckerID,
       user.Name          AS CheckerName,
       user.Phone         AS CheckerPhone,
       user.Score         AS CheckerScore,
       user.Reputation    AS CheckerReputation
FROM garbage
         LEFT JOIN user on garbage.CheckerID = user.UserID;

DROP VIEW IF EXISTS garbage_checker_user;
CREATE VIEW garbage_checker_user AS
SELECT garbage_user.GarbageID       AS GarbageID,
       garbage_user.CreateTime      AS CreateTime,

       garbage_user.UserID          AS UserID,
       garbage_user.UserName        AS UserName,
       garbage_user.UserPhone       AS UserPhone,
       garbage_user.UserScore       AS UserScore,
       garbage_user.UserReputation  AS UserReputation,

       garbage_user.UseTime         AS UseTime,
       garbage_user.GarbageType     AS GarbageType,
       garbage_user.Location        AS Location,
       garbage_user.CheckResult     AS CheckResult,
       garbage_user.CheckerID       AS CheckerID,
       garbage_checker.CheckerName  AS CheckerName,
       garbage_checker.CheckerPhone AS CheckerPhone
FROM garbage_user
         LEFT JOIN garbage_checker on garbage_user.GarbageID = garbage_checker.GarbageID;

DROP VIEW IF EXISTS garbage_7d;
CREATE VIEW garbage_7d AS
SELECT (TO_DAYS(NOW()) - TO_DAYS(UseTime)) AS days,
       GarbageID,
       CreateTime,
       Flat,
       UserID,
       UseTime,
       GarbageType,
       Location,
       CheckResult,
       CheckerID
FROM garbage
WHERE TO_DAYS(NOW()) - TO_DAYS(UseTime) < 7;

DROP VIEW IF EXISTS garbage_30d;
CREATE VIEW garbage_30d AS
SELECT (TO_DAYS(NOW()) - TO_DAYS(UseTime)) AS days,
       GarbageID,
       CreateTime,
       Flat,
       UserID,
       UseTime,
       GarbageType,
       Location,
       CheckResult,
       CheckerID
FROM garbage
WHERE TO_DAYS(NOW()) - TO_DAYS(UseTime) < 30;

-- 创建函数
CREATE FUNCTION get_avg(num1 int, num2 int)
    RETURNS DECIMAL(5, 4)
    not deterministic
    reads sql data
    COMMENT '计算两个数相除'
BEGIN
    IF num2 = 0 or num1 = 0 THEN
        RETURN 0;
    END IF;
    RETURN num1 / num2;
END;

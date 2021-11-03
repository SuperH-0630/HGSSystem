DROP DATABASE IF EXISTS hgssystem;
CREATE DATABASE IF NOT EXISTS hgssystem;
USE hgssystem;

CREATE TABLE IF NOT EXISTS user -- 创建用户表
(
    ID         INT PRIMARY KEY AUTO_INCREMENT,
    UserID     CHAR(32)    NOT NULL UNIQUE CHECK (UserID REGEXP '[a-zA-Z0-9]{32}'),
    Name       VARCHAR(50) NOT NULL,
    IsManager  BIT         NOT NULL DEFAULT 0 CHECK (IsManager IN (0, 1)),
    Phone      CHAR(11)    NOT NULL CHECK (Phone REGEXP '[0-9]{11}'),
    Score      INT         NOT NULL CHECK (Score <= 500 and Score >= 0),
    Reputation INT         NOT NULL CHECK (Reputation <= 1000 and Reputation >= 1),
    CreateTime DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS garbage -- 创建普通垃圾表
(
    GarbageID   INT PRIMARY KEY AUTO_INCREMENT,
    CreateTime  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    Flat        TINYINT  NOT NULL DEFAULT 0 CHECK (Flat IN (0, 1, 2)),
    UserID      CHAR(34),
    UseTime     DATETIME,
    GarbageType TINYBLOB CHECK (GarbageType IS NULL OR GarbageType IN (1, 2, 3, 4)),
    Location    VARCHAR(50),
    CheckResult BIT CHECK (CheckResult IS NULL OR CheckResult IN (0, 1)),
    CheckerID   CHAR(34),
    FOREIGN KEY (UserID) REFERENCES user (UserID),
    FOREIGN KEY (CheckerID) REFERENCES user (UserID)
);

CREATE TABLE IF NOT EXISTS goods -- 商品
(
    GoodsID  INT PRIMARY KEY AUTO_INCREMENT,
    Name     CHAR(100) NOT NULL,
    Quantity INT       NOT NULL CHECK (Quantity >= 0),
    Score    INT       NOT NULL CHECK (Score > 0 and Score <= 500)
);

CREATE TABLE IF NOT EXISTS orders -- 订单
(
    OrderID INT PRIMARY KEY AUTO_INCREMENT,
    UserID  CHAR(34) NOT NULL,
    Status  BIT      NOT NULL DEFAULT 0,
    FOREIGN KEY (UserID) REFERENCES user (UserID)
);


CREATE TABLE IF NOT EXISTS ordergoods -- 订单内容
(
    OrderGoodsID INT PRIMARY KEY AUTO_INCREMENT,
    OrderID      INT NOT NULL,
    GoodsID      INT NOT NULL,
    Quantity     INT NOT NULL DEFAULT 1 CHECK (Quantity >= 0),
    FOREIGN KEY (OrderID) REFERENCES Orders (OrderID),
    FOREIGN KEY (GoodsID) REFERENCES Goods (GoodsID)
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
        RETURN 0; -- 注释, 防止python在此处分割SQL
    END IF; -- 注释, 防止python在此处分割SQL
    RETURN num1 / num2; -- 注释, 防止python在此处分割SQL
END;

-- ***In update case***
DROP TABLE IF EXISTS `sellers`;
DROP TABLE IF EXISTS `created`;
DROP TABLE IF EXISTS `products`;
DROP TABLE IF EXISTS `customers`;
DROP TABLE IF EXISTS `suppliers`;

-- ***Create data***
CREATE TABLE IF NOT EXISTS `suppliers`(
    `Id` INT AUTO_INCREMENT,
    `Name` VARCHAR(30) NOT NULL,
    PRIMARY KEY(`Id`)
);

CREATE TABLE IF NOT EXISTS `customers`(
    `Id` INT AUTO_INCREMENT,
    `Total` DECIMAL(10, 2) NOT NULL CHECK(`Total` > 0),
    PRIMARY KEY(`Id`)
);

CREATE TABLE IF NOT EXISTS `products`(
    `Id` INT AUTO_INCREMENT,
    `Code` CHAR(16) NOT NULL UNIQUE,
    `Name` VARCHAR(30) NOT NULL,
    `Price` DECIMAL(10, 2) NOT NULL CHECK(`Price` > 0),
    `AgeRestriction` INT(1) CHECK(`AgeRestriction` >= 0 AND `ageRestriction` <= 18),
    `OnStock` INT,
    PRIMARY KEY(`Id`)
);

CREATE TABLE IF NOT EXISTS `created`(
    `SupplierId` INT,
    `ProductId` INT,
    FOREIGN KEY(`SupplierId`) REFERENCES `suppliers`(`Id`),
    FOREIGN KEY(`ProductId`) REFERENCES `products`(`Id`)
);

CREATE TABLE IF NOT EXISTS `sellers`(
    `Id` INT AUTO_INCREMENT,
    `CustomerId` INT,
    `ProductId` INT,
    `Date` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `Amount` INT NOT NULL CHECK(`Amount` > 0),
    `Total` DECIMAL(10, 2) NOT NULL CHECK(`Total` > 0),
    PRIMARY KEY(`Id`),
    FOREIGN KEY(`CustomerId`) REFERENCES `customers`(`Id`),
    FOREIGN KEY(`ProductId`) REFERENCES `products`(`Id`)
);

INSERT INTO `suppliers`(Name) VALUES
    ('panimi'),
    ('manga world')
;

INSERT INTO `products`(Code, Name, Price, AgeRestriction, OnStock) VALUES
    ('1', 'Manga: Oshi No Ko', '31.99', 16, 1),
    ('2', 'Manga: Shingueki No Kiojin', '25.99', 18, 3),
    ('3', 'Manga: Naruto', '29.99', 16, 2),
    ('4', 'Manga: Konosubarashi', '31.99', 16, 0)
;

INSERT INTO `created`(SupplierId, ProductId) VALUE
    (1, 1),
    (1, 2),
    (1, 3),
    (2, 3),
    (2, 4)
;

-- ***Display data to verify***
SELECT * FROM `suppliers` LIMIT 5;
SELECT * FROM `products` LIMIT 5;
SELECT * FROM `created` LIMIT 5;
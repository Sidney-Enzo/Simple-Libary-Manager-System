-- ***In update case***
DROP TABLE IF EXISTS `sellers`;
DROP TABLE IF EXISTS `products`;
DROP TABLE IF EXISTS `customers`;
DROP TABLE IF EXISTS `suppliers`;

-- ***Create data***
CREATE TABLE IF NOT EXISTS `suppliers`(
    `Id` INT AUTO_INCREMENT,
    `Name` VARCHAR(30) NOT NULL UNIQUE,
    PRIMARY KEY(`Id`)
);


CREATE TABLE IF NOT EXISTS `customers`(
    `Id` INT AUTO_INCREMENT,
    `Total` DECIMAL(10, 2) NOT NULL CHECK(`Total` > 0),
    PRIMARY KEY(`Id`)
);

CREATE TABLE IF NOT EXISTS`products`(
    `Id` INT AUTO_INCREMENT,
    `Code` CHAR(16) NOT NULL UNIQUE,
    `Item` VARCHAR(30) NOT NULL UNIQUE,
    `Price` DECIMAL(10, 2) NOT NULL CHECK(`Price` > 0),
    `AgeRestriction` INT(1) CHECK(`AgeRestriction` >= 0 AND `ageRestriction` <= 18),
    `SupplierId` INT,
    `OnStock` INT,
    PRIMARY KEY(`Id`),
    FOREIGN KEY(`SupplierId`) REFERENCES `suppliers`(`Id`)
);

CREATE TABLE IF NOT EXISTS `sellers`(
    `Id` INT AUTO_INCREMENT,
    `CustumerId` INT,
    `ProductId` INT,
    `Date` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `Amount` INT NOT NULL CHECK(`Amount` > 0),
    `Price` DECIMAL(10, 2) NOT NULL CHECK(`Price` > 0),
    PRIMARY KEY(`Id`),
    FOREIGN KEY(`CustumerId`) REFERENCES `customers`(`Id`),
    FOREIGN KEY(`ProductId`) REFERENCES `products`(`Id`)
);

-- ***Insert test data***
INSERT INTO `suppliers`(Name) VALUES
    ('panimi'),
    ('mangaworld')
;

INSERT INTO `products`(Code, Item, Price, AgeRestriction, SupplierId, OnStock) VALUES 
    ('1', 'Manga: Oshi No Ko', '31.99', 16, 1, 1),
    ('2', 'Manga: Shingueki No Kiojin', '25.99', 18, 1, 3),
    ('3', 'Manga: Naruto', '29.99', 16, 2, 2),
    ('4', 'Manga: Konosubarashi', '31.99', 16, 2, 0)
;

-- ***Display data for verify***
SELECT * FROM `suppliers` LIMIT 5;
SELECT * FROM `products` LIMIT 5;
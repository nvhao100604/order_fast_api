-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jan 28, 2026 at 10:51 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";

START TRANSACTION;

SET time_zone = "+00:00";

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */
;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */
;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */
;
/*!40101 SET NAMES utf8mb4 */
;

--
-- Database: `website_order`
--

-- --------------------------------------------------------

--
-- Table structure for table `categories`
--
TRUNCATE TABLE roles,
staff,
categories,
dish,
tables,
customer,
orders,
order_detail,
reviews,
discount
RESTART IDENTITY CASCADE;

CREATE TABLE `categories` (
    `id` int(11) NOT NULL,
    `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

--
-- Dumping data for table `categories`
--

INSERT INTO
    `categories` (`id`, `name`)
VALUES (1, 'Appetizers'),
    (2, 'Main Courses'),
    (3, 'Desserts'),
    (4, 'Beverages'),
    (5, 'Soups'),
    (6, 'Salads'),
    (7, 'Seafood'),
    (8, 'Vegetarian'),
    (9, 'Noodles & Pasta'),
    (10, 'Rice Dishes'),
    (11, 'Breakfast'),
    (12, 'Lunch Specials'),
    (13, 'Dinner Specials'),
    (14, 'Fast Food'),
    (15, 'Street Food');

-- --------------------------------------------------------

--
-- Table structure for table `customer`
--

CREATE TABLE `customer` (
    `id` int(11) NOT NULL,
    `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
    `phoneNumber` varchar(10) NOT NULL
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

--
-- Dumping data for table `customer`
--

INSERT INTO
    `customer` (`id`, `name`, `phoneNumber`)
VALUES (1, 'Lê Hoàng', '0911223344'),
    (2, 'Nguyễn Thu', '0912345678'),
    (3, 'Trần Anh', '0913456789'),
    (4, 'Phạm Mai', '0914567890'),
    (5, 'Khách vãng lai', '');

-- --------------------------------------------------------

--
-- Table structure for table `discount`
--

CREATE TABLE `discount` (
    `id` int(11) NOT NULL,
    `category` enum('order', 'dish') NOT NULL,
    `dateBegin` datetime NOT NULL,
    `dateEnd` datetime NOT NULL,
    `status` tinyint(1) DEFAULT 0
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

--
-- Dumping data for table `discount`
--

INSERT INTO
    `discount` (
        `id`,
        `category`,
        `dateBegin`,
        `dateEnd`,
        `status`
    )
VALUES (
        1,
        'order',
        '2025-07-01 00:00:00',
        '2025-07-31 23:59:59',
        0
    ),
    (
        2,
        'dish',
        '2025-07-05 00:00:00',
        '2025-07-15 23:59:59',
        0
    ),
    (
        3,
        'order',
        '2025-06-01 00:00:00',
        '2025-06-30 23:59:59',
        1
    ),
    (
        4,
        'dish',
        '2025-07-01 00:00:00',
        '2025-07-10 23:59:59',
        0
    );

-- --------------------------------------------------------

--
-- Table structure for table `discount_detail_dish`
--

CREATE TABLE `discount_detail_dish` (
    `discountID` int(11) NOT NULL,
    `dishID` int(11) NOT NULL,
    `percent` int(2) NOT NULL
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

--
-- Dumping data for table `discount_detail_dish`
--

INSERT INTO
    `discount_detail_dish` (
        `discountID`,
        `dishID`,
        `percent`
    )
VALUES (2, 2, 15),
    (2, 5, 10),
    (4, 1, 20),
    (4, 10, 15);

-- --------------------------------------------------------

--
-- Table structure for table `discount_detail_order`
--

CREATE TABLE `discount_detail_order` (
    `discountID` int(11) NOT NULL,
    `nameDiscount` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
    `percent` int(2) NOT NULL,
    `term` double DEFAULT NULL
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

--
-- Dumping data for table `discount_detail_order`
--

INSERT INTO
    `discount_detail_order` (
        `discountID`,
        `nameDiscount`,
        `percent`,
        `term`
    )
VALUES (
        1,
        'Giảm 10% tổng hóa đơn',
        10,
        500000
    ),
    (
        3,
        'Giảm 5% hóa đơn',
        5,
        200000
    );

-- --------------------------------------------------------

--
-- Table structure for table `dish`
--

CREATE TABLE `dish` (
    `id` int(11) NOT NULL,
    `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
    `categoryID` int(11) NOT NULL,
    `price` double NOT NULL,
    `imgUrl` varchar(255) NOT NULL,
    `describe` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
    `status` tinyint(1) DEFAULT 0
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

--
-- Dumping data for table `dish`
--

INSERT INTO
    `dish` (
        `id`,
        `name`,
        `categoryID`,
        `price`,
        `imgUrl`,
        `describe`,
        `status`
    )
VALUES (
        1,
        'Gỏi cuốn tôm thịt',
        1,
        55000,
        'https://www.vimishop-vnfoods.com/cdn/shop/articles/240627_1200x1200.jpg?v=1720164521',
        'Món khai vị truyền thống Việt Nam.',
        0
    ),
    (
        2,
        'Phở Bò',
        9,
        80000,
        'https://tiki.vn/blog/wp-content/uploads/2023/07/thumb-12.jpg',
        'Món phở bò tái truyền thống.',
        0
    ),
    (
        3,
        'Cơm chiên hải sản',
        10,
        95000,
        'https://locduongseafood.com/wp-content/uploads/2023/05/z4393560428481_7d2950915240b05a6f3791c7650e501c.jpg',
        'Cơm chiên cùng tôm, mực và rau củ.',
        0
    ),
    (
        4,
        'Bánh Flan',
        3,
        30000,
        'https://static.hawonkoo.vn/hwks1/images/2023/07/cach-lam-banh-flan-bang-noi-chien-khong-dau-1-1.jpg',
        'Bánh flan mềm mịn, thơm ngon.',
        0
    ),
    (
        5,
        'Nước cam ép',
        4,
        40000,
        'https://bazaarvietnam.vn/wp-content/uploads/2021/08/uong-nuoc-cam-co-dep-da-khong_547801399.jpg',
        'Nước cam tươi nguyên chất.',
        0
    ),
    (
        6,
        'Súp bí đỏ',
        5,
        60000,
        'https://cdn.tgdd.vn/Files/2021/09/10/1381722/huong-dan-lam-sup-bi-do-tai-nha-ngon-nhu-nha-hang-202208311606274453.jpg',
        'Súp kem bí đỏ thơm béo.',
        0
    ),
    (
        7,
        'Salad Caesar',
        6,
        75000,
        'https://file.hstatic.net/200000692767/file/caesar-salad__1_.jpg',
        'Salad trộn với xà lách, croutons.',
        0
    ),
    (
        8,
        'Cá hồi nướng bơ tỏi',
        7,
        180000,
        'https://cdn.tgdd.vn/Files/2020/03/19/1243099/ca-hoi-nuong-bo-toi-thom-ngon-giau-duong-chat-lai-lam-cuc-de-dang-202003190933577877.jpg',
        'Cá hồi nướng vàng ruộm, thơm ngon.',
        0
    ),
    (
        9,
        'Mì Ý sốt cà chua cay',
        8,
        85000,
        'https://i-giadinh.vnecdn.net/2022/04/20/Buoc-9-9-3230-1650439557.jpg',
        'Mì Ý với sốt cà chua tươi và rau củ.',
        0
    ),
    (
        10,
        'Bò lúc lắc',
        2,
        150000,
        'https://comnieubepviet.com/thumbs/670x600x2/upload/product/bepviet2318-copy-2756.jpg',
        'Thịt bò mềm, đậm đà, dùng kèm cơm.',
        0
    ),
    (
        11,
        'Chè khúc bạch',
        3,
        35000,
        'https://cdn.mediamart.vn/images/news/huong-dan-cach-lam-che-khuc-bach-thanh-mat-thom-ngon-hap-dan_ada6ac3c.png',
        'Món tráng miệng thanh mát.',
        0
    );

-- --------------------------------------------------------

--
-- Table structure for table `orders`
--

CREATE TABLE `orders` (
    `id` int(11) NOT NULL,
    `staffID` int(11) NOT NULL,
    `customerID` int(11) NOT NULL,
    `tableID` int(3) NOT NULL,
    `discountID` int(11) DEFAULT NULL,
    `dateOrder` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
    `status` enum(
        'Pending confirmation',
        'Out for Delivery',
        'Delivery Successful',
        'Cancelled',
        'Pending Payment'
    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'Pending confirmation',
    `totalPrice` double NOT NULL,
    `notes` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

--
-- Dumping data for table `orders`
--

INSERT INTO
    `orders` (
        `id`,
        `staffID`,
        `customerID`,
        `tableID`,
        `discountID`,
        `dateOrder`,
        `status`,
        `totalPrice`,
        `notes`
    )
VALUES (
        1,
        4,
        1,
        2,
        1,
        '2025-07-09 15:21:29',
        'Pending confirmation',
        600000,
        'Không hành'
    ),
    (
        2,
        4,
        2,
        4,
        NULL,
        '2025-07-09 15:22:06',
        'Pending confirmation',
        250000,
        NULL
    ),
    (
        3,
        6,
        3,
        1,
        NULL,
        '2025-07-09 15:22:09',
        'Pending confirmation',
        120000,
        NULL
    ),
    (
        4,
        4,
        5,
        5,
        NULL,
        '2025-07-09 15:22:13',
        'Pending confirmation',
        0,
        'Khách hủy'
    ),
    (
        5,
        6,
        1,
        2,
        1,
        '2025-07-09 15:22:16',
        'Pending confirmation',
        750000,
        NULL
    ),
    (
        6,
        4,
        4,
        3,
        NULL,
        '2025-07-09 15:22:20',
        'Pending confirmation',
        300000,
        'Có thêm nước đá'
    );

-- --------------------------------------------------------

--
-- Table structure for table `order_detail`
--

CREATE TABLE `order_detail` (
    `orderID` int(11) NOT NULL,
    `dishID` int(11) NOT NULL,
    `quantity` int(11) NOT NULL,
    `price` double NOT NULL
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

--
-- Dumping data for table `order_detail`
--

INSERT INTO
    `order_detail` (
        `orderID`,
        `dishID`,
        `quantity`,
        `price`
    )
VALUES (1, 2, 2, 80000),
    (1, 10, 1, 150000),
    (1, 5, 3, 40000),
    (1, 4, 2, 30000),
    (2, 1, 3, 55000),
    (2, 5, 2, 40000),
    (3, 6, 1, 60000),
    (3, 7, 1, 75000),
    (5, 8, 2, 180000),
    (5, 9, 3, 85000),
    (5, 1, 1, 55000),
    (6, 3, 2, 95000),
    (6, 11, 3, 35000);

-- --------------------------------------------------------

--
-- Table structure for table `reviews`
--

CREATE TABLE `reviews` (
    `id` int(11) NOT NULL,
    `customerID` int(11) NOT NULL,
    `dishID` int(11) NOT NULL,
    `rating` int(1) NOT NULL,
    `comment` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
    `created_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
    `status` tinyint(1) DEFAULT 0
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

--
-- Dumping data for table `reviews`
--

INSERT INTO
    `reviews` (
        `id`,
        `customerID`,
        `dishID`,
        `rating`,
        `comment`,
        `created_at`,
        `status`
    )
VALUES (
        1,
        1,
        2,
        5,
        'Phở rất ngon và đậm đà!',
        '2025-07-08 14:45:00',
        0
    ),
    (
        2,
        2,
        1,
        4,
        'Gỏi cuốn tươi ngon, chấm vừa.',
        '2025-07-08 15:30:00',
        0
    ),
    (
        3,
        3,
        6,
        5,
        'Súp bí đỏ rất béo và thơm.',
        '2025-07-08 16:30:00',
        0
    ),
    (
        4,
        1,
        10,
        4,
        'Bò lúc lắc mềm, nhưng hơi ít.',
        '2025-07-08 15:00:00',
        0
    ),
    (
        5,
        4,
        3,
        3,
        'Cơm chiên tạm được.',
        '2025-07-09 11:45:00',
        0
    );

-- --------------------------------------------------------

--
-- Table structure for table `roles`
--

CREATE TABLE `roles` (
    `id` int(11) NOT NULL,
    `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

--
-- Dumping data for table `roles`
--

INSERT INTO
    `roles` (`id`, `name`)
VALUES (1, 'Admin'),
    (2, 'Manager'),
    (3, 'Chef'),
    (4, 'Waiter'),
    (5, 'Cashier');

-- --------------------------------------------------------

--
-- Table structure for table `staff`
--

CREATE TABLE `staff` (
    `id` int(11) NOT NULL,
    `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
    `email` varchar(255) NOT NULL,
    `phoneNumber` varchar(10) NOT NULL,
    `username` varchar(255) NOT NULL,
    `password` varchar(255) NOT NULL,
    `roleID` int(11) DEFAULT 1,
    `status` tinyint(1) DEFAULT 0
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

--
-- Dumping data for table `staff`
--

INSERT INTO
    `staff` (
        `id`,
        `name`,
        `email`,
        `phoneNumber`,
        `username`,
        `password`,
        `roleID`,
        `status`
    )
VALUES (
        1,
        'Nguyễn Văn A',
        'admin.a@res.com',
        '0901234567',
        'admin_a',
        'pass123',
        1,
        1
    ),
    (
        2,
        'Trần Thị B',
        'manager.b@res.com',
        '0902345678',
        'manager_b',
        'pass123',
        2,
        1
    ),
    (
        3,
        'Lê Văn C',
        'chef.c@res.com',
        '0903456789',
        'chef_c',
        'pass123',
        3,
        1
    ),
    (
        4,
        'Phạm Thị D',
        'waiter.d@res.com',
        '0904567890',
        'waiter_d',
        'pass123',
        4,
        1
    ),
    (
        5,
        'Hoàng Văn E',
        'cashier.e@res.com',
        '0905678901',
        'cashier_e',
        'pass123',
        5,
        1
    ),
    (
        6,
        'Phan Thị G',
        'waiter.g@res.com',
        '0906789012',
        'waiter_g',
        'pass123',
        4,
        1
    ),
    (
        7,
        'Đỗ Văn H',
        'chef.h@res.com',
        '0907890123',
        'chef_h',
        'pass123',
        3,
        1
    );

-- --------------------------------------------------------

--
-- Table structure for table `tables`
--

CREATE TABLE `tables` (
    `id` int(3) NOT NULL,
    `status` enum(
        'Empty',
        'Booked',
        'Deleted',
        'Taken'
    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'Empty'
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

--
-- Dumping data for table `tables`
--

INSERT INTO
    `tables` (`id`, `status`)
VALUES (1, 'Empty'),
    (2, 'Empty'),
    (3, 'Empty'),
    (4, 'Empty'),
    (5, 'Empty'),
    (6, 'Booked'),
    (7, 'Taken');

-- --------------------------------------------------------

--
-- Table structure for table `__efmigrationshistory`
--

CREATE TABLE `__efmigrationshistory` (
    `MigrationId` varchar(150) NOT NULL,
    `ProductVersion` varchar(32) NOT NULL
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `categories`
--
ALTER TABLE `categories` ADD PRIMARY KEY (`id`);

--
-- Indexes for table `customer`
--
ALTER TABLE `customer` ADD PRIMARY KEY (`id`);

--
-- Indexes for table `discount`
--
ALTER TABLE `discount` ADD PRIMARY KEY (`id`);

--
-- Indexes for table `discount_detail_dish`
--
ALTER TABLE `discount_detail_dish`
ADD KEY `discountID` (`discountID`),
ADD KEY `dishID` (`dishID`);

--
-- Indexes for table `discount_detail_order`
--
ALTER TABLE `discount_detail_order`
ADD KEY `discountID` (`discountID`);

--
-- Indexes for table `dish`
--
ALTER TABLE `dish`
ADD PRIMARY KEY (`id`),
ADD KEY `categoryID` (`categoryID`);

--
-- Indexes for table `orders`
--
ALTER TABLE `orders`
ADD PRIMARY KEY (`id`),
ADD KEY `staffID` (`staffID`),
ADD KEY `discountID` (`discountID`),
ADD KEY `customerID` (`customerID`),
ADD KEY `tableID` (`tableID`);

--
-- Indexes for table `order_detail`
--
ALTER TABLE `order_detail`
ADD KEY `orderID` (`orderID`),
ADD KEY `dishID` (`dishID`);

--
-- Indexes for table `reviews`
--
ALTER TABLE `reviews`
ADD PRIMARY KEY (`id`),
ADD KEY `customerID` (`customerID`),
ADD KEY `dishID` (`dishID`);

--
-- Indexes for table `roles`
--
ALTER TABLE `roles` ADD PRIMARY KEY (`id`);

--
-- Indexes for table `staff`
--
ALTER TABLE `staff`
ADD PRIMARY KEY (`id`),
ADD UNIQUE KEY `email` (`email`),
ADD KEY `roleID` (`roleID`);

--
-- Indexes for table `tables`
--
ALTER TABLE `tables` ADD PRIMARY KEY (`id`);

--
-- Indexes for table `__efmigrationshistory`
--
ALTER TABLE `__efmigrationshistory` ADD PRIMARY KEY (`MigrationId`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `categories`
--
ALTER TABLE `categories`
MODIFY `id` int(11) NOT NULL AUTO_INCREMENT,
AUTO_INCREMENT = 16;

--
-- AUTO_INCREMENT for table `customer`
--
ALTER TABLE `customer`
MODIFY `id` int(11) NOT NULL AUTO_INCREMENT,
AUTO_INCREMENT = 6;

--
-- AUTO_INCREMENT for table `discount`
--
ALTER TABLE `discount`
MODIFY `id` int(11) NOT NULL AUTO_INCREMENT,
AUTO_INCREMENT = 5;

--
-- AUTO_INCREMENT for table `dish`
--
ALTER TABLE `dish`
MODIFY `id` int(11) NOT NULL AUTO_INCREMENT,
AUTO_INCREMENT = 12;

--
-- AUTO_INCREMENT for table `orders`
--
ALTER TABLE `orders`
MODIFY `id` int(11) NOT NULL AUTO_INCREMENT,
AUTO_INCREMENT = 7;

--
-- AUTO_INCREMENT for table `reviews`
--
ALTER TABLE `reviews`
MODIFY `id` int(11) NOT NULL AUTO_INCREMENT,
AUTO_INCREMENT = 6;

--
-- AUTO_INCREMENT for table `staff`
--
ALTER TABLE `staff`
MODIFY `id` int(11) NOT NULL AUTO_INCREMENT,
AUTO_INCREMENT = 8;

--
-- AUTO_INCREMENT for table `tables`
--
ALTER TABLE `tables`
MODIFY `id` int(3) NOT NULL AUTO_INCREMENT,
AUTO_INCREMENT = 8;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `discount_detail_dish`
--
ALTER TABLE `discount_detail_dish`
ADD CONSTRAINT `discount_detail_dish_discount` FOREIGN KEY (`discountID`) REFERENCES `discount` (`id`),
ADD CONSTRAINT `discount_detail_dish_dish` FOREIGN KEY (`dishID`) REFERENCES `dish` (`id`);

--
-- Constraints for table `discount_detail_order`
--
ALTER TABLE `discount_detail_order`
ADD CONSTRAINT `discount_detail_order_discount` FOREIGN KEY (`discountID`) REFERENCES `discount` (`id`);

--
-- Constraints for table `dish`
--
ALTER TABLE `dish`
ADD CONSTRAINT `dish_categories` FOREIGN KEY (`categoryID`) REFERENCES `categories` (`id`);

--
-- Constraints for table `orders`
--
ALTER TABLE `orders`
ADD CONSTRAINT `orders_customer` FOREIGN KEY (`customerID`) REFERENCES `customer` (`id`),
ADD CONSTRAINT `orders_discount` FOREIGN KEY (`discountID`) REFERENCES `discount` (`id`),
ADD CONSTRAINT `orders_staff` FOREIGN KEY (`staffID`) REFERENCES `staff` (`id`),
ADD CONSTRAINT `orders_tables` FOREIGN KEY (`tableID`) REFERENCES `tables` (`id`);

--
-- Constraints for table `order_detail`
--
ALTER TABLE `order_detail`
ADD CONSTRAINT `order_detail_dish` FOREIGN KEY (`dishID`) REFERENCES `dish` (`id`),
ADD CONSTRAINT `order_detail_orders` FOREIGN KEY (`orderID`) REFERENCES `orders` (`id`);

--
-- Constraints for table `reviews`
--
ALTER TABLE `reviews`
ADD CONSTRAINT `reviews_customer` FOREIGN KEY (`customerID`) REFERENCES `customer` (`id`),
ADD CONSTRAINT `reviews_dish` FOREIGN KEY (`dishID`) REFERENCES `dish` (`id`);

--
-- Constraints for table `staff`
--
ALTER TABLE `staff`
ADD CONSTRAINT `staff_roles` FOREIGN KEY (`roleID`) REFERENCES `roles` (`id`);

COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */
;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */
;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */
;
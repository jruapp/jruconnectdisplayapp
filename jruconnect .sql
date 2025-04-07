-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Sep 01, 2024 at 09:59 AM
-- Server version: 11.5.2-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `jruconnect`
--

-- --------------------------------------------------------

--
-- Table structure for table `django_content_type`
--

CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `django_migrations`
--

CREATE TABLE `django_migrations` (
  `id` bigint(20) NOT NULL,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `engagement`
--

CREATE TABLE `engagement` (
  `engagement_id` int(11) NOT NULL,
  `product_id` int(11) DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  `type` enum('like','click') NOT NULL,
  `date_created` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `engagement`
--

INSERT INTO `engagement` (`engagement_id`, `product_id`, `user_id`, `type`, `date_created`) VALUES
(1, 1, 2, 'like', '2024-08-27 12:00:00'),
(2, 2, 3, 'click', '2024-08-27 12:05:00'),
(3, 3, 4, 'like', '2024-08-27 12:10:00'),
(4, 4, 1, 'click', '2024-08-27 12:15:00'),
(5, 5, 5, 'like', '2024-08-27 12:20:00'),
(6, 4, 4, 'like', '2024-09-01 04:04:19');

-- --------------------------------------------------------

--
-- Table structure for table `feedback`
--

CREATE TABLE `feedback` (
  `feedback_id` int(11) NOT NULL,
  `product_id` int(11) DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  `rating` int(11) DEFAULT NULL CHECK (`rating` >= 1 and `rating` <= 5),
  `comment` text DEFAULT NULL,
  `date_created` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `feedback`
--

INSERT INTO `feedback` (`feedback_id`, `product_id`, `user_id`, `rating`, `comment`, `date_created`) VALUES
(1, 1, 2, 5, 'Great product!', '2024-08-27 13:00:00'),
(2, 2, 3, 4, 'Good value for money.', '2024-08-27 13:05:00'),
(3, 3, 4, 3, 'Average quality.', '2024-08-27 13:10:00'),
(4, 4, 1, 2, 'Not as expected.', '2024-08-27 13:15:00'),
(5, 5, 5, 1, 'Very disappointed.', '2024-08-27 13:20:00'),
(6, 3, 4, 5, 'fdgdfg', '2024-09-01 04:04:27');

-- --------------------------------------------------------

--
-- Table structure for table `messages`
--

CREATE TABLE `messages` (
  `message_id` int(11) NOT NULL,
  `sender_id` int(11) DEFAULT NULL,
  `receiver_id` int(11) DEFAULT NULL,
  `content` text NOT NULL,
  `date_sent` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `messages`
--

INSERT INTO `messages` (`message_id`, `sender_id`, `receiver_id`, `content`, `date_sent`) VALUES
(1, 5, 4, 'Hello, how are youewrewr', '2024-08-27 14:00:00'),
(2, 2, 3, 'Can you send me the details?', '2024-08-27 14:05:00'),
(3, 3, 4, 'Thank you for your help!', '2024-08-27 14:10:00'),
(4, 4, 1, 'When can we meet?', '2024-08-27 14:15:00'),
(5, 5, 2, 'Let me know if you need anything.', '2024-08-27 14:20:00');

-- --------------------------------------------------------

--
-- Table structure for table `products`
--

CREATE TABLE `products` (
  `product_id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `title` varchar(100) NOT NULL,
  `description` text NOT NULL,
  `category` varchar(50) DEFAULT NULL,
  `price` decimal(10,2) DEFAULT NULL,
  `stock` int(15) NOT NULL,
  `location` varchar(100) DEFAULT NULL,
  `image_url` varchar(255) DEFAULT NULL,
  `date_posted` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `products`
--

INSERT INTO `products` (`product_id`, `user_id`, `title`, `description`, `category`, `price`, `stock`, `location`, `image_url`, `date_posted`) VALUES
(1, 1, 'Laptop', 'High-performance laptop', 'Electronics', 999.99, 0, 'New York, NY', 'http://example.com/laptop.jpg', '2024-08-27 15:00:00'),
(2, 2, 'Smartphone', 'Latest model smartphone', 'Electronics', 799.99, 0, 'Los Angeles, CA', 'http://example.com/smartphone.jpg', '2024-08-27 15:05:00'),
(3, 3, 'Bicycle', 'Mountain bike', 'Sports', 499.99, 0, 'Chicago, IL', 'http://example.com/bicycle.jpg', '2024-08-27 15:10:00'),
(4, 4, 'Desk', 'Office desk', 'Furniture', 199.99, 0, 'Houston, TX', 'http://example.com/desk.jpg', '2024-08-27 15:15:00'),
(5, 5, 'Chair', 'Ergonomic office chair', 'Furniture', 149.99, 0, 'Phoenix, AZ', 'http://example.com/chair.jpg', '2024-08-27 15:20:00');

-- --------------------------------------------------------

--
-- Stand-in structure for view `product_engagement_summary`
-- (See below for the actual view)
--
CREATE TABLE `product_engagement_summary` (
`product_id` int(11)
,`user_id` int(11)
,`title` varchar(100)
,`description` text
,`stock` int(15)
,`category` varchar(50)
,`price` decimal(10,2)
,`location` varchar(100)
,`image_url` varchar(255)
,`date_posted` datetime
,`purchase_count` bigint(21)
,`likes_count` bigint(21)
);

-- --------------------------------------------------------

--
-- Table structure for table `profiles`
--

CREATE TABLE `profiles` (
  `profile_id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `bio` text DEFAULT NULL,
  `profile_picture` varchar(255) DEFAULT NULL,
  `contact_number` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `profiles`
--

INSERT INTO `profiles` (`profile_id`, `user_id`, `bio`, `profile_picture`, `contact_number`) VALUES
(1, 1, 'Tech enthusiast', 'http://example.com/profile1.jpg', '123-456-7890'),
(2, 2, 'Gadget loverasdasasdasdas', 'http://example.com/profile2.jpg', '234-567-8901'),
(3, 3, 'Sports fanss', 'http://example.com/profile3.jpg', '345-678-9012s'),
(4, 4, 'Furniture designer', 'http://example.com/profile4.jpg', '456-789-0123'),
(5, 5, 'Office worker', 'http://example.com/profile5.jpg', '567-890-1234');

-- --------------------------------------------------------

--
-- Table structure for table `support_inquiries`
--

CREATE TABLE `support_inquiries` (
  `inquiry_id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `subject` varchar(100) DEFAULT NULL,
  `message` text DEFAULT NULL,
  `status` enum('open','closed') DEFAULT 'open',
  `date_created` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `support_inquiries`
--

INSERT INTO `support_inquiries` (`inquiry_id`, `user_id`, `subject`, `message`, `status`, `date_created`) VALUES
(3, 5, 'Issue with orderass', 'I haven\'t received my order yet.sss', 'open', '2024-08-27 16:00:00'),
(4, 2, 'Account problems', 'Unable to log in.', 'open', '2024-08-27 16:05:00'),
(5, 3, 'Payment error', 'My payment was declined.', 'open', '2024-08-27 16:10:00'),
(6, 4, 'Shipping delay', 'My package is delayed.', 'open', '2024-08-27 16:15:00'),
(7, 5, 'Wrong item received', 'I received the wrong product.', 'open', '2024-08-27 16:20:00');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `user_id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `email` varchar(100) NOT NULL,
  `full_name` varchar(100) NOT NULL,
  `role` enum('student','admin') NOT NULL,
  `verified` tinyint(1) DEFAULT 0,
  `last_login` datetime DEFAULT NULL,
  `date_created` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`user_id`, `username`, `password_hash`, `email`, `full_name`, `role`, `verified`, `last_login`, `date_created`) VALUES
(1, 'johndoe', 'passwordhash1', 'johndoe@example.com', 'John Doe', 'student', 1, '2024-08-27 10:00:00', '2024-08-27 09:00:00'),
(2, 'janedoe', 'passwordhash2', 'janedoe@example.com', 'Jane Doe', 'student', 0, NULL, '2024-08-27 09:05:00'),
(3, 'admin1', 'passwordhash3', 'admin1@example.com', 'Admin One', 'admin', 1, '2024-08-27 11:00:00', '2024-08-27 09:10:00'),
(4, 'student1', 'passwordhash4', 'student1@example.com', 'Student One', 'student', 0, NULL, '2024-08-27 09:15:00'),
(5, 'student2', 'passwordhash5', 'student2@example.com', 'Student Two', 'admin', 1, '2024-08-27 12:00:00', '2024-08-27 09:20:00'),
(13, 'dsfds', 'dfdsf', 'sdfsdfs@gmail.com', 'fdsf', 'admin', 0, NULL, '2024-09-01 07:48:39');

-- --------------------------------------------------------

--
-- Structure for view `product_engagement_summary`
--
DROP TABLE IF EXISTS `product_engagement_summary`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `product_engagement_summary`  AS SELECT `p`.`product_id` AS `product_id`, `p`.`user_id` AS `user_id`, `p`.`title` AS `title`, `p`.`description` AS `description`, `p`.`stock` AS `stock`, `p`.`category` AS `category`, `p`.`price` AS `price`, `p`.`location` AS `location`, `p`.`image_url` AS `image_url`, `p`.`date_posted` AS `date_posted`, coalesce(`fb`.`feedback_count`,0) AS `purchase_count`, coalesce(`e`.`likes_count`,0) AS `likes_count` FROM ((`products` `p` left join (select `feedback`.`product_id` AS `product_id`,count(0) AS `feedback_count` from `feedback` group by `feedback`.`product_id`) `fb` on(`p`.`product_id` = `fb`.`product_id`)) left join (select `engagement`.`product_id` AS `product_id`,count(0) AS `likes_count` from `engagement` where `engagement`.`type` = 'like' group by `engagement`.`product_id`) `e` on(`p`.`product_id` = `e`.`product_id`)) ;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `django_content_type`
--
ALTER TABLE `django_content_type`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `django_migrations`
--
ALTER TABLE `django_migrations`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `engagement`
--
ALTER TABLE `engagement`
  ADD PRIMARY KEY (`engagement_id`),
  ADD KEY `product_id` (`product_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `feedback`
--
ALTER TABLE `feedback`
  ADD PRIMARY KEY (`feedback_id`),
  ADD KEY `product_id` (`product_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `messages`
--
ALTER TABLE `messages`
  ADD PRIMARY KEY (`message_id`),
  ADD KEY `sender_id` (`sender_id`),
  ADD KEY `receiver_id` (`receiver_id`);

--
-- Indexes for table `products`
--
ALTER TABLE `products`
  ADD PRIMARY KEY (`product_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `profiles`
--
ALTER TABLE `profiles`
  ADD PRIMARY KEY (`profile_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `support_inquiries`
--
ALTER TABLE `support_inquiries`
  ADD PRIMARY KEY (`inquiry_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`user_id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `django_content_type`
--
ALTER TABLE `django_content_type`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `django_migrations`
--
ALTER TABLE `django_migrations`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `engagement`
--
ALTER TABLE `engagement`
  MODIFY `engagement_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `feedback`
--
ALTER TABLE `feedback`
  MODIFY `feedback_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `messages`
--
ALTER TABLE `messages`
  MODIFY `message_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `products`
--
ALTER TABLE `products`
  MODIFY `product_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `profiles`
--
ALTER TABLE `profiles`
  MODIFY `profile_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT for table `support_inquiries`
--
ALTER TABLE `support_inquiries`
  MODIFY `inquiry_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `engagement`
--
ALTER TABLE `engagement`
  ADD CONSTRAINT `engagement_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`),
  ADD CONSTRAINT `engagement_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);

--
-- Constraints for table `feedback`
--
ALTER TABLE `feedback`
  ADD CONSTRAINT `feedback_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`),
  ADD CONSTRAINT `feedback_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);

--
-- Constraints for table `messages`
--
ALTER TABLE `messages`
  ADD CONSTRAINT `messages_ibfk_1` FOREIGN KEY (`sender_id`) REFERENCES `users` (`user_id`),
  ADD CONSTRAINT `messages_ibfk_2` FOREIGN KEY (`receiver_id`) REFERENCES `users` (`user_id`);

--
-- Constraints for table `products`
--
ALTER TABLE `products`
  ADD CONSTRAINT `products_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);

--
-- Constraints for table `profiles`
--
ALTER TABLE `profiles`
  ADD CONSTRAINT `profiles_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);

--
-- Constraints for table `support_inquiries`
--
ALTER TABLE `support_inquiries`
  ADD CONSTRAINT `support_inquiries_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

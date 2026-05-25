/*
 Navicat Premium Data Transfer

 Source Server         : 本地-lqz用户
 Source Server Type    : MySQL
 Source Server Version : 50728
 Source Host           : localhost:3306
 Source Schema         : luffy

 Target Server Type    : MySQL
 Target Server Version : 50728
 File Encoding         : 65001

 Date: 06/05/2022 17:31:37
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for auth_group
-- ----------------------------
DROP TABLE IF EXISTS `auth_group`;
CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of auth_group
-- ----------------------------
BEGIN;
COMMIT;

-- ----------------------------
-- Table structure for auth_group_permissions
-- ----------------------------
DROP TABLE IF EXISTS `auth_group_permissions`;
CREATE TABLE `auth_group_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of auth_group_permissions
-- ----------------------------
BEGIN;
COMMIT;

-- ----------------------------
-- Table structure for auth_permission
-- ----------------------------
DROP TABLE IF EXISTS `auth_permission`;
CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=57 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of auth_permission
-- ----------------------------
BEGIN;
INSERT INTO `auth_permission` VALUES (1, 'Can add log entry', 1, 'add_logentry');
INSERT INTO `auth_permission` VALUES (2, 'Can change log entry', 1, 'change_logentry');
INSERT INTO `auth_permission` VALUES (3, 'Can delete log entry', 1, 'delete_logentry');
INSERT INTO `auth_permission` VALUES (4, 'Can view log entry', 1, 'view_logentry');
INSERT INTO `auth_permission` VALUES (5, 'Can add permission', 2, 'add_permission');
INSERT INTO `auth_permission` VALUES (6, 'Can change permission', 2, 'change_permission');
INSERT INTO `auth_permission` VALUES (7, 'Can delete permission', 2, 'delete_permission');
INSERT INTO `auth_permission` VALUES (8, 'Can view permission', 2, 'view_permission');
INSERT INTO `auth_permission` VALUES (9, 'Can add group', 3, 'add_group');
INSERT INTO `auth_permission` VALUES (10, 'Can change group', 3, 'change_group');
INSERT INTO `auth_permission` VALUES (11, 'Can delete group', 3, 'delete_group');
INSERT INTO `auth_permission` VALUES (12, 'Can view group', 3, 'view_group');
INSERT INTO `auth_permission` VALUES (13, 'Can add content type', 4, 'add_contenttype');
INSERT INTO `auth_permission` VALUES (14, 'Can change content type', 4, 'change_contenttype');
INSERT INTO `auth_permission` VALUES (15, 'Can delete content type', 4, 'delete_contenttype');
INSERT INTO `auth_permission` VALUES (16, 'Can view content type', 4, 'view_contenttype');
INSERT INTO `auth_permission` VALUES (17, 'Can add session', 5, 'add_session');
INSERT INTO `auth_permission` VALUES (18, 'Can change session', 5, 'change_session');
INSERT INTO `auth_permission` VALUES (19, 'Can delete session', 5, 'delete_session');
INSERT INTO `auth_permission` VALUES (20, 'Can view session', 5, 'view_session');
INSERT INTO `auth_permission` VALUES (21, 'Can add 用户表', 6, 'add_user');
INSERT INTO `auth_permission` VALUES (22, 'Can change 用户表', 6, 'change_user');
INSERT INTO `auth_permission` VALUES (23, 'Can delete 用户表', 6, 'delete_user');
INSERT INTO `auth_permission` VALUES (24, 'Can view 用户表', 6, 'view_user');
INSERT INTO `auth_permission` VALUES (25, 'Can add banner', 7, 'add_banner');
INSERT INTO `auth_permission` VALUES (26, 'Can change banner', 7, 'change_banner');
INSERT INTO `auth_permission` VALUES (27, 'Can delete banner', 7, 'delete_banner');
INSERT INTO `auth_permission` VALUES (28, 'Can view banner', 7, 'view_banner');
INSERT INTO `auth_permission` VALUES (29, 'Can add 导师', 8, 'add_teacher');
INSERT INTO `auth_permission` VALUES (30, 'Can change 导师', 8, 'change_teacher');
INSERT INTO `auth_permission` VALUES (31, 'Can delete 导师', 8, 'delete_teacher');
INSERT INTO `auth_permission` VALUES (32, 'Can view 导师', 8, 'view_teacher');
INSERT INTO `auth_permission` VALUES (33, 'Can add 课程', 9, 'add_course');
INSERT INTO `auth_permission` VALUES (34, 'Can change 课程', 9, 'change_course');
INSERT INTO `auth_permission` VALUES (35, 'Can delete 课程', 9, 'delete_course');
INSERT INTO `auth_permission` VALUES (36, 'Can view 课程', 9, 'view_course');
INSERT INTO `auth_permission` VALUES (37, 'Can add 章节', 10, 'add_coursechapter');
INSERT INTO `auth_permission` VALUES (38, 'Can change 章节', 10, 'change_coursechapter');
INSERT INTO `auth_permission` VALUES (39, 'Can delete 章节', 10, 'delete_coursechapter');
INSERT INTO `auth_permission` VALUES (40, 'Can view 章节', 10, 'view_coursechapter');
INSERT INTO `auth_permission` VALUES (41, 'Can add 课时', 11, 'add_coursesection');
INSERT INTO `auth_permission` VALUES (42, 'Can change 课时', 11, 'change_coursesection');
INSERT INTO `auth_permission` VALUES (43, 'Can delete 课时', 11, 'delete_coursesection');
INSERT INTO `auth_permission` VALUES (44, 'Can view 课时', 11, 'view_coursesection');
INSERT INTO `auth_permission` VALUES (45, 'Can add 分类', 12, 'add_coursecategory');
INSERT INTO `auth_permission` VALUES (46, 'Can change 分类', 12, 'change_coursecategory');
INSERT INTO `auth_permission` VALUES (47, 'Can delete 分类', 12, 'delete_coursecategory');
INSERT INTO `auth_permission` VALUES (48, 'Can view 分类', 12, 'view_coursecategory');
INSERT INTO `auth_permission` VALUES (49, 'Can add 订单记录', 13, 'add_order');
INSERT INTO `auth_permission` VALUES (50, 'Can change 订单记录', 13, 'change_order');
INSERT INTO `auth_permission` VALUES (51, 'Can delete 订单记录', 13, 'delete_order');
INSERT INTO `auth_permission` VALUES (52, 'Can view 订单记录', 13, 'view_order');
INSERT INTO `auth_permission` VALUES (53, 'Can add 订单详情', 14, 'add_orderdetail');
INSERT INTO `auth_permission` VALUES (54, 'Can change 订单详情', 14, 'change_orderdetail');
INSERT INTO `auth_permission` VALUES (55, 'Can delete 订单详情', 14, 'delete_orderdetail');
INSERT INTO `auth_permission` VALUES (56, 'Can view 订单详情', 14, 'view_orderdetail');
COMMIT;

-- ----------------------------
-- Table structure for django_admin_log
-- ----------------------------
DROP TABLE IF EXISTS `django_admin_log`;
CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_luffy_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_luffy_user_id` FOREIGN KEY (`user_id`) REFERENCES `luffy_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=52 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of django_admin_log
-- ----------------------------
BEGIN;
INSERT INTO `django_admin_log` VALUES (1, '2022-04-20 12:26:39.337091', '1', 'banner1', 1, '[{\"added\": {}}]', 7, 1);
INSERT INTO `django_admin_log` VALUES (2, '2022-04-20 12:26:59.824548', '2', 'banner2', 1, '[{\"added\": {}}]', 7, 1);
INSERT INTO `django_admin_log` VALUES (3, '2022-04-20 12:27:18.960951', '3', 'banner3', 1, '[{\"added\": {}}]', 7, 1);
INSERT INTO `django_admin_log` VALUES (4, '2022-04-20 12:27:38.831043', '4', 'banner4', 1, '[{\"added\": {}}]', 7, 1);
INSERT INTO `django_admin_log` VALUES (5, '2022-04-24 10:21:50.322449', '1', 'banner1', 2, '[{\"changed\": {\"fields\": [\"link\"]}}]', 7, 1);
INSERT INTO `django_admin_log` VALUES (6, '2022-04-28 12:06:36.570133', '4', 'DRF从入门到放弃', 1, '[{\"added\": {}}]', 9, 1);
INSERT INTO `django_admin_log` VALUES (7, '2022-04-28 12:07:33.315740', '3', 'Go语言', 1, '[{\"added\": {}}]', 12, 1);
INSERT INTO `django_admin_log` VALUES (8, '2022-04-28 12:08:36.682642', '5', 'Linux系统基础5周入门精讲:(第2章)Linux5周第二章', 1, '[{\"added\": {}}]', 10, 1);
INSERT INTO `django_admin_log` VALUES (9, '2022-04-28 12:09:19.325246', '6', 'Python项目实战:(第2章)py实战项目第二章', 1, '[{\"added\": {}}]', 10, 1);
INSERT INTO `django_admin_log` VALUES (10, '2022-04-28 12:09:32.533680', '7', 'Python项目实战:(第3章)py实战项目第三章', 1, '[{\"added\": {}}]', 10, 1);
INSERT INTO `django_admin_log` VALUES (11, '2022-04-28 12:09:55.498613', '8', 'DRF从入门到放弃:(第1章)drf入门1', 1, '[{\"added\": {}}]', 10, 1);
INSERT INTO `django_admin_log` VALUES (12, '2022-04-28 12:10:08.491400', '9', 'DRF从入门到放弃:(第2章)drf入门2', 1, '[{\"added\": {}}]', 10, 1);
INSERT INTO `django_admin_log` VALUES (13, '2022-04-28 12:10:22.089280', '10', 'DRF从入门到放弃:(第3章)drf入门3', 1, '[{\"added\": {}}]', 10, 1);
INSERT INTO `django_admin_log` VALUES (14, '2022-04-28 12:10:33.565009', '11', 'DRF从入门到放弃:(第4章)drf入门4', 1, '[{\"added\": {}}]', 10, 1);
INSERT INTO `django_admin_log` VALUES (15, '2022-04-28 12:10:43.243483', '12', 'DRF从入门到放弃:(第5章)drf入门5', 1, '[{\"added\": {}}]', 10, 1);
INSERT INTO `django_admin_log` VALUES (16, '2022-04-28 12:12:01.309390', '7', 'Linux系统基础5周入门精讲:(第2章)Linux5周第二章-文件操作', 1, '[{\"added\": {}}]', 11, 1);
INSERT INTO `django_admin_log` VALUES (17, '2022-04-28 12:12:11.295332', '8', 'Linux系统基础5周入门精讲:(第2章)Linux5周第二章-软件操作', 1, '[{\"added\": {}}]', 11, 1);
INSERT INTO `django_admin_log` VALUES (18, '2022-04-28 12:12:26.330255', '9', 'DRF从入门到放弃:(第1章)drf入门1-请求响应', 1, '[{\"added\": {}}]', 11, 1);
INSERT INTO `django_admin_log` VALUES (19, '2022-04-28 12:12:36.367205', '10', 'DRF从入门到放弃:(第1章)drf入门1-序列化类', 1, '[{\"added\": {}}]', 11, 1);
INSERT INTO `django_admin_log` VALUES (20, '2022-04-28 12:12:48.317342', '11', 'DRF从入门到放弃:(第2章)drf入门2-三大认证', 1, '[{\"added\": {}}]', 11, 1);
INSERT INTO `django_admin_log` VALUES (21, '2022-04-28 12:13:06.887166', '12', 'DRF从入门到放弃:(第2章)drf入门2-认证', 1, '[{\"added\": {}}]', 11, 1);
INSERT INTO `django_admin_log` VALUES (22, '2022-04-28 12:13:15.802118', '13', 'DRF从入门到放弃:(第3章)drf入门3-jwt认证', 1, '[{\"added\": {}}]', 11, 1);
INSERT INTO `django_admin_log` VALUES (23, '2022-04-28 12:13:27.855218', '14', 'DRF从入门到放弃:(第3章)drf入门3-jwt认证2', 1, '[{\"added\": {}}]', 11, 1);
INSERT INTO `django_admin_log` VALUES (24, '2022-04-28 12:13:37.295584', '15', 'DRF从入门到放弃:(第4章)drf入门4-后台管理', 1, '[{\"added\": {}}]', 11, 1);
INSERT INTO `django_admin_log` VALUES (25, '2022-04-28 12:13:51.196831', '16', 'DRF从入门到放弃:(第4章)drf入门4-后台管理2', 1, '[{\"added\": {}}]', 11, 1);
INSERT INTO `django_admin_log` VALUES (26, '2022-04-28 12:14:05.339795', '17', 'DRF从入门到放弃:(第5章)drf入门5-rbac1', 1, '[{\"added\": {}}]', 11, 1);
INSERT INTO `django_admin_log` VALUES (27, '2022-04-28 12:14:14.042457', '18', 'DRF从入门到放弃:(第5章)drf入门5-rbac2', 1, '[{\"added\": {}}]', 11, 1);
INSERT INTO `django_admin_log` VALUES (28, '2022-04-28 12:35:44.322274', '5', 'Go语言从入门到入坑', 1, '[{\"added\": {}}]', 9, 1);
INSERT INTO `django_admin_log` VALUES (29, '2022-04-28 12:36:04.813769', '4', 'DRF从入门到放弃', 2, '[{\"changed\": {\"fields\": [\"students\", \"price\"]}}]', 9, 1);
INSERT INTO `django_admin_log` VALUES (30, '2022-04-28 12:36:32.604942', '1', 'Python开发21天入门', 2, '[{\"changed\": {\"fields\": [\"price\"]}}]', 9, 1);
INSERT INTO `django_admin_log` VALUES (31, '2022-04-28 12:36:58.510433', '13', 'Go语言从入门到入坑:(第1章)go第一章', 1, '[{\"added\": {}}]', 10, 1);
INSERT INTO `django_admin_log` VALUES (32, '2022-04-28 12:37:08.588772', '14', 'Go语言从入门到入坑:(第2章)go第二章', 1, '[{\"added\": {}}]', 10, 1);
INSERT INTO `django_admin_log` VALUES (33, '2022-04-28 12:37:19.219868', '15', 'Go语言从入门到入坑:(第3章)go第三章', 1, '[{\"added\": {}}]', 10, 1);
INSERT INTO `django_admin_log` VALUES (34, '2022-04-28 12:37:34.683643', '19', 'Go语言从入门到入坑:(第1章)go第一章-环境搭建', 1, '[{\"added\": {}}]', 11, 1);
INSERT INTO `django_admin_log` VALUES (35, '2022-04-28 12:37:46.319051', '20', 'Go语言从入门到入坑:(第1章)go第一章-第一个helloworld', 1, '[{\"added\": {}}]', 11, 1);
INSERT INTO `django_admin_log` VALUES (36, '2022-04-28 12:37:54.201623', '21', 'Go语言从入门到入坑:(第2章)go第二章-变量定义', 1, '[{\"added\": {}}]', 11, 1);
INSERT INTO `django_admin_log` VALUES (37, '2022-04-28 12:38:03.467191', '22', 'Go语言从入门到入坑:(第2章)go第二章-常量', 1, '[{\"added\": {}}]', 11, 1);
INSERT INTO `django_admin_log` VALUES (38, '2022-04-28 12:38:13.148682', '23', 'Go语言从入门到入坑:(第3章)go第三章-go结构体', 1, '[{\"added\": {}}]', 11, 1);
INSERT INTO `django_admin_log` VALUES (39, '2022-04-28 12:38:26.314632', '24', 'Go语言从入门到入坑:(第3章)go第三章-go接口', 1, '[{\"added\": {}}]', 11, 1);
INSERT INTO `django_admin_log` VALUES (40, '2022-04-28 12:39:55.563959', '6', 'Go语言微服务', 1, '[{\"added\": {}}]', 9, 1);
INSERT INTO `django_admin_log` VALUES (41, '2022-04-28 12:40:11.446768', '16', 'Go语言微服务:(第1章)微服务第一章', 1, '[{\"added\": {}}]', 10, 1);
INSERT INTO `django_admin_log` VALUES (42, '2022-04-28 12:40:22.812748', '17', 'Go语言微服务:(第2章)微服务第二章', 1, '[{\"added\": {}}]', 10, 1);
INSERT INTO `django_admin_log` VALUES (43, '2022-04-28 12:40:36.534067', '25', 'Go语言微服务:(第1章)微服务第一章-微服务第二章第一课时', 1, '[{\"added\": {}}]', 11, 1);
INSERT INTO `django_admin_log` VALUES (44, '2022-04-28 12:40:45.122085', '26', 'Go语言微服务:(第1章)微服务第一章-微服务第二章第二课时', 1, '[{\"added\": {}}]', 11, 1);
INSERT INTO `django_admin_log` VALUES (45, '2022-04-28 12:40:57.478657', '27', 'Go语言微服务:(第2章)微服务第二章-微服务第二章第一课时', 1, '[{\"added\": {}}]', 11, 1);
INSERT INTO `django_admin_log` VALUES (46, '2022-04-28 12:41:04.674937', '28', 'Go语言微服务:(第2章)微服务第二章-微服务第二章第二课时', 1, '[{\"added\": {}}]', 11, 1);
INSERT INTO `django_admin_log` VALUES (47, '2022-04-28 12:41:14.343642', '26', 'Go语言微服务:(第1章)微服务第一章-微服务第一章第二课时', 2, '[{\"changed\": {\"fields\": [\"name\"]}}]', 11, 1);
INSERT INTO `django_admin_log` VALUES (48, '2022-04-28 12:41:43.226115', '25', 'Go语言微服务:(第1章)微服务第一章-微服务第一章第一课时', 2, '[{\"changed\": {\"fields\": [\"name\"]}}]', 11, 1);
INSERT INTO `django_admin_log` VALUES (49, '2022-04-29 10:11:45.747479', '3', 'Python项目实战:(第1章)项目创建', 2, '[{\"changed\": {\"fields\": [\"orders\"]}}]', 10, 1);
INSERT INTO `django_admin_log` VALUES (50, '2022-04-29 10:11:57.550752', '7', 'Python项目实战:(第3章)py实战项目第三章', 2, '[]', 10, 1);
INSERT INTO `django_admin_log` VALUES (51, '2022-04-29 10:12:42.502465', '25', 'Go语言微服务:(第1章)微服务第一章-微服务第一章第一课时', 2, '[{\"changed\": {\"fields\": [\"free_trail\"]}}]', 11, 1);
COMMIT;

-- ----------------------------
-- Table structure for django_content_type
-- ----------------------------
DROP TABLE IF EXISTS `django_content_type`;
CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of django_content_type
-- ----------------------------
BEGIN;
INSERT INTO `django_content_type` VALUES (1, 'admin', 'logentry');
INSERT INTO `django_content_type` VALUES (3, 'auth', 'group');
INSERT INTO `django_content_type` VALUES (2, 'auth', 'permission');
INSERT INTO `django_content_type` VALUES (4, 'contenttypes', 'contenttype');
INSERT INTO `django_content_type` VALUES (9, 'course', 'course');
INSERT INTO `django_content_type` VALUES (12, 'course', 'coursecategory');
INSERT INTO `django_content_type` VALUES (10, 'course', 'coursechapter');
INSERT INTO `django_content_type` VALUES (11, 'course', 'coursesection');
INSERT INTO `django_content_type` VALUES (8, 'course', 'teacher');
INSERT INTO `django_content_type` VALUES (7, 'home', 'banner');
INSERT INTO `django_content_type` VALUES (13, 'order', 'order');
INSERT INTO `django_content_type` VALUES (14, 'order', 'orderdetail');
INSERT INTO `django_content_type` VALUES (5, 'sessions', 'session');
INSERT INTO `django_content_type` VALUES (6, 'user', 'user');
COMMIT;

-- ----------------------------
-- Table structure for django_migrations
-- ----------------------------
DROP TABLE IF EXISTS `django_migrations`;
CREATE TABLE `django_migrations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of django_migrations
-- ----------------------------
BEGIN;
INSERT INTO `django_migrations` VALUES (1, 'contenttypes', '0001_initial', '2022-04-19 12:11:01.229326');
INSERT INTO `django_migrations` VALUES (2, 'contenttypes', '0002_remove_content_type_name', '2022-04-19 12:11:01.326431');
INSERT INTO `django_migrations` VALUES (3, 'auth', '0001_initial', '2022-04-19 12:11:01.445871');
INSERT INTO `django_migrations` VALUES (4, 'auth', '0002_alter_permission_name_max_length', '2022-04-19 12:11:01.670419');
INSERT INTO `django_migrations` VALUES (5, 'auth', '0003_alter_user_email_max_length', '2022-04-19 12:11:01.676624');
INSERT INTO `django_migrations` VALUES (6, 'auth', '0004_alter_user_username_opts', '2022-04-19 12:11:01.682738');
INSERT INTO `django_migrations` VALUES (7, 'auth', '0005_alter_user_last_login_null', '2022-04-19 12:11:01.692402');
INSERT INTO `django_migrations` VALUES (8, 'auth', '0006_require_contenttypes_0002', '2022-04-19 12:11:01.695788');
INSERT INTO `django_migrations` VALUES (9, 'auth', '0007_alter_validators_add_error_messages', '2022-04-19 12:11:01.715177');
INSERT INTO `django_migrations` VALUES (10, 'auth', '0008_alter_user_username_max_length', '2022-04-19 12:11:01.738395');
INSERT INTO `django_migrations` VALUES (11, 'auth', '0009_alter_user_last_name_max_length', '2022-04-19 12:11:01.748090');
INSERT INTO `django_migrations` VALUES (12, 'auth', '0010_alter_group_name_max_length', '2022-04-19 12:11:01.799861');
INSERT INTO `django_migrations` VALUES (13, 'auth', '0011_update_proxy_permissions', '2022-04-19 12:11:01.810063');
INSERT INTO `django_migrations` VALUES (14, 'user', '0001_initial', '2022-04-19 12:11:01.926275');
INSERT INTO `django_migrations` VALUES (15, 'admin', '0001_initial', '2022-04-19 12:11:02.151706');
INSERT INTO `django_migrations` VALUES (16, 'admin', '0002_logentry_remove_auto_add', '2022-04-19 12:11:02.227284');
INSERT INTO `django_migrations` VALUES (17, 'admin', '0003_logentry_add_action_flag_choices', '2022-04-19 12:11:02.236925');
INSERT INTO `django_migrations` VALUES (18, 'admin', '0004_auto_20220419_1210', '2022-04-19 12:11:02.308268');
INSERT INTO `django_migrations` VALUES (19, 'sessions', '0001_initial', '2022-04-19 12:11:02.340296');
INSERT INTO `django_migrations` VALUES (20, 'home', '0001_initial', '2022-04-20 12:14:09.728780');
INSERT INTO `django_migrations` VALUES (21, 'course', '0001_initial', '2022-04-28 11:38:23.351856');
INSERT INTO `django_migrations` VALUES (22, 'order', '0001_initial', '2022-04-29 16:02:11.763379');
COMMIT;

-- ----------------------------
-- Table structure for django_session
-- ----------------------------
DROP TABLE IF EXISTS `django_session`;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of django_session
-- ----------------------------
BEGIN;
INSERT INTO `django_session` VALUES ('1y79aa8yvmqu8t9cljbaophh8l7admes', 'MGYxYzM0ZTE4MjI0ZjgwYjRiZGFiNmIxYTNiMmQ2OTIwNTcwNWU1Nzp7Il9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5kcy5Nb2RlbEJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiI5NzQwNDlhNWQ5OTc4NmU4OWViZTcwZDgwYjkxM2JiZTUwZTM2NjFhIiwiX21lbnVzIjoiW3tcIm5hbWVcIjogXCJIb21lXCIsIFwiaWNvblwiOiBcImZhciBmYS1jaXJjbGVcIiwgXCJtb2RlbHNcIjogW3tcIm5hbWVcIjogXCJcXHU4ZjZlXFx1NjRhZFxcdTU2ZmVcXHU4ODY4XCIsIFwiaWNvblwiOiBcImZhciBmYS1jaXJjbGVcIiwgXCJ1cmxcIjogXCIvYWRtaW4vaG9tZS9iYW5uZXIvXCIsIFwiYWRkVXJsXCI6IFwiL2FkbWluL2hvbWUvYmFubmVyL2FkZC9cIiwgXCJicmVhZGNydW1ic1wiOiBbe1wibmFtZVwiOiBcIkhvbWVcIiwgXCJpY29uXCI6IFwiZmFyIGZhLWNpcmNsZVwifSwge1wibmFtZVwiOiBcIlxcdThmNmVcXHU2NGFkXFx1NTZmZVxcdTg4NjhcIiwgXCJpY29uXCI6IFwiZmFyIGZhLWNpcmNsZVwifV0sIFwiZWlkXCI6IDEwMDJ9XSwgXCJlaWRcIjogMTAwMX0sIHtcIm5hbWVcIjogXCJcXHU4YmE0XFx1OGJjMVxcdTU0OGNcXHU2Mzg4XFx1Njc0M1wiLCBcImljb25cIjogXCJmYXMgZmEtc2hpZWxkLWFsdFwiLCBcIm1vZGVsc1wiOiBbe1wibmFtZVwiOiBcIlxcdTdlYzRcIiwgXCJpY29uXCI6IFwiZmFzIGZhLXVzZXJzLWNvZ1wiLCBcInVybFwiOiBcIi9hZG1pbi9hdXRoL2dyb3VwL1wiLCBcImFkZFVybFwiOiBcIi9hZG1pbi9hdXRoL2dyb3VwL2FkZC9cIiwgXCJicmVhZGNydW1ic1wiOiBbe1wibmFtZVwiOiBcIlxcdThiYTRcXHU4YmMxXFx1NTQ4Y1xcdTYzODhcXHU2NzQzXCIsIFwiaWNvblwiOiBcImZhcyBmYS1zaGllbGQtYWx0XCJ9LCB7XCJuYW1lXCI6IFwiXFx1N2VjNFwiLCBcImljb25cIjogXCJmYXMgZmEtdXNlcnMtY29nXCJ9XSwgXCJlaWRcIjogMTAwNH1dLCBcImVpZFwiOiAxMDAzfV0ifQ==', '2022-05-08 10:25:41.084603');
INSERT INTO `django_session` VALUES ('i8yjjgns3xkof50vlgkjotjtme2xbw57', 'NmIyMGE5NTNhNGQ5OTE1ZTljZjNlMTdmYzAwYTY1NjE3MTVkYTc5Zjp7Il9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5kcy5Nb2RlbEJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiI5NzQwNDlhNWQ5OTc4NmU4OWViZTcwZDgwYjkxM2JiZTUwZTM2NjFhIiwiX21lbnVzIjoiW3tcIm5hbWVcIjogXCJDb3Vyc2VcIiwgXCJpY29uXCI6IFwiZmFyIGZhLWNpcmNsZVwiLCBcIm1vZGVsc1wiOiBbe1wibmFtZVwiOiBcIlxcdTUyMDZcXHU3YzdiXCIsIFwiaWNvblwiOiBcImZhciBmYS1jaXJjbGVcIiwgXCJ1cmxcIjogXCIvYWRtaW4vY291cnNlL2NvdXJzZWNhdGVnb3J5L1wiLCBcImFkZFVybFwiOiBcIi9hZG1pbi9jb3Vyc2UvY291cnNlY2F0ZWdvcnkvYWRkL1wiLCBcImJyZWFkY3J1bWJzXCI6IFt7XCJuYW1lXCI6IFwiQ291cnNlXCIsIFwiaWNvblwiOiBcImZhciBmYS1jaXJjbGVcIn0sIHtcIm5hbWVcIjogXCJcXHU1MjA2XFx1N2M3YlwiLCBcImljb25cIjogXCJmYXIgZmEtY2lyY2xlXCJ9XSwgXCJlaWRcIjogMTAwMn0sIHtcIm5hbWVcIjogXCJcXHU1YmZjXFx1NWUwOFwiLCBcImljb25cIjogXCJmYXIgZmEtY2lyY2xlXCIsIFwidXJsXCI6IFwiL2FkbWluL2NvdXJzZS90ZWFjaGVyL1wiLCBcImFkZFVybFwiOiBcIi9hZG1pbi9jb3Vyc2UvdGVhY2hlci9hZGQvXCIsIFwiYnJlYWRjcnVtYnNcIjogW3tcIm5hbWVcIjogXCJDb3Vyc2VcIiwgXCJpY29uXCI6IFwiZmFyIGZhLWNpcmNsZVwifSwge1wibmFtZVwiOiBcIlxcdTViZmNcXHU1ZTA4XCIsIFwiaWNvblwiOiBcImZhciBmYS1jaXJjbGVcIn1dLCBcImVpZFwiOiAxMDAzfSwge1wibmFtZVwiOiBcIlxcdTdhZTBcXHU4MjgyXCIsIFwiaWNvblwiOiBcImZhciBmYS1jaXJjbGVcIiwgXCJ1cmxcIjogXCIvYWRtaW4vY291cnNlL2NvdXJzZWNoYXB0ZXIvXCIsIFwiYWRkVXJsXCI6IFwiL2FkbWluL2NvdXJzZS9jb3Vyc2VjaGFwdGVyL2FkZC9cIiwgXCJicmVhZGNydW1ic1wiOiBbe1wibmFtZVwiOiBcIkNvdXJzZVwiLCBcImljb25cIjogXCJmYXIgZmEtY2lyY2xlXCJ9LCB7XCJuYW1lXCI6IFwiXFx1N2FlMFxcdTgyODJcIiwgXCJpY29uXCI6IFwiZmFyIGZhLWNpcmNsZVwifV0sIFwiZWlkXCI6IDEwMDR9LCB7XCJuYW1lXCI6IFwiXFx1OGJmZVxcdTY1ZjZcIiwgXCJpY29uXCI6IFwiZmFyIGZhLWNpcmNsZVwiLCBcInVybFwiOiBcIi9hZG1pbi9jb3Vyc2UvY291cnNlc2VjdGlvbi9cIiwgXCJhZGRVcmxcIjogXCIvYWRtaW4vY291cnNlL2NvdXJzZXNlY3Rpb24vYWRkL1wiLCBcImJyZWFkY3J1bWJzXCI6IFt7XCJuYW1lXCI6IFwiQ291cnNlXCIsIFwiaWNvblwiOiBcImZhciBmYS1jaXJjbGVcIn0sIHtcIm5hbWVcIjogXCJcXHU4YmZlXFx1NjVmNlwiLCBcImljb25cIjogXCJmYXIgZmEtY2lyY2xlXCJ9XSwgXCJlaWRcIjogMTAwNX0sIHtcIm5hbWVcIjogXCJcXHU4YmZlXFx1N2EwYlwiLCBcImljb25cIjogXCJmYXIgZmEtY2lyY2xlXCIsIFwidXJsXCI6IFwiL2FkbWluL2NvdXJzZS9jb3Vyc2UvXCIsIFwiYWRkVXJsXCI6IFwiL2FkbWluL2NvdXJzZS9jb3Vyc2UvYWRkL1wiLCBcImJyZWFkY3J1bWJzXCI6IFt7XCJuYW1lXCI6IFwiQ291cnNlXCIsIFwiaWNvblwiOiBcImZhciBmYS1jaXJjbGVcIn0sIHtcIm5hbWVcIjogXCJcXHU4YmZlXFx1N2EwYlwiLCBcImljb25cIjogXCJmYXIgZmEtY2lyY2xlXCJ9XSwgXCJlaWRcIjogMTAwNn1dLCBcImVpZFwiOiAxMDAxfSwge1wibmFtZVwiOiBcIkhvbWVcIiwgXCJpY29uXCI6IFwiZmFyIGZhLWNpcmNsZVwiLCBcIm1vZGVsc1wiOiBbe1wibmFtZVwiOiBcIlxcdThmNmVcXHU2NGFkXFx1NTZmZVxcdTg4NjhcIiwgXCJpY29uXCI6IFwiZmFyIGZhLWNpcmNsZVwiLCBcInVybFwiOiBcIi9hZG1pbi9ob21lL2Jhbm5lci9cIiwgXCJhZGRVcmxcIjogXCIvYWRtaW4vaG9tZS9iYW5uZXIvYWRkL1wiLCBcImJyZWFkY3J1bWJzXCI6IFt7XCJuYW1lXCI6IFwiSG9tZVwiLCBcImljb25cIjogXCJmYXIgZmEtY2lyY2xlXCJ9LCB7XCJuYW1lXCI6IFwiXFx1OGY2ZVxcdTY0YWRcXHU1NmZlXFx1ODg2OFwiLCBcImljb25cIjogXCJmYXIgZmEtY2lyY2xlXCJ9XSwgXCJlaWRcIjogMTAwOH1dLCBcImVpZFwiOiAxMDA3fSwge1wibmFtZVwiOiBcIlxcdThiYTRcXHU4YmMxXFx1NTQ4Y1xcdTYzODhcXHU2NzQzXCIsIFwiaWNvblwiOiBcImZhcyBmYS1zaGllbGQtYWx0XCIsIFwibW9kZWxzXCI6IFt7XCJuYW1lXCI6IFwiXFx1N2VjNFwiLCBcImljb25cIjogXCJmYXMgZmEtdXNlcnMtY29nXCIsIFwidXJsXCI6IFwiL2FkbWluL2F1dGgvZ3JvdXAvXCIsIFwiYWRkVXJsXCI6IFwiL2FkbWluL2F1dGgvZ3JvdXAvYWRkL1wiLCBcImJyZWFkY3J1bWJzXCI6IFt7XCJuYW1lXCI6IFwiXFx1OGJhNFxcdThiYzFcXHU1NDhjXFx1NjM4OFxcdTY3NDNcIiwgXCJpY29uXCI6IFwiZmFzIGZhLXNoaWVsZC1hbHRcIn0sIHtcIm5hbWVcIjogXCJcXHU3ZWM0XCIsIFwiaWNvblwiOiBcImZhcyBmYS11c2Vycy1jb2dcIn1dLCBcImVpZFwiOiAxMDEwfV0sIFwiZWlkXCI6IDEwMDl9XSJ9', '2022-05-13 10:11:27.961377');
COMMIT;

-- ----------------------------
-- Table structure for luffy_banner
-- ----------------------------
DROP TABLE IF EXISTS `luffy_banner`;
CREATE TABLE `luffy_banner` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_time` datetime(6) NOT NULL,
  `updated_time` datetime(6) NOT NULL,
  `is_delete` tinyint(1) NOT NULL,
  `is_show` tinyint(1) NOT NULL,
  `orders` int(11) NOT NULL,
  `title` varchar(16) NOT NULL,
  `image` varchar(100) NOT NULL,
  `link` varchar(64) NOT NULL,
  `info` longtext NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `title` (`title`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of luffy_banner
-- ----------------------------
BEGIN;
INSERT INTO `luffy_banner` VALUES (1, '2022-04-20 12:26:39.334880', '2022-04-24 10:21:50.320108', 0, 1, 1, 'banner1', 'banner/banner1.png', 'http://www.cnblogs.com', '首页1');
INSERT INTO `luffy_banner` VALUES (2, '2022-04-20 12:26:59.822785', '2022-04-20 12:26:59.822810', 0, 1, 2, 'banner2', 'banner/banner2.png', '/home', 'banner2');
INSERT INTO `luffy_banner` VALUES (3, '2022-04-20 12:27:18.959757', '2022-04-20 12:27:18.959781', 0, 1, 3, 'banner3', 'banner/banner3.png', '/home', 'banner3');
INSERT INTO `luffy_banner` VALUES (4, '2022-04-20 12:27:38.829129', '2022-04-20 12:27:38.829159', 0, 1, 4, 'banner4', 'banner/banner4.png', '/home', 'banner4');
COMMIT;

-- ----------------------------
-- Table structure for luffy_course
-- ----------------------------
DROP TABLE IF EXISTS `luffy_course`;
CREATE TABLE `luffy_course` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_time` datetime(6) NOT NULL,
  `updated_time` datetime(6) NOT NULL,
  `is_delete` tinyint(1) NOT NULL,
  `is_show` tinyint(1) NOT NULL,
  `orders` int(11) NOT NULL,
  `name` varchar(128) NOT NULL,
  `course_img` varchar(255) DEFAULT NULL,
  `course_type` smallint(6) NOT NULL,
  `brief` longtext,
  `level` smallint(6) NOT NULL,
  `pub_date` date NOT NULL,
  `period` int(11) NOT NULL,
  `attachment_path` varchar(128) DEFAULT NULL,
  `status` smallint(6) NOT NULL,
  `students` int(11) NOT NULL,
  `sections` int(11) NOT NULL,
  `pub_sections` int(11) NOT NULL,
  `price` decimal(6,2) NOT NULL,
  `course_category_id` int(11) DEFAULT NULL,
  `teacher_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `luffy_course_course_category_id_ae7376a3` (`course_category_id`),
  KEY `luffy_course_teacher_id_0202c7b2_fk_luffy_teacher_id` (`teacher_id`),
  CONSTRAINT `luffy_course_teacher_id_0202c7b2_fk_luffy_teacher_id` FOREIGN KEY (`teacher_id`) REFERENCES `luffy_teacher` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of luffy_course
-- ----------------------------
BEGIN;
INSERT INTO `luffy_course` VALUES (1, '2019-07-14 13:54:33.095201', '2022-04-28 12:36:32.603852', 0, 1, 1, 'Python开发21天入门', 'courses/alex_python.png', 0, 'Python从入门到入土&&&Python从入门到入土&&&Python从入门到入土&&&Python从入门到入土&&&Python从入门到入土&&&Python从入门到入土&&&Python从入门到入土&&&Python从入门到入土&&&Python从入门到入土&&&Python从入门到入土&&&Python从入门到入土&&&Python从入门到入土', 0, '2019-07-14', 21, '', 0, 231, 120, 120, 199.00, 1, 1);
INSERT INTO `luffy_course` VALUES (2, '2019-07-14 13:56:05.051103', '2019-07-14 13:56:05.051142', 0, 1, 2, 'Python项目实战', 'courses/mjj_python.png', 0, '', 1, '2019-07-14', 30, '', 0, 340, 120, 120, 99.00, 1, 2);
INSERT INTO `luffy_course` VALUES (3, '2019-07-14 13:57:21.190053', '2019-07-14 13:57:21.190095', 0, 1, 3, 'Linux系统基础5周入门精讲', 'courses/lyy_linux.png', 0, '', 0, '2019-07-14', 25, '', 0, 219, 100, 100, 39.00, 2, 3);
INSERT INTO `luffy_course` VALUES (4, '2022-04-28 12:06:36.564933', '2022-04-28 12:36:04.812789', 0, 1, 4, 'DRF从入门到放弃', 'courses/drf.png', 0, 'drf很牛逼', 4, '2022-04-28', 7, '', 0, 399, 0, 0, 77.00, 1, 1);
INSERT INTO `luffy_course` VALUES (5, '2022-04-28 12:35:44.319734', '2022-04-28 12:35:44.319757', 0, 1, 5, 'Go语言从入门到入坑', 'courses/msbd.png', 0, 'Go语言从入门到入坑Go语言从入门到入坑Go语言从入门到入坑Go语言从入门到入坑', 0, '2022-04-28', 20, '', 0, 30, 200, 100, 66.00, 3, 1);
INSERT INTO `luffy_course` VALUES (6, '2022-04-28 12:39:55.562716', '2022-04-28 12:39:55.562741', 0, 1, 6, 'Go语言微服务', 'courses/celery.png', 0, 'Go语言微服务Go语言微服务Go语言微服务Go语言微服务', 4, '2022-04-28', 7, '', 0, 122, 0, 0, 299.00, 3, 2);
COMMIT;

-- ----------------------------
-- Table structure for luffy_course_category
-- ----------------------------
DROP TABLE IF EXISTS `luffy_course_category`;
CREATE TABLE `luffy_course_category` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_time` datetime(6) NOT NULL,
  `updated_time` datetime(6) NOT NULL,
  `is_delete` tinyint(1) NOT NULL,
  `is_show` tinyint(1) NOT NULL,
  `orders` int(11) NOT NULL,
  `name` varchar(64) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of luffy_course_category
-- ----------------------------
BEGIN;
INSERT INTO `luffy_course_category` VALUES (1, '2019-07-14 13:40:58.690413', '2019-07-14 13:40:58.690477', 0, 1, 1, 'Python');
INSERT INTO `luffy_course_category` VALUES (2, '2019-07-14 13:41:08.249735', '2019-07-14 13:41:08.249817', 0, 1, 2, 'Linux');
INSERT INTO `luffy_course_category` VALUES (3, '2022-04-28 12:07:33.314057', '2022-04-28 12:07:33.314088', 0, 1, 3, 'Go语言');
COMMIT;

-- ----------------------------
-- Table structure for luffy_course_chapter
-- ----------------------------
DROP TABLE IF EXISTS `luffy_course_chapter`;
CREATE TABLE `luffy_course_chapter` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_time` datetime(6) NOT NULL,
  `updated_time` datetime(6) NOT NULL,
  `is_delete` tinyint(1) NOT NULL,
  `is_show` tinyint(1) NOT NULL,
  `orders` int(11) NOT NULL,
  `chapter` smallint(6) NOT NULL,
  `name` varchar(128) NOT NULL,
  `summary` longtext,
  `pub_date` date NOT NULL,
  `course_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `luffy_course_chapter_course_id_fa245b81_fk_luffy_course_id` (`course_id`),
  CONSTRAINT `luffy_course_chapter_course_id_fa245b81_fk_luffy_course_id` FOREIGN KEY (`course_id`) REFERENCES `luffy_course` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of luffy_course_chapter
-- ----------------------------
BEGIN;
INSERT INTO `luffy_course_chapter` VALUES (1, '2019-07-14 13:58:34.867005', '2019-07-14 14:00:58.276541', 0, 1, 1, 1, '计算机原理', '', '2019-07-14', 1);
INSERT INTO `luffy_course_chapter` VALUES (2, '2019-07-14 13:58:48.051543', '2019-07-14 14:01:22.024206', 0, 1, 2, 2, '环境搭建', '', '2019-07-14', 1);
INSERT INTO `luffy_course_chapter` VALUES (3, '2019-07-14 13:59:09.878183', '2022-04-29 10:11:45.744898', 0, 1, 1, 1, '项目创建', '', '2019-07-14', 2);
INSERT INTO `luffy_course_chapter` VALUES (4, '2019-07-14 13:59:37.448626', '2019-07-14 14:01:58.709652', 0, 1, 4, 1, 'Linux环境创建', '', '2019-07-14', 3);
INSERT INTO `luffy_course_chapter` VALUES (5, '2022-04-28 12:08:36.679922', '2022-04-28 12:08:36.680014', 0, 1, 2, 2, 'Linux5周第二章', 'Linux5周第二章Linux5周第二章Linux5周第二章Linux5周第二章Linux5周第二章', '2022-04-28', 3);
INSERT INTO `luffy_course_chapter` VALUES (6, '2022-04-28 12:09:19.324504', '2022-04-28 12:09:19.324533', 0, 1, 2, 2, 'py实战项目第二章', 'py实战项目第二章py实战项目第二章py实战项目第二章py实战项目第二章', '2022-04-28', 2);
INSERT INTO `luffy_course_chapter` VALUES (7, '2022-04-28 12:09:32.532905', '2022-04-29 10:11:57.546455', 0, 1, 3, 3, 'py实战项目第三章', 'py实战项目第三章py实战项目第三章py实战项目第三章', '2022-04-28', 2);
INSERT INTO `luffy_course_chapter` VALUES (8, '2022-04-28 12:09:55.496622', '2022-04-28 12:09:55.496686', 0, 1, 1, 1, 'drf入门1', 'drf入门1drf入门1drf入门1', '2022-04-28', 4);
INSERT INTO `luffy_course_chapter` VALUES (9, '2022-04-28 12:10:08.490618', '2022-04-28 12:10:08.490642', 0, 1, 2, 2, 'drf入门2', 'drf入门drf入门1drf入门1drf入门1drf入门1', '2022-04-28', 4);
INSERT INTO `luffy_course_chapter` VALUES (10, '2022-04-28 12:10:22.088684', '2022-04-28 12:10:22.088710', 0, 1, 3, 3, 'drf入门3', 'drf入门1drf入门1drf入门1drf入门1drf入门1drf入门1', '2022-04-28', 4);
INSERT INTO `luffy_course_chapter` VALUES (11, '2022-04-28 12:10:33.564141', '2022-04-28 12:10:33.564177', 0, 1, 4, 4, 'drf入门4', 'drf入门1drf入门1drf入门1drf入门1', '2022-04-28', 4);
INSERT INTO `luffy_course_chapter` VALUES (12, '2022-04-28 12:10:43.242918', '2022-04-28 12:10:43.242947', 0, 1, 5, 5, 'drf入门5', 'drf入门1drf入门1drf入门1drf入门1', '2022-04-28', 4);
INSERT INTO `luffy_course_chapter` VALUES (13, '2022-04-28 12:36:58.508995', '2022-04-28 12:36:58.509020', 0, 1, 1, 1, 'go第一章', 'go第一章', '2022-04-28', 5);
INSERT INTO `luffy_course_chapter` VALUES (14, '2022-04-28 12:37:08.588265', '2022-04-28 12:37:08.588287', 0, 1, 2, 2, 'go第二章', 'go第一章go第一章go第一章', '2022-04-28', 5);
INSERT INTO `luffy_course_chapter` VALUES (15, '2022-04-28 12:37:19.219405', '2022-04-28 12:37:19.219426', 0, 1, 3, 3, 'go第三章', 'go第一章go第一章go第一章', '2022-04-28', 5);
INSERT INTO `luffy_course_chapter` VALUES (16, '2022-04-28 12:40:11.445750', '2022-04-28 12:40:11.445774', 0, 1, 1, 1, '微服务第一章', '微服务第一章', '2022-04-28', 6);
INSERT INTO `luffy_course_chapter` VALUES (17, '2022-04-28 12:40:22.811647', '2022-04-28 12:40:22.811670', 0, 1, 2, 2, '微服务第二章', '微服务第二章微服务第二章微服务第二章', '2022-04-28', 6);
COMMIT;

-- ----------------------------
-- Table structure for luffy_course_section
-- ----------------------------
DROP TABLE IF EXISTS `luffy_course_section`;
CREATE TABLE `luffy_course_section` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_time` datetime(6) NOT NULL,
  `updated_time` datetime(6) NOT NULL,
  `is_delete` tinyint(1) NOT NULL,
  `is_show` tinyint(1) NOT NULL,
  `name` varchar(128) NOT NULL,
  `orders` smallint(5) unsigned NOT NULL,
  `section_type` smallint(6) NOT NULL,
  `section_link` varchar(255) DEFAULT NULL,
  `duration` varchar(32) DEFAULT NULL,
  `pub_date` datetime(6) NOT NULL,
  `free_trail` tinyint(1) NOT NULL,
  `chapter_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `luffy_course_section_chapter_id_98cfb330_fk_luffy_cou` (`chapter_id`),
  CONSTRAINT `luffy_course_section_chapter_id_98cfb330_fk_luffy_cou` FOREIGN KEY (`chapter_id`) REFERENCES `luffy_course_chapter` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of luffy_course_section
-- ----------------------------
BEGIN;
INSERT INTO `luffy_course_section` VALUES (1, '2019-07-14 14:02:33.779098', '2019-07-14 14:02:33.779135', 0, 1, '计算机原理上', 1, 2, '', NULL, '2019-07-14 14:02:33.779193', 1, 1);
INSERT INTO `luffy_course_section` VALUES (2, '2019-07-14 14:02:56.657134', '2019-07-14 14:02:56.657173', 0, 1, '计算机原理下', 2, 2, NULL, NULL, '2019-07-14 14:02:56.657227', 1, 1);
INSERT INTO `luffy_course_section` VALUES (3, '2019-07-14 14:03:20.493324', '2019-07-14 14:03:52.329394', 0, 1, '环境搭建上', 1, 2, NULL, NULL, '2019-07-14 14:03:20.493420', 0, 2);
INSERT INTO `luffy_course_section` VALUES (4, '2019-07-14 14:03:36.472742', '2019-07-14 14:03:36.472779', 0, 1, '环境搭建下', 2, 2, NULL, NULL, '2019-07-14 14:03:36.472831', 0, 2);
INSERT INTO `luffy_course_section` VALUES (5, '2019-07-14 14:04:19.338153', '2019-07-14 14:04:19.338192', 0, 1, 'web项目的创建', 1, 2, NULL, NULL, '2019-07-14 14:04:19.338252', 1, 3);
INSERT INTO `luffy_course_section` VALUES (6, '2019-07-14 14:04:52.895855', '2019-07-14 14:04:52.895890', 0, 1, 'Linux的环境搭建', 1, 2, NULL, NULL, '2019-07-14 14:04:52.895942', 1, 4);
INSERT INTO `luffy_course_section` VALUES (7, '2022-04-28 12:12:01.304920', '2022-04-28 12:12:01.304994', 0, 1, '文件操作', 2, 2, NULL, NULL, '2022-04-28 12:12:01.305074', 0, 5);
INSERT INTO `luffy_course_section` VALUES (8, '2022-04-28 12:12:11.287759', '2022-04-28 12:12:11.287884', 0, 1, '软件操作', 2, 2, NULL, NULL, '2022-04-28 12:12:11.288079', 0, 5);
INSERT INTO `luffy_course_section` VALUES (9, '2022-04-28 12:12:26.326077', '2022-04-28 12:12:26.326112', 0, 1, '请求响应', 1, 2, NULL, NULL, '2022-04-28 12:12:26.326174', 0, 8);
INSERT INTO `luffy_course_section` VALUES (10, '2022-04-28 12:12:36.364356', '2022-04-28 12:12:36.364391', 0, 1, '序列化类', 2, 2, NULL, NULL, '2022-04-28 12:12:36.364446', 0, 8);
INSERT INTO `luffy_course_section` VALUES (11, '2022-04-28 12:12:48.306119', '2022-04-28 12:12:48.306187', 0, 1, '三大认证', 1, 2, NULL, NULL, '2022-04-28 12:12:48.306396', 0, 9);
INSERT INTO `luffy_course_section` VALUES (12, '2022-04-28 12:13:06.882558', '2022-04-28 12:13:06.882620', 0, 1, '认证', 2, 2, NULL, NULL, '2022-04-28 12:13:06.882826', 0, 9);
INSERT INTO `luffy_course_section` VALUES (13, '2022-04-28 12:13:15.799043', '2022-04-28 12:13:15.799084', 0, 1, 'jwt认证', 1, 2, NULL, NULL, '2022-04-28 12:13:15.799146', 0, 10);
INSERT INTO `luffy_course_section` VALUES (14, '2022-04-28 12:13:27.852981', '2022-04-28 12:13:27.853011', 0, 1, 'jwt认证2', 3, 2, NULL, NULL, '2022-04-28 12:13:27.853066', 0, 10);
INSERT INTO `luffy_course_section` VALUES (15, '2022-04-28 12:13:37.292779', '2022-04-28 12:13:37.292806', 0, 1, '后台管理', 1, 2, NULL, NULL, '2022-04-28 12:13:37.292855', 0, 11);
INSERT INTO `luffy_course_section` VALUES (16, '2022-04-28 12:13:51.194585', '2022-04-28 12:13:51.194612', 0, 1, '后台管理2', 2, 2, NULL, NULL, '2022-04-28 12:13:51.194660', 0, 11);
INSERT INTO `luffy_course_section` VALUES (17, '2022-04-28 12:14:05.334836', '2022-04-28 12:14:05.334902', 0, 1, 'rbac1', 1, 2, NULL, NULL, '2022-04-28 12:14:05.335053', 0, 12);
INSERT INTO `luffy_course_section` VALUES (18, '2022-04-28 12:14:14.039605', '2022-04-28 12:14:14.039770', 0, 1, 'rbac2', 2, 2, NULL, NULL, '2022-04-28 12:14:14.039895', 0, 12);
INSERT INTO `luffy_course_section` VALUES (19, '2022-04-28 12:37:34.682049', '2022-04-28 12:37:34.682072', 0, 1, '环境搭建', 1, 2, NULL, NULL, '2022-04-28 12:37:34.682116', 0, 13);
INSERT INTO `luffy_course_section` VALUES (20, '2022-04-28 12:37:46.317414', '2022-04-28 12:37:46.317440', 0, 1, '第一个helloworld', 2, 2, NULL, NULL, '2022-04-28 12:37:46.317483', 0, 13);
INSERT INTO `luffy_course_section` VALUES (21, '2022-04-28 12:37:54.200236', '2022-04-28 12:37:54.200257', 0, 1, '变量定义', 1, 2, NULL, NULL, '2022-04-28 12:37:54.200297', 0, 14);
INSERT INTO `luffy_course_section` VALUES (22, '2022-04-28 12:38:03.465663', '2022-04-28 12:38:03.465686', 0, 1, '常量', 2, 2, NULL, NULL, '2022-04-28 12:38:03.465731', 0, 14);
INSERT INTO `luffy_course_section` VALUES (23, '2022-04-28 12:38:13.144613', '2022-04-28 12:38:13.144636', 0, 1, 'go结构体', 1, 2, NULL, NULL, '2022-04-28 12:38:13.144679', 0, 15);
INSERT INTO `luffy_course_section` VALUES (24, '2022-04-28 12:38:26.312273', '2022-04-28 12:38:26.312306', 0, 1, 'go接口', 2, 2, NULL, NULL, '2022-04-28 12:38:26.312380', 0, 15);
INSERT INTO `luffy_course_section` VALUES (25, '2022-04-28 12:40:36.531566', '2022-04-29 10:12:42.497098', 0, 1, '微服务第一章第一课时', 1, 2, NULL, NULL, '2022-04-28 12:40:36.531625', 1, 16);
INSERT INTO `luffy_course_section` VALUES (26, '2022-04-28 12:40:45.120568', '2022-04-28 12:41:14.341536', 0, 1, '微服务第一章第二课时', 2, 2, NULL, NULL, '2022-04-28 12:40:45.120627', 0, 16);
INSERT INTO `luffy_course_section` VALUES (27, '2022-04-28 12:40:57.477026', '2022-04-28 12:40:57.477048', 0, 1, '微服务第二章第一课时', 1, 2, NULL, NULL, '2022-04-28 12:40:57.477088', 0, 17);
INSERT INTO `luffy_course_section` VALUES (28, '2022-04-28 12:41:04.673613', '2022-04-28 12:41:04.673634', 0, 1, '微服务第二章第二课时', 2, 2, NULL, NULL, '2022-04-28 12:41:04.673673', 0, 17);
COMMIT;

-- ----------------------------
-- Table structure for luffy_order
-- ----------------------------
DROP TABLE IF EXISTS `luffy_order`;
CREATE TABLE `luffy_order` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `subject` varchar(150) NOT NULL,
  `total_amount` decimal(10,2) NOT NULL,
  `out_trade_no` varchar(64) NOT NULL,
  `trade_no` varchar(64) DEFAULT NULL,
  `order_status` smallint(6) NOT NULL,
  `pay_type` smallint(6) NOT NULL,
  `pay_time` datetime(6) DEFAULT NULL,
  `created_time` datetime(6) NOT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `out_trade_no` (`out_trade_no`),
  KEY `luffy_order_user_id_e450c68c` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of luffy_order
-- ----------------------------
BEGIN;
INSERT INTO `luffy_order` VALUES (1, 'xx课程', 299.00, 'ebaef6bdfb66477cad0a7a4007b94ccd', NULL, 0, 1, NULL, '2022-04-29 16:38:31.776750', 1);
INSERT INTO `luffy_order` VALUES (2, 'DRF从入门到放弃', 77.00, '6a1675c021e548a2a5666ac9dcf09860', NULL, 0, 1, NULL, '2022-04-29 16:50:28.534737', 1);
INSERT INTO `luffy_order` VALUES (3, 'Go语言微服务', 299.00, '905b19b0c97548bfa6fb54bef068dc62', NULL, 0, 1, NULL, '2022-04-29 16:50:43.096336', 1);
INSERT INTO `luffy_order` VALUES (4, 'Go语言微服务', 299.00, '9844b023f97648d39e8baa9e2896ffbb', NULL, 1, 1, NULL, '2022-04-29 17:03:50.688145', 1);
INSERT INTO `luffy_order` VALUES (5, 'Python开发21天入门', 199.00, '227fdea2d2324c288435e13c89e8c586', NULL, 1, 1, NULL, '2022-04-29 17:12:41.437436', 1);
INSERT INTO `luffy_order` VALUES (6, 'Go语言从入门到入坑', 66.00, '1d1e81f11925411281cd25e6c80bce57', NULL, 0, 1, NULL, '2022-04-30 10:13:00.748737', 1);
COMMIT;

-- ----------------------------
-- Table structure for luffy_order_detail
-- ----------------------------
DROP TABLE IF EXISTS `luffy_order_detail`;
CREATE TABLE `luffy_order_detail` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `price` decimal(6,2) NOT NULL,
  `real_price` decimal(6,2) NOT NULL,
  `course_id` int(11) NOT NULL,
  `order_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `luffy_order_detail_course_id_eb4f1d29` (`course_id`),
  KEY `luffy_order_detail_order_id_57bb4e1a` (`order_id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of luffy_order_detail
-- ----------------------------
BEGIN;
INSERT INTO `luffy_order_detail` VALUES (1, 299.00, 299.00, 6, 1);
INSERT INTO `luffy_order_detail` VALUES (2, 77.00, 77.00, 4, 2);
INSERT INTO `luffy_order_detail` VALUES (3, 299.00, 299.00, 6, 3);
INSERT INTO `luffy_order_detail` VALUES (4, 299.00, 299.00, 6, 4);
INSERT INTO `luffy_order_detail` VALUES (5, 199.00, 199.00, 1, 5);
INSERT INTO `luffy_order_detail` VALUES (6, 66.00, 66.00, 5, 6);
COMMIT;

-- ----------------------------
-- Table structure for luffy_teacher
-- ----------------------------
DROP TABLE IF EXISTS `luffy_teacher`;
CREATE TABLE `luffy_teacher` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_time` datetime(6) NOT NULL,
  `updated_time` datetime(6) NOT NULL,
  `is_delete` tinyint(1) NOT NULL,
  `is_show` tinyint(1) NOT NULL,
  `orders` int(11) NOT NULL,
  `name` varchar(32) NOT NULL,
  `role` smallint(6) NOT NULL,
  `title` varchar(64) NOT NULL,
  `signature` varchar(255) DEFAULT NULL,
  `image` varchar(100) DEFAULT NULL,
  `brief` longtext NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of luffy_teacher
-- ----------------------------
BEGIN;
INSERT INTO `luffy_teacher` VALUES (1, '2019-07-14 13:44:19.661327', '2019-07-14 13:46:54.246271', 0, 1, 1, 'Alex', 1, '老男孩Python教学总监', '金角大王', 'teacher/alex_icon.png', '老男孩教育CTO & CO-FOUNDER 国内知名PYTHON语言推广者 51CTO学院20162017年度最受学员喜爱10大讲师之一 多款开源软件作者 曾任职公安部、飞信、中金公司、NOKIA中国研究院、华尔街英语、ADVENT、汽车之家等公司');
INSERT INTO `luffy_teacher` VALUES (2, '2019-07-14 13:45:25.092902', '2019-07-14 13:45:25.092936', 0, 1, 2, 'Mjj', 0, '前美团前端项目组架构师', NULL, 'teacher/mjj_icon.png', '是马JJ老师, 一个集美貌与才华于一身的男人，搞过几年IOS，又转了前端开发几年，曾就职于美团网任高级前端开发，后来因为不同意王兴(美团老板)的战略布局而出家做老师去了，有丰富的教学经验，开起车来也毫不含糊。一直专注在前端的前沿技术领域。同时，爱好抽烟、喝酒、烫头(锡纸烫)。 我的最爱是前端，因为前端妹子多。');
INSERT INTO `luffy_teacher` VALUES (3, '2019-07-14 13:46:21.997846', '2019-07-14 13:46:21.997880', 0, 1, 3, 'Lyy', 0, '老男孩Linux学科带头人', NULL, 'teacher/lyy_icon.png', 'Linux运维技术专家，老男孩Linux金牌讲师，讲课风趣幽默、深入浅出、声音洪亮到爆炸');
COMMIT;

-- ----------------------------
-- Table structure for luffy_user
-- ----------------------------
DROP TABLE IF EXISTS `luffy_user`;
CREATE TABLE `luffy_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(30) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `mobile` varchar(11) NOT NULL,
  `icon` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `mobile` (`mobile`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of luffy_user
-- ----------------------------
BEGIN;
INSERT INTO `luffy_user` VALUES (1, 'pbkdf2_sha256$150000$GzSu8nqzDiqZ$KA2usjbMtAtvxlLyT0Cf7p840vMzlfUZ+y/QybAnCus=', '2022-04-28 11:39:51.807486', 1, 'lqz', '', '', '3@qq.com', 1, 1, '2022-04-20 12:14:34.013997', '18953675221', 'icon/default.png');
INSERT INTO `luffy_user` VALUES (2, 'pbkdf2_sha256$150000$xCV8p7UaVOBt$Em2kLIzI64GcL/7+l1jCzD4XFTPVddxT5BdjDmsNSQc=', NULL, 0, '15058066669', '', '', '', 0, 1, '2022-04-25 11:48:19.050064', '15058066669', 'icon/default.png');
INSERT INTO `luffy_user` VALUES (3, 'pbkdf2_sha256$150000$7NDocUXzFZSq$A43bx0o3ZrGabttb8NB7q32E0SBunncNIWH1pxMR+hI=', NULL, 0, '17673255100', '', '', '', 0, 1, '2022-04-25 11:51:49.918611', '17673255100', 'icon/default.png');
INSERT INTO `luffy_user` VALUES (4, 'pbkdf2_sha256$150000$4SFWTbi3c013$NuXd9kJuXWbvYChsS00NUfXCXAUTPonr7P7BNCxQ5wg=', NULL, 0, '13088229550', '', '', '', 0, 1, '2022-04-25 16:12:11.743720', '13088229550', 'icon/default.png');
INSERT INTO `luffy_user` VALUES (5, 'pbkdf2_sha256$150000$ftqIt2qLoVgJ$Gap4Bj5IhnwjnsknRQKcjPONKW4wbyZj3VGKbRI9iQ4=', NULL, 0, 'lqznb', '', '', '', 0, 1, '2022-04-27 12:32:20.458435', '12222222', 'icon/default.png');
COMMIT;

-- ----------------------------
-- Table structure for luffy_user_groups
-- ----------------------------
DROP TABLE IF EXISTS `luffy_user_groups`;
CREATE TABLE `luffy_user_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `luffy_user_groups_user_id_group_id_65493864_uniq` (`user_id`,`group_id`),
  KEY `luffy_user_groups_group_id_2c552c5a_fk_auth_group_id` (`group_id`),
  CONSTRAINT `luffy_user_groups_group_id_2c552c5a_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `luffy_user_groups_user_id_118ec1b6_fk_luffy_user_id` FOREIGN KEY (`user_id`) REFERENCES `luffy_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of luffy_user_groups
-- ----------------------------
BEGIN;
COMMIT;

-- ----------------------------
-- Table structure for luffy_user_user_permissions
-- ----------------------------
DROP TABLE IF EXISTS `luffy_user_user_permissions`;
CREATE TABLE `luffy_user_user_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `luffy_user_user_permissions_user_id_permission_id_a7014396_uniq` (`user_id`,`permission_id`),
  KEY `luffy_user_user_perm_permission_id_3150f78c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `luffy_user_user_perm_permission_id_3150f78c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `luffy_user_user_permissions_user_id_b132f823_fk_luffy_user_id` FOREIGN KEY (`user_id`) REFERENCES `luffy_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of luffy_user_user_permissions
-- ----------------------------
BEGIN;
COMMIT;

SET FOREIGN_KEY_CHECKS = 1;

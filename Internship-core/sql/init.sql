-- ============================================================
-- 组织架构模块 — 初始化 SQL
-- 参考《组织架构模块设计方案.md》第 3.3 节
-- 执行前请先创建数据库: CREATE DATABASE internship_db DEFAULT CHARSET utf8mb4;
-- ============================================================

-- 部门表
CREATE TABLE IF NOT EXISTS `sys_department` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `parent_id` BIGINT NULL,
    `dept_name` VARCHAR(64) NOT NULL,
    `leader` VARCHAR(64) NOT NULL DEFAULT '',
    `phone` VARCHAR(20) NOT NULL DEFAULT '',
    `email` VARCHAR(128) NOT NULL DEFAULT '',
    `sort_order` INT NOT NULL DEFAULT 0,
    `status` TINYINT NOT NULL DEFAULT 1 COMMENT '1启用 0禁用',
    `create_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    CONSTRAINT `fk_dept_parent` FOREIGN KEY (`parent_id`) REFERENCES `sys_department`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='部门表';

-- 用户表
CREATE TABLE IF NOT EXISTS `sys_user` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(64) NOT NULL UNIQUE,
    `password` VARCHAR(128) NOT NULL,
    `nickname` VARCHAR(64) NOT NULL DEFAULT '',
    `real_name` VARCHAR(64) NOT NULL DEFAULT '',
    `email` VARCHAR(128) NOT NULL DEFAULT '',
    `telephone` VARCHAR(20) NOT NULL DEFAULT '',
    `gender` TINYINT NOT NULL DEFAULT 0 COMMENT '0未知 1男 2女',
    `avatar` VARCHAR(255) NOT NULL DEFAULT '',
    `department_id` BIGINT NULL,
    `status` TINYINT NOT NULL DEFAULT 1 COMMENT '1启用 0禁用',
    `is_superuser` TINYINT(1) NOT NULL DEFAULT 0,
    `last_login` DATETIME(6) NULL,
    `create_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    CONSTRAINT `fk_user_dept` FOREIGN KEY (`department_id`) REFERENCES `sys_department`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 角色表
CREATE TABLE IF NOT EXISTS `sys_role` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `role_name` VARCHAR(64) NOT NULL UNIQUE,
    `role_key` VARCHAR(64) NOT NULL UNIQUE,
    `role_sort` INT NOT NULL DEFAULT 0,
    `status` TINYINT NOT NULL DEFAULT 1,
    `remark` VARCHAR(255) NOT NULL DEFAULT '',
    `create_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色表';

-- 用户-角色关联表
CREATE TABLE IF NOT EXISTS `sys_user_role_relation` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `user_id` BIGINT NOT NULL,
    `role_id` BIGINT NOT NULL,
    UNIQUE KEY `uk_user_role` (`user_id`, `role_id`),
    CONSTRAINT `fk_urr_user` FOREIGN KEY (`user_id`) REFERENCES `sys_user`(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_urr_role` FOREIGN KEY (`role_id`) REFERENCES `sys_role`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户-角色关联表';

-- 菜单表
CREATE TABLE IF NOT EXISTS `sys_menu` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `parent_id` BIGINT NULL,
    `menu_name` VARCHAR(64) NOT NULL,
    `menu_type` TINYINT NOT NULL DEFAULT 0 COMMENT '0目录 1菜单 2按钮',
    `path` VARCHAR(255) NOT NULL DEFAULT '',
    `component` VARCHAR(255) NOT NULL DEFAULT '',
    `icon` VARCHAR(64) NOT NULL DEFAULT '',
    `permission` VARCHAR(64) NOT NULL DEFAULT '',
    `sort_order` INT NOT NULL DEFAULT 0,
    `visible` TINYINT NOT NULL DEFAULT 1 COMMENT '1显示 0隐藏',
    `is_frame` TINYINT NOT NULL DEFAULT 0 COMMENT '0内部 1外部',
    `status` TINYINT NOT NULL DEFAULT 1,
    `create_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    CONSTRAINT `fk_menu_parent` FOREIGN KEY (`parent_id`) REFERENCES `sys_menu`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='菜单表';

-- 角色-菜单关联表
CREATE TABLE IF NOT EXISTS `sys_role_menu_relation` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `role_id` BIGINT NOT NULL,
    `menu_id` BIGINT NOT NULL,
    UNIQUE KEY `uk_role_menu` (`role_id`, `menu_id`),
    CONSTRAINT `fk_rmr_role` FOREIGN KEY (`role_id`) REFERENCES `sys_role`(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_rmr_menu` FOREIGN KEY (`menu_id`) REFERENCES `sys_menu`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色-菜单关联表';

-- 权限表
CREATE TABLE IF NOT EXISTS `sys_permission` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `permission_name` VARCHAR(64) NOT NULL,
    `permission_key` VARCHAR(64) NOT NULL UNIQUE,
    `sort_order` INT NOT NULL DEFAULT 0,
    `status` TINYINT NOT NULL DEFAULT 1,
    `create_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='权限表';

-- 菜单-权限关联表
CREATE TABLE IF NOT EXISTS `sys_menu_permission_relation` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `menu_id` BIGINT NOT NULL,
    `permission_id` BIGINT NOT NULL,
    UNIQUE KEY `uk_menu_perm` (`menu_id`, `permission_id`),
    CONSTRAINT `fk_mpr_menu` FOREIGN KEY (`menu_id`) REFERENCES `sys_menu`(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_mpr_perm` FOREIGN KEY (`permission_id`) REFERENCES `sys_permission`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='菜单-权限关联表';

-- 操作日志表
CREATE TABLE IF NOT EXISTS `sys_operation_log` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(64) NOT NULL,
    `module` VARCHAR(64) NOT NULL,
    `operation` VARCHAR(64) NOT NULL,
    `method` VARCHAR(10) NOT NULL,
    `request_url` VARCHAR(255) NOT NULL,
    `request_params` LONGTEXT NOT NULL,
    `response_result` LONGTEXT NOT NULL,
    `ip` VARCHAR(64) NOT NULL DEFAULT '',
    `status` TINYINT NOT NULL DEFAULT 1 COMMENT '1成功 0失败',
    `execution_time` INT NOT NULL DEFAULT 0 COMMENT '执行耗时(ms)',
    `create_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='操作日志表';

-- 系统配置表
CREATE TABLE IF NOT EXISTS `sys_config` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `config_name` VARCHAR(64) NOT NULL,
    `config_key` VARCHAR(64) NOT NULL UNIQUE,
    `config_value` LONGTEXT NOT NULL,
    `config_type` TINYINT NOT NULL DEFAULT 0 COMMENT '0字符串 1数字 2布尔 3JSON',
    `remark` VARCHAR(255) NOT NULL DEFAULT '',
    `sort_order` INT NOT NULL DEFAULT 0,
    `create_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统配置表';
-- ============================================================
-- 企业智能分析平台 — 完整数据库初始化脚本
-- 项目：Internship
-- 生成时间：2026-06-17
-- 执行方式：mysql -u root -p < database_init.sql
-- ============================================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS `internship_db` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `internship_db`;

-- ============================================================
-- 1. 基础模块
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

-- ============================================================
-- 2. 菜单权限模块
-- ============================================================

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

-- ============================================================
-- 3. 日志与配置模块
-- ============================================================

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
    `status` TINYINT NOT NULL DEFAULT 1,
    `create_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统配置表';

-- 字典类型表
CREATE TABLE IF NOT EXISTS `sys_dict_type` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `dict_name` VARCHAR(100) NOT NULL COMMENT '字典名称',
    `dict_type` VARCHAR(100) NOT NULL UNIQUE COMMENT '字典类型编码',
    `status` TINYINT NOT NULL DEFAULT 1 COMMENT '1启用 0禁用',
    `remark` VARCHAR(500) NOT NULL DEFAULT '' COMMENT '备注',
    `create_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='字典类型表';

-- 字典数据表
CREATE TABLE IF NOT EXISTS `sys_dict_data` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `dict_type` VARCHAR(100) NOT NULL COMMENT '字典类型编码',
    `dict_label` VARCHAR(100) NOT NULL COMMENT '字典标签',
    `dict_value` VARCHAR(100) NOT NULL COMMENT '字典键值',
    `css_class` VARCHAR(100) NOT NULL DEFAULT '' COMMENT '样式属性',
    `list_class` VARCHAR(100) NOT NULL DEFAULT '' COMMENT '表格回显样式',
    `sort_order` INT NOT NULL DEFAULT 0 COMMENT '排序号',
    `status` TINYINT NOT NULL DEFAULT 1 COMMENT '1启用 0禁用',
    `is_default` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否默认',
    `remark` VARCHAR(500) NOT NULL DEFAULT '' COMMENT '备注',
    `create_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    CONSTRAINT `fk_dict_data_type` FOREIGN KEY (`dict_type`) REFERENCES `sys_dict_type`(`dict_type`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='字典数据表';

-- AI 模型配置表
CREATE TABLE IF NOT EXISTS `ai_model_config` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL COMMENT '配置名称',
    `provider` VARCHAR(50) NOT NULL DEFAULT 'zhipu' COMMENT '提供商',
    `model_type` VARCHAR(20) NOT NULL COMMENT '模型类型: chat/embedding/multimodal',
    `model_name` VARCHAR(100) NOT NULL COMMENT '模型名称',
    `api_key` VARCHAR(500) NOT NULL COMMENT 'API Key',
    `api_base_url` VARCHAR(500) NOT NULL COMMENT 'API 地址',
    `is_default` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否默认',
    `status` TINYINT NOT NULL DEFAULT 1 COMMENT '1启用 0禁用',
    `remark` VARCHAR(255) NOT NULL DEFAULT '' COMMENT '备注',
    `create_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='AI 模型配置表';

-- ============================================================
-- 4. 学生管理模块
-- ============================================================

-- 学生信息表
CREATE TABLE IF NOT EXISTS `student_info` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `student_no` VARCHAR(32) NOT NULL UNIQUE COMMENT '学号',
    `name` VARCHAR(64) NOT NULL COMMENT '姓名',
    `gender` TINYINT NOT NULL DEFAULT 0 COMMENT '0未知 1男 2女',
    `class_name` VARCHAR(64) NOT NULL DEFAULT '' COMMENT '班级',
    `major` VARCHAR(128) NOT NULL DEFAULT '' COMMENT '专业',
    `college` VARCHAR(128) NOT NULL DEFAULT '' COMMENT '学院',
    `phone` VARCHAR(20) NOT NULL DEFAULT '' COMMENT '手机号',
    `email` VARCHAR(128) NOT NULL DEFAULT '' COMMENT '邮箱',
    `enrollment_year` INT NULL COMMENT '入学年份',
    `status` TINYINT NOT NULL DEFAULT 1 COMMENT '0休学 1在读 2毕业',
    `remark` VARCHAR(255) NOT NULL DEFAULT '' COMMENT '备注',
    `create_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学生信息表';

-- 学生成绩表
CREATE TABLE IF NOT EXISTS `student_score` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `student_id` BIGINT NOT NULL COMMENT '学生ID',
    `course_name` VARCHAR(128) NOT NULL COMMENT '课程名称',
    `score` DECIMAL(5,2) NOT NULL COMMENT '成绩',
    `semester` VARCHAR(32) NOT NULL COMMENT '学期',
    `credit` DECIMAL(4,1) NULL COMMENT '学分',
    `remark` VARCHAR(255) NOT NULL DEFAULT '' COMMENT '备注',
    `create_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    UNIQUE KEY `uk_student_course_semester` (`student_id`, `course_name`, `semester`),
    CONSTRAINT `fk_score_student` FOREIGN KEY (`student_id`) REFERENCES `student_info`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学生成绩表';

-- ============================================================
-- 5. 通知模块
-- ============================================================

-- 通知表
CREATE TABLE IF NOT EXISTS `sys_notification` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `user_id` BIGINT NOT NULL COMMENT '接收用户',
    `title` VARCHAR(200) NOT NULL COMMENT '标题',
    `content` TEXT NOT NULL COMMENT '内容',
    `is_read` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否已读',
    `create_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    CONSTRAINT `fk_notif_user` FOREIGN KEY (`user_id`) REFERENCES `sys_user`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='通知表';

-- ============================================================
-- 6. RAG 知识库模块
-- ============================================================

-- 知识库表
CREATE TABLE IF NOT EXISTS `rag_knowledgebase` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(128) NOT NULL COMMENT '名称',
    `description` TEXT NOT NULL DEFAULT '' COMMENT '描述',
    `status` TINYINT NOT NULL DEFAULT 1 COMMENT '1启用 0禁用',
    `doc_count` INT NOT NULL DEFAULT 0 COMMENT '文档总数',
    `chunk_count` INT NOT NULL DEFAULT 0 COMMENT '文档块总数',
    `creator_id` BIGINT NULL COMMENT '创建者',
    `create_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    CONSTRAINT `fk_kb_creator` FOREIGN KEY (`creator_id`) REFERENCES `sys_user`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='知识库表';

-- 文档表
CREATE TABLE IF NOT EXISTS `rag_document` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `knowledge_base_id` BIGINT NOT NULL COMMENT '所属知识库',
    `file_name` VARCHAR(255) NOT NULL COMMENT '文件名',
    `file_path` VARCHAR(500) NOT NULL COMMENT '存储路径',
    `file_type` VARCHAR(16) NOT NULL COMMENT '文件类型',
    `file_size` BIGINT NOT NULL DEFAULT 0 COMMENT '文件大小(字节)',
    `chunk_count` INT NOT NULL DEFAULT 0 COMMENT '分块数',
    `status` TINYINT NOT NULL DEFAULT 0 COMMENT '0待处理 1处理中 2已完成 3失败',
    `error_message` TEXT NOT NULL DEFAULT '' COMMENT '错误信息',
    `create_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    CONSTRAINT `fk_doc_kb` FOREIGN KEY (`knowledge_base_id`) REFERENCES `rag_knowledgebase`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='文档表';

-- 文档块表
CREATE TABLE IF NOT EXISTS `rag_document_chunk` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `document_id` BIGINT NOT NULL COMMENT '所属文档',
    `chunk_index` INT NOT NULL COMMENT '块序号',
    `content` TEXT NOT NULL COMMENT '内容',
    `vector_id` VARCHAR(64) NOT NULL UNIQUE COMMENT '向量ID',
    `token_count` INT NOT NULL DEFAULT 0 COMMENT 'Token数',
    `create_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    CONSTRAINT `fk_chunk_doc` FOREIGN KEY (`document_id`) REFERENCES `rag_document`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='文档块表';

-- ============================================================
-- 7. NL2SQL 模块
-- ============================================================

-- 数据源表
CREATE TABLE IF NOT EXISTS `nl2sql_datasource` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL COMMENT '数据源名称',
    `db_type` VARCHAR(20) NOT NULL DEFAULT 'mysql' COMMENT '数据库类型',
    `host` VARCHAR(200) NOT NULL DEFAULT '127.0.0.1' COMMENT '主机地址',
    `port` INT NOT NULL DEFAULT 3306 COMMENT '端口',
    `db_name` VARCHAR(100) NOT NULL COMMENT '数据库名',
    `username` VARCHAR(100) NOT NULL DEFAULT 'root' COMMENT '用户名',
    `password_enc` VARCHAR(500) NOT NULL DEFAULT '' COMMENT '密码(加密)',
    `description` TEXT NOT NULL DEFAULT '' COMMENT '描述',
    `status` TINYINT NOT NULL DEFAULT 1 COMMENT '1启用 0禁用',
    `created_by_id` BIGINT NULL COMMENT '创建者',
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    CONSTRAINT `fk_ds_creator` FOREIGN KEY (`created_by_id`) REFERENCES `sys_user`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='数据源表';

-- 查询历史表
CREATE TABLE IF NOT EXISTS `nl2sql_query_history` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `user_id` BIGINT NOT NULL COMMENT '查询用户',
    `datasource_id` BIGINT NULL COMMENT '数据源',
    `question` TEXT NOT NULL COMMENT '自然语言问题',
    `generated_sql` TEXT NOT NULL DEFAULT '' COMMENT '生成的SQL',
    `natural_language_result` TEXT NOT NULL DEFAULT '' COMMENT '自然语言结果',
    `execution_time` FLOAT NOT NULL DEFAULT 0 COMMENT '执行耗时(秒)',
    `result_count` INT NOT NULL DEFAULT 0 COMMENT '结果行数',
    `status` TINYINT NOT NULL DEFAULT 1 COMMENT '0失败 1成功',
    `is_favorite` TINYINT NOT NULL DEFAULT 0 COMMENT '0否 1是',
    `error_message` TEXT NOT NULL DEFAULT '' COMMENT '错误信息',
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    CONSTRAINT `fk_qh_user` FOREIGN KEY (`user_id`) REFERENCES `sys_user`(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_qh_ds` FOREIGN KEY (`datasource_id`) REFERENCES `nl2sql_datasource`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='查询历史表';

-- ============================================================
-- 8. Django 内置表（由 Django 自动创建，此处仅作参考）
-- ============================================================

-- 以下表由 Django 框架自动创建，无需手动执行：
-- auth_group, auth_group_permissions, auth_permission
-- django_admin_log, django_content_type, django_migrations, django_session
-- token_blacklist_blacklistedtoken, token_blacklist_outstandingtoken

-- ============================================================
-- 9. 初始数据
-- ============================================================

-- 管理员用户（密码：admin123，已使用 bcrypt 加密）
INSERT INTO `sys_user` (`username`, `password`, `nickname`, `is_superuser`, `status`) VALUES
('admin', '$2b$12$LJ3m4ys3Lz0YBMOcP3wq6OBKGOFPwOlGfaVzPN0gOlYGbqcMKhIte', '系统管理员', 1, 1)
ON DUPLICATE KEY UPDATE `username` = `username`;

-- 测试用户（密码：test123）
INSERT INTO `sys_user` (`username`, `password`, `nickname`, `is_superuser`, `status`) VALUES
('test', '$2b$12$xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx', '测试用户', 0, 1)
ON DUPLICATE KEY UPDATE `username` = `username`;

-- 默认角色
INSERT INTO `sys_role` (`role_name`, `role_key`, `role_sort`, `status`) VALUES
('系统管理员', 'admin', 1, 1),
('普通用户', 'user', 2, 1)
ON DUPLICATE KEY UPDATE `role_name` = `role_name`;

-- ============================================================
-- 完成！
-- ============================================================
-- 执行完成后，请运行 Django 的 seed 命令来初始化菜单和权限数据：
-- python manage.py seed
-- ============================================================

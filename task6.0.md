# Task 6.0 — UI 全面优化

> **目标**：提升系统整体视觉效果，使其更加专业、美观、高级
> **负责人**：人员 A（feature/jingwc）
> **分支策略**：在 `feature/jingwc` 分支上开发
> **截止时间**：尽快完成

---

## 一、问题分析

当前 UI 存在的问题：

| 问题 | 表现 |
|------|------|
| 页面风格不统一 | 各页面间距、配色、圆角不一致 |
| 卡片样式单调 | 默认 Element Plus 样式，没有层次感 |
| 表格缺乏美感 | 行高、对齐、操作按钮样式需要优化 |
| 弹窗表单简陋 | 缺少分组、间距、视觉层次 |
| 图标使用不足 | 操作按钮缺少图标，辨识度低 |
| 响应式不完善 | 部分页面在小屏幕上显示异常 |

---

## 二、任务清单

### 任务 1：全局样式增强
**优先级：P0**

优化 `src/styles/index.css` 和 `src/styles/variables.css`：

```css
:root {
  /* 更高级的配色方案 */
  --primary-color: #6366f1;      /* 靛蓝紫，更有质感 */
  --primary-light: #eef2ff;
  --primary-dark: #4f46e5;
  
  /* 更精致的阴影 */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1);
  
  /* 更圆润的圆角 */
  --border-radius: 12px;
  --border-radius-sm: 6px;
  --border-radius-lg: 16px;
}
```

**涉及文件**：
- `src/styles/variables.css`
- `src/styles/index.css`

---

### 任务 2：登录页面优化
**优先级：P0**

优化 `src/views/login/Login.vue`：

- 背景添加渐变动效（缓慢流动的渐变）
- 登录卡片添加毛玻璃效果
- 输入框添加图标前缀
- 登录按钮添加渐变和 hover 动效
- 添加"记住密码"复选框样式优化

**涉及文件**：
- `src/views/login/Login.vue`

---

### 任务 3：Dashboard 仪表盘优化
**优先级：P0**

优化 `src/views/dashboard/Dashboard.vue`：

- 统计卡片添加渐变背景色
- 添加数字滚动动画
- 图表区域优化卡片样式
- 添加欢迎区域的个性化信息
- 优化日志表格样式

**涉及文件**：
- `src/views/dashboard/Dashboard.vue`

---

### 任务 4：Layout 布局优化
**优先级：P1**

优化 `src/layout/Layout.vue`：

- 侧边栏添加渐变背景
- 菜单项 hover 添加过渡动效
- 折叠按钮样式优化
- 顶栏添加阴影和背景模糊

**涉及文件**：
- `src/layout/Layout.vue`

---

### 任务 5：表格页面通用样式
**优先级：P0**

优化所有表格页面的通用样式：

- 表头添加背景色和加粗
- 行高优化（增加到 56px）
- 操作列按钮添加图标
- 状态开关添加动画
- 分页器样式优化

**涉及文件**：
- `src/styles/index.css`（通用表格样式）
- `src/views/system/user/UserList.vue`
- `src/views/system/role/RoleList.vue`
- `src/views/system/permission/PermissionList.vue`
- `src/views/system/department/DeptTree.vue`
- `src/views/system/menu/MenuTree.vue`
- `src/views/system/dict/DictList.vue`
- `src/views/system/log/LogList.vue`
- `src/views/system/config/ConfigList.vue`

---

### 任务 6：表单弹窗优化
**优先级：P0**

优化所有表单弹窗的样式：

- 弹窗头部添加渐变背景
- 表单项添加分组（基本信息、高级设置）
- 输入框添加图标前缀
- 按钮添加 loading 动效
- 错误提示样式优化

**涉及文件**：
- `src/views/system/user/UserForm.vue`
- `src/views/system/role/RoleForm.vue`
- `src/views/system/permission/PermissionForm.vue`
- `src/views/system/department/DeptForm.vue`
- `src/views/system/menu/MenuForm.vue`
- `src/views/system/dict/DictForm.vue`
- `src/views/system/config/ConfigForm.vue`

---

### 任务 7：树形页面优化
**优先级：P1**

优化部门管理和菜单管理的树形展示：

- 树节点添加展开/折叠动画
- 选中节点高亮样式
- 添加右键菜单
- 拖拽排序的视觉反馈

**涉及文件**：
- `src/views/system/department/DeptTree.vue`
- `src/views/system/menu/MenuTree.vue`

---

### 任务 8：角色权限分配弹窗优化
**优先级：P1**

优化角色管理的权限分配弹窗：

- 菜单树添加全选/全不选按钮
- 添加搜索过滤功能
- 勾选框添加动画效果
- 已选权限数量显示

**涉及文件**：
- `src/views/system/role/RoleList.vue`

---

### 任务 9：RAG 知识库页面优化
**优先级：P0**

优化 RAG 相关页面：

- 知识库卡片添加封面图或渐变背景
- 文档列表添加文件类型图标
- 聊天气泡样式优化（区分用户/AI）
- 添加消息加载动画
- 输入框添加工具栏图标

**涉及文件**：
- `src/views/rag/KBList.vue`
- `src/views/rag/KBDetail.vue`
- `src/views/rag/ChatView.vue`

---

### 任务 10：NL2SQL 页面优化
**优先级：P1**

优化 NL2SQL 相关页面：

- 查询页面添加 SQL 语法高亮
- 结果表格添加列宽自适应
- 数据源卡片样式优化
- 历史记录添加收藏图标样式

**涉及文件**：
- `src/views/nl2sql/QueryView.vue`
- `src/views/nl2sql/HistoryList.vue`
- `src/views/nl2sql/DataSourceList.vue`

---

### 任务 11：学生管理页面优化
**优先级：P1**

优化学生管理相关页面：

- 学生列表添加头像列
- 成绩管理添加分数颜色标记
- 导入导出按钮样式优化

**涉及文件**：
- `src/views/student/StudentList.vue`
- `src/views/student/ScoreList.vue`
- `src/views/student/StudentForm.vue`
- `src/views/student/ScoreForm.vue`

---

### 任务 12：错误页面优化
**优先级：P2**

优化 403 和 404 错误页面：

- 添加插画或动画
- 添加返回首页按钮
- 添加搜索框或导航建议

**涉及文件**：
- `src/views/error/403.vue`
- `src/views/error/404.vue`

---

### 任务 13：个人中心和通知页面优化
**优先级：P2**

优化用户中心相关页面：

- 个人资料页面添加头像上传区域
- 通知列表添加未读标记样式
- 添加消息时间线效果

**涉及文件**：
- `src/views/user-center/ProfileView.vue`
- `src/views/user-center/NotificationList.vue`
- `src/views/system/profile/Profile.vue`

---

## 三、设计规范

### 配色方案

| 用途 | 颜色值 | 说明 |
|------|--------|------|
| 主色 | `#6366f1` | 靛蓝紫，专业有质感 |
| 成功 | `#10b981` | 翠绿，清爽 |
| 警告 | `#f59e0b` | 琥珀，醒目 |
| 危险 | `#ef4444` | 红色，警示 |
| 背景 | `#f8fafc` | 浅灰，干净 |
| 卡片 | `#ffffff` | 纯白，层次感 |

### 间距规范

| 场景 | 间距 |
|------|------|
| 页面内边距 | 24px |
| 卡片间距 | 16px |
| 表单项间距 | 16px |
| 按钮间距 | 8px |

### 圆角规范

| 元素 | 圆角 |
|------|------|
| 卡片 | 12px |
| 按钮 | 8px |
| 输入框 | 8px |
| 标签 | 6px |
| 头像 | 50% |

### 阴影规范

| 场景 | 阴影 |
|------|------|
| 卡片默认 | `0 1px 3px rgba(0,0,0,0.1)` |
| 卡片悬停 | `0 4px 12px rgba(0,0,0,0.15)` |
| 弹窗 | `0 8px 24px rgba(0,0,0,0.2)` |
| 下拉菜单 | `0 4px 16px rgba(0,0,0,0.12)` |

---

## 四、验收标准

- [ ] 全局配色方案更新
- [ ] 登录页面视觉效果提升
- [ ] Dashboard 统计卡片有渐变效果
- [ ] Layout 侧边栏样式优化
- [ ] 所有表格页面样式统一
- [ ] 表单弹窗添加分组和图标
- [ ] 树形页面展开折叠动画
- [ ] 角色权限分配弹窗优化
- [ ] RAG 聊天气泡样式优化
- [ ] NL2SQL SQL 语法高亮
- [ ] 学生管理页面优化
- [ ] 错误页面添加插画

---

## 五、注意事项

1. **不要破坏现有功能**：只改样式，不改逻辑
2. **保持一致性**：所有页面使用统一的设计规范
3. **响应式优先**：确保在不同屏幕尺寸下正常显示
4. **性能考虑**：动画使用 CSS transform，避免重排
5. **可访问性**：保持足够的对比度，支持键盘导航

---

**加油！🚀**

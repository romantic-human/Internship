# Task 5.0 — 老师反馈问题修复

> **目标**：根据老师演示反馈，修复三个核心问题
> **团队**：3 人分工，每人负责的功能模块**完全解耦**，互不依赖
> **分支策略**：不创建新分支，在各自已有的 `feature/` 分支上开发
> **截止时间**：尽快完成

---

## 一、问题清单

| # | 问题 | 严重度 | 负责人 |
|---|------|--------|--------|
| 1 | 页面丑陋，UI 需要优化 | 🔴 高 | 人员 B |
| 2 | 角色没有分配权限的按钮 | 🔴 高 | 人员 C |
| 3 | RAG 和 NL2SQL 模型应外置，让用户能换模型 | 🟡 中 | 人员 A |

---

## 二、任务分配

### 人员 A（feature/jingwc）— 模型外置配置

**核心目标**：将 RAG 和 NL2SQL 的模型配置从代码中提取出来，让用户可以在前端选择和切换模型。

#### 任务 A-1：后端 — 创建模型配置表
**优先级：P0**

新建 `apps/config_app/models.py` 中的 `AIModelConfig` 模型：

```python
class AIModelConfig(models.Model):
    """AI 模型配置表"""
    name = models.CharField("配置名称", max_length=100)  # 如 "智谱GLM-4"
    provider = models.CharField("提供商", max_length=50)  # 如 "zhipu", "dashscope", "openai"
    model_type = models.CharField("模型类型", max_length=20, choices=[
        ("chat", "对话模型"),
        ("embedding", "向量模型"),
        ("multimodal", "多模态模型"),
    ])
    model_name = models.CharField("模型名称", max_length=100)  # 如 "glm-4-flash"
    api_key = models.CharField("API Key", max_length=500)
    api_base_url = models.CharField("API 地址", max_length=500)
    is_default = models.BooleanField("是否默认", default=False)
    status = models.SmallIntegerField("状态", default=1)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
```

**涉及文件**：
- `apps/config_app/models.py`
- `apps/config_app/serializers.py`
- `apps/config_app/views.py`
- `apps/config_app/urls.py`

#### 任务 A-2：后端 — 修改 RAG 服务使用配置表
**优先级：P0**

修改 `apps/rag/services/llm_service.py`，从数据库读取模型配置而不是从 settings.py：

```python
@classmethod
def get_model_config(cls, model_type="chat"):
    """从数据库获取模型配置"""
    config = AIModelConfig.objects.filter(
        model_type=model_type, is_default=True, status=1
    ).first()
    if not config:
        # 回退到 settings.py 配置
        return {
            "api_key": settings.DEEPSEEK_API_KEY,
            "api_base_url": settings.DEEPSEEK_BASE_URL,
            "model_name": settings.DEEPSEEK_CHAT_MODEL,
        }
    return {
        "api_key": config.api_key,
        "api_base_url": config.api_base_url,
        "model_name": config.model_name,
    }
```

**涉及文件**：
- `apps/rag/services/llm_service.py`
- `apps/rag/services/document_processor.py`
- `apps/nl2sql/services/nl2sql_service.py`

#### 任务 A-3：前端 — 模型配置管理页面
**优先级：P0**

新建 `src/views/system/ai-model/AIModelList.vue`，提供模型配置的 CRUD 功能：

- 模型列表（名称、提供商、类型、状态）
- 新增/编辑模型配置表单
- 设置默认模型
- 测试模型连接

**涉及文件**：
- `src/views/system/ai-model/AIModelList.vue`
- `src/views/system/ai-model/AIModelForm.vue`
- `src/api/ai-model.ts`

#### 任务 A-4：前端 — RAG 和 NL2SQL 页面添加模型选择
**优先级：P1**

在 RAG 问答页面和 NL2SQL 查询页面添加模型选择下拉框：

- RAG 聊天页面：选择对话模型
- NL2SQL 查询页面：选择 SQL 生成模型
- 知识库详情页：选择 Embedding 模型

**涉及文件**：
- `src/views/rag/ChatView.vue`
- `src/views/nl2sql/QueryView.vue`
- `src/views/rag/KBDetail.vue`

---

### 人员 B（feature/lijz）— UI 优化

**核心目标**：提升系统整体视觉效果，使其更加专业和美观。

#### 任务 B-1：全局样式优化
**优先级：P0**

优化 `src/styles/index.css` 全局样式：

- 统一字体：使用系统默认字体栈
- 优化颜色方案：主色调、辅助色、背景色
- 优化间距和圆角
- 添加过渡动画

```css
/* 示例优化 */
:root {
  --primary-color: #409eff;
  --bg-color: #f5f7fa;
  --card-bg: #ffffff;
  --text-primary: #303133;
  --text-secondary: #606266;
  --border-radius: 8px;
  --box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}
```

**涉及文件**：
- `src/styles/index.css`
- `src/styles/variables.css`（新建）

#### 任务 B-2：登录页面优化
**优先级：P0**

优化 `src/views/login/Login.vue`：

- 添加渐变背景或图片背景
- 优化登录卡片样式
- 添加 Logo 和系统名称
- 优化表单样式

**涉及文件**：
- `src/views/login/Login.vue`

#### 任务 B-3：Dashboard 页面优化
**优先级：P0**

优化 `src/views/dashboard/Dashboard.vue`：

- 优化统计卡片样式（添加渐变背景、图标）
- 优化图表样式
- 添加欢迎语和用户信息

**涉及文件**：
- `src/views/dashboard/Dashboard.vue`

#### 任务 B-4：表格页面统一优化
**优先级：P1**

优化所有列表页面的表格样式：

- 统一表头样式
- 优化行高和间距
- 添加斑马纹
- 优化操作按钮样式
- 统一分页器样式

**涉及文件**：
- `src/views/system/user/UserList.vue`
- `src/views/system/role/RoleList.vue`
- `src/views/system/menu/MenuTree.vue`
- `src/views/system/department/DeptTree.vue`
- `src/views/system/permission/PermissionList.vue`
- `src/views/system/dict/DictList.vue`
- `src/views/system/log/LogList.vue`
- `src/views/student/StudentList.vue`
- `src/views/student/ScoreList.vue`

#### 任务 B-5：Layout 布局优化
**优先级：P1**

优化 `src/layout/Layout.vue`：

- 优化侧边栏样式（添加渐变背景）
- 优化顶栏样式
- 添加面包屑导航
- 优化折叠按钮

**涉及文件**：
- `src/layout/Layout.vue`

---

### 人员 C（feature/sunyf）— 角色权限分配

**核心目标**：确保角色管理页面的"分配权限"按钮正常显示和工作。

#### 任务 C-1：检查权限按钮显示问题
**优先级：P0**

排查为什么"分配菜单"和"分配用户"按钮不显示：

1. 检查 `v-permission` 指令是否正确注册
2. 检查用户是否有 `role:assign` 权限
3. 检查权限数据是否正确

**当前代码分析**：

```vue
<!-- RoleList.vue 第 55-56 行 -->
<el-button v-permission="'role:assign'" link type="primary" @click="handleAssignMenu(row)">分配菜单</el-button>
<el-button v-permission="'role:assign'" link type="primary" @click="handleAssignUser(row)">分配用户</el-button>
```

**可能的问题**：
1. 种子数据中没有创建 `role:assign` 权限
2. 管理员角色没有分配 `role:assign` 权限
3. `v-permission` 指令实现有问题

**涉及文件**：
- `src/directives/permission.ts`
- `src/views/system/role/RoleList.vue`
- `apps/user/management/commands/seed.py`（检查权限数据）

#### 任务 C-2：确保权限数据完整
**优先级：P0**

检查并修复 `seed.py`，确保以下权限存在：

```python
# 角色管理权限
"role:list": ("角色查询", role_m),
"role:add": ("角色新增", role_m),
"role:edit": ("角色编辑", role_m),
"role:delete": ("角色删除", role_m),
"role:assign": ("角色分配", role_m),  # 确保存在
```

**涉及文件**：
- `apps/user/management/commands/seed.py`

#### 任务 C-3：优化权限分配弹窗
**优先级：P1**

优化角色管理页面的权限分配弹窗：

- 优化菜单树的展示样式
- 添加全选/全不选功能
- 添加搜索功能
- 优化保存后的反馈

**涉及文件**：
- `src/views/system/role/RoleList.vue`

#### 任务 C-4：添加权限预览功能
**优先级：P2**

在角色详情中添加权限预览，方便查看该角色拥有哪些权限：

- 在角色列表中添加"查看权限"按钮
- 弹窗展示该角色的所有权限（只读）

**涉及文件**：
- `src/views/system/role/RoleList.vue`

---

## 三、文件冲突检查

| 文件 | 人员 A | 人员 B | 人员 C | 冲突？ |
|------|--------|--------|--------|--------|
| `config_app/` | ✅ 主要修改 | ❌ | ❌ | ✅ 无冲突 |
| `rag/services/` | ✅ 主要修改 | ❌ | ❌ | ✅ 无冲突 |
| `nl2sql/services/` | ✅ 主要修改 | ❌ | ❌ | ✅ 无冲突 |
| `views/login/` | ❌ | ✅ 主要修改 | ❌ | ✅ 无冲突 |
| `views/dashboard/` | ❌ | ✅ 主要修改 | ❌ | ✅ 无冲突 |
| `layout/` | ❌ | ✅ 主要修改 | ❌ | ✅ 无冲突 |
| `styles/` | ❌ | ✅ 主要修改 | ❌ | ✅ 无冲突 |
| `views/system/role/` | ❌ | ⚠️ 表格样式 | ✅ 主要修改 | ⚠️ 需协调 |
| `seed.py` | ❌ | ❌ | ✅ 可能修改 | ✅ 无冲突 |

**⚠️ 注意**：人员 B 和人员 C 都会修改 `RoleList.vue`，需要协调：
- 人员 B 负责表格样式优化
- 人员 C 负责功能逻辑修复
- 建议人员 C 先完成功能修复，人员 B 再优化样式

---

## 四、合并顺序建议

```
人员 C (feature/sunyf) → develop    先合并（修复权限按钮问题）
        ↓
人员 A (feature/jingwc) → develop   其次（模型外置功能）
        ↓
人员 B (feature/lijz) → develop     最后（UI 优化，需要前两人代码稳定）
```

---

## 五、验收标准

### 人员 A
- [ ] 后端：AIModelConfig 模型创建成功
- [ ] 后端：RAG 和 NL2SQL 能从数据库读取模型配置
- [ ] 前端：模型配置管理页面可用
- [ ] 前端：RAG 和 NL2SQL 页面能选择模型

### 人员 B
- [ ] 登录页面视觉效果提升
- [ ] Dashboard 页面视觉效果提升
- [ ] 表格页面样式统一
- [ ] 整体配色和间距协调

### 人员 C
- [ ] 角色管理页面"分配菜单"按钮可见
- [ ] 角色管理页面"分配用户"按钮可见
- [ ] 权限分配功能正常工作
- [ ] 种子数据包含完整权限

---

## 六、测试要点

1. **模型配置**：创建、编辑、删除、设置默认、测试连接
2. **UI 优化**：各页面在不同分辨率下的显示效果
3. **权限分配**：分配菜单后，用户登录能看到对应菜单

---

**祝大家顺利完成任务！🚀**

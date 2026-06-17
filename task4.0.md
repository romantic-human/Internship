# Task 4.0 — 交付前冲刺：多模态增强 + P1/P2 修复

> **目标**：交付前最后一周，完成多模态能力引入、修复全部 P1 安全问题、清理 P2 优化项
> **团队**：3 人分工，每人负责的模块**完全解耦**，互不依赖
> **分支策略**：不创建新分支，在各自已有的 `feature/` 分支上开发，完成后提 PR 到 `develop`
> **截止时间**：本周五下班前

---

## 一、任务分配总览

| 人员 | 分支 | 负责方向 | 任务数 |
|------|------|----------|--------|
| **人员 A（你）** | `feature/jingwc` | 🤖 多模态能力增强 | 5 项 |
| **人员 B** | `feature/lijz` | 🔒 后端安全与配置修复 | 6 项 |
| **人员 C** | `feature/sunyf` | 🧹 前端优化与代码清理 | 5 项 |

---

## 二、人员 A — 多模态能力增强（feature/jingwc）

**核心目标：为 RAG 知识库引入图片理解能力，支持图文问答**

### 任务 A-1：新增多模态 LLM 服务
**优先级：P0**
**涉及文件：`apps/rag/services/llm_service.py`**

在现有 `LLMService` 类中新增多模态聊天方法：

```python
@classmethod
def chat_with_image(cls, question: str, image_base64: str, context_chunks: list[dict]) -> dict:
    """图文多模态问答：支持图片+文本输入"""
    # 构建多模态 messages 格式
    # 使用 qwen-vl-max 模型
    # 返回结构与 chat() 一致
```

- 复用现有 `_get_client()` 和 `SYSTEM_PROMPT`
- 调用百炼 DashScope 的 `qwen-vl-max` 模型
- message 格式改为 `{"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64}"}}`

### 任务 A-2：新增图片处理工具
**优先级：P0**
**涉及文件：`apps/rag/services/document_processor.py`（或新建 `image_processor.py`）**

- 新增 `process_image(file_path: str) -> str` 函数
- 使用 Pillow 对图片进行压缩（最大 2048px）、格式转换（统一为 JPEG/PNG）
- 返回 base64 编码字符串
- 支持格式：JPG、PNG、BMP、WEBP

### 任务 A-3：后端 API 支持图片上传
**优先级：P0**
**涉及文件：`apps/rag/views.py`、`apps/rag/serializers.py`**

- 知识库文档上传接口新增 `image` 文件类型支持
- 聊天接口 `chat` action 新增可选参数 `image`（base64 或文件）
- 调用 `chat_with_image()` 处理图文问答

```python
@action(detail=False, methods=["post"], url_path="chat")
def chat(self, request):
    question = request.data.get("question", "")
    image = request.data.get("image", "")  # 新增：base64 图片
    kb_id = request.data.get("kb_id")
    # ...
    if image:
        result = LLMService.chat_with_image(question, image, context_chunks)
    else:
        result = LLMService.chat(question, context_chunks)
```

### 任务 A-4：前端 RAG 聊天页面增加图片上传
**优先级：P0**
**涉及文件：`views/rag/ChatView.vue`、`api/rag.ts`**

- 聊天输入框旁增加「📷 上传图片」按钮（`el-upload`）
- 支持拖拽上传、粘贴上传
- 图片预览（缩略图）+ 删除按钮
- 发送时将图片转为 base64 一起提交
- 消息气泡中展示图片

### 任务 A-5：更新依赖和配置
**优先级：P1**
**涉及文件：`requirements.txt`、`Internship-core/.env`**

- `requirements.txt` 添加：`Pillow>=10.0.0`
- `.env` 新增配置项（可选）：
  ```
  MULTIMODAL_MODEL=qwen-vl-max
  ```
- `settings.py` 新增 `MULTIMODAL_MODEL` 配置读取

**验收标准：**
- ✅ 上传一张图片 + 输入问题，AI 能理解图片内容并回答
- ✅ 纯文本问答功能不受影响（向后兼容）
- ✅ 图片过大时自动压缩，不报错

---

## 三、人员 B — 后端安全与配置修复（feature/lijz）

**核心目标：修复全部 P1 安全问题 + 后端配置优化**

### 任务 B-1：添加 JWT Token 黑名单
**优先级：P1**
**涉及文件：`config/settings.py`、迁移文件**

```python
# settings.py INSTALLED_APPS 中添加：
"rest_framework_simplejwt.token_blacklist",
```

然后执行：
```bash
python manage.py migrate
```

### 任务 B-2：补充 RAG 模块依赖到 requirements.txt
**优先级：P1**
**涉及文件：`requirements.txt`**

在文件末尾追加：
```
# RAG 知识库依赖
chromadb>=0.4.0
dashscope>=1.14.0
openai>=1.0.0
langchain-text-splitters>=0.0.1
pypdf>=3.0.0
python-docx>=0.8.11
```

### 任务 B-3：修复 Redis 硬编码密码
**优先级：P1**
**涉及文件：`config/settings.py`**

将：
```python
REDIS_URL = os.getenv("REDIS_URL", "redis://:123456@127.0.0.1:6379/1")
```
改为：
```python
REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/1")
```

### 任务 B-4：修复 NL2SQL SQL 校验绕过漏洞
**优先级：P1**
**涉及文件：`apps/nl2sql/services/sql_executor.py`**

当前 `validate_sql` 只检查 `FROM` 之前的关键字，需改为检查整个 SQL：

```python
for kw in FORBIDDEN_KEYWORDS:
    pattern = r"\b" + re.escape(kw) + r"\b"
    if re.search(pattern, sql_upper):
        return False, f"SQL 中包含禁止的关键字: {kw}"
```

### 任务 B-5：Dashboard 缓存失效机制
**优先级：P1**
**涉及文件：`apps/dashboard/views.py`、`apps/user/views.py`、`apps/role/views.py`、`apps/student/views.py`**

在各模块的 `create`、`update`、`destroy` 操作后调用：
```python
from django.core.cache import cache
cache.delete("dashboard_stats")
```

涉及模块：user、role、student、department

### 任务 B-6：后端配置收尾
**优先级：P2**
**涉及文件：多个**

- 新建 `Internship-core/.env.example`，列出所有环境变量
- `settings.py` 更新 API 文档标题为 `"企业智能分析平台 API"`
- 清理根目录 `seed.py`（确认已合并到 management command 后删除）
- 修复 `DictDataViewSet.by_type` 路由冲突（加路由前缀或正则约束）

**验收标准：**
- ✅ Token 轮换后旧 Token 失效
- ✅ `pip install -r requirements.txt` 一次性安装所有依赖
- ✅ SQL 注入测试：`SELECT 1 FROM dual; DROP TABLE users;--` 被拦截

---

## 四、人员 C — 前端优化与代码清理（feature/sunyf）

**核心目标：前端体验优化 + 代码质量提升 + 测试补全**

### 任务 C-1：修复前端路由参数不匹配
**优先级：P1**
**涉及文件：`src/store/auth.ts`、`src/router/index.ts`**

修复 `generateDynamicRoutes` 函数，支持 `force` 参数：

```typescript
async function generateDynamicRoutes(force = false) {
  if (dynamicRoutesLoaded.value && !force) return;
  // ...原有逻辑
}
```

### 任务 C-2：前端代码清理
**优先级：P2**
**涉及文件：多个**

- 删除未使用的组件：`TabsNav.vue`、`ClockWidget.vue`
- 清理 `api/menu.ts` 中未使用的函数：`getMenuOptions`、`getMenuDetail`、`updateMenuSort`
- 清理 `api/department.ts` 中未使用的函数
- 清理 `request.ts` 中多余的 `code === 1000` 判断，统一为 `code === 200`

### 任务 C-3：统一导出格式为 Excel
**优先级：P2**
**涉及文件：`apps/user/views.py`、`apps/role/views.py`**

将仍使用 CSV 导出的模块统一改为 Excel（openpyxl）：
- user 模块的 export 接口
- role 模块的 export 接口（如有 CSV）

### 任务 C-4：操作日志中间件优化
**优先级：P2**
**涉及文件：`utils/middleware.py`**

将 `SKIP_METHODS` 改为只记录写操作：
```python
RECORD_METHODS = ("POST", "PUT", "PATCH", "DELETE")
```

GET 请求不再写入日志表，避免日志膨胀。

### 任务 C-5：补全 Django Admin 注册
**优先级：P2**
**涉及文件：各 app 的 `admin.py`**

为以下模块添加 Admin 注册（便于调试和紧急数据修复）：

```python
# apps/user/admin.py
from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "nickname", "is_active", "create_time")
    search_fields = ("username", "nickname")
```

同理补全：role、permission、menu、department、dict、log、config、student、notification

**验收标准：**
- ✅ 刷新页面后路由正确加载
- ✅ 导出文件统一为 .xlsx 格式
- ✅ `GET` 请求不再产生操作日志
- ✅ `/admin/` 后台可查看所有模块数据

---

## 五、文件冲突检查

| 文件 | 人员 A | 人员 B | 人员 C | 冲突？ |
|------|--------|--------|--------|--------|
| `requirements.txt` | ✅ 添加 Pillow | ✅ 添加 RAG 依赖 | ❌ | ⚠️ 合并时注意 |
| `settings.py` | ⚠️ 可能添加配置 | ✅ 修改 | ❌ | ⚠️ 合并时注意 |
| `rag/views.py` | ✅ 主要修改 | ❌ | ❌ | ✅ 无冲突 |
| `rag/services/` | ✅ 主要修改 | ❌ | ❌ | ✅ 无冲突 |
| `nl2sql/` | ❌ | ✅ | ❌ | ✅ 无冲突 |
| `dashboard/` | ❌ | ✅ | ❌ | ✅ 无冲突 |
| `user/views.py` | ❌ | ❌ | ✅ | ✅ 无冲突 |
| `store/auth.ts` | ❌ | ❌ | ✅ | ✅ 无冲突 |
| `ChatView.vue` | ✅ | ❌ | ❌ | ✅ 无冲突 |

**⚠️ 唯一可能冲突的文件**：`requirements.txt` 和 `settings.py`
- 合并 PR 时需要手动合并这两处
- 建议：人员 A 先提 PR，合并后 B 再提，最后 C

---

## 六、合并顺序建议

```
人员 A (feature/jingwc) → develop    先合并（多模态 + Pillow 依赖）
        ↓
人员 B (feature/lijz) → develop      其次（后端修复 + RAG 依赖）
        ↓
人员 C (feature/sunyf) → develop     最后（前端优化 + 测试）
```

---

## 七、每日站会 Checklist

每人每天汇报：
1. ✅ 昨天完成了什么
2. 📋 今天计划做什么
3. ❓ 遇到什么阻塞

---

**祝大家本周冲刺顺利，按时交付！🚀**

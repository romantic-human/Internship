# RAG 知识库模块文档

## 一、模块概述

RAG（Retrieval-Augmented Generation，检索增强生成）知识库模块是管理系统的核心功能模块之一，支持用户上传文档构建知识库，并基于知识库内容进行 AI 智能问答。

### 1.1 核心能力

| 能力 | 说明 |
|---|---|
| 知识库管理 | 创建、编辑、删除知识库，支持启用/禁用 |
| 文档管理 | 上传 PDF/DOCX/TXT/MD 文件，自动解析、分块、向量化 |
| AI 问答 | 基于知识库文档的智能问答，带来源引用和相似度评分 |

### 1.2 技术架构

```
用户提问 → 通义千问 Embedding → ChromaDB 向量检索 → Top-K 相关文档块
                                                        ↓
                              通义千问 LLM ← 构建 Prompt（问题 + 参考资料）
                                    ↓
                              返回答案 + 来源引用
```

| 组件 | 技术选型 | 说明 |
|---|---|---|
| LLM | 通义千问 qwen-turbo（百炼平台） | 通过 OpenAI 兼容接口调用 |
| Embedding | 通义千问 text-embedding-v3 | 1024 维向量，DashScope SDK 调用 |
| 向量数据库 | ChromaDB | 本地持久化，余弦相似度检索 |
| 文档解析 | pypdf / python-docx | 支持 PDF、DOCX、TXT、MD |
| 文本分块 | langchain-text-splitters | RecursiveCharacterTextSplitter |

---

## 二、模块结构

### 2.1 后端文件

```
Internship-core/apps/rag/
├── __init__.py
├── models.py              # 数据模型：KnowledgeBase、Document、DocumentChunk
├── serializers.py         # DRF 序列化器
├── urls.py                # 路由配置
├── views.py               # 视图：KnowledgeBaseViewSet、DocumentViewSet、ChatView
├── migrations/
│   └── 0001_initial.py    # 数据库迁移
└── services/
    ├── document_processor.py  # 文档处理：解析 → 分块 → 向量化 → 存储
    ├── llm_service.py         # LLM 服务：问答 + Embedding
    └── vector_store.py        # ChromaDB 向量存储封装
```

### 2.2 前端文件

```
Internship-Pre/src/
├── api/rag.ts                 # API 接口封装
└── views/rag/
    ├── KBList.vue             # 知识库列表页
    ├── KBDetail.vue           # 文档管理页
    └── ChatView.vue           # AI 问答页
```

### 2.3 数据模型

```
KnowledgeBase (知识库)
├── id, name, description, status
├── doc_count, chunk_count (统计字段)
├── creator (外键 → User)
└── create_time, update_time

Document (文档)
├── id, knowledge_base (外键 → KnowledgeBase)
├── file_name, file_path, file_type, file_size
├── chunk_count, status (0待处理/1处理中/2已完成/3失败)
├── error_message
└── create_time, update_time

DocumentChunk (文档块)
├── id, document (外键 → Document)
├── chunk_index, content, vector_id, token_count
└── create_time
```

---

## 三、API 接口

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/rag/kb/` | 知识库列表（支持 name 搜索、分页） |
| POST | `/api/rag/kb/` | 创建知识库 |
| GET | `/api/rag/kb/{id}/` | 知识库详情 |
| PUT | `/api/rag/kb/{id}/` | 更新知识库 |
| DELETE | `/api/rag/kb/{id}/` | 删除知识库（级联删除文档和向量） |
| GET | `/api/rag/documents/?knowledge_base={kb_id}` | 文档列表 |
| POST | `/api/rag/documents/upload/` | 上传文档（multipart/form-data） |
| DELETE | `/api/rag/documents/{id}/` | 删除文档 |
| POST | `/api/rag/documents/{id}/reprocess/` | 重新处理失败的文档 |
| POST | `/api/rag/kb/{kb_id}/chat/` | AI 问答 |

> **注意**：所有 DRF 路由路径必须带尾部 `/`。

---

## 四、环境配置

### 4.1 依赖安装

```bash
cd Internship-core
pip install -r requirements.txt
```

RAG 相关依赖：
```
openai>=1.0.0               # OpenAI SDK（调用百炼 LLM）
dashscope>=1.14.0            # DashScope SDK（调用 Embedding）
chromadb>=0.4.0              # 向量数据库
langchain>=0.1.0             # LangChain
langchain-text-splitters>=0.1.0  # 文本分块
pypdf>=3.17.0                # PDF 解析
python-docx>=1.1.0           # DOCX 解析
```

### 4.2 数据库迁移

```bash
python manage.py makemigrations rag
python manage.py migrate rag
```

### 4.3 配置 API Key

复制 `.env.example` 为 `.env`，填入百炼 API Key：

```env
# RAG 知识库配置（使用阿里云百炼平台）
# 注册地址: https://bailian.console.aliyun.com/
# 同一个 API Key 同时用于 LLM 问答和文档向量化
DEEPSEEK_API_KEY=sk-你的百炼API-Key
DEEPSEEK_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
DEEPSEEK_CHAT_MODEL=qwen-turbo
DASHSCOPE_API_KEY=sk-你的百炼API-Key
```

**获取 API Key 步骤**：
1. 注册阿里云账号，开通 [百炼大模型服务平台](https://bailian.console.aliyun.com/)
2. 进入控制台 → API-KEY 管理 → 创建 API Key
3. 将 Key 填入 `.env` 的 `DEEPSEEK_API_KEY` 和 `DASHSCOPE_API_KEY`

**可选配置**：

| 配置项 | 默认值 | 说明 |
|---|---|---|
| `CHROMA_PERSIST_DIR` | `Internship-core/chroma_data` | 向量数据持久化目录 |
| `RAG_CHUNK_SIZE` | 500 | 文档分块大小（字符数） |
| `RAG_CHUNK_OVERLAP` | 100 | 分块重叠大小 |
| `RAG_TOP_K` | 5 | 问答检索返回的 Top-K 文档块数 |
| `RAG_MAX_FILE_SIZE_MB` | 20 | 上传文件大小限制 |

### 4.4 菜单数据初始化

如果数据库中没有 RAG 知识库菜单，运行 seed 命令：

```bash
python manage.py seed
```

---

## 五、使用指南

### 5.1 创建知识库

1. 进入 **RAG知识库 → 知识库列表**
2. 点击右上角 **「新建知识库」**
3. 填写名称和描述，选择启用状态
4. 点击确定

### 5.2 上传文档

1. 在知识库列表中，点击目标知识库的 **「管理」** 按钮
2. 进入文档管理页面，点击右上角 **「上传文档」**
3. 选择文件（支持 `.pdf`、`.docx`、`.txt`、`.md`，最大 20MB）
4. 上传后系统自动执行：
   - 文件保存到 `media/rag_docs/{kb_id}/` 目录
   - 后台线程异步处理：解析文本 → 分块 → 调用 Embedding API 向量化 → 存入 ChromaDB
5. 文档状态流转：待处理 → 处理中 → 已完成 / 失败
6. 如果处理失败，可点击 **「重新处理」** 重试

### 5.3 AI 问答

1. 在知识库列表中，点击目标知识库的 **「问答」** 按钮
2. 进入对话界面，在输入框中输入问题
3. 系统执行流程：
   - 调用 Embedding API 将问题向量化
   - 在 ChromaDB 中检索 Top-K 最相关的文档块
   - 将问题 + 参考资料构建 Prompt
   - 调用 LLM 生成回答
4. 回答会标注 **来源引用**（文档名 + 块序号 + 相关度百分比）
5. 可展开查看引用的原文内容

### 5.4 管理操作

| 操作 | 说明 |
|---|---|
| 编辑知识库 | 修改名称、描述、状态 |
| 删除知识库 | 级联删除所有文档、文档块、ChromaDB 向量和物理文件 |
| 删除文档 | 删除文档记录、ChromaDB 向量和物理文件，更新知识库统计 |
| 重新处理 | 仅对失败的文档重新执行解析→分块→向量化流程 |

---

## 六、注意事项

1. **API Key 必须配置**：未配置 Key 时，文档上传会成功但后台处理会失败，AI 问答会报错
2. **文件大小限制**：默认 20MB，可通过 `RAG_MAX_FILE_SIZE_MB` 调整
3. **支持的文件格式**：PDF、DOCX、TXT、MD
4. **文档处理是异步的**：上传后需要等待几秒到几分钟（取决于文件大小和 API 响应速度）
5. **向量数据持久化**：默认存储在 `Internship-core/chroma_data/` 目录，该目录已加入 `.gitignore`
6. **模型切换**：如需更强的回答质量，可将 `DEEPSEEK_CHAT_MODEL` 改为 `qwen-plus`（需付费）

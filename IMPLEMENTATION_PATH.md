# 🛤️ DeepSeek AI 分析功能 - 具体实现路径

## 目录
1. [系统架构](#系统架构)
2. [数据流转](#数据流转)
3. [核心代码解析](#核心代码解析)
4. [API 调用详解](#api-调用详解)
5. [前端展示流程](#前端展示流程)
6. [错误处理机制](#错误处理机制)

---

## 1. 系统架构

### 文件结构
```
bandung/
├── app.py              # 主界面 - Streamlit 前端
├── database.py         # 数据库操作 - SQLite
├── ai_analysis.py      # AI 分析模块 - DeepSeek API
├── attention.db        # 数据存储
└── requirements.txt    # 依赖包（含 openai）
```

### 模块关系图
```
┌─────────────┐
│   app.py    │ ← 用户界面
└──────┬──────┘
       │
       ├─→ ┌──────────────┐
       │   │ database.py  │ ← 读取今日记录
       │   └──────────────┘
       │
       └─→ ┌──────────────────┐
           │ ai_analysis.py   │ ← 调用 DeepSeek API
           └──────────────────┘
                    │
                    ↓
           ┌─────────────────┐
           │ DeepSeek API    │ ← 云端 AI 模型
           └─────────────────┘
```

---

## 2. 数据流转（完整路径）

### 步骤 1: 用户记录时间
```python
# app.py: 用户点击任务卡片
if st.button(f"选择 {task['icon']} {task['name']}", ...):
    # 保存记录到数据库
    save_record(
        start_time=...,      # 开始时间
        end_time=...,        # 结束时间
        task_type="工作",    # 任务类型
        task_icon="💼",      # 任务图标
        focus_level="high",  # 专注度
        notes="完成项目文档" # 备注（可选）
    )
```

**数据存入**: `attention.db` → `records` 表

---

### 步骤 2: 用户切换到 AI 分析标签
```python
# app.py: 第三个标签页
with tab3:
    st.header("🤖 AI 智能分析")

    # 读取今日所有记录
    today_records = get_today_records()
    # 返回: [{
    #   'start_time': datetime(2025, 10, 5, 14, 0),
    #   'end_time': datetime(2025, 10, 5, 15, 0),
    #   'duration': 60,
    #   'task_type': '工作',
    #   'task_icon': '💼',
    #   'focus_level': 'high',
    #   'notes': '完成项目文档'
    # }, ...]
```

**数据来源**: `attention.db` → `records` 表（WHERE date = 今天）

---

### 步骤 3: 用户点击「生成 AI 分析」按钮
```python
# app.py: 按钮事件
if st.button("🚀 生成 AI 分析", type="primary"):
    with st.spinner("🧠 AI 正在分析中..."):
        # 调用 AI 分析模块
        analysis = get_daily_analysis(today_records)

        # 保存到 session_state（会话状态）
        st.session_state['daily_analysis'] = analysis
```

**触发**: `ai_analysis.py` 的 `get_daily_analysis()` 函数

---

### 步骤 4: 数据预处理（AI 分析模块）
```python
# ai_analysis.py: get_daily_analysis() 函数

# 4.1 检查 API Key
if not DEEPSEEK_API_KEY:
    return "⚠️ 未配置 API Key..."

# 4.2 统计数据
total_minutes = sum(r['duration'] for r in records)
# total_minutes = 180  # 例如：3小时

task_summary = {}
for record in records:
    task_type = record['task_type']
    task_summary[task_type] = task_summary.get(task_type, 0) + record['duration']
# task_summary = {'工作': 120, '学习': 60}

focus_summary = {"high": 0, "medium": 0, "low": 0}
for record in records:
    focus_summary[record['focus_level']] += record['duration']
# focus_summary = {'high': 120, 'medium': 60, 'low': 0}
```

**输出**: 汇总统计数据

---

### 步骤 5: 构建提示词（Prompt Engineering）
```python
# ai_analysis.py: 构建发送给 AI 的提示词

prompt = f"""你是一位专业的时间管理顾问。请分析以下用户在 {date_str} 的时间使用数据，给出个性化建议。

**总时长**: 180 分钟 (3.0 小时)

**任务分布**:
- 工作: 120分钟 (66.7%)
- 学习: 60分钟 (33.3%)

**专注度分布**:
- 高专注: 120分钟 (66.7%)
- 中专注: 60分钟 (33.3%)
- 低专注: 0分钟 (0.0%)

**详细记录**:
- 14:00-15:00: 工作 (专注度:high, 备注:完成项目文档)
- 15:00-16:00: 工作 (专注度:high)
- 16:00-17:00: 学习 (专注度:medium, 备注:看了Python教程)

请从以下角度给出分析和建议（使用 Markdown 格式）：

1. **整体评价** (2-3句话概括今天的时间使用情况)
2. **亮点发现** (做得好的地方，1-2个亮点)
3. **改进建议** (具体可执行的建议，2-3条)
4. **明日规划** (基于今天的数据，给出明天的时间安排建议)

要求：
- 语气友好、鼓励为主
- 建议具体可行，不要空泛
- 字数控制在300字以内
- 使用 emoji 让内容更生动
"""
```

**关键点**:
- ✅ 数据结构化（表格形式）
- ✅ 明确分析维度（4个方面）
- ✅ 限定输出格式（Markdown）
- ✅ 控制输出长度（300字）

---

### 步骤 6: 调用 DeepSeek API
```python
# ai_analysis.py: API 调用核心代码

try:
    # 6.1 创建客户端
    client = OpenAI(
        api_key=DEEPSEEK_API_KEY,           # sk-xxxxxxxx
        base_url="https://api.deepseek.com" # DeepSeek 专用地址
    )

    # 6.2 发送请求
    response = client.chat.completions.create(
        model="deepseek-chat",               # 模型名称
        messages=[
            {
                "role": "system",
                "content": "你是一位专业且友好的时间管理顾问，擅长帮助用户优化时间使用、提升专注力。"
            },
            {
                "role": "user",
                "content": prompt                # 上一步构建的提示词
            }
        ],
        temperature=0.7,                      # 创造性参数（0-1）
        max_tokens=1000                       # 最大输出长度
    )

    # 6.3 提取结果
    analysis = response.choices[0].message.content
    # analysis = "### 1. 整体评价\n今天你..."

    return analysis

except Exception as e:
    return f"❌ AI 分析失败\n\n错误: {str(e)}"
```

**HTTP 请求详解**（底层发生了什么）:

```http
POST https://api.deepseek.com/v1/chat/completions
Content-Type: application/json
Authorization: Bearer sk-xxxxxxxx

{
  "model": "deepseek-chat",
  "messages": [
    {
      "role": "system",
      "content": "你是一位专业且友好的时间管理顾问..."
    },
    {
      "role": "user",
      "content": "你是一位专业的时间管理顾问。请分析以下用户在 2025年10月05日 的时间使用数据..."
    }
  ],
  "temperature": 0.7,
  "max_tokens": 1000
}
```

**返回结果**（JSON 格式）:
```json
{
  "id": "chatcmpl-xxx",
  "object": "chat.completion",
  "created": 1728123456,
  "model": "deepseek-chat",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "### 1. 整体评价\n\n今天你的时间利用效率很高！..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 523,
    "completion_tokens": 412,
    "total_tokens": 935
  }
}
```

---

### 步骤 7: 返回结果到前端
```python
# app.py: 显示 AI 分析结果

if 'daily_analysis' in st.session_state:
    # 渲染 Markdown
    st.markdown(st.session_state['daily_analysis'])
    # 显示类似：
    # ### 1. 整体评价
    # 今天你的时间利用效率很高！...
```

**Streamlit 自动渲染**: Markdown → HTML → 用户看到的界面

---

## 3. 核心代码解析

### 3.1 数据库读取（database.py）

```python
def get_today_records():
    """获取今日所有记录"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # 返回字典格式
    c = conn.cursor()

    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    c.execute('''
        SELECT * FROM records
        WHERE start_time >= ? AND start_time < ?
        ORDER BY start_time
    ''', (today_start, today_end))

    records = [dict(row) for row in c.fetchall()]
    conn.close()

    return records
```

**SQL 查询逻辑**:
- `start_time >= today_start`: 今天 00:00 开始
- `start_time < today_end`: 明天 00:00 之前
- `ORDER BY start_time`: 按时间顺序排列

---

### 3.2 提示词工程（ai_analysis.py）

**关键设计原则**:

1. **角色设定** (System Prompt)
   ```python
   {"role": "system", "content": "你是一位专业且友好的时间管理顾问..."}
   ```
   → 让 AI 进入"时间管理专家"角色

2. **数据结构化** (User Prompt)
   ```python
   prompt = f"""
   **总时长**: {total_minutes} 分钟
   **任务分布**: ...
   **专注度分布**: ...
   """
   ```
   → 表格形式，便于 AI 理解

3. **明确输出要求**
   ```python
   请从以下角度给出分析和建议：
   1. **整体评价** (2-3句话)
   2. **亮点发现** (1-2个亮点)
   ...
   ```
   → 结构化输出，避免 AI 发散

4. **限制条件**
   ```python
   要求：
   - 语气友好、鼓励为主
   - 建议具体可行，不要空泛
   - 字数控制在300字以内
   ```
   → 控制输出质量和长度

---

### 3.3 API 调用封装（ai_analysis.py）

```python
from openai import OpenAI

# 兼容性说明：
# DeepSeek API 完全兼容 OpenAI SDK
# 只需修改 base_url 即可

client = OpenAI(
    api_key=DEEPSEEK_API_KEY,              # 你的 API Key
    base_url="https://api.deepseek.com"    # DeepSeek 服务器
)

response = client.chat.completions.create(
    model="deepseek-chat",                 # 模型选择
    messages=[...],                        # 对话历史
    temperature=0.7,                       # 随机性（0=确定，1=创造）
    max_tokens=1000                        # 最大输出长度
)
```

**参数详解**:

| 参数 | 说明 | 推荐值 |
|------|------|--------|
| `model` | 模型名称 | `deepseek-chat`（通用）<br>`deepseek-coder`（代码） |
| `temperature` | 创造性 | `0.3`（稳定分析）<br>`0.7`（平衡）<br>`0.9`（创意） |
| `max_tokens` | 输出长度 | `500`（简短）<br>`1000`（正常）<br>`2000`（详细） |
| `top_p` | 核采样 | `0.9`（默认） |
| `frequency_penalty` | 重复惩罚 | `0.0`（默认） |

---

## 4. API 调用详解

### 4.1 请求构造

**完整请求示例**:
```python
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {
            "role": "system",
            "content": "你是一位专业且友好的时间管理顾问，擅长帮助用户优化时间使用、提升专注力。"
        },
        {
            "role": "user",
            "content": "你是一位专业的时间管理顾问。请分析以下用户在 2025年10月05日 的时间使用数据，给出个性化建议。\n\n**总时长**: 180 分钟 (3.0 小时)\n\n..."
        }
    ],
    temperature=0.7,
    max_tokens=1000,
    stream=False  # 是否流式输出
)
```

### 4.2 响应解析

**标准响应结构**:
```python
# response 对象包含：
response.id                          # "chatcmpl-xxx"
response.model                       # "deepseek-chat"
response.created                     # 1728123456 (Unix 时间戳)
response.choices[0].message.role     # "assistant"
response.choices[0].message.content  # AI 生成的内容（Markdown）
response.choices[0].finish_reason    # "stop" (正常结束)
response.usage.prompt_tokens         # 输入 tokens 数量
response.usage.completion_tokens     # 输出 tokens 数量
response.usage.total_tokens          # 总 tokens 数量
```

**提取结果**:
```python
# 方法1: 直接提取
analysis = response.choices[0].message.content

# 方法2: 包含元数据
result = {
    'content': response.choices[0].message.content,
    'tokens_used': response.usage.total_tokens,
    'cost': response.usage.total_tokens * 0.000001  # 估算成本
}
```

### 4.3 Token 计算

**计算公式**:
```
成本 = (输入tokens × ¥1/百万) + (输出tokens × ¥2/百万)
```

**实际示例**:
```python
# 假设 API 返回
response.usage.prompt_tokens = 523      # 输入
response.usage.completion_tokens = 412  # 输出

# 成本计算
input_cost = 523 / 1_000_000 * 1   # ¥0.000523
output_cost = 412 / 1_000_000 * 2  # ¥0.000824
total_cost = input_cost + output_cost  # ¥0.001347 (约1.3厘)
```

---

## 5. 前端展示流程

### 5.1 Streamlit 会话状态管理

```python
# app.py: 使用 session_state 保存分析结果

if st.button("🚀 生成 AI 分析"):
    # 调用 API
    analysis = get_daily_analysis(today_records)

    # 保存到会话状态（关键！）
    st.session_state['daily_analysis'] = analysis
    # session_state 是 Streamlit 的持久化存储
    # 页面刷新后数据仍然存在

# 显示结果
if 'daily_analysis' in st.session_state:
    st.markdown(st.session_state['daily_analysis'])
```

**为什么要用 session_state？**
- ❌ 不用: 每次页面刷新，分析结果消失
- ✅ 使用: 结果持久化，避免重复调用 API

### 5.2 Markdown 渲染

**AI 返回的内容**（Markdown 格式）:
```markdown
### 1. 整体评价

今天你的时间利用效率很高！工作时间占比66.7%，且大部分时间保持高专注状态。

### 2. 亮点发现 🌟

- ✅ 高专注工作2小时，完成项目文档，执行力很强
- ✅ 安排了1小时学习时间，坚持自我提升

### 3. 改进建议 💡

1. 学习时段专注度为中，可以尝试番茄工作法提升效率
2. 建议增加10-15分钟休息，长期专注需要劳逸结合

### 4. 明日规划 📅

- 把最重要的任务安排在9-11点（今天的高效时段）
- 学习时关闭手机通知，提升专注度
```

**Streamlit 渲染后**（HTML）:
```html
<h3>1. 整体评价</h3>
<p>今天你的时间利用效率很高！工作时间占比66.7%，且大部分时间保持高专注状态。</p>

<h3>2. 亮点发现 🌟</h3>
<ul>
  <li>✅ 高专注工作2小时，完成项目文档，执行力很强</li>
  <li>✅ 安排了1小时学习时间，坚持自我提升</li>
</ul>
...
```

### 5.3 加载状态管理

```python
# app.py: 使用 spinner 显示加载动画

with st.spinner("🧠 AI 正在分析中..."):
    analysis = get_daily_analysis(today_records)
    # 这期间显示转圈动画
    # 完成后自动消失
```

---

## 6. 错误处理机制

### 6.1 分层错误处理

**第1层: API Key 检查**（ai_analysis.py）
```python
if not DEEPSEEK_API_KEY:
    return """
    ### ⚠️ 未配置 API Key
    请设置环境变量：...
    """
```

**第2层: 数据验证**（ai_analysis.py）
```python
if not records:
    return "### 📭 暂无数据\n\n今天还没有记录..."
```

**第3层: API 调用异常**（ai_analysis.py）
```python
try:
    response = client.chat.completions.create(...)
    return response.choices[0].message.content

except Exception as e:
    return f"""
    ### ❌ AI 分析失败

    错误信息: {str(e)}

    可能的原因：
    1. API Key 无效或已过期
    2. 网络连接问题
    3. API 配额不足
    """
```

### 6.2 常见错误类型

| 错误类型 | 原因 | 解决方法 |
|----------|------|----------|
| `AuthenticationError` | API Key 错误 | 检查环境变量 `DEEPSEEK_API_KEY` |
| `RateLimitError` | 请求频率超限 | 等待1分钟后重试 |
| `InsufficientBalanceError` | 余额不足 | 充值账户 |
| `TimeoutError` | 网络超时 | 增加 `timeout` 参数 |
| `InvalidRequestError` | 请求参数错误 | 检查 `max_tokens` 等参数 |

### 6.3 超时处理

```python
# ai_analysis.py: 设置超时时间

client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url=DEEPSEEK_BASE_URL,
    timeout=30.0  # 30秒超时
)

# 或者在请求时设置
response = client.chat.completions.create(
    ...,
    timeout=30.0
)
```

---

## 7. 完整数据流（实例演示）

### 输入数据
```python
today_records = [
    {
        'start_time': datetime(2025, 10, 5, 14, 0),
        'end_time': datetime(2025, 10, 5, 15, 0),
        'duration': 60,
        'task_type': '工作',
        'task_icon': '💼',
        'focus_level': 'high',
        'notes': '完成项目文档'
    },
    {
        'start_time': datetime(2025, 10, 5, 15, 0),
        'end_time': datetime(2025, 10, 5, 16, 0),
        'duration': 60,
        'task_type': '工作',
        'task_icon': '💼',
        'focus_level': 'high',
        'notes': ''
    },
    {
        'start_time': datetime(2025, 10, 5, 16, 0),
        'end_time': datetime(2025, 10, 5, 17, 0),
        'duration': 60,
        'task_type': '学习',
        'task_icon': '📚',
        'focus_level': 'medium',
        'notes': '看了Python教程'
    }
]
```

### 数据统计
```python
total_minutes = 180
task_summary = {'工作': 120, '学习': 60}
focus_summary = {'high': 120, 'medium': 60, 'low': 0}
```

### 构建的提示词
```
你是一位专业的时间管理顾问。请分析以下用户在 2025年10月05日 的时间使用数据，给出个性化建议。

**总时长**: 180 分钟 (3.0 小时)

**任务分布**:
- 工作: 120分钟 (66.7%)
- 学习: 60分钟 (33.3%)

**专注度分布**:
- 高专注: 120分钟 (66.7%)
- 中专注: 60分钟 (33.3%)
- 低专注: 0分钟 (0.0%)

**详细记录**:
- 14:00-15:00: 工作 (专注度:high, 备注:完成项目文档)
- 15:00-16:00: 工作 (专注度:high)
- 16:00-17:00: 学习 (专注度:medium, 备注:看了Python教程)

请从以下角度给出分析和建议（使用 Markdown 格式）：...
```

### API 返回结果
```markdown
### 1. 整体评价

今天你的时间利用效率很高！工作时间占比66.7%，且大部分时间保持高专注状态，这是非常值得肯定的表现 🎉

### 2. 亮点发现 🌟

- ✅ 高专注工作2小时，还完成了项目文档，执行力很强
- ✅ 安排了1小时学习Python，坚持自我提升的习惯很棒

### 3. 改进建议 💡

1. 学习时段专注度为中等，可以尝试用番茄工作法（25分钟专注+5分钟休息）提升效率
2. 连续工作2小时后，建议增加10-15分钟休息，站起来走走，长期专注需要劳逸结合
3. 可以在学习前明确目标（今天要学会XX知识点），有目标的学习更容易保持专注

### 4. 明日规划 📅

- 把最重要、需要深度思考的任务安排在14-16点（今天的高效时段）
- 学习时关闭手机通知，创造无干扰环境
- 晚上睡前30分钟远离电子设备，改善睡眠质量
```

### 用户看到的界面
![AI Analysis UI](示意图)

---

## 8. 性能优化

### 8.1 缓存策略（未来）

```python
# 可以添加缓存，避免重复分析同一天数据

@st.cache_data(ttl=3600)  # 缓存1小时
def get_daily_analysis_cached(records_json: str, date: str):
    records = json.loads(records_json)
    return get_daily_analysis(records)
```

### 8.2 异步调用（未来）

```python
# 使用异步避免阻塞

import asyncio
from openai import AsyncOpenAI

async def get_daily_analysis_async(records):
    client = AsyncOpenAI(...)
    response = await client.chat.completions.create(...)
    return response.choices[0].message.content
```

### 8.3 流式输出（未来）

```python
# 实时显示 AI 生成过程

response = client.chat.completions.create(
    ...,
    stream=True  # 开启流式输出
)

for chunk in response:
    if chunk.choices[0].delta.content:
        st.write(chunk.choices[0].delta.content, end='')
```

---

## 9. 总结

### 核心流程回顾
```
用户记录时间 → 数据存入 SQLite → 用户点击分析按钮
    ↓
读取今日记录 → 数据统计汇总 → 构建提示词
    ↓
调用 DeepSeek API → 接收 Markdown 结果 → Streamlit 渲染
    ↓
用户看到个性化分析报告
```

### 关键技术点
1. ✅ **SQLite 数据读取** - `get_today_records()`
2. ✅ **数据汇总统计** - 任务分布、专注度计算
3. ✅ **提示词工程** - 结构化 prompt 设计
4. ✅ **API 调用封装** - OpenAI SDK 兼容
5. ✅ **结果展示** - Streamlit Markdown 渲染
6. ✅ **错误处理** - 多层异常捕获

### 扩展方向
- [ ] 周报/月报生成
- [ ] 多模型切换（GPT-4、Claude、通义千问）
- [ ] 自定义分析模板
- [ ] 语音播报分析结果
- [ ] 导出 PDF 报告

---

**完整实现路径就是这样！🎉**

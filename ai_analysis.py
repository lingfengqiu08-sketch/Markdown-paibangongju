"""
AI 分析模块 - 使用 DeepSeek API
"""
import os
from datetime import datetime, timedelta
from openai import OpenAI

# DeepSeek API 配置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"

def get_daily_analysis(records: list, date: datetime = None) -> str:
    """
    生成每日注意力分析报告

    Args:
        records: 当天的所有记录列表
        date: 分析日期（默认为今天）

    Returns:
        AI 生成的分析报告（Markdown 格式）
    """
    if not DEEPSEEK_API_KEY:
        return """
### ⚠️ 未配置 API Key

请设置环境变量：
```bash
export DEEPSEEK_API_KEY="your-api-key-here"
```

获取 API Key：https://platform.deepseek.com
"""

    if not records:
        return "### 📭 暂无数据\n\n今天还没有记录，开始记录你的时间吧！"

    # 构建数据摘要
    total_minutes = sum(r['duration'] for r in records)
    task_summary = {}
    focus_summary = {"high": 0, "medium": 0, "low": 0}

    for record in records:
        task_type = record['task_type']
        task_summary[task_type] = task_summary.get(task_type, 0) + record['duration']
        focus_summary[record['focus_level']] += record['duration']

    # 构建提示词
    date_str = date.strftime("%Y年%m月%d日") if date else datetime.now().strftime("%Y年%m月%d日")

    prompt = f"""你是一位专业的时间管理顾问。请分析以下用户在 {date_str} 的时间使用数据，给出个性化建议。

**总时长**: {total_minutes} 分钟 ({total_minutes/60:.1f} 小时)

**任务分布**:
"""
    for task, minutes in sorted(task_summary.items(), key=lambda x: x[1], reverse=True):
        prompt += f"- {task}: {minutes}分钟 ({minutes/total_minutes*100:.1f}%)\n"

    prompt += f"""
**专注度分布**:
- 高专注: {focus_summary['high']}分钟 ({focus_summary['high']/total_minutes*100:.1f}%)
- 中专注: {focus_summary['medium']}分钟 ({focus_summary['medium']/total_minutes*100:.1f}%)
- 低专注: {focus_summary['low']}分钟 ({focus_summary['low']/total_minutes*100:.1f}%)

**详细记录**:
"""
    for record in records:
        prompt += f"- {record['start_time']:%H:%M}-{record['end_time']:%H:%M}: {record['task_type']} (专注度:{record['focus_level']}"
        if record.get('notes'):
            prompt += f", 备注:{record['notes']}"
        prompt += ")\n"

    prompt += """
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

    try:
        # 调用 DeepSeek API
        client = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_BASE_URL
        )

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一位专业且友好的时间管理顾问，擅长帮助用户优化时间使用、提升专注力。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )

        analysis = response.choices[0].message.content
        return analysis

    except Exception as e:
        return f"""
### ❌ AI 分析失败

错误信息: {str(e)}

**可能的原因：**
1. API Key 无效或已过期
2. 网络连接问题
3. API 配额不足

**解决方法：**
- 检查 DEEPSEEK_API_KEY 环境变量是否正确
- 访问 https://platform.deepseek.com 检查账户状态
"""


def get_weekly_analysis(daily_records: dict) -> str:
    """
    生成每周注意力分析报告

    Args:
        daily_records: 字典，key 为日期，value 为当天的记录列表

    Returns:
        AI 生成的周报（Markdown 格式）
    """
    if not DEEPSEEK_API_KEY:
        return """
### ⚠️ 未配置 API Key

请设置环境变量：
```bash
export DEEPSEEK_API_KEY="your-api-key-here"
```
"""

    if not daily_records:
        return "### 📭 暂无数据\n\n本周还没有记录。"

    # 构建周数据摘要
    total_minutes = 0
    task_summary = {}
    focus_summary = {"high": 0, "medium": 0, "low": 0}
    daily_summary = []

    for date_str, records in sorted(daily_records.items()):
        daily_total = sum(r['duration'] for r in records)
        total_minutes += daily_total
        daily_summary.append(f"{date_str}: {daily_total}分钟")

        for record in records:
            task_type = record['task_type']
            task_summary[task_type] = task_summary.get(task_type, 0) + record['duration']
            focus_summary[record['focus_level']] += record['duration']

    prompt = f"""你是一位专业的时间管理顾问。请分析用户本周的时间使用数据，给出周报和下周规划。

**本周总时长**: {total_minutes} 分钟 ({total_minutes/60:.1f} 小时)
**平均每天**: {total_minutes/len(daily_records):.0f} 分钟

**每日时长**:
"""
    for day_summary in daily_summary:
        prompt += f"- {day_summary}\n"

    prompt += f"""
**任务分布**:
"""
    for task, minutes in sorted(task_summary.items(), key=lambda x: x[1], reverse=True):
        prompt += f"- {task}: {minutes}分钟 ({minutes/total_minutes*100:.1f}%)\n"

    prompt += f"""
**专注度分布**:
- 高专注: {focus_summary['high']}分钟 ({focus_summary['high']/total_minutes*100:.1f}%)
- 中专注: {focus_summary['medium']}分钟 ({focus_summary['medium']/total_minutes*100:.1f}%)
- 低专注: {focus_summary['low']}分钟 ({focus_summary['low']/total_minutes*100:.1f}%)

请从以下角度给出周报（使用 Markdown 格式）：

1. **本周总结** (3-4句话)
2. **最佳表现日** (哪天表现最好，为什么)
3. **待改进点** (2-3个具体问题)
4. **下周目标** (给出可执行的3个目标)

要求：
- 数据驱动，基于具体数字
- 建议可落地执行
- 字数控制在400字以内
"""

    try:
        client = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_BASE_URL
        )

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一位专业的时间管理顾问，擅长数据分析和目标制定。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"### ❌ AI 分析失败\n\n错误: {str(e)}"


def get_productivity_tips(records: list) -> list:
    """
    基于用户数据，生成3条快速提示

    Returns:
        提示列表，每条是一个字符串
    """
    if not records:
        return [
            "💡 开始记录你的时间，了解时间都去哪了",
            "🎯 设定今天的优先任务，专注完成3件重要的事",
            "⏰ 使用番茄工作法，25分钟专注 + 5分钟休息"
        ]

    total_minutes = sum(r['duration'] for r in records)
    high_focus = sum(r['duration'] for r in records if r['focus_level'] == 'high')
    low_focus = sum(r['duration'] for r in records if r['focus_level'] == 'low')

    tips = []

    # 基于专注度给建议
    if low_focus > total_minutes * 0.3:
        tips.append("⚠️ 低专注时段较多，建议减少干扰源（关闭通知、整理桌面）")
    elif high_focus > total_minutes * 0.5:
        tips.append("🎉 高专注比例很棒！保持这个节奏")

    # 基于记录频率给建议
    if len(records) < 4:
        tips.append("📝 增加记录频率，每1-2小时记录一次，数据更准确")

    # 基于时长给建议
    if total_minutes < 240:  # 少于4小时
        tips.append("⏱️ 今天记录时间较少，别忘了记录其他活动哦")

    # 补充通用建议
    generic_tips = [
        "🌅 找出你的黄金时段，把重要任务安排在这个时间",
        "🔄 每90分钟休息一次，长期专注需要劳逸结合",
        "📊 每周回顾数据，发现时间使用模式"
    ]

    while len(tips) < 3:
        tips.append(generic_tips[len(tips)])

    return tips[:3]

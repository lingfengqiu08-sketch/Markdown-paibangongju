"""
注意力追踪系统 - 主界面
"""
import streamlit as st
from datetime import datetime, timedelta
from database import *
from ai_analysis import get_daily_analysis, get_productivity_tips

# 页面配置
st.set_page_config(
    page_title="注意力追踪系统",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化数据库
init_database()

# 自定义CSS - 卡片式设计
st.markdown("""
<style>
/* 卡片样式 */
.task-card {
    padding: 20px;
    border-radius: 16px;
    margin: 10px 0;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.task-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 12px rgba(0, 0, 0, 0.15);
}

.task-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 6px;
    height: 100%;
}

.task-icon {
    font-size: 2.5em;
    margin-bottom: 10px;
}

.task-name {
    font-size: 1.2em;
    font-weight: 600;
    margin-bottom: 5px;
}

.task-description {
    font-size: 0.9em;
    color: #6B7280;
    margin-bottom: 10px;
}

.task-stats {
    font-size: 0.85em;
    color: #9CA3AF;
}

/* 按钮样式 */
.stButton button {
    border-radius: 8px;
    font-weight: 500;
}

/* 模板卡片 */
.template-card {
    padding: 15px;
    border-radius: 12px;
    border: 2px solid #E5E7EB;
    cursor: pointer;
    transition: all 0.2s;
}

.template-card:hover {
    border-color: #3B82F6;
    background: #EFF6FF;
}
</style>
""", unsafe_allow_html=True)

# ========== 侧边栏：任务管理 ==========

with st.sidebar:
    st.header("⚙️ 任务管理")

    # 预设模板
    with st.expander("📦 快速导入模板", expanded=False):
        st.write("选择适合你的预设模板：")

        template_options = list(TASK_TEMPLATES.keys())
        selected_template = st.selectbox(
            "选择模板",
            template_options,
            label_visibility="collapsed"
        )

        # 预览模板内容
        if selected_template:
            st.write(f"**{selected_template}模板包含：**")
            for task in TASK_TEMPLATES[selected_template]:
                st.write(f"{task[1]} {task[0]}")

        if st.button("🚀 应用模板", use_container_width=True):
            if apply_template(selected_template):
                st.success(f"✅ 已应用 {selected_template} 模板！")
                st.rerun()
            else:
                st.error("应用模板失败")

    st.markdown("---")

    # 我的任务列表
    st.subheader("📋 我的任务")

    tasks = get_all_task_types()

    if not tasks:
        st.info("暂无任务，请先导入模板或手动添加")
    else:
        for i, task in enumerate(tasks):
            with st.container():
                # 任务卡片
                st.markdown(f"""
                <div class="task-card" style="background: {task['color']}15; border-left: 4px solid {task['color']}">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="flex: 1;">
                            <span style="font-size: 1.5em;">{task['icon']}</span>
                            <span style="font-size: 1.1em; font-weight: 600; margin-left: 10px;">{task['name']}</span>
                        </div>
                    </div>
                    <div style="font-size: 0.85em; color: #6B7280; margin-top: 5px;">
                        {task['description']}
                    </div>
                    <div style="font-size: 0.8em; color: #9CA3AF; margin-top: 5px;">
                        使用 {task['use_count']} 次
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # 操作按钮
                col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

                with col1:
                    if st.button("⬆️", key=f"up_{task['id']}", help="上移"):
                        move_task_up(task['id'])
                        st.rerun()

                with col2:
                    if st.button("⬇️", key=f"down_{task['id']}", help="下移"):
                        move_task_down(task['id'])
                        st.rerun()

                with col3:
                    if st.button("✏️", key=f"edit_{task['id']}", help="编辑"):
                        st.session_state[f'editing_{task["id"]}'] = True
                        st.rerun()

                with col4:
                    if st.button("🗑️", key=f"del_{task['id']}", help="删除"):
                        delete_task_type(task['id'])
                        st.rerun()

                # 编辑模式
                if st.session_state.get(f'editing_{task["id"]}', False):
                    with st.form(f"edit_form_{task['id']}"):
                        new_name = st.text_input("名称", task['name'])
                        new_icon = st.text_input("图标", task['icon'])
                        new_color = st.color_picker("颜色", task['color'])
                        new_desc = st.text_area("描述", task['description'])

                        col_save, col_cancel = st.columns(2)
                        with col_save:
                            if st.form_submit_button("保存", use_container_width=True):
                                update_task_type(task['id'], new_name, new_icon,
                                               new_color, new_desc)
                                st.session_state[f'editing_{task["id"]}'] = False
                                st.rerun()
                        with col_cancel:
                            if st.form_submit_button("取消", use_container_width=True):
                                st.session_state[f'editing_{task["id"]}'] = False
                                st.rerun()

                st.markdown("---")

    # 添加新任务
    with st.expander("➕ 添加新任务", expanded=False):
        with st.form("add_task_form"):
            new_name = st.text_input("任务名称*")
            new_icon = st.text_input("图标（Emoji）", "📝")
            new_color = st.color_picker("颜色", "#3B82F6")
            new_desc = st.text_area("描述（可选）")

            if st.form_submit_button("✅ 保存", use_container_width=True):
                if new_name:
                    task_id = add_task_type(new_name, new_icon, new_color, new_desc)
                    if task_id:
                        st.success(f"✅ 已添加：{new_icon} {new_name}")
                        st.rerun()
                    else:
                        st.error("任务名称已存在")
                else:
                    st.error("请输入任务名称")

# ========== 主界面 ==========

st.title("🎯 注意力追踪系统")

# Tab导航
tab1, tab2, tab3 = st.tabs(["📝 快速记录", "📊 今日数据", "📈 统计报告"])

# ========== Tab 1: 快速记录 ==========

with tab1:
    # 计算上一小时时间段
    now = datetime.now()
    last_hour_start = now.replace(minute=0, second=0, microsecond=0) - timedelta(hours=1)
    last_hour_end = now.replace(minute=0, second=0, microsecond=0)

    st.header(f"⏰ {last_hour_start:%H:%M} - {last_hour_end:%H:%M} 你在做什么？")

    tasks = get_all_task_types()

    if not tasks:
        st.warning("⚠️ 暂无任务类型，请先在侧边栏添加或导入模板")
    else:
        # 卡片式布局（每行3个）
        cols_per_row = 3

        for i in range(0, len(tasks), cols_per_row):
            cols = st.columns(cols_per_row)

            for j, task in enumerate(tasks[i:i+cols_per_row]):
                with cols[j]:
                    # 创建可点击的卡片
                    card_html = f"""
                    <div class="task-card" style="background: {task['color']}20; border-left: 6px solid {task['color']}; min-height: 180px;">
                        <div class="task-icon">{task['icon']}</div>
                        <div class="task-name">{task['name']}</div>
                        <div class="task-description">{task['description']}</div>
                        <div class="task-stats">已使用 {task['use_count']} 次</div>
                    </div>
                    """
                    st.markdown(card_html, unsafe_allow_html=True)

                    # 点击按钮
                    if st.button(
                        f"选择 {task['icon']} {task['name']}",
                        key=f"select_{task['id']}",
                        use_container_width=True
                    ):
                        st.session_state['selected_task'] = task
                        st.session_state['show_focus_selector'] = True
                        st.rerun()

        # 显示专注度选择（选择任务后）
        if st.session_state.get('show_focus_selector', False):
            selected_task = st.session_state.get('selected_task')

            st.markdown("---")
            st.subheader(f"已选择：{selected_task['icon']} {selected_task['name']}")

            # 专注度选择
            focus_options = {
                "😊 高": "high",
                "😐 中": "medium",
                "😢 低": "low"
            }

            selected_focus = st.radio(
                "专注度如何？",
                list(focus_options.keys()),
                horizontal=True,
                index=1
            )

            # 可选备注
            notes = st.text_input("备注（可选）", placeholder="例如：开了3个会...")

            # 确认按钮
            col1, col2 = st.columns([1, 1])

            with col1:
                if st.button("✅ 确认记录", use_container_width=True, type="primary"):
                    # 保存记录
                    save_record(
                        last_hour_start,
                        last_hour_end,
                        selected_task['name'],
                        selected_task['icon'],
                        focus_options[selected_focus],
                        notes
                    )
                    # 增加使用次数
                    increment_use_count(selected_task['id'])

                    st.success(f"✅ 已记录：{selected_task['icon']} {selected_task['name']} ({selected_focus})")

                    # 清空状态
                    st.session_state['show_focus_selector'] = False
                    st.session_state['selected_task'] = None

                    st.rerun()

            with col2:
                if st.button("❌ 取消", use_container_width=True):
                    st.session_state['show_focus_selector'] = False
                    st.session_state['selected_task'] = None
                    st.rerun()

        # 快速添加按钮
        st.markdown("---")
        with st.expander("➕ 快速添加新任务并使用"):
            quick_name = st.text_input("任务名称", key="quick_name")
            quick_icon = st.text_input("图标", "📝", key="quick_icon")

            if st.button("添加并使用", key="quick_add"):
                if quick_name:
                    task_id = add_task_type(quick_name, quick_icon)
                    if task_id:
                        st.success(f"✅ 已添加：{quick_icon} {quick_name}")
                        st.rerun()
                    else:
                        st.error("任务名称已存在")
                else:
                    st.error("请输入任务名称")

# ========== Tab 2: 今日数据 ==========

with tab2:
    st.header("📊 今日时间分布")

    today_records = get_today_records()

    if not today_records:
        st.info("今天还没有记录，去快速记录一下吧！")
    else:
        # 时间轴展示
        st.subheader("⏰ 时间轴")

        for record in today_records:
            focus_emoji = {
                'high': '😊',
                'medium': '😐',
                'low': '😢'
            }.get(record['focus_level'], '😐')

            st.markdown(f"""
            <div style="padding: 15px; background: #F9FAFB; border-radius: 8px; margin: 10px 0; border-left: 4px solid #3B82F6;">
                <div style="display: flex; justify-content: space-between;">
                    <div>
                        <span style="font-size: 1.2em;">{record['task_icon']} {record['task_type']}</span>
                        <span style="margin-left: 10px; color: #6B7280;">
                            {record['start_time']:%H:%M} - {record['end_time']:%H:%M}
                        </span>
                    </div>
                    <div>
                        <span style="color: #6B7280;">
                            {record['duration']}分钟 {focus_emoji}
                        </span>
                    </div>
                </div>
                {f'<div style="color: #9CA3AF; margin-top: 5px; font-size: 0.9em;">💬 {record["notes"]}</div>' if record['notes'] else ''}
            </div>
            """, unsafe_allow_html=True)

        # 统计汇总
        st.markdown("---")
        st.subheader("📈 今日汇总")

        # 按任务类型统计
        task_stats = {}
        for record in today_records:
            if record['task_type'] not in task_stats:
                task_stats[record['task_type']] = {
                    'icon': record['task_icon'],
                    'duration': 0,
                    'count': 0
                }
            task_stats[record['task_type']]['duration'] += record['duration']
            task_stats[record['task_type']]['count'] += 1

        # 显示统计卡片
        cols = st.columns(len(task_stats))

        for i, (task_name, stats) in enumerate(task_stats.items()):
            with cols[i]:
                st.metric(
                    label=f"{stats['icon']} {task_name}",
                    value=f"{stats['duration']}分钟",
                    delta=f"{stats['count']}次"
                )

# ========== Tab 3: AI 分析 ==========

with tab3:
    st.header("🤖 AI 智能分析")

    # 快速提示
    st.subheader("💡 今日提示")
    tips = get_productivity_tips(today_records)
    for tip in tips:
        st.info(tip)

    st.markdown("---")

    # 每日分析
    st.subheader("📊 今日深度分析")

    if not today_records:
        st.warning("📭 今天还没有记录，记录至少1小时后即可生成 AI 分析！")
    else:
        # 显示分析按钮
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("🚀 生成 AI 分析", type="primary", use_container_width=True):
                with st.spinner("🧠 AI 正在分析中..."):
                    analysis = get_daily_analysis(today_records)
                    st.session_state['daily_analysis'] = analysis

        # 显示分析结果
        if 'daily_analysis' in st.session_state:
            st.markdown(st.session_state['daily_analysis'])
        else:
            st.markdown("""
            👆 点击「生成 AI 分析」按钮，获取个性化建议

            **AI 会分析：**
            - ✅ 今日时间使用评价
            - 🌟 你做得好的地方
            - 💡 具体改进建议
            - 📅 明日规划建议
            """)

    st.markdown("---")

    # API Key 配置提示
    with st.expander("⚙️ 配置 DeepSeek API Key"):
        st.markdown("""
        ### 如何配置 API Key？

        **方法1：环境变量（推荐）**
        ```bash
        export DEEPSEEK_API_KEY="your-api-key-here"
        ```

        **方法2：在启动命令中设置**
        ```bash
        DEEPSEEK_API_KEY="your-api-key" streamlit run app.py
        ```

        ### 获取 API Key

        1. 访问 [DeepSeek 平台](https://platform.deepseek.com)
        2. 注册/登录账号
        3. 进入「API Keys」页面
        4. 创建新的 API Key
        5. 复制并保存（只显示一次）

        ### 价格说明

        DeepSeek API 价格非常实惠：
        - **输入**: ¥1 / 百万 tokens
        - **输出**: ¥2 / 百万 tokens
        - 每日分析约消耗 0.001 元

        **首次注册赠送 ¥10 体验金！**
        """)

# ========== 页脚 ==========

st.markdown("---")
st.caption("💡 提示：每小时会自动提醒你记录，也可以手动在这里记录")

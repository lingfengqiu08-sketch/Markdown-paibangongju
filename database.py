"""
注意力追踪系统 - 数据库操作模块
"""
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional

DB_PATH = 'attention.db'

# ========== 数据库初始化 ==========

def init_database():
    """初始化所有数据库表"""
    init_task_types_table()
    init_records_table()
    insert_default_tasks()

def init_task_types_table():
    """创建任务类型表"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS task_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            icon TEXT DEFAULT '📝',
            color TEXT DEFAULT '#3B82F6',
            description TEXT DEFAULT '',
            sort_order INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            use_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

def init_records_table():
    """创建记录表"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_time TIMESTAMP NOT NULL,
            end_time TIMESTAMP NOT NULL,
            duration INTEGER NOT NULL,
            task_type TEXT NOT NULL,
            task_icon TEXT DEFAULT '📝',
            focus_level TEXT DEFAULT 'medium',
            notes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

# ========== 任务类型操作 ==========

def insert_default_tasks():
    """插入默认任务类型（仅在首次运行时）"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 检查是否已有数据
    c.execute('SELECT COUNT(*) FROM task_types')
    if c.fetchone()[0] > 0:
        conn.close()
        return

    default_tasks = [
        ('工作', '💼', '#3B82F6', '深度工作，需要高度专注', 1),
        ('学习', '📚', '#10B981', '知识积累，终身成长', 2),
        ('娱乐', '📱', '#F59E0B', '放松休闲，适度娱乐', 3),
        ('休息', '☕', '#6B7280', '充电恢复，劳逸结合', 4),
    ]

    for task in default_tasks:
        c.execute('''
            INSERT INTO task_types (name, icon, color, description, sort_order)
            VALUES (?, ?, ?, ?, ?)
        ''', task)

    conn.commit()
    conn.close()

def get_all_task_types() -> List[Dict]:
    """获取所有激活的任务类型（按sort_order排序）"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('''
        SELECT id, name, icon, color, description, sort_order, use_count
        FROM task_types
        WHERE is_active = 1
        ORDER BY sort_order ASC
    ''')

    tasks = []
    for row in c.fetchall():
        tasks.append({
            'id': row[0],
            'name': row[1],
            'icon': row[2],
            'color': row[3],
            'description': row[4],
            'sort_order': row[5],
            'use_count': row[6]
        })

    conn.close()
    return tasks

def add_task_type(name: str, icon: str = '📝', color: str = '#3B82F6',
                  description: str = '') -> Optional[int]:
    """添加新任务类型"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    try:
        # 获取当前最大sort_order
        c.execute('SELECT MAX(sort_order) FROM task_types')
        max_order = c.fetchone()[0] or 0

        c.execute('''
            INSERT INTO task_types (name, icon, color, description, sort_order)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, icon, color, description, max_order + 1))

        task_id = c.lastrowid
        conn.commit()
        return task_id
    except sqlite3.IntegrityError:
        # 任务名称已存在
        return None
    finally:
        conn.close()

def update_task_type(task_id: int, name: str = None, icon: str = None,
                     color: str = None, description: str = None):
    """更新任务类型"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    updates = []
    params = []

    if name is not None:
        updates.append('name = ?')
        params.append(name)
    if icon is not None:
        updates.append('icon = ?')
        params.append(icon)
    if color is not None:
        updates.append('color = ?')
        params.append(color)
    if description is not None:
        updates.append('description = ?')
        params.append(description)

    if updates:
        params.append(task_id)
        c.execute(f'''
            UPDATE task_types
            SET {', '.join(updates)}
            WHERE id = ?
        ''', params)
        conn.commit()

    conn.close()

def delete_task_type(task_id: int):
    """软删除任务类型"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('''
        UPDATE task_types
        SET is_active = 0
        WHERE id = ?
    ''', (task_id,))

    conn.commit()
    conn.close()

def move_task_up(task_id: int):
    """上移任务（与前一个交换sort_order）"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 获取当前任务的sort_order
    c.execute('SELECT sort_order FROM task_types WHERE id = ?', (task_id,))
    current_order = c.fetchone()[0]

    # 查找前一个任务
    c.execute('''
        SELECT id, sort_order FROM task_types
        WHERE sort_order < ? AND is_active = 1
        ORDER BY sort_order DESC
        LIMIT 1
    ''', (current_order,))

    prev_task = c.fetchone()
    if prev_task:
        prev_id, prev_order = prev_task

        # 交换sort_order
        c.execute('UPDATE task_types SET sort_order = ? WHERE id = ?',
                 (prev_order, task_id))
        c.execute('UPDATE task_types SET sort_order = ? WHERE id = ?',
                 (current_order, prev_id))

        conn.commit()

    conn.close()

def move_task_down(task_id: int):
    """下移任务（与后一个交换sort_order）"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 获取当前任务的sort_order
    c.execute('SELECT sort_order FROM task_types WHERE id = ?', (task_id,))
    current_order = c.fetchone()[0]

    # 查找后一个任务
    c.execute('''
        SELECT id, sort_order FROM task_types
        WHERE sort_order > ? AND is_active = 1
        ORDER BY sort_order ASC
        LIMIT 1
    ''', (current_order,))

    next_task = c.fetchone()
    if next_task:
        next_id, next_order = next_task

        # 交换sort_order
        c.execute('UPDATE task_types SET sort_order = ? WHERE id = ?',
                 (next_order, task_id))
        c.execute('UPDATE task_types SET sort_order = ? WHERE id = ?',
                 (current_order, next_id))

        conn.commit()

    conn.close()

def increment_use_count(task_id: int):
    """增加使用次数"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('''
        UPDATE task_types
        SET use_count = use_count + 1
        WHERE id = ?
    ''', (task_id,))

    conn.commit()
    conn.close()

# ========== 记录操作 ==========

def save_record(start_time: datetime, end_time: datetime,
                task_type: str, task_icon: str = '📝',
                focus_level: str = 'medium', notes: str = ''):
    """保存时间记录"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    duration = int((end_time - start_time).total_seconds() / 60)  # 分钟

    c.execute('''
        INSERT INTO records (start_time, end_time, duration, task_type,
                            task_icon, focus_level, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (start_time, end_time, duration, task_type, task_icon,
          focus_level, notes))

    conn.commit()
    conn.close()

def get_today_records() -> List[Dict]:
    """获取今日所有记录"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    c.execute('''
        SELECT id, start_time, end_time, duration, task_type,
               task_icon, focus_level, notes
        FROM records
        WHERE start_time >= ?
        ORDER BY start_time ASC
    ''', (today_start,))

    records = []
    for row in c.fetchall():
        records.append({
            'id': row[0],
            'start_time': datetime.fromisoformat(row[1]),
            'end_time': datetime.fromisoformat(row[2]),
            'duration': row[3],
            'task_type': row[4],
            'task_icon': row[5],
            'focus_level': row[6],
            'notes': row[7]
        })

    conn.close()
    return records

# ========== 预设模板 ==========

TASK_TEMPLATES = {
    "学生": [
        ("上课", "📖", "#3B82F6", "课堂学习，认真听讲"),
        ("作业", "✍️", "#10B981", "完成课后作业"),
        ("复习", "📚", "#8B5CF6", "温故知新，巩固知识"),
        ("考试", "📝", "#EF4444", "检验学习成果"),
        ("课外活动", "⚽", "#F59E0B", "社团活动，锻炼身体"),
        ("娱乐", "🎮", "#EC4899", "适度放松"),
    ],
    "打工人": [
        ("工作", "💼", "#3B82F6", "专注工作，高效产出"),
        ("开会", "💬", "#8B5CF6", "团队沟通协作"),
        ("学习", "📚", "#10B981", "提升技能"),
        ("通勤", "🚗", "#6B7280", "往返路上"),
        ("摸鱼", "🐟", "#F59E0B", "适度休息"),
        ("加班", "🌙", "#EF4444", "额外工作时间"),
    ],
    "成长者": [
        ("深度工作", "🎯", "#3B82F6", "专注重要任务"),
        ("阅读", "📖", "#10B981", "知识输入"),
        ("写作", "✍️", "#8B5CF6", "思考输出"),
        ("运动", "🏃", "#EF4444", "身体健康"),
        ("冥想", "🧘", "#EC4899", "内心平静"),
        ("社交", "👥", "#F59E0B", "人际连接"),
    ],
    "创业者": [
        ("产品开发", "💻", "#3B82F6", "核心业务"),
        ("客户沟通", "📞", "#10B981", "商务拓展"),
        ("市场营销", "📢", "#F59E0B", "品牌推广"),
        ("学习", "📚", "#8B5CF6", "行业研究"),
        ("融资", "💰", "#EF4444", "资金筹备"),
        ("团队管理", "👥", "#6B7280", "组织建设"),
    ]
}

def apply_template(template_name: str):
    """应用预设模板"""
    if template_name not in TASK_TEMPLATES:
        return False

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 先清空现有任务（软删除）
    c.execute('UPDATE task_types SET is_active = 0')
    conn.commit()

    # 添加模板任务
    tasks = TASK_TEMPLATES[template_name]
    for i, (name, icon, color, desc) in enumerate(tasks):
        # 检查任务是否已存在（即使是软删除的）
        c.execute('SELECT id FROM task_types WHERE name = ?', (name,))
        existing = c.fetchone()

        if existing:
            # 如果存在，重新激活并更新信息
            c.execute('''
                UPDATE task_types
                SET icon = ?, color = ?, description = ?, sort_order = ?, is_active = 1
                WHERE name = ?
            ''', (icon, color, desc, i + 1, name))
        else:
            # 如果不存在，插入新记录
            c.execute('''
                INSERT INTO task_types (name, icon, color, description, sort_order)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, icon, color, desc, i + 1))

        conn.commit()

    conn.close()
    return True

# 📱 微信小程序版本 - 开发指南

## 🎯 为什么小程序更适合？

### 优势对比

| 对比项 | 微信小程序 | 原生APP | PWA |
|--------|-----------|---------|-----|
| **开发难度** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ |
| **开发时间** | 3-5天 | 2-4周 | 1天 |
| **用户门槛** | 无需下载 | 需要下载安装 | 需要添加 |
| **分享传播** | ✅ 微信内一键分享 | ❌ 需要下载链接 | ⚠️ 受限 |
| **推送通知** | ✅ 模板消息 | ✅ | ⚠️ 受限 |
| **支付功能** | ✅ 微信支付 | 需集成 | 需集成 |
| **审核周期** | 1-3天 | 7-14天 | 无需审核 |
| **用户基数** | 12亿+ | 需推广 | 需推广 |

### 核心优势
✅ **无需下载** - 扫码即用，降低使用门槛
✅ **易于传播** - 微信内分享，天然社交属性
✅ **开发简单** - 类似Web开发，学习成本低
✅ **推送方便** - 模板消息，到达率高
✅ **支付便捷** - 微信支付集成简单

---

## 🛠️ 技术方案选择

### 方案1：原生小程序（推荐）

**技术栈：**
- 前端：WXML + WXSS + JavaScript
- 后端：Python FastAPI（复用现有代码）
- 数据库：MySQL/PostgreSQL（云端）
- AI：DeepSeek API

**架构图：**
```
微信小程序前端
      ↓
  FastAPI 后端
      ↓
  MySQL 数据库
      ↓
 DeepSeek API
```

---

### 方案2：Taro/uni-app（跨平台）

**技术栈：**
- 框架：Taro（React语法）或 uni-app（Vue语法）
- 一次开发，生成：微信/支付宝/抖音/百度小程序

**优势：**
✅ 一套代码，多端运行
✅ 使用熟悉的前端框架
✅ 社区活跃，组件丰富

---

## 🚀 原生小程序开发（详细步骤）

### 第1步：注册小程序账号

1. 访问 [微信公众平台](https://mp.weixin.qq.com)
2. 注册"小程序"账号
3. 完成主体信息认证
4. 获取 **AppID**（开发必需）

**费用：**
- 个人版：免费
- 企业版：¥300/年认证费（支持微信支付）

---

### 第2步：安装开发工具

下载 [微信开发者工具](https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html)

```bash
# macOS 安装后启动
open /Applications/wechatwebdevtools.app
```

---

### 第3步：创建小程序项目

**项目结构：**
```
attention-tracker-miniprogram/
├── pages/                    # 页面目录
│   ├── index/               # 首页（记录时间）
│   │   ├── index.wxml       # 页面结构
│   │   ├── index.wxss       # 页面样式
│   │   ├── index.js         # 页面逻辑
│   │   └── index.json       # 页面配置
│   ├── data/                # 数据页面
│   │   ├── data.wxml
│   │   ├── data.wxss
│   │   ├── data.js
│   │   └── data.json
│   └── analysis/            # AI分析页面
│       ├── analysis.wxml
│       ├── analysis.wxss
│       ├── analysis.js
│       └── analysis.json
├── components/              # 组件目录
│   └── task-card/          # 任务卡片组件
│       ├── task-card.wxml
│       ├── task-card.wxss
│       ├── task-card.js
│       └── task-card.json
├── utils/                   # 工具函数
│   ├── api.js              # API封装
│   └── util.js             # 通用工具
├── app.js                   # 小程序逻辑
├── app.json                 # 全局配置
├── app.wxss                 # 全局样式
└── project.config.json      # 项目配置
```

---

### 第4步：开发核心页面

#### 4.1 首页 - 记录时间 (pages/index/index.wxml)

```xml
<!-- 顶部时间段显示 -->
<view class="time-range">
  <text class="time-text">{{lastHourStart}} - {{lastHourEnd}}</text>
  <text class="time-desc">刚才这1小时你在做什么？</text>
</view>

<!-- 任务卡片网格 -->
<view class="task-grid">
  <block wx:for="{{tasks}}" wx:key="id">
    <view class="task-card"
          style="background-color: {{item.color}}20; border-left: 4px solid {{item.color}}"
          bindtap="selectTask"
          data-task="{{item}}">
      <text class="task-icon">{{item.icon}}</text>
      <text class="task-name">{{item.name}}</text>
    </view>
  </block>
</view>

<!-- 快速添加按钮 -->
<view class="quick-add" bindtap="showAddDialog">
  <text class="add-icon">+</text>
  <text>添加任务</text>
</view>

<!-- 专注度选择弹窗 -->
<view class="modal" wx:if="{{showFocusModal}}">
  <view class="modal-content">
    <view class="modal-title">选择专注度</view>
    <view class="focus-options">
      <view class="focus-item" bindtap="confirmRecord" data-level="high">
        <text class="focus-emoji">😊</text>
        <text>高专注</text>
      </view>
      <view class="focus-item" bindtap="confirmRecord" data-level="medium">
        <text class="focus-emoji">😐</text>
        <text>中专注</text>
      </view>
      <view class="focus-item" bindtap="confirmRecord" data-level="low">
        <text class="focus-emoji">😢</text>
        <text>低专注</text>
      </view>
    </view>
    <view class="modal-footer">
      <button bindtap="cancelRecord">取消</button>
    </view>
  </view>
</view>
```

#### 4.2 首页逻辑 (pages/index/index.js)

```javascript
const app = getApp()
const api = require('../../utils/api.js')

Page({
  data: {
    tasks: [],
    lastHourStart: '',
    lastHourEnd: '',
    showFocusModal: false,
    selectedTask: null
  },

  onLoad() {
    this.loadTasks()
    this.calculateTimeRange()
  },

  // 加载任务列表
  async loadTasks() {
    try {
      const res = await api.getTasks()
      this.setData({ tasks: res.data })
    } catch (err) {
      wx.showToast({ title: '加载失败', icon: 'none' })
    }
  },

  // 计算上一小时时间段
  calculateTimeRange() {
    const now = new Date()
    const lastHour = new Date(now.getTime() - 3600000)

    const start = this.formatTime(lastHour)
    const end = this.formatTime(now)

    this.setData({
      lastHourStart: start,
      lastHourEnd: end
    })
  },

  formatTime(date) {
    const h = date.getHours().toString().padStart(2, '0')
    const m = date.getMinutes().toString().padStart(2, '0')
    return `${h}:${m}`
  },

  // 选择任务
  selectTask(e) {
    const task = e.currentTarget.dataset.task
    this.setData({
      selectedTask: task,
      showFocusModal: true
    })
  },

  // 确认记录
  async confirmRecord(e) {
    const focusLevel = e.currentTarget.dataset.level
    const { selectedTask } = this.data

    wx.showLoading({ title: '保存中...' })

    try {
      await api.saveRecord({
        task_type: selectedTask.name,
        task_icon: selectedTask.icon,
        focus_level: focusLevel,
        start_time: this.data.lastHourStart,
        end_time: this.data.lastHourEnd,
        duration: 60
      })

      wx.hideLoading()
      wx.showToast({ title: '记录成功！', icon: 'success' })

      this.setData({ showFocusModal: false })

      // 跳转到数据页面
      setTimeout(() => {
        wx.switchTab({ url: '/pages/data/data' })
      }, 1500)

    } catch (err) {
      wx.hideLoading()
      wx.showToast({ title: '保存失败', icon: 'none' })
    }
  },

  // 取消记录
  cancelRecord() {
    this.setData({ showFocusModal: false })
  },

  // 显示添加对话框
  showAddDialog() {
    wx.navigateTo({ url: '/pages/add-task/add-task' })
  }
})
```

#### 4.3 首页样式 (pages/index/index.wxss)

```css
/* 时间段显示 */
.time-range {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 40rpx 30rpx;
  text-align: center;
  color: white;
}

.time-text {
  display: block;
  font-size: 48rpx;
  font-weight: bold;
  margin-bottom: 10rpx;
}

.time-desc {
  font-size: 28rpx;
  opacity: 0.9;
}

/* 任务卡片网格 */
.task-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20rpx;
  padding: 30rpx;
}

.task-card {
  background: white;
  border-radius: 16rpx;
  padding: 40rpx 20rpx;
  text-align: center;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.08);
  transition: all 0.3s;
}

.task-card:active {
  transform: scale(0.95);
}

.task-icon {
  display: block;
  font-size: 60rpx;
  margin-bottom: 10rpx;
}

.task-name {
  display: block;
  font-size: 28rpx;
  color: #333;
}

/* 快速添加 */
.quick-add {
  position: fixed;
  bottom: 100rpx;
  right: 30rpx;
  background: #667eea;
  color: white;
  padding: 20rpx 30rpx;
  border-radius: 50rpx;
  box-shadow: 0 8rpx 16rpx rgba(102, 126, 234, 0.3);
  display: flex;
  align-items: center;
  gap: 10rpx;
}

.add-icon {
  font-size: 36rpx;
  font-weight: bold;
}

/* 弹窗 */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
}

.modal-content {
  background: white;
  width: 80%;
  border-radius: 16rpx;
  padding: 40rpx;
}

.modal-title {
  font-size: 32rpx;
  font-weight: bold;
  text-align: center;
  margin-bottom: 30rpx;
}

.focus-options {
  display: flex;
  justify-content: space-around;
  margin-bottom: 30rpx;
}

.focus-item {
  text-align: center;
  padding: 20rpx;
  border-radius: 12rpx;
  background: #f5f5f5;
}

.focus-emoji {
  display: block;
  font-size: 48rpx;
  margin-bottom: 10rpx;
}
```

---

### 第5步：API 封装 (utils/api.js)

```javascript
// 配置
const BASE_URL = 'https://your-api.com/api'  // 你的后端API地址
const TIMEOUT = 10000

// 请求封装
function request(url, method = 'GET', data = {}) {
  return new Promise((resolve, reject) => {
    wx.request({
      url: BASE_URL + url,
      method,
      data,
      timeout: TIMEOUT,
      header: {
        'Content-Type': 'application/json',
        // 如果需要登录，添加 token
        // 'Authorization': 'Bearer ' + wx.getStorageSync('token')
      },
      success(res) {
        if (res.statusCode === 200) {
          resolve(res.data)
        } else {
          reject(new Error('请求失败'))
        }
      },
      fail(err) {
        reject(err)
      }
    })
  })
}

// 导出 API
module.exports = {
  // 获取任务列表
  getTasks() {
    return request('/tasks')
  },

  // 保存记录
  saveRecord(data) {
    return request('/records', 'POST', data)
  },

  // 获取今日记录
  getTodayRecords() {
    return request('/records/today')
  },

  // 生成 AI 分析
  getAIAnalysis() {
    return request('/analysis/daily')
  },

  // 添加任务
  addTask(data) {
    return request('/tasks', 'POST', data)
  },

  // 更新任务
  updateTask(id, data) {
    return request(`/tasks/${id}`, 'PUT', data)
  },

  // 删除任务
  deleteTask(id) {
    return request(`/tasks/${id}`, 'DELETE')
  }
}
```

---

### 第6步：后端 API 开发（FastAPI）

创建 `backend/main.py`：

```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
import uvicorn

# 复用现有的数据库模块
from database import *
from ai_analysis import get_daily_analysis

app = FastAPI(title="注意力追踪 API")

# 允许小程序跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== 数据模型 ==========

class Task(BaseModel):
    name: str
    icon: str = "📝"
    color: str = "#3B82F6"
    description: str = ""

class Record(BaseModel):
    task_type: str
    task_icon: str
    focus_level: str
    start_time: str
    end_time: str
    duration: int
    notes: str = ""

# ========== API 路由 ==========

@app.get("/")
def read_root():
    return {"message": "注意力追踪 API 运行中"}

# 获取所有任务
@app.get("/api/tasks")
def get_tasks():
    init_database()
    tasks = get_all_task_types()
    return {"code": 0, "data": tasks}

# 添加任务
@app.post("/api/tasks")
def create_task(task: Task):
    task_id = add_task_type(
        task.name,
        task.icon,
        task.color,
        task.description
    )
    if task_id:
        return {"code": 0, "message": "添加成功", "data": {"id": task_id}}
    else:
        raise HTTPException(status_code=400, detail="任务名称已存在")

# 保存记录
@app.post("/api/records")
def create_record(record: Record):
    # 转换时间格式
    start_time = datetime.strptime(record.start_time, "%H:%M")
    end_time = datetime.strptime(record.end_time, "%H:%M")

    # 设置为今天的时间
    now = datetime.now()
    start_time = start_time.replace(year=now.year, month=now.month, day=now.day)
    end_time = end_time.replace(year=now.year, month=now.month, day=now.day)

    save_record(
        start_time,
        end_time,
        record.task_type,
        record.task_icon,
        record.focus_level,
        record.notes
    )

    return {"code": 0, "message": "记录成功"}

# 获取今日记录
@app.get("/api/records/today")
def get_today():
    records = get_today_records()
    return {"code": 0, "data": records}

# 生成 AI 分析
@app.get("/api/analysis/daily")
def daily_analysis():
    records = get_today_records()
    if not records:
        return {"code": 0, "data": "暂无数据"}

    analysis = get_daily_analysis(records)
    return {"code": 0, "data": analysis}

# 启动服务器
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**启动后端：**
```bash
# 安装 FastAPI
pip install fastapi uvicorn

# 启动
python backend/main.py

# API 地址: http://localhost:8000
```

---

### 第7步：数据页面 (pages/data/data.wxml)

```xml
<view class="container">
  <!-- 日期选择 -->
  <view class="date-picker">
    <picker mode="date" value="{{currentDate}}" bindchange="onDateChange">
      <view class="picker-text">
        <text class="date-icon">📅</text>
        <text>{{currentDate}}</text>
      </view>
    </picker>
  </view>

  <!-- 统计卡片 -->
  <view class="stats-cards">
    <view class="stat-card">
      <text class="stat-value">{{totalHours}}</text>
      <text class="stat-label">总时长（小时）</text>
    </view>
    <view class="stat-card">
      <text class="stat-value">{{recordCount}}</text>
      <text class="stat-label">记录次数</text>
    </view>
    <view class="stat-card">
      <text class="stat-value">{{focusRate}}%</text>
      <text class="stat-label">高专注占比</text>
    </view>
  </view>

  <!-- 时间轴 -->
  <view class="timeline">
    <view class="timeline-title">今日时间轴</view>
    <block wx:for="{{records}}" wx:key="id">
      <view class="timeline-item">
        <view class="timeline-time">{{item.start_time}}</view>
        <view class="timeline-dot" style="background: {{item.color}}"></view>
        <view class="timeline-content">
          <view class="timeline-task">
            <text>{{item.task_icon}} {{item.task_type}}</text>
            <text class="timeline-focus">{{item.focus_emoji}}</text>
          </view>
          <view class="timeline-duration">{{item.duration}}分钟</view>
          <view class="timeline-notes" wx:if="{{item.notes}}">💬 {{item.notes}}</view>
        </view>
      </view>
    </block>
  </view>
</view>
```

---

### 第8步：AI 分析页面 (pages/analysis/analysis.wxml)

```xml
<view class="container">
  <!-- 快速提示 -->
  <view class="tips-section">
    <view class="section-title">💡 今日提示</view>
    <block wx:for="{{tips}}" wx:key="index">
      <view class="tip-card">{{item}}</view>
    </block>
  </view>

  <!-- AI 分析按钮 -->
  <view class="analysis-section">
    <view class="section-title">📊 AI 深度分析</view>
    <button
      class="analysis-btn"
      bindtap="generateAnalysis"
      loading="{{loading}}"
      disabled="{{loading}}">
      {{loading ? 'AI 正在分析中...' : '🚀 生成 AI 分析'}}
    </button>
  </view>

  <!-- 分析结果 -->
  <view class="result-section" wx:if="{{analysisResult}}">
    <rich-text nodes="{{analysisHtml}}"></rich-text>
  </view>

  <!-- API 配置说明 -->
  <view class="config-section">
    <view class="config-title" bindtap="toggleConfig">
      ⚙️ API 配置说明
      <text class="arrow">{{showConfig ? '▼' : '▶'}}</text>
    </view>
    <view class="config-content" wx:if="{{showConfig}}">
      <text>需要配置 DeepSeek API Key</text>
      <text>每次分析约 ¥0.001</text>
      <text>访问 platform.deepseek.com 获取</text>
    </view>
  </view>
</view>
```

**AI 分析逻辑 (pages/analysis/analysis.js):**

```javascript
const api = require('../../utils/api.js')
const towxml = require('../../towxml/index')  // Markdown 渲染库

Page({
  data: {
    tips: [],
    loading: false,
    analysisResult: '',
    analysisHtml: '',
    showConfig: false
  },

  onLoad() {
    this.loadTips()
  },

  // 加载快速提示
  loadTips() {
    // 前端简单判断逻辑
    this.setData({
      tips: [
        '💡 开始记录你的时间，了解时间都去哪了',
        '🎯 设定今天的优先任务，专注完成3件重要的事',
        '⏰ 使用番茄工作法，25分钟专注 + 5分钟休息'
      ]
    })
  },

  // 生成 AI 分析
  async generateAnalysis() {
    this.setData({ loading: true })

    try {
      const res = await api.getAIAnalysis()

      // 将 Markdown 转换为 HTML
      const result = towxml(res.data, 'markdown')

      this.setData({
        analysisResult: res.data,
        analysisHtml: result,
        loading: false
      })

      wx.showToast({ title: '分析完成！', icon: 'success' })

    } catch (err) {
      this.setData({ loading: false })
      wx.showModal({
        title: '分析失败',
        content: err.message || '请检查网络连接',
        showCancel: false
      })
    }
  },

  // 切换配置说明
  toggleConfig() {
    this.setData({ showConfig: !this.data.showConfig })
  }
})
```

---

### 第9步：全局配置 (app.json)

```json
{
  "pages": [
    "pages/index/index",
    "pages/data/data",
    "pages/analysis/analysis",
    "pages/add-task/add-task"
  ],
  "window": {
    "backgroundTextStyle": "light",
    "navigationBarBackgroundColor": "#667eea",
    "navigationBarTitleText": "注意力追踪",
    "navigationBarTextStyle": "white",
    "backgroundColor": "#f5f5f5"
  },
  "tabBar": {
    "color": "#999",
    "selectedColor": "#667eea",
    "backgroundColor": "#ffffff",
    "borderStyle": "black",
    "list": [
      {
        "pagePath": "pages/index/index",
        "text": "记录",
        "iconPath": "images/record.png",
        "selectedIconPath": "images/record-active.png"
      },
      {
        "pagePath": "pages/data/data",
        "text": "数据",
        "iconPath": "images/data.png",
        "selectedIconPath": "images/data-active.png"
      },
      {
        "pagePath": "pages/analysis/analysis",
        "text": "AI分析",
        "iconPath": "images/ai.png",
        "selectedIconPath": "images/ai-active.png"
      }
    ]
  },
  "sitemapLocation": "sitemap.json"
}
```

---

### 第10步：部署后端到云服务器

#### 选项1：腾讯云（推荐微信小程序）

```bash
# 1. 购买云服务器（最低配置 2核2G，约¥100/年）

# 2. 安装环境
ssh root@your-server-ip
apt update
apt install python3 python3-pip nginx

# 3. 上传代码
scp -r backend/ root@your-server-ip:/home/

# 4. 安装依赖
cd /home/backend
pip3 install -r requirements.txt

# 5. 使用 supervisor 守护进程
apt install supervisor
nano /etc/supervisor/conf.d/attention-tracker.conf

# 配置内容：
[program:attention-tracker]
command=/usr/bin/python3 /home/backend/main.py
autostart=true
autorestart=true
stderr_logfile=/var/log/attention-tracker.err.log
stdout_logfile=/var/log/attention-tracker.out.log

# 6. 启动
supervisorctl reread
supervisorctl update
supervisorctl start attention-tracker

# 7. 配置 Nginx 反向代理
nano /etc/nginx/sites-available/attention-tracker

# Nginx 配置：
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# 8. 启用配置
ln -s /etc/nginx/sites-available/attention-tracker /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx

# 9. 配置 HTTPS（微信小程序必需）
apt install certbot python3-certbot-nginx
certbot --nginx -d your-domain.com

# API 地址: https://your-domain.com
```

#### 选项2：使用云函数（Serverless，更便宜）

**腾讯云云函数：**
- 免费额度：每月 100万次调用
- 适合小程序后端
- 按需付费，成本极低

---

## 📊 开发时间表

| 阶段 | 任务 | 时间 |
|------|------|------|
| Day 1 | 注册小程序 + 环境搭建 | 2小时 |
| Day 2 | 首页开发（记录功能） | 4小时 |
| Day 3 | 数据页面 + AI分析页面 | 4小时 |
| Day 4 | 后端API开发 | 4小时 |
| Day 5 | 联调测试 + 优化 | 4小时 |
| Day 6 | 部署上线 + 提交审核 | 2小时 |
| **总计** | | **3-5天** |

---

## 💰 成本预算

| 项目 | 费用 | 说明 |
|------|------|------|
| 小程序注册 | ¥0 or ¥300 | 个人免费，企业¥300/年 |
| 云服务器 | ¥100-300/年 | 腾讯云/阿里云 |
| 域名 | ¥50/年 | .com 域名 |
| SSL证书 | ¥0 | Let's Encrypt 免费 |
| DeepSeek API | ¥10 | 首次赠送¥10 |
| **总计** | **¥160-360/年** | 企业版约¥460/年 |

---

## 🎯 我的推荐方案

### 最快路径（黑客松适用）

**Day 1-2: 快速原型**
1. 使用微信开发者工具创建项目
2. 开发首页（记录功能）
3. 后端直接用现有 `app.py`（Streamlit）作为API

**Day 3: 完善功能**
1. 开发数据页面
2. 接入 AI 分析

**Day 4-5: 优化发布**
1. UI/UX 优化
2. 提交审核

### 技术选型建议

✅ **前端**: 原生小程序（学习曲线低）
✅ **后端**: FastAPI（复用现有Python代码）
✅ **数据库**: SQLite → MySQL（部署后升级）
✅ **AI**: DeepSeek API（成本低）
✅ **部署**: 腾讯云（与微信生态集成好）

---

## 🚀 立即开始

### 第1步：现在就注册小程序账号
访问 https://mp.weixin.qq.com 注册

### 第2步：下载开发工具
https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html

### 第3步：创建项目
使用我提供的代码模板开始开发

---

## 📱 额外福利：支付宝/抖音小程序

如果使用 **uni-app** 或 **Taro** 开发，一套代码可以生成：

- ✅ 微信小程序
- ✅ 支付宝小程序
- ✅ 抖音小程序
- ✅ 百度小程序
- ✅ QQ 小程序
- ✅ H5 网页版

**覆盖 15亿+ 用户！**

---

## 🎉 总结

### 小程序 vs APP vs PWA

| 维度 | 小程序 | 原生APP | PWA |
|------|--------|---------|-----|
| 开发时间 | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ |
| 用户门槛 | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐ |
| 传播能力 | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ |
| 用户体验 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 开发成本 | 低 | 高 | 极低 |

### 推荐路线

```
第1阶段（黑客松）: 微信小程序
        ↓
第2阶段（产品化）: uni-app 多端小程序
        ↓
第3阶段（规模化）: Flutter 原生APP
```

**小程序确实是当前最佳选择！3-5天就能上线！🚀**

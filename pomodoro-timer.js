class PomodoroTimer {
    constructor() {
        this.workTime = 25 * 60;
        this.shortBreakTime = 5 * 60;
        this.longBreakTime = 30 * 60;
        
        this.currentTime = this.workTime;
        this.totalTime = this.workTime;
        this.isRunning = false;
        this.isPaused = false;
        this.isBreak = false;
        
        this.sessionCount = 0;
        this.totalSessions = 4;
        
        this.timer = null;
        this.audioContext = null;
        this.startTimestamp = null;
        this.pausedTime = 0;
        
        this.elements = {
            timer: document.getElementById('timer'),
            status: document.getElementById('status'),
            startBtn: document.getElementById('startBtn'),
            pauseBtn: document.getElementById('pauseBtn'),
            resetBtn: document.getElementById('resetBtn'),
            progress: document.getElementById('progress'),
            sessionDots: document.getElementById('sessionDots').children,
            sessionText: document.getElementById('sessionText'),
            workTimeInput: document.getElementById('workTime'),
            shortBreakInput: document.getElementById('shortBreak'),
            longBreakInput: document.getElementById('longBreak'),
            soundToggle: document.getElementById('soundToggle'),
            notificationToggle: document.getElementById('notificationToggle'),
            notificationPermission: document.getElementById('notificationPermission')
        };
        
        this.init();
    }
    
    init() {
        this.loadSettings();
        this.setupEventListeners();
        this.updateDisplay();
        this.checkNotificationPermission();
        this.initAudioContext();
    }
    
    initAudioContext() {
        try {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        } catch (e) {
            console.log('Web Audio API not supported');
        }
    }
    
    playSound(frequency = 800, duration = 200) {
        if (!this.elements.soundToggle.checked || !this.audioContext) return;
        
        const oscillator = this.audioContext.createOscillator();
        const gainNode = this.audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(this.audioContext.destination);
        
        oscillator.frequency.value = frequency;
        oscillator.type = 'sine';
        
        gainNode.gain.setValueAtTime(0.3, this.audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + duration / 1000);
        
        oscillator.start(this.audioContext.currentTime);
        oscillator.stop(this.audioContext.currentTime + duration / 1000);
    }
    
    playNotificationSound() {
        if (!this.elements.soundToggle.checked || !this.audioContext) return;
        
        const pattern = [
            { freq: 523, time: 0 },
            { freq: 659, time: 200 },
            { freq: 784, time: 400 },
            { freq: 1047, time: 600 },
            { freq: 784, time: 800 },
            { freq: 659, time: 1000 },
            { freq: 523, time: 1200 },
            { freq: 659, time: 1400 },
            { freq: 784, time: 1600 },
            { freq: 1047, time: 1800 },
            { freq: 1319, time: 2000 },
            { freq: 1047, time: 2200 },
            { freq: 784, time: 2400 },
            { freq: 659, time: 2600 },
            { freq: 523, time: 2800 }
        ];
        
        pattern.forEach(note => {
            setTimeout(() => this.playSound(note.freq, 180), note.time);
        });
    }
    
    setupEventListeners() {
        this.elements.workTimeInput.addEventListener('change', () => {
            this.workTime = parseInt(this.elements.workTimeInput.value) * 60;
            if (!this.isRunning && !this.isBreak) {
                this.currentTime = this.workTime;
                this.totalTime = this.workTime;
                this.updateDisplay();
            }
            this.saveSettings();
        });
        
        this.elements.shortBreakInput.addEventListener('change', () => {
            this.shortBreakTime = parseInt(this.elements.shortBreakInput.value) * 60;
            this.saveSettings();
        });
        
        this.elements.longBreakInput.addEventListener('change', () => {
            this.longBreakTime = parseInt(this.elements.longBreakInput.value) * 60;
            this.saveSettings();
        });
        
        this.elements.soundToggle.addEventListener('change', () => {
            this.saveSettings();
        });
        
        this.elements.notificationToggle.addEventListener('change', () => {
            if (this.elements.notificationToggle.checked) {
                this.requestNotificationPermission();
            }
            this.saveSettings();
        });
        
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden && this.isRunning) {
                this.updateDisplay();
            }
        });
    }
    
    loadSettings() {
        const settings = localStorage.getItem('pomodoroSettings');
        if (settings) {
            const parsed = JSON.parse(settings);
            this.elements.workTimeInput.value = parsed.workTime || 25;
            this.elements.shortBreakInput.value = parsed.shortBreak || 5;
            this.elements.longBreakInput.value = parsed.longBreak || 30;
            this.elements.soundToggle.checked = parsed.sound !== false;
            this.elements.notificationToggle.checked = parsed.notification || false;
            
            this.workTime = parseInt(this.elements.workTimeInput.value) * 60;
            this.shortBreakTime = parseInt(this.elements.shortBreakInput.value) * 60;
            this.longBreakTime = parseInt(this.elements.longBreakInput.value) * 60;
            this.currentTime = this.workTime;
            this.totalTime = this.workTime;
        }
    }
    
    saveSettings() {
        const settings = {
            workTime: parseInt(this.elements.workTimeInput.value),
            shortBreak: parseInt(this.elements.shortBreakInput.value),
            longBreak: parseInt(this.elements.longBreakInput.value),
            sound: this.elements.soundToggle.checked,
            notification: this.elements.notificationToggle.checked
        };
        localStorage.setItem('pomodoroSettings', JSON.stringify(settings));
    }
    
    checkNotificationPermission() {
        if ('Notification' in window) {
            if (Notification.permission === 'default') {
                this.elements.notificationPermission.style.display = 'block';
            } else if (Notification.permission === 'granted') {
                this.elements.notificationPermission.style.display = 'none';
            }
        }
    }
    
    requestNotificationPermission() {
        if ('Notification' in window) {
            Notification.requestPermission().then(permission => {
                if (permission === 'granted') {
                    this.elements.notificationPermission.style.display = 'none';
                    this.elements.notificationToggle.checked = true;
                    this.saveSettings();
                    new Notification('番茄工作法', {
                        body: '通知已启用！',
                        icon: '🍅'
                    });
                } else {
                    this.elements.notificationToggle.checked = false;
                    this.saveSettings();
                }
            });
        }
    }
    
    startTimer() {
        if (!this.isRunning) {
            this.isRunning = true;
            this.isPaused = false;
            
            this.elements.startBtn.disabled = true;
            this.elements.pauseBtn.disabled = false;
            
            if (!this.isBreak && this.currentTime === this.workTime) {
                this.sessionCount++;
                this.updateSessionDisplay();
            }
            
            this.startTimestamp = Date.now() - (this.totalTime - this.currentTime) * 1000;
            
            this.timer = setInterval(() => this.tick(), 100);
            this.updateStatus();
            
            if (this.audioContext && this.audioContext.state === 'suspended') {
                this.audioContext.resume();
            }
        }
    }
    
    pauseTimer() {
        if (this.isRunning && !this.isPaused) {
            this.isPaused = true;
            this.isRunning = false;
            clearInterval(this.timer);
            
            this.pausedTime = Date.now() - this.startTimestamp;
            
            this.elements.startBtn.disabled = false;
            this.elements.startBtn.textContent = '继续';
            this.elements.pauseBtn.disabled = true;
            
            this.elements.status.textContent = '已暂停';
        }
    }
    
    resetTimer() {
        clearInterval(this.timer);
        
        this.isRunning = false;
        this.isPaused = false;
        this.isBreak = false;
        this.sessionCount = 0;
        this.startTimestamp = null;
        this.pausedTime = 0;
        
        this.workTime = parseInt(this.elements.workTimeInput.value) * 60;
        this.currentTime = this.workTime;
        this.totalTime = this.workTime;
        
        this.elements.startBtn.disabled = false;
        this.elements.startBtn.textContent = '开始';
        this.elements.pauseBtn.disabled = true;
        
        this.updateDisplay();
        this.updateSessionDisplay();
        this.updateStatus();
    }
    
    tick() {
        const elapsed = Math.floor((Date.now() - this.startTimestamp) / 1000);
        const newTime = this.totalTime - elapsed;
        
        if (newTime !== this.currentTime) {
            this.currentTime = newTime;
            
            if (this.currentTime <= 0) {
                this.currentTime = 0;
                this.timerComplete();
            } else {
                this.updateDisplay();
            }
        }
    }
    
    timerComplete() {
        clearInterval(this.timer);
        this.isRunning = false;
        
        this.playNotificationSound();
        
        if (this.isBreak) {
            this.showNotification('休息结束', '是时候继续工作了！');
            this.startWorkSession();
        } else {
            this.markSessionComplete();
            
            if (this.sessionCount % this.totalSessions === 0) {
                this.showNotification('长休息时间', '恭喜完成4个番茄！享受30分钟的休息吧！');
                this.startBreak(true);
            } else {
                this.showNotification('工作完成', '休息5分钟吧！');
                this.startBreak(false);
            }
        }
    }
    
    startWorkSession() {
        this.isBreak = false;
        this.currentTime = this.workTime;
        this.totalTime = this.workTime;
        this.startTimestamp = null;
        this.pausedTime = 0;
        
        this.elements.startBtn.disabled = false;
        this.elements.startBtn.textContent = '开始';
        this.elements.pauseBtn.disabled = true;
        
        this.updateDisplay();
        this.updateStatus();
    }
    
    startBreak(isLong) {
        this.isBreak = true;
        this.startTimestamp = null;
        this.pausedTime = 0;
        
        if (isLong) {
            this.currentTime = this.longBreakTime;
            this.totalTime = this.longBreakTime;
        } else {
            this.currentTime = this.shortBreakTime;
            this.totalTime = this.shortBreakTime;
        }
        
        this.updateDisplay();
        this.updateStatus();
        
        setTimeout(() => {
            this.startTimer();
        }, 1000);
    }
    
    markSessionComplete() {
        const sessionIndex = (this.sessionCount - 1) % this.totalSessions;
        if (sessionIndex >= 0 && sessionIndex < this.elements.sessionDots.length) {
            this.elements.sessionDots[sessionIndex].classList.add('completed');
            this.elements.sessionDots[sessionIndex].classList.remove('active');
        }
    }
    
    updateSessionDisplay() {
        for (let i = 0; i < this.elements.sessionDots.length; i++) {
            this.elements.sessionDots[i].classList.remove('active', 'completed');
            
            const completedInCycle = (this.sessionCount - 1) % this.totalSessions;
            const currentInCycle = this.sessionCount % this.totalSessions;
            
            if (i < completedInCycle || (this.sessionCount > 0 && currentInCycle === 0 && !this.isBreak)) {
                this.elements.sessionDots[i].classList.add('completed');
            } else if (i === currentInCycle - 1 && !this.isBreak && this.isRunning) {
                this.elements.sessionDots[i].classList.add('active');
            }
        }
        
        const displaySession = this.sessionCount === 0 ? 1 : 
                             ((this.sessionCount - 1) % this.totalSessions) + 1;
        
        if (this.isBreak) {
            if (this.sessionCount % this.totalSessions === 0) {
                this.elements.sessionText.textContent = '长休息时间';
            } else {
                this.elements.sessionText.textContent = '短休息时间';
            }
        } else {
            this.elements.sessionText.textContent = `第 ${displaySession} 个番茄时间`;
        }
    }
    
    updateStatus() {
        if (this.isRunning) {
            if (this.isBreak) {
                this.elements.status.textContent = this.currentTime > this.shortBreakTime ? '长休息中...' : '休息中...';
            } else {
                this.elements.status.textContent = '专注工作中...';
            }
        } else if (this.isPaused) {
            this.elements.status.textContent = '已暂停';
        } else {
            if (this.sessionCount === 0) {
                this.elements.status.textContent = '准备开始工作';
            } else {
                this.elements.status.textContent = this.isBreak ? '准备休息' : '准备工作';
            }
        }
    }
    
    updateDisplay() {
        const minutes = Math.floor(this.currentTime / 60);
        const seconds = this.currentTime % 60;
        
        this.elements.timer.textContent = 
            `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        
        const progress = ((this.totalTime - this.currentTime) / this.totalTime) * 729;
        this.elements.progress.style.strokeDashoffset = 729 - progress;
        
        if (this.isBreak) {
            this.elements.progress.style.stroke = 'url(#gradient-break)';
            
            if (!document.getElementById('gradient-break')) {
                const svg = this.elements.progress.parentElement;
                const defs = svg.querySelector('defs');
                const gradientBreak = document.createElementNS('http://www.w3.org/2000/svg', 'linearGradient');
                gradientBreak.setAttribute('id', 'gradient-break');
                gradientBreak.innerHTML = `
                    <stop offset="0%" style="stop-color:#4CAF50;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#8BC34A;stop-opacity:1" />
                `;
                defs.appendChild(gradientBreak);
            }
        } else {
            this.elements.progress.style.stroke = 'url(#gradient)';
        }
        
        if (this.isRunning && this.currentTime <= 10 && this.currentTime > 0) {
            this.elements.timer.style.color = '#ff5722';
        } else {
            this.elements.timer.style.color = '#333';
        }
    }
    
    showNotification(title, body) {
        if (this.elements.notificationToggle.checked && 'Notification' in window && Notification.permission === 'granted') {
            new Notification(title, {
                body: body,
                icon: '🍅',
                requireInteraction: false,
                tag: 'pomodoro-timer'
            });
        }
    }
}

let timer;

window.onload = () => {
    timer = new PomodoroTimer();
};

function startTimer() {
    timer.startTimer();
}

function pauseTimer() {
    timer.pauseTimer();
}

function resetTimer() {
    timer.resetTimer();
}

function requestNotificationPermission() {
    timer.requestNotificationPermission();
}
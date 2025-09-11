class RecursiveMaze {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.cellSize = 25;
        this.mazeWidth = 31;
        this.mazeHeight = 23;
        
        this.player = { x: 1, y: 1 };
        this.exit = { x: this.mazeWidth - 2, y: this.mazeHeight - 2 };
        this.subMazes = [];
        this.lockedDoors = [];
        this.unlockedDoors = new Set();
        
        this.currentLevel = 1;
        this.maxLevel = 3;
        this.stepCount = 0;
        this.isInSubMaze = false;
        this.mazeStack = [];
        
        this.colors = {
            wall: '#2c3e50',
            path: '#34495e',
            player: '#4CAF50',
            exit: '#FFD700',
            subMaze: '#9C27B0',
            lockedDoor: '#FF5722',
            unlockedDoor: '#8BC34A',
            visited: '#1a1a2e'
        };
        
        this.visitedCells = new Set();
        this.keys = {};
        
        this.init();
    }
    
    init() {
        this.generateMaze();
        this.placeSubMazes();
        this.placeLockedDoors();
        this.setupEventListeners();
        this.render();
        this.updateInfo();
    }
    
    generateMaze() {
        this.maze = Array(this.mazeHeight).fill().map(() => 
            Array(this.mazeWidth).fill(1)
        );
        
        const stack = [];
        const visited = new Set();
        
        const startX = 1;
        const startY = 1;
        
        this.maze[startY][startX] = 0;
        visited.add(`${startX},${startY}`);
        stack.push({ x: startX, y: startY });
        
        const directions = [
            { dx: 0, dy: -2 },
            { dx: 2, dy: 0 },
            { dx: 0, dy: 2 },
            { dx: -2, dy: 0 }
        ];
        
        while (stack.length > 0) {
            const current = stack[stack.length - 1];
            const neighbors = [];
            
            for (const dir of directions) {
                const nx = current.x + dir.dx;
                const ny = current.y + dir.dy;
                
                if (nx > 0 && nx < this.mazeWidth - 1 && 
                    ny > 0 && ny < this.mazeHeight - 1 &&
                    !visited.has(`${nx},${ny}`)) {
                    neighbors.push({ x: nx, y: ny, dx: dir.dx / 2, dy: dir.dy / 2 });
                }
            }
            
            if (neighbors.length > 0) {
                const next = neighbors[Math.floor(Math.random() * neighbors.length)];
                
                this.maze[next.y][next.x] = 0;
                this.maze[current.y + next.dy][current.x + next.dx] = 0;
                
                visited.add(`${next.x},${next.y}`);
                stack.push(next);
            } else {
                stack.pop();
            }
        }
        
        this.maze[this.exit.y][this.exit.x] = 0;
        
        for (let y = 0; y < this.mazeHeight; y++) {
            for (let x = 0; x < this.mazeWidth; x++) {
                if (this.maze[y][x] === 0 && Math.random() < 0.1) {
                    const hasPath = this.checkConnectivity(x, y);
                    if (!hasPath) {
                        this.maze[y][x] = 0;
                    }
                }
            }
        }
    }
    
    checkConnectivity(x, y) {
        const directions = [
            { dx: 0, dy: -1 },
            { dx: 1, dy: 0 },
            { dx: 0, dy: 1 },
            { dx: -1, dy: 0 }
        ];
        
        let pathCount = 0;
        for (const dir of directions) {
            const nx = x + dir.dx;
            const ny = y + dir.dy;
            if (nx >= 0 && nx < this.mazeWidth && 
                ny >= 0 && ny < this.mazeHeight &&
                this.maze[ny][nx] === 0) {
                pathCount++;
            }
        }
        
        return pathCount >= 2;
    }
    
    placeSubMazes() {
        this.subMazes = [];
        const numSubMazes = 3;
        const minDistance = 5;
        
        for (let i = 0; i < numSubMazes; i++) {
            let placed = false;
            let attempts = 0;
            
            while (!placed && attempts < 100) {
                const x = Math.floor(Math.random() * (this.mazeWidth - 4)) + 2;
                const y = Math.floor(Math.random() * (this.mazeHeight - 4)) + 2;
                
                if (this.maze[y][x] === 0) {
                    let tooClose = false;
                    
                    for (const sm of this.subMazes) {
                        const dist = Math.abs(sm.x - x) + Math.abs(sm.y - y);
                        if (dist < minDistance) {
                            tooClose = true;
                            break;
                        }
                    }
                    
                    const playerDist = Math.abs(this.player.x - x) + Math.abs(this.player.y - y);
                    const exitDist = Math.abs(this.exit.x - x) + Math.abs(this.exit.y - y);
                    
                    if (!tooClose && playerDist > 3 && exitDist > 3) {
                        this.subMazes.push({ 
                            x, 
                            y, 
                            id: i,
                            solved: false,
                            keyRequired: i
                        });
                        placed = true;
                    }
                }
                attempts++;
            }
        }
    }
    
    placeLockedDoors() {
        this.lockedDoors = [];
        
        for (let i = 0; i < 3; i++) {
            let placed = false;
            let attempts = 0;
            
            while (!placed && attempts < 100) {
                const x = Math.floor(Math.random() * (this.mazeWidth - 2)) + 1;
                const y = Math.floor(Math.random() * (this.mazeHeight - 2)) + 1;
                
                if (this.maze[y][x] === 0) {
                    const isChoke = this.isChokePoint(x, y);
                    
                    if (isChoke) {
                        this.lockedDoors.push({ 
                            x, 
                            y, 
                            id: i,
                            keyId: i
                        });
                        placed = true;
                    }
                }
                attempts++;
            }
        }
    }
    
    isChokePoint(x, y) {
        const directions = [
            { dx: 0, dy: -1 },
            { dx: 1, dy: 0 },
            { dx: 0, dy: 1 },
            { dx: -1, dy: 0 }
        ];
        
        let wallCount = 0;
        let pathCount = 0;
        
        for (const dir of directions) {
            const nx = x + dir.dx;
            const ny = y + dir.dy;
            
            if (nx >= 0 && nx < this.mazeWidth && 
                ny >= 0 && ny < this.mazeHeight) {
                if (this.maze[ny][nx] === 1) {
                    wallCount++;
                } else {
                    pathCount++;
                }
            }
        }
        
        return wallCount === 2 && pathCount === 2;
    }
    
    setupEventListeners() {
        document.addEventListener('keydown', (e) => this.handleKeyPress(e));
        
        this.canvas.addEventListener('click', (e) => {
            const rect = this.canvas.getBoundingClientRect();
            const x = Math.floor((e.clientX - rect.left) / this.cellSize);
            const y = Math.floor((e.clientY - rect.top) / this.cellSize);
            
            this.handleClick(x, y);
        });
    }
    
    handleKeyPress(e) {
        const moves = {
            'ArrowUp': { dx: 0, dy: -1 },
            'ArrowDown': { dx: 0, dy: 1 },
            'ArrowLeft': { dx: -1, dy: 0 },
            'ArrowRight': { dx: 1, dy: 0 },
            'w': { dx: 0, dy: -1 },
            's': { dx: 0, dy: 1 },
            'a': { dx: -1, dy: 0 },
            'd': { dx: 1, dy: 0 },
            'W': { dx: 0, dy: -1 },
            'S': { dx: 0, dy: 1 },
            'A': { dx: -1, dy: 0 },
            'D': { dx: 1, dy: 0 }
        };
        
        if (moves[e.key]) {
            e.preventDefault();
            const move = moves[e.key];
            this.movePlayer(move.dx, move.dy);
        } else if (e.key === ' ') {
            e.preventDefault();
            this.enterSubMaze();
        } else if (e.key === 'Escape' && this.isInSubMaze) {
            e.preventDefault();
            this.exitSubMaze();
        }
    }
    
    movePlayer(dx, dy) {
        const newX = this.player.x + dx;
        const newY = this.player.y + dy;
        
        if (newX >= 0 && newX < this.mazeWidth && 
            newY >= 0 && newY < this.mazeHeight && 
            this.maze[newY][newX] === 0) {
            
            const door = this.lockedDoors.find(d => d.x === newX && d.y === newY);
            if (door && !this.unlockedDoors.has(door.id)) {
                this.showMessage('这扇门被锁住了！在子迷宫中找到钥匙来解锁。');
                return;
            }
            
            this.player.x = newX;
            this.player.y = newY;
            this.stepCount++;
            
            this.visitedCells.add(`${newX},${newY}`);
            
            this.checkWinCondition();
            this.checkSubMazeEntry();
            this.render();
            this.updateInfo();
        }
    }
    
    enterSubMaze() {
        const subMaze = this.subMazes.find(sm => 
            sm.x === this.player.x && sm.y === this.player.y && !sm.solved
        );
        
        if (subMaze) {
            this.mazeStack.push({
                maze: this.maze,
                player: { ...this.player },
                exit: { ...this.exit },
                subMazes: [...this.subMazes],
                lockedDoors: [...this.lockedDoors],
                visitedCells: new Set(this.visitedCells)
            });
            
            this.isInSubMaze = true;
            this.currentLevel++;
            
            this.mazeWidth = Math.max(11, this.mazeWidth - 8);
            this.mazeHeight = Math.max(11, this.mazeHeight - 6);
            this.player = { x: 1, y: 1 };
            this.exit = { x: this.mazeWidth - 2, y: this.mazeHeight - 2 };
            this.visitedCells = new Set();
            
            this.generateMaze();
            
            if (this.currentLevel < this.maxLevel) {
                this.placeSubMazes();
            }
            
            this.showMessage(`进入第 ${this.currentLevel} 层迷宫！`);
            this.render();
            this.updateInfo();
        }
    }
    
    exitSubMaze() {
        if (this.mazeStack.length > 0) {
            const prevState = this.mazeStack.pop();
            
            this.maze = prevState.maze;
            this.player = prevState.player;
            this.exit = prevState.exit;
            this.subMazes = prevState.subMazes;
            this.lockedDoors = prevState.lockedDoors;
            this.visitedCells = prevState.visitedCells;
            
            this.mazeWidth = this.maze[0].length;
            this.mazeHeight = this.maze.length;
            
            this.isInSubMaze = this.mazeStack.length > 0;
            this.currentLevel--;
            
            this.showMessage(`返回第 ${this.currentLevel} 层迷宫`);
            this.render();
            this.updateInfo();
        }
    }
    
    checkSubMazeEntry() {
        const subMaze = this.subMazes.find(sm => 
            sm.x === this.player.x && sm.y === this.player.y && !sm.solved
        );
        
        if (subMaze) {
            this.showMessage('按空格键进入子迷宫！');
        }
    }
    
    checkWinCondition() {
        if (this.player.x === this.exit.x && this.player.y === this.exit.y) {
            if (this.isInSubMaze) {
                const doorId = this.mazeStack.length - 1;
                this.unlockedDoors.add(doorId);
                
                if (this.mazeStack.length > 0) {
                    const parentState = this.mazeStack[this.mazeStack.length - 1];
                    const subMaze = parentState.subMazes.find(sm => 
                        sm.x === parentState.player.x && sm.y === parentState.player.y
                    );
                    if (subMaze) {
                        subMaze.solved = true;
                    }
                }
                
                this.showMessage(`子迷宫完成！解锁了一扇门！`);
                setTimeout(() => this.exitSubMaze(), 1500);
            } else {
                this.showVictory();
            }
        }
    }
    
    showVictory() {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.style.display = 'flex';
        modal.innerHTML = `
            <div class="modal-content">
                <h2>🎉 恭喜通关！</h2>
                <p>
                    你成功逃出了递归迷宫！<br>
                    总步数：${this.stepCount}<br>
                    解锁的门：${this.unlockedDoors.size}
                </p>
                <button onclick="resetGame()">再玩一次</button>
            </div>
        `;
        document.body.appendChild(modal);
    }
    
    showMessage(text) {
        const msg = document.createElement('div');
        msg.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 20px 40px;
            border-radius: 10px;
            font-size: 1.2em;
            z-index: 1000;
            animation: fadeInOut 2s ease;
        `;
        msg.textContent = text;
        document.body.appendChild(msg);
        
        setTimeout(() => msg.remove(), 2000);
    }
    
    handleClick(x, y) {
        console.log(`Clicked at (${x}, ${y})`);
    }
    
    render() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        this.ctx.fillStyle = this.colors.path;
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        for (let y = 0; y < this.mazeHeight; y++) {
            for (let x = 0; x < this.mazeWidth; x++) {
                const cellX = x * this.cellSize;
                const cellY = y * this.cellSize;
                
                if (this.visitedCells.has(`${x},${y}`)) {
                    this.ctx.fillStyle = this.colors.visited;
                    this.ctx.fillRect(cellX, cellY, this.cellSize, this.cellSize);
                }
                
                if (this.maze[y][x] === 1) {
                    this.ctx.fillStyle = this.colors.wall;
                    this.ctx.fillRect(cellX, cellY, this.cellSize, this.cellSize);
                    
                    this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
                    this.ctx.strokeRect(cellX, cellY, this.cellSize, this.cellSize);
                }
                
                const door = this.lockedDoors.find(d => d.x === x && d.y === y);
                if (door) {
                    if (this.unlockedDoors.has(door.id)) {
                        this.ctx.fillStyle = this.colors.unlockedDoor;
                    } else {
                        this.ctx.fillStyle = this.colors.lockedDoor;
                    }
                    this.ctx.fillRect(cellX + 2, cellY + 2, this.cellSize - 4, this.cellSize - 4);
                }
                
                const subMaze = this.subMazes.find(sm => sm.x === x && sm.y === y);
                if (subMaze && !subMaze.solved) {
                    this.ctx.fillStyle = this.colors.subMaze;
                    this.ctx.beginPath();
                    this.ctx.arc(
                        cellX + this.cellSize / 2,
                        cellY + this.cellSize / 2,
                        this.cellSize / 3,
                        0,
                        Math.PI * 2
                    );
                    this.ctx.fill();
                    
                    this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.5)';
                    this.ctx.lineWidth = 2;
                    this.ctx.stroke();
                }
            }
        }
        
        this.ctx.fillStyle = this.colors.exit;
        this.ctx.fillRect(
            this.exit.x * this.cellSize + 3,
            this.exit.y * this.cellSize + 3,
            this.cellSize - 6,
            this.cellSize - 6
        );
        
        this.ctx.fillStyle = this.colors.player;
        this.ctx.beginPath();
        this.ctx.arc(
            this.player.x * this.cellSize + this.cellSize / 2,
            this.player.y * this.cellSize + this.cellSize / 2,
            this.cellSize / 3,
            0,
            Math.PI * 2
        );
        this.ctx.fill();
        
        this.ctx.strokeStyle = 'white';
        this.ctx.lineWidth = 2;
        this.ctx.stroke();
    }
    
    updateInfo() {
        document.getElementById('currentLevel').textContent = this.currentLevel;
        document.getElementById('stepCount').textContent = this.stepCount;
        document.getElementById('unlockedDoors').textContent = `${this.unlockedDoors.size}/3`;
    }
}

let game;

window.onload = () => {
    const canvas = document.getElementById('gameCanvas');
    game = new RecursiveMaze(canvas);
    
    const style = document.createElement('style');
    style.textContent = `
        @keyframes fadeInOut {
            0% { opacity: 0; transform: translate(-50%, -50%) scale(0.8); }
            50% { opacity: 1; transform: translate(-50%, -50%) scale(1); }
            100% { opacity: 0; transform: translate(-50%, -50%) scale(0.8); }
        }
    `;
    document.head.appendChild(style);
};

function resetGame() {
    const canvas = document.getElementById('gameCanvas');
    game = new RecursiveMaze(canvas);
    
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => modal.remove());
}

function showHelp() {
    document.getElementById('helpModal').style.display = 'flex';
}

function closeHelp() {
    document.getElementById('helpModal').style.display = 'none';
}
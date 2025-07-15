// Z-Waifu Launcher Web Interface - Advanced Features JavaScript

class ZWaifuLauncher {
    constructor() {
        this.socket = null;
        this.currentTheme = 'light';
        this.notifications = [];
        this.init();
    }

    init() {
        this.setupTheme();
        this.setupSocket();
        this.setupEventListeners();
        this.loadInitialData();
    }

    setupTheme() {
        // Check for saved theme preference
        const savedTheme = localStorage.getItem('zwaifu-theme') || 'light';
        this.setTheme(savedTheme);
        
        // Create theme toggle button
        this.createThemeToggle();
    }

    createThemeToggle() {
        const toggle = document.createElement('div');
        toggle.className = 'theme-toggle';
        toggle.innerHTML = `<span class="icon">${this.currentTheme === 'dark' ? '☀️' : '🌙'}</span>`;
        toggle.addEventListener('click', () => this.toggleTheme());
        document.body.appendChild(toggle);
    }

    setTheme(theme) {
        this.currentTheme = theme;
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('zwaifu-theme', theme);
        
        // Update theme toggle icon
        const toggle = document.querySelector('.theme-toggle .icon');
        if (toggle) {
            toggle.textContent = theme === 'dark' ? '☀️' : '🌙';
        }

        // Emit theme change to server
        if (this.socket) {
            this.socket.emit('theme_update', {
                mode: theme,
                colors: this.getThemeColors(theme)
            });
        }
    }

    toggleTheme() {
        const newTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
        this.setTheme(newTheme);
    }

    getThemeColors(theme) {
        const colors = {
            light: {
                bg: '#ffffff',
                fg: '#212529',
                accent: '#007bff',
                success: '#28a745',
                warning: '#ffc107',
                danger: '#dc3545'
            },
            dark: {
                bg: '#1a1a1a',
                fg: '#ffffff',
                accent: '#00ccff',
                success: '#00ff99',
                warning: '#ffcc00',
                danger: '#ff6666'
            }
        };
        return colors[theme] || colors.light;
    }

    setupSocket() {
        // Initialize Socket.IO connection
        if (typeof io !== 'undefined') {
            this.socket = io();
            
            this.socket.on('connect', () => {
                console.log('Connected to Z-Waifu Launcher');
                this.showNotification('Connected to launcher', 'success');
            });

            this.socket.on('disconnect', () => {
                console.log('Disconnected from Z-Waifu Launcher');
                this.showNotification('Disconnected from launcher', 'error');
            });

            this.socket.on('status_update', (data) => {
                this.updateProcessStatus(data);
            });

            this.socket.on('theme_update', (data) => {
                this.setTheme(data.mode);
            });

            this.socket.on('notification', (data) => {
                this.showNotification(data.message, data.type);
            });

            this.socket.on('analytics_update', (data) => {
                this.updateAnalytics(data);
            });

            this.socket.on('plugin_update', (data) => {
                this.updatePluginStatus(data);
            });
        }
    }

    setupEventListeners() {
        // Process control buttons
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('btn')) {
                const action = e.target.getAttribute('data-action');
                const process = e.target.getAttribute('data-process');
                
                if (action && process) {
                    this.handleProcessAction(action, process);
                }
            }
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch (e.key) {
                    case 't':
                        e.preventDefault();
                        this.toggleTheme();
                        break;
                    case 'r':
                        e.preventDefault();
                        this.refreshAll();
                        break;
                }
            }
        });
    }

    handleProcessAction(action, process) {
        if (this.socket) {
            this.socket.emit('process_action', { action, process });
            this.showNotification(`${action} ${process}...`, 'info');
        } else {
            // Fallback to REST API
            this.apiCall(action, process);
        }
    }

    async apiCall(action, process) {
        try {
            const response = await fetch(`/api/${action}/${process}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showNotification(`${process} ${action} successful`, 'success');
            } else {
                this.showNotification(`${process} ${action} failed: ${result.error}`, 'error');
            }
        } catch (error) {
            this.showNotification(`API call failed: ${error.message}`, 'error');
        }
    }

    updateProcessStatus(data) {
        Object.keys(data).forEach(process => {
            const statusElement = document.getElementById(`${process}-status`);
            if (statusElement) {
                statusElement.textContent = data[process].status;
                statusElement.className = `status ${data[process].status}`;
                
                // Update buttons
                const startBtn = document.querySelector(`[data-process="${process}"][data-action="start"]`);
                const stopBtn = document.querySelector(`[data-process="${process}"][data-action="stop"]`);
                
                if (startBtn && stopBtn) {
                    if (data[process].status === 'running') {
                        startBtn.disabled = true;
                        stopBtn.disabled = false;
                    } else {
                        startBtn.disabled = false;
                        stopBtn.disabled = true;
                    }
                }
            }
        });
    }

    updateAnalytics(data) {
        // Update analytics dashboard
        if (data.cpu) {
            const cpuElement = document.getElementById('cpu-usage');
            if (cpuElement) cpuElement.textContent = `${data.cpu}%`;
        }
        
        if (data.memory) {
            const memoryElement = document.getElementById('memory-usage');
            if (memoryElement) memoryElement.textContent = `${data.memory}%`;
        }
        
        if (data.processes) {
            const totalElement = document.getElementById('total-processes');
            const runningElement = document.getElementById('running-processes');
            
            if (totalElement) totalElement.textContent = data.processes.total;
            if (runningElement) runningElement.textContent = data.processes.running;
        }
    }

    updatePluginStatus(data) {
        const pluginList = document.getElementById('plugin-list');
        if (pluginList && data.plugins) {
            pluginList.innerHTML = '';
            
            data.plugins.forEach(plugin => {
                const pluginItem = document.createElement('div');
                pluginItem.className = 'plugin-item';
                pluginItem.innerHTML = `
                    <div class="plugin-info">
                        <h4>${plugin.name}</h4>
                        <p>${plugin.description}</p>
                    </div>
                    <span class="plugin-status ${plugin.enabled ? 'enabled' : 'disabled'}">
                        ${plugin.enabled ? 'Enabled' : 'Disabled'}
                    </span>
                `;
                pluginList.appendChild(pluginItem);
            });
        }
    }

    showNotification(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        // Auto-remove after duration
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, duration);
        
        // Store for reference
        this.notifications.push(notification);
        
        // Remove from array after auto-remove
        setTimeout(() => {
            const index = this.notifications.indexOf(notification);
            if (index > -1) {
                this.notifications.splice(index, 1);
            }
        }, duration);
    }

    refreshAll() {
        if (this.socket) {
            this.socket.emit('refresh_request');
        }
        this.showNotification('Refreshing data...', 'info');
    }

    loadInitialData() {
        // Load initial process status
        this.refreshAll();
        
        // Load analytics if available
        if (document.getElementById('analytics-dashboard')) {
            this.loadAnalytics();
        }
        
        // Load plugins if available
        if (document.getElementById('plugin-list')) {
            this.loadPlugins();
        }
    }

    async loadAnalytics() {
        try {
            const response = await fetch('/api/analytics');
            const data = await response.json();
            this.updateAnalytics(data);
        } catch (error) {
            console.error('Failed to load analytics:', error);
        }
    }

    async loadPlugins() {
        try {
            const response = await fetch('/api/plugins');
            const data = await response.json();
            this.updatePluginStatus(data);
        } catch (error) {
            console.error('Failed to load plugins:', error);
        }
    }

    // Terminal functionality
    setupTerminal(terminalId) {
        const terminal = document.getElementById(terminalId);
        if (!terminal) return;

        const input = terminal.querySelector('.terminal-input');
        const output = terminal.querySelector('.terminal-output');

        if (input && output) {
            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    const command = input.value;
                    input.value = '';
                    
                    // Add command to output
                    this.addTerminalLine(output, `$ ${command}`, 'command');
                    
                    // Send command to server
                    if (this.socket) {
                        this.socket.emit('terminal_command', { command, terminalId });
                    }
                }
            });
        }
    }

    addTerminalLine(output, text, type = 'output') {
        const line = document.createElement('div');
        line.className = `line ${type}`;
        line.innerHTML = `
            <span class="timestamp">${new Date().toLocaleTimeString()}</span>
            <span class="text">${text}</span>
        `;
        output.appendChild(line);
        output.scrollTop = output.scrollHeight;
    }

    // Chart functionality
    createChart(canvasId, data, options = {}) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return null;

        const ctx = canvas.getContext('2d');
        
        // Default options
        const defaultOptions = {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    grid: {
                        color: this.currentTheme === 'dark' ? '#404040' : '#e0e0e0'
                    },
                    ticks: {
                        color: this.currentTheme === 'dark' ? '#ffffff' : '#000000'
                    }
                },
                y: {
                    grid: {
                        color: this.currentTheme === 'dark' ? '#404040' : '#e0e0e0'
                    },
                    ticks: {
                        color: this.currentTheme === 'dark' ? '#ffffff' : '#000000'
                    }
                }
            },
            plugins: {
                legend: {
                    labels: {
                        color: this.currentTheme === 'dark' ? '#ffffff' : '#000000'
                    }
                }
            }
        };

        return new Chart(ctx, {
            type: options.type || 'line',
            data: data,
            options: { ...defaultOptions, ...options }
        });
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.zwaifuLauncher = new ZWaifuLauncher();
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ZWaifuLauncher;
}

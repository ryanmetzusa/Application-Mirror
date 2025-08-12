# Window Mirror - Real-Time Window Capture & Display

A high-performance Python application that captures and mirrors any window in real-time, perfect for gaming, streaming, presentations, and multi-monitor setups.

## 🚀 Quick Start

### Download & Run (Standalone EXE)
1. **Download** the latest `WindowMirror.exe` from [Releases](../../releases)
2. **Extract** the zip file
3. **Run** `WindowMirror.exe` - no installation needed!

### Python Version
```bash
git clone <repository-url>
cd window-mirror
pip install -r requirements.txt
python window_mirror.py
```

## ⚠️ Antivirus Notice

**Some antivirus software may flag the executable as suspicious.** This is a **FALSE POSITIVE** common with PyInstaller-built applications.

**If your antivirus flags it:**
- ✅ Add `WindowMirror.exe` to your antivirus exclusions/whitelist
- ✅ Right-click file → Properties → "Unblock" (if available)
- ✅ Click "More info" → "Run anyway" on Windows SmartScreen
- ✅ Temporarily disable real-time protection during first run

**Why this happens:** PyInstaller bundles the Python runtime into the executable, which triggers heuristic detection algorithms. The software is completely safe and open source.

## ✨ Features

### Core Functionality
- **Real-time window capture** at 60+ FPS
- **Background capture** - no window switching or interruption
- **Title bar exclusion** for clean content-only capture
- **Multi-monitor support** with automatic detection
- **Customizable FPS targets** (60, 120, 144 Hz)
- **Smooth performance** optimized for gaming

### Technical Features
- **Pure background capture** using Windows API
- **Memory-efficient** streaming with optimized buffers
- **No dragging pause issues** (uses Tkinter display)
- **Automatic window tracking** even when moved/resized
- **Low CPU overhead** with intelligent frame skipping
- **Works with any application** - games, browsers, media players

## 🎮 Perfect For

- **Gaming**: Mirror Last War-Survival Game, League of Legends, etc.
- **Streaming**: Capture specific windows for OBS/streaming software
- **Presentations**: Display application windows on secondary screens
- **Monitoring**: Keep an eye on multiple applications simultaneously
- **Development**: Monitor applications during testing

## 🖥️ System Requirements

- **OS**: Windows 10/11 (64-bit)
- **RAM**: 4GB minimum (8GB recommended)
- **CPU**: Any modern processor (multi-core recommended for high FPS)
- **Graphics**: DirectX 11 compatible
- **Python**: 3.8+ (if running from source)

## 📖 How to Use

### 1. Launch the Application
- **Standalone**: Double-click `WindowMirror.exe`
- **Python**: Run `python window_mirror.py`

### 2. Select Target Window
- Choose from the dropdown list of available windows
- Applications must be visible (not minimized)
- Example: "Last War-Survival Game", "Google Chrome", etc.

### 3. Configure Settings
- **✅ Exclude title bar**: Captures only window content (recommended)
- **✅ Target FPS**: Select 60, 120, or 144 Hz based on your needs
- **✅ Display size**: Automatic or custom resolution

### 4. Start Mirroring
- Click "Start Mirroring"
- A new window opens showing the live capture
- Original window remains fully functional

### 5. Control Playback
- **Stop**: Press 'q' in the mirror window or close it
- **Pause**: Click the mirror window and press spacebar
- **Adjust**: Resize the mirror window as needed

## ⚙️ Configuration Options

### FPS Settings
- **60 FPS**: Balanced performance, good for most applications
- **120 FPS**: High performance, great for fast-paced games
- **144 FPS**: Maximum smoothness, requires powerful hardware

### Capture Modes
- **Full Window**: Includes title bar and borders
- **Content Only**: Excludes title bar (recommended for clean capture)
- **Auto-resize**: Mirror window matches source dimensions

### Performance Tuning
- **High Priority**: Boost capture priority for demanding applications
- **GPU Acceleration**: Uses hardware acceleration when available
- **Memory Optimization**: Automatic cleanup for long sessions

## 🔧 Troubleshooting

### Common Issues

**"No windows found" or empty dropdown**
- Ensure target applications are open and visible (not minimized)
- Run as administrator if capturing system applications
- Restart the application if list doesn't update

**Black screen or no capture**
- Check if target window uses hardware acceleration (try disabling in target app)
- Ensure target window is not minimized or hidden
- Try "Full Window" mode instead of "Content Only"
- Run WindowMirror as administrator

**Low FPS or choppy performance**
- Lower the target FPS setting
- Close unnecessary applications
- Check CPU usage in Task Manager
- Ensure adequate RAM is available

**Antivirus blocking execution**
- Add WindowMirror.exe to antivirus exclusions
- See "Antivirus Notice" section above
- Download from official GitHub releases only

**Window not found after moving/resizing**
- Stop and restart mirroring
- Refresh the window list
- Ensure target window hasn't changed its title

### Performance Optimization

**For Gaming:**
- Set target FPS to match your monitor refresh rate
- Use "Content Only" mode
- Close other capture software (OBS, etc.)
- Run in High Priority mode

**For Low-End Hardware:**
- Use 60 FPS setting
- Enable memory optimization
- Close unnecessary background applications
- Consider windowed mode in target application

## 🛠️ Development

### Building from Source

```bash
# Clone repository
git clone <repository-url>
cd window-mirror

# Install dependencies
pip install -r requirements.txt

# Run application
python window_mirror.py

# Build executable (optional)
pip install pyinstaller
pyinstaller --onefile --windowed window_mirror.py
```

### Dependencies
- `opencv-python` - Video capture and processing
- `pillow` - Image handling
- `pygetwindow` - Window enumeration
- `mss` - Screen capture
- `pywin32` - Windows API access
- `tkinter` - GUI framework (included with Python)

### Project Structure
```
window-mirror/
├── window_mirror.py      # Main application
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── .github/workflows/   # GitHub Actions CI/CD
└── dist/               # Built executables (after build)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🆘 Support

- **Issues**: [GitHub Issues](../../issues)
- **Discussions**: [GitHub Discussions](../../discussions)
- **Wiki**: [Project Wiki](../../wiki)

## 🏆 Acknowledgments

- Built with Python and modern Windows APIs
- Optimized for high-performance real-time capture
- Designed for gamers, streamers, and power users
- Thoroughly tested with popular applications and games

---

**⭐ If this project helps you, please give it a star on GitHub!**

Made with ❤️ for the Windows community

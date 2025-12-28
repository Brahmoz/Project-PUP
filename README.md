# Project PUP 🐕
**Premium Unified Platform for Desk Robot**

A MicroPython-powered quadruped robot with voice control, real-time sensor monitoring, and a beautiful glassmorphism web interface.

![Premium Glassmorphism UI](PUP%20Gemini.png)

## ✨ Features

### 🎯 Dual-Page Interface
- **Live Dashboard** (`/`) - Real-time sensor monitoring with voice control
- **Configuration Page** (`/config`) - Full settings management and servo calibration

### 🌐 WiFi Configuration
- Configure WiFi credentials directly from the web interface
- Credentials saved to `config.json` for persistence
- No need to reflash code when changing networks

### 🎙️ Voice Control
- Web Speech API integration
- Real-time voice command recognition
- Customizable command mapping via TinyML

### 📊 Live Monitoring
- Real-time battery status
- Radar motion detection (RCWL-0516)
- Light and sound sensor readings
- Auto-refresh every 2 seconds

### ⚙️ Advanced Configuration
- Servo calibration (0-180°)
- Gait speed adjustment
- Touch sensor response mapping
- Quick mode presets (Normal/Sentry/Sport)

## 🚀 Quick Start

### Hardware Required
- Raspberry Pi Pico 2W
- 4x Servo Motors (SG90 or similar)
- RCWL-0516 Radar Sensor
- Optional: Light sensor (LDR), Sound sensor (microphone)
- 2200mAh LiPo battery

### Setup

1. **Flash MicroPython** to your Pico 2W
2. **Install dependencies**:
   ```bash
   pip install phew
   ```
3. **Upload files** to Pico:
   - `main.py`
   - `Dashboard.html`
   - `config.html`
   - `bot_preview.png`

4. **First Boot**:
   - Edit WiFi credentials in `main.py` DEFAULT_CONFIG
   - Or use AP mode (if implemented)
   - Restart Pico

5. **Access the Dashboard**:
   - Find IP address from serial monitor
   - Open browser: `http://[PICO_IP]/`

## 📁 Project Structure

```
OMD-Bot/
├── main.py              # Main Python server & robot control
├── Dashboard.html       # Live monitoring dashboard
├── config.html          # Configuration interface
├── bot_preview.png      # Robot image
├── config.json          # Saved configuration (auto-generated)
└── README.md            # This file
```

## 🎨 Design Philosophy

**Premium Glassmorphism** - A modern, frosted-glass aesthetic with:
- Blur effects and transparency
- Smooth gradients and neon accents
- Micro-animations for enhanced UX
- Responsive grid layout

## 🔧 Configuration

### WiFi Setup
1. Navigate to `/config`
2. Scroll to "WiFi Network" card
3. Enter SSID and Password
4. Click "Save System Config"
5. **Restart robot** to connect

### Voice Commands
Map TinyML inference labels to actions:
- Sit, Stand, Walk, Dance
- Bark, Wag, Search Light/Sound

### Servo Calibration
Fine-tune each servo's min/max angles for your mechanical build.

## 🔋 Battery Life

With 2200mAh battery:
- **Active Dashboard Use**: ~2-3 hours
- **Standby Mode**: ~8-12 hours
- **Deep Sleep**: Days

### Power Optimization
- WiFi modem sleep mode enabled
- Adjustable polling rate (2-5s)
- Auto-sleep after inactivity (planned)

## 📡 API Endpoints

- `GET /` - Dashboard page
- `GET /config` - Configuration page
- `POST /config` - Save configuration
- `GET /status` - Live sensor data (JSON)
- `POST /trigger` - Execute command

## 🛠️ Development

### Adding New Commands
1. Edit `main.py` - Add function
2. Go to `/config` - Map voice label
3. Test with mic button on dashboard

### Customizing UI
- Colors: Edit CSS `:root` variables
- Layout: Modify `.card-*` grid positions
- Sensors: Update `fetchStatus()` in Dashboard.html

## 📝 License

MIT License - Feel free to modify and use!

## 🙏 Credits

- **Phew** - MicroPython web framework
- **Edge Impulse** - TinyML voice recognition
- **Inter Font** - Google Fonts

---

**Made with ❤️ for robotics enthusiasts**

# Hardware Setup Guide - Project PUP 🐕

Complete step-by-step guide to building your quadruped robot with Raspberry Pi Pico 2W.

---

## 📦 Parts List

### Required Components

| Component | Quantity | Specifications | Notes |
|-----------|----------|----------------|-------|
| **Raspberry Pi Pico 2W** | 1 | With WiFi/BLE | Main controller |
| **Servo Motors** | 4 | SG90 or MG90S | 9g micro servos, 180° |
| **RCWL-0516 Radar** | 1 | Microwave motion sensor | 3.3V compatible |
| **LiPo Battery** | 1 | 2200mAh, 7.4V (2S) | With JST connector |
| **Voltage Regulator** | 1 | LM2596 Buck Converter | 7.4V → 5V for servos |
| **Breadboard** | 1 | Half-size or larger | For prototyping |
| **Jumper Wires** | 20+ | M-M, M-F | Various lengths |

### Optional Components

| Component | Purpose | Specifications |
|-----------|---------|----------------|
| **LDR (Light Sensor)** | Ambient light detection | With 10kΩ resistor |
| **Electret Microphone** | Sound level detection | MAX4466 module |
| **Capacitor** | Servo power stability | 470µF, 16V |
| **Power Switch** | Easy on/off | SPST toggle switch |

---

## 🔌 Wiring Diagram

### Pin Assignments

| Function | Pico Pin | GPIO | Notes |
|----------|----------|------|-------|
| **Servo 0** (Front Left) | Pin 1 | GP0 | Signal wire (orange) |
| **Servo 1** (Front Right) | Pin 2 | GP1 | Signal wire (orange) |
| **Servo 2** (Back Left) | Pin 4 | GP2 | Signal wire (orange) |
| **Servo 3** (Back Right) | Pin 5 | GP3 | Signal wire (orange) |
| **Radar Signal** | Pin 21 | GP16 | Motion detection |
| **Light Sensor** | Pin 31 | GP26/ADC0 | Optional |
| **Sound Sensor** | Pin 32 | GP27/ADC1 | Optional |

### Power Distribution

```
Battery (7.4V 2S LiPo)
    │
    ├──► Buck Converter (5V output)
    │       │
    │       ├──► Servo VCC (Red wires, all 4)
    │       ├──► Radar VCC
    │       └──► Pico VSYS (Pin 39)
    │
    └──► GND (Common ground for all components)
```

---

## 🔧 Step-by-Step Assembly

### Step 1: Prepare the Pico 2W

1. **Flash MicroPython**:
   - Download latest MicroPython UF2 for Pico 2W from [micropython.org](https://micropython.org/download/rp2-pico-w/)
   - Hold BOOTSEL button while plugging in USB
   - Drag UF2 file to RPI-RP2 drive
   - Wait for reboot

2. **Install Thonny IDE** (if not already installed):
   - Download from [thonny.org](https://thonny.org/)
   - Select "MicroPython (Raspberry Pi Pico)" interpreter

### Step 2: Power System Setup

⚠️ **IMPORTANT**: Complete power setup BEFORE connecting servos!

1. **Configure Buck Converter**:
   ```
   Input: Connect battery (+) to IN+, (-) to IN-
   Output: Adjust potentiometer to exactly 5.0V
   ```
   
2. **Measure with multimeter**: Verify 5V output before proceeding

3. **Connect Power to Pico**:
   - Buck converter 5V → Pico VSYS (Pin 39)
   - Buck converter GND → Pico GND (Pin 38)

4. **Add capacitor** (recommended):
   - Solder 470µF capacitor across 5V and GND near servos
   - Positive leg to 5V, negative to GND

### Step 3: Servo Wiring

Each servo has 3 wires:
- **Brown/Black** = GND
- **Red** = VCC (5V)
- **Orange/Yellow** = Signal (PWM)

**Wiring connections**:

| Servo | Position | Signal → Pico | VCC | GND |
|-------|----------|---------------|-----|-----|
| **Servo 0** | Front Left Leg | GP0 (Pin 1) | 5V Rail | GND Rail |
| **Servo 1** | Front Right Leg | GP1 (Pin 2) | 5V Rail | GND Rail |
| **Servo 2** | Back Left Leg | GP2 (Pin 4) | 5V Rail | GND Rail |
| **Servo 3** | Back Right Leg | GP3 (Pin 5) | 5V Rail | GND Rail |

**Best Practices**:
- Keep servo signal wires short (<15cm)
- Route power wires separately from signal wires
- Connect all GND together (common ground)

### Step 4: Radar Sensor Setup

**RCWL-0516 Pinout**:
```
[    RCWL-0516    ]
  3V3  GND  OUT  VIN
   │    │    │    │
   X    │    │    ├──► 5V (from buck converter)
        │    │
        │    └──────► GP16 (Pin 21) on Pico
        │
        └───────────► GND (common ground)
```

**Notes**:
- Leave 3V3 pin unconnected
- Use VIN (5V) for stable operation
- OUT goes HIGH when motion detected

### Step 5: Optional Sensors

#### Light Sensor (LDR)

```
3.3V (Pin 36) ──┬──── LDR ──── GP26/ADC0 (Pin 31)
                │
                └── 10kΩ resistor ──── GND
```

#### Sound Sensor (MAX4466 Microphone Module)

```
MAX4466 Module:
  VCC ──► 3.3V (Pin 36)
  GND ──► GND
  OUT ──► GP27/ADC1 (Pin 32)
```

### Step 6: Physical Assembly

1. **Mount servos** to robot frame/chassis
2. **Attach servo horns** to legs
3. **Secure Pico** to frame with standoffs or double-sided tape
4. **Mount radar** facing forward/upward
5. **Secure battery** with velcro or battery strap
6. **Cable management**: Use zip ties or spiral wrap

---

## 💾 Software Setup

### Step 1: Install Dependencies

1. **Connect Pico via USB**
2. **Open Thonny IDE**
3. **Install phew library**:
   ```python
   import mip
   mip.install("github:pimoroni/phew")
   ```

### Step 2: Upload Project Files

Using Thonny, upload these files to Pico:

1. `main.py` - Main robot control code
2. `Dashboard.html` - Live monitoring interface
3. `config.html` - Configuration page
4. `bot_preview.png` - Robot image

**Upload method**:
- File → Save As → Raspberry Pi Pico
- Select file, save to root directory

### Step 3: Configure WiFi

**Option A: Edit main.py directly** (first boot only)
```python
DEFAULT_CONFIG = {
    "wifi": {"ssid": "YOUR_WIFI_NAME", "password": "YOUR_PASSWORD"},
    # ... rest of config
}
```

**Option B: Use web interface** (after first connection)
- Navigate to `/config`
- Enter WiFi credentials
- Save and restart

### Step 4: First Boot

1. **Power on** the robot
2. **Watch Thonny console** for:
   ```
   Connected to Wi-Fi. IP: 192.168.x.x
   Hardware initialized. Servos ready.
   Initializing servos to standing position...
   Bot Started. Waiting for commands or motion...
   ```
3. **Note the IP address**

---

## 🧪 Testing & Calibration

### Test 1: Network Connection

1. Open browser: `http://[PICO_IP]/`
2. You should see the Dashboard
3. Check live sensor readings

### Test 2: Servo Movement

1. Go to `/config` page
2. Navigate to "Servo Calibration"
3. Adjust min/max angles for each servo
4. Click "Save System Config"

**Expected behavior**: Servos should move smoothly without buzzing

### Test 3: Voice Commands

1. On Dashboard, click microphone button
2. Say a command (e.g., "sit", "stand", "walk")
3. Robot should respond

### Test 4: Radar Sensor

1. Wave hand in front of radar
2. Dashboard should show "MOTION DETECTED"
3. Robot may wag (default behavior)

### Test 5: Battery Level

Monitor battery voltage. Recharge when below 6.8V (2S LiPo safe minimum).

---

## ⚙️ Servo Calibration Guide

Each robot's mechanical build is slightly different. Follow these steps:

### 1. Find Neutral Position
- Set all servos to 90° (center)
- Attach servo horns so legs are vertical

### 2. Find Movement Range
- Test maximum forward/backward positions
- Note angles where servo stalls or struggles
- Set these as min/max in config page

### 3. Adjust Gait
- Start with slow walk speed (0.5s)
- Gradually decrease for faster walking
- Too fast = unstable gait

---

## 🔍 Troubleshooting

| Issue | Possible Cause | Solution |
|-------|----------------|----------|
| **Servos jittering** | Insufficient power | Add capacitor, check battery voltage |
| **WiFi won't connect** | Wrong credentials | Check SSID/password, restart Pico |
| **Radar always triggered** | Sensitivity too high | Move away from walls/metal objects |
| **Web page won't load** | Incorrect IP | Check Thonny console for IP address |
| **Servo doesn't move** | Wiring issue | Check signal wire connection |
| **Random restarts** | Low battery | Recharge or use larger battery |

---

## 📊 Power Consumption Guide

| Mode | Current Draw | Runtime (2200mAh) |
|------|--------------|-------------------|
| **Idle** | ~80mA | ~27 hours |
| **WiFi Active** | ~120mA | ~18 hours |
| **Servos Moving** | ~500-800mA | ~3-4 hours |
| **All Active** | ~900mA | ~2.5 hours |

**Optimization Tips**:
- Disable WiFi when not needed
- Reduce polling frequency
- Use sleep mode between commands

---

## 🛡️ Safety Guidelines

⚠️ **Important Safety Rules**:

1. **Never connect 7.4V directly to Pico** - Always use buck converter
2. **Check polarity** before connecting battery
3. **Don't run servos without load** (attach legs first)
4. **Monitor battery temperature** during use
5. **Use LiPo safety bag** for charging/storage
6. **Add fuse** to battery (+) wire for protection

---

## 📸 Visual Assembly Guide

### Recommended Build Order:

```
1. Power System Test
   ↓
2. Mount Pico to Frame
   ↓
3. Install Servos
   ↓
4. Wire Servos to Pico
   ↓
5. Add Radar Sensor
   ↓
6. Optional Sensors
   ↓
7. Upload Software
   ↓
8. Calibrate & Test
```

---

## 🎓 Need Help?

- **GitHub Issues**: https://github.com/Brahmoz/Project-PUP/issues
- **Documentation**: See README.md
- **Community**: Share your build!

---

**Ready to build?** Start with Step 1 and work through systematically. Take your time with wiring - double-check every connection! 🚀

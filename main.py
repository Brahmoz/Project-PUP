import json
import os
from machine import Pin, PWM, I2S, ADC
import time
import ei_model  # Your Edge Impulse model
from phew import server, render_template, connect_to_wifi, logging

# Wi-Fi Setup - Will be loaded from config
# Default values used on first boot only

# Default Config (if no file)
DEFAULT_CONFIG = {
    "bot_name": "DeskDog",
    "wifi": {"ssid": "your_wifi_ssid", "password": "your_wifi_password"},
    "cmds": {"0": "sit", "1": "bark", "2": "walk", "3": "search light", "4": "search sound"},
    "touch": {"head": "happy_wag", "body": "excited_dance"},
    "config": {"walk_speed": 0.2, "light_threshold": 40000, "sound_threshold": 10000},
    "calib": {
        "servo_0_min": 0, "servo_0_max": 180,
        "servo_1_min": 0, "servo_1_max": 180,
        "servo_2_min": 0, "servo_2_max": 180,
        "servo_3_min": 0, "servo_3_max": 180
    }
}

# Load Config
CONFIG_FILE = "config.json"
config = DEFAULT_CONFIG.copy()
if CONFIG_FILE in os.listdir():
    with open(CONFIG_FILE, "r") as f:
        config.update(json.load(f))

# Connect to WiFi using config
SSID = config["wifi"]["ssid"]
PASSWORD = config["wifi"]["password"]
wlan = connect_to_wifi(SSID, PASSWORD)
logging.info("Connected to Wi-Fi. IP:", wlan.ifconfig()[0])

# --- Hardware Setup ---
# Servo Pins (adjust to your wiring)
SERVO_PINS = [0, 1, 2, 3]  # GP0, GP1, GP2, GP3
servos = []
for pin in SERVO_PINS:
    pwm = PWM(Pin(pin))
    pwm.freq(50)  # 50Hz for servos
    servos.append(pwm)

print("Hardware initialized. Servos ready.")

# Helpers (update to use config)
def servo_angle(idx, angle):
    min_angle = config["calib"].get(f"servo_{idx}_min", 0)
    max_angle = config["calib"].get(f"servo_{idx}_max", 180)
    angle = max(min_angle, min(angle, max_angle))  # Clamp
    duty = int(1000 + (angle / 180) * 8000)
    servos[idx].duty_u16(duty)

# Update actions to use config (e.g., walk speed from config["config"]["walk_speed"])

# Movement Functions
def stand():
    print("Standing")
    # Example angles - adjust for your robot
    servo_angle(0, 90)
    servo_angle(1, 90)
    servo_angle(2, 90)
    servo_angle(3, 90)

def sit():
    print("Sitting")
    servo_angle(0, 150) # Front legs up/back
    servo_angle(1, 150)
    servo_angle(2, 30)  # Back legs down/forward
    servo_angle(3, 30)
    time.sleep(0.5)

def wag():
    print("Wagging")
    for _ in range(3):
        servo_angle(2, 60) # Move back legs/tail
        servo_angle(3, 120)
        time.sleep(0.2)
        servo_angle(2, 120)
        servo_angle(3, 60)
        time.sleep(0.2)
    stand()

def dance():
    print("Dancing")
    for _ in range(3):
        servo_angle(0, 45)
        servo_angle(1, 135)
        time.sleep(0.2)
        servo_angle(0, 135)
        servo_angle(1, 45)
        time.sleep(0.2)
    stand()

def walk():
    print("Walking")
    speed = config["config"]["walk_speed"]
    # Simple gait sequence
    for _ in range(4): # Take 4 steps
        servo_angle(0, 120) # Lift FL
        time.sleep(speed)
        servo_angle(0, 90)  # Place FL
        servo_angle(3, 60)  # Lift BR
        time.sleep(speed)
        servo_angle(3, 90)  # Place BR
        servo_angle(1, 120) # Lift FR
        time.sleep(speed)
        servo_angle(1, 90)  # Place FR
        servo_angle(2, 60)  # Lift BL
        time.sleep(speed)
        servo_angle(2, 90)  # Place BL

# Web Server Routes
@server.route("/", methods=["GET"])
def dashboard(request):
    return render_template("Dashboard.html", bot_name=config["bot_name"])

@server.route("/config", methods=["GET", "POST"])
def config_page(request):
    if request.method == "GET":
        # Generate Voice Command HTML
        voice_html = ""
        for id, name in config["cmds"].items():
            voice_html += f"""
            <div class='form-group'>
              <label>Command {id}</label>
              <div class='input-group'>
                <input type='text' id='cmd_{id}' name='cmd_{id}' value='{name}'>
                <button type='button' class='btn-icon' onclick="triggerCommand('cmd_{id}')" title='Test Command'>
                  <svg viewBox="0 0 24 24" width="24" height="24"><path fill="currentColor" d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
                </button>
              </div>
              <div class='chips'>
                <span class='chip' onclick="fillInput('Sit', 'cmd_{id}')">Sit</span>
                <span class='chip' onclick="fillInput('Bark', 'cmd_{id}')">Bark</span>
                <span class='chip' onclick="fillInput('Walk', 'cmd_{id}')">Walk</span>
                <span class='chip' onclick="fillInput('Dance', 'cmd_{id}')">Dance</span>
                <span class='chip' onclick="fillInput('Stop', 'cmd_{id}')">Stop</span>
              </div>
            </div>"""

        # Generate Servo HTML
        servo_html = "<div class='servo-grid'>"
        for i in range(4):
            min_val = config["calib"].get(f"servo_{i}_min", 0)
            max_val = config["calib"].get(f"servo_{i}_max", 180)
            servo_html += f"""
            <div class='servo-group'>
              <h3>Servo {i}</h3>
              <div class='form-group'>
                <label>Min Angle</label>
                <div class='range-container'>
                  <input type='range' min='0' max='180' value='{min_val}' oninput="syncServoInput(this, 'servo_{i}_min_num')">
                  <input type='number' id='servo_{i}_min_num' name='servo_{i}_min' class='range-value' style='width: 60px;' value='{min_val}' oninput="syncServoInput(this, this.previousElementSibling)">
                </div>
              </div>
              <div class='form-group'>
                <label>Max Angle</label>
                <div class='range-container'>
                  <input type='range' min='0' max='180' value='{max_val}' oninput="syncServoInput(this, 'servo_{i}_max_num')">
                  <input type='number' id='servo_{i}_max_num' name='servo_{i}_max' class='range-value' style='width: 60px;' value='{max_val}' oninput="syncServoInput(this, this.previousElementSibling)">
                </div>
              </div>
            </div>"""
        servo_html += "</div>"

        return render_template("config.html", 
                               bot_name=config["bot_name"],
                               voice_html=voice_html,
                               servo_html=servo_html,
                               touch=config["touch"],
                               config=config["config"],
                               wifi=config["wifi"],
                               calib=config["calib"])
    
    if request.method == "POST":
        form = request.form
        try:
            # Parse and update config dynamically
            new_config = {
                "bot_name": form.get("bot_name", config["bot_name"]),
                "wifi": {
                    "ssid": form.get("wifi_ssid", config["wifi"]["ssid"]),
                    "password": form.get("wifi_password", config["wifi"]["password"])
                },
                "cmds": {
                    k: form.get(f"cmd_{k}", v) for k, v in config["cmds"].items()
                },
                "touch": {
                    "head": form.get("touch_head", config["touch"]["head"]),
                    "body": form.get("touch_body", config["touch"]["body"])
                },
                "config": {
                    "walk_speed": float(form.get("walk_speed", config["config"]["walk_speed"])),
                    "light_threshold": int(form.get("light_threshold", config["config"]["light_threshold"])),
                    "sound_threshold": int(form.get("sound_threshold", config["config"]["sound_threshold"]))
                },
                "calib": {
                    k: int(form.get(k, v)) for k, v in config["calib"].items()
                }
            }
            
            # Save to file
            with open(CONFIG_FILE, "w") as f:
                json.dump(new_config, f)
            
            # Apply immediately
            global config
            config = new_config
            return "Configuration saved! <a href='/config'>Back</a>", 200
        except Exception as e:
            logging.error(f"Config save error: {e}")
            return f"Error saving config: {e}", 500

@server.route("/trigger", methods=["POST"])
def trigger_command(request):
    cmd = request.form.get("command", "unknown").lower()
    print(f"Triggering command: {cmd}")
    
    if "sit" in cmd:
        sit()
    elif "stand" in cmd:
        stand()
    elif "walk" in cmd:
        walk()
    elif "dance" in cmd:
        dance()
    elif "wag" in cmd or "bark" in cmd: # Assuming bark triggers wag too
        wag()
    else:
        print("Unknown command")
        
    return f"Triggered: {cmd}", 200

@server.route("/status", methods=["GET"])
def get_status(request):
    # Return live sensor data (JSON)
    # Note: Light/Sound are simulated here. Connect your ADCs to read real values.
    status = {
        "radar": radar.value(),
        "light": 45000, # Simulated
        "sound": 500,   # Simulated
        "battery": 85   # Simulated
    }
    return json.dumps(status), 200, {"Content-Type": "application/json"}

@server.catchall()
def not_found(request):
    return "Not Found", 404

# Start Server in Background (asyncio)
import _thread
_thread.start_new_thread(server.run, ())

# Initialize servos to standing position
time.sleep(1)  # Wait for server to start
print("Initializing servos to standing position...")
stand()

# ... (Your existing bot loop: while True, voice inference, etc.)
# In inference: Use config["cmds"].get(prediction['label'], 'unknown') to map

# --- Radar Sensor Setup (RCWL-0516) ---
RADAR_PIN = 16  # Adjust to your wiring
radar = Pin(RADAR_PIN, Pin.IN)

# --- Main Loop ---
print("Bot Started. Waiting for commands or motion...")
while True:
    # 1. Check Radar Motion
    if radar.value() == 1:
        print("Motion Detected (Radar)!")
        wag() # React to motion
        time.sleep(2) # Wait before checking again
        
    # 2. Add your Voice Inference / Other Sensor logic here
    # ...
    
    time.sleep(0.1)

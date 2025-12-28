import bluetooth
import struct
import time
import machine
import math
from ble_simple_peripheral import BLESimplePeripheral
from machine import Pin, PWM, I2S

# --- CONFIGURATION ---
MIN_PULSE = 1638  # 0 degrees (approx)
MAX_PULSE = 8192  # 180 degrees (approx)
WALK_SPEED = 0.1

# --- HARDWARE SETUP ---
# Servos
servos = [PWM(Pin(i)) for i in range(4)]
for s in servos: s.freq(50)

# Sensors
radar = Pin(22, Pin.IN, Pin.PULL_DOWN)
ir_sensor = Pin(15, Pin.IN)
touch_head = Pin(16, Pin.IN)
touch_back = Pin(17, Pin.IN)

# RGB LED (Common Cathode assumed)
led_r = PWM(Pin(6))
led_g = PWM(Pin(7))
led_b = PWM(Pin(8))
for l in [led_r, led_g, led_b]: l.freq(1000)

# Audio
buzzer = PWM(Pin(18))
audio_in = I2S(0, sck=Pin(10), ws=Pin(11), sd=Pin(12), 
              mode=I2S.RX, bits=16, format=I2S.MONO, rate=16000, ibuf=2048)

# BLE
ble = bluetooth.BLE()
sp = BLESimplePeripheral(ble, name="PUP-Robot")

# Global State
is_walking = False
test_mode = False

# --- HELPERS ---
def set_servo(idx, angle):
    # Map 0-180 to duty cycle
    duty = int(MIN_PULSE + (angle/180) * (MAX_PULSE - MIN_PULSE))
    servos[idx].duty_u16(duty)

def set_color(hex_code):
    # hex_code format: "RRGGBB" (e.g. "FF0000")
    r = int(hex_code[0:2], 16) * 257
    g = int(hex_code[2:4], 16) * 257
    b = int(hex_code[4:6], 16) * 257
    led_r.duty_u16(r)
    led_g.duty_u16(g)
    led_b.duty_u16(b)

def play_tone(freq, duration):
    buzzer.freq(freq)
    buzzer.duty_u16(30000)
    time.sleep(duration)
    buzzer.duty_u16(0)

def read_mic_volume():
    # Simple RMS-like reading (read 256 samples)
    buf = bytearray(512)
    audio_in.readinto(buf)
    # Just return a simple sum of absolute values as "volume"
    vol = sum([abs(x) for x in struct.unpack('<256h', buf)])
    return vol // 256

# --- BLE HANDLER ---
def on_rx(data):
    global is_walking, test_mode
    msg = data.decode().strip()
    
    try:
        cmd, val = msg.split(":")
        
        # 1. MOVEMENT (Joystick)
        if cmd == "JOY":
            x, y = map(float, val.split(","))
            if abs(x) > 0.1 or abs(y) > 0.1:
                is_walking = True
                # Simple inverse kinematics or hardcoded gait goes here
                # For test: just move head/legs slightly
                angle = 90 + (x * 45)
                set_servo(0, angle) 
                set_servo(1, 180-angle)
            else:
                is_walking = False
                
        # 2. TEST MODE (Individual Control)
        elif cmd == "CALIB":
            # Format: CALIB:servo_idx,angle
            s_idx, s_ang = map(int, val.split(","))
            set_servo(s_idx, s_ang)
            test_mode = True
            
        elif cmd == "QUERY":
            # Return all sensor data for the Test Dashboard
            # Format: SENSORS:Radar,IR,Head,Back,MicVol
            vol = read_mic_volume()
            status = f"SENSORS:{radar.value()},{ir_sensor.value()},{touch_head.value()},{touch_back.value()},{vol}"
            sp.send(status + "\n")
            
        elif cmd == "MOOD":
            set_color(val)
            
    except Exception as e:
        print("Error:", e)

sp.on_write(on_rx)

# --- MAIN LOOP ---
last_report = 0

while True:
    current_time = time.ticks_ms()
    
    # Standard Operation (Only if NOT in test mode)
    if not test_mode:
        # Radar Logic (Ignore if walking to prevent self-trigger)
        if not is_walking and radar.value() == 1:
            set_color("FF0000") # Red alert
            
        # Obstacle Logic
        if ir_sensor.value() == 0: # Detects object
            play_tone(1000, 0.1)
            
    # Heartbeat / Auto-reporting for App Dashboard
    # If app requested continuous monitoring, send every 500ms
    if test_mode and time.ticks_diff(current_time, last_report) > 500:
        vol = read_mic_volume()
        status = f"SENSORS:{radar.value()},{ir_sensor.value()},{touch_head.value()},{touch_back.value()},{vol}"
        sp.send(status + "\n")
        last_report = current_time

    time.sleep(0.01)
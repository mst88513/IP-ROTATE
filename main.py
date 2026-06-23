#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║     🔥 TOOLS v6.0 - ANTI-BAN PRO 🔥                             ║
║                                                                   ║
║     👨‍💻 Developer: MR. SANTO PRO                                ║
║     🏆 Team: FIRE OTP SQUAD                                     ║
║     🛡️ Anti-Ban: MAXIMUM PRO                                    ║
║     🔑 HWID License System Active                               ║
║     ⏰ 24/7/365 UPTIME                                          ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
"""

import time
import os
import subprocess
import random
import string
import json
from datetime import datetime, timezone
import sys
import signal
import hashlib
import platform
import requests
import threading
import uuid

# ================================================================
# 🔧 কনফিগারেশন
# ================================================================

CONFIG = {
    "tor_host": "127.0.0.1",
    "tor_port": 9050,
    "rotation_interval": 10,
    "max_retries": 5,
    "retry_delay": 2,
    "auto_restart_tor": True,
    "tor_restart_delay": 2,
    "max_failures": 30,
    "keep_alive": True,
    "log_to_file": True,
    "show_tor_logs": False,
    "anti_ban_mode": True,
    "random_delay": True,
    "user_agent_rotation": True,
    "header_spoofing": True,
    "dns_rotation": True,
}

# ================================================================
# 🔑 Firebase Configuration
# ================================================================

FIREBASE_CONFIG = {
    "databaseURL": "https://unlimitedig-default-rtdb.asia-southeast1.firebasedatabase.app"
}

# ================================================================
# 🔑 HWID System (পার্মানেন্ট - ফিক্সড)
# ================================================================

class HWIDSystem:
    @staticmethod
    def generate_hwid():
        """ইউনিক HWID জেনারেট - একবারই জেনারেট হবে"""
        
        # স্ক্রিপ্টের ডিরেক্টরিতে .hwid ফাইল
        script_dir = os.path.dirname(os.path.abspath(__file__))
        hwid_file = os.path.join(script_dir, ".hwid")
        
        # আগের HWID আছে কিনা চেক
        if os.path.exists(hwid_file):
            try:
                with open(hwid_file, "r") as f:
                    saved_hwid = f.read().strip()
                    if saved_hwid and len(saved_hwid) == 36:
                        return saved_hwid
            except:
                pass
        
        # নতুন HWID জেনারেট
        try:
            system_info = {
                "hostname": platform.node(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "termux": os.environ.get("PREFIX", ""),
                "android": os.environ.get("ANDROID_ROOT", ""),
                "home": os.path.expanduser("~"),
                "cpu_count": os.cpu_count(),
                "uuid": str(uuid.getnode()),
            }
            
            info_string = json.dumps(system_info, sort_keys=True)
            hwid = hashlib.sha256(info_string.encode()).hexdigest()
            
            formatted = f"{hwid[:8]}-{hwid[8:12]}-{hwid[12:16]}-{hwid[16:20]}-{hwid[20:32]}".upper()
            
            try:
                with open(hwid_file, "w") as f:
                    f.write(formatted)
            except:
                pass
            
            return formatted
            
        except:
            fallback = "".join(random.choices(string.hexdigits.upper(), k=36))
            fallback = f"{fallback[:8]}-{fallback[8:12]}-{fallback[12:16]}-{fallback[16:20]}-{fallback[20:32]}"
            
            try:
                with open(hwid_file, "w") as f:
                    f.write(fallback)
            except:
                pass
            
            return fallback

# ================================================================
# 🔐 Firebase License Checker
# ================================================================

class FirebaseLicense:
    def __init__(self):
        self.base_url = FIREBASE_CONFIG["databaseURL"]
        self.hwid = HWIDSystem.generate_hwid()
        
    def check_license(self):
        """লাইসেন্স চেক"""
        try:
            url = f"{self.base_url}/licenses/{self.hwid}.json"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    status = data.get("status", "inactive")
                    expiry = data.get("expiry", "")
                    group = data.get("group", "Unknown")
                    name = data.get("name", "Unknown")
                    
                    if status == "active":
                        if expiry:
                            try:
                                expiry_date = datetime.fromisoformat(expiry.replace("Z", "+00:00"))
                                now = datetime.now(timezone.utc)
                                
                                if now > expiry_date:
                                    return {"valid": False, "reason": "Expired"}
                            except:
                                pass
                        
                        return {"valid": True, "group": group, "name": name, "expiry": expiry}
                    else:
                        return {"valid": False, "reason": "Inactive"}
                else:
                    return {"valid": False, "reason": "Not Found"}
            else:
                return {"valid": False, "reason": "Connection Error"}
                
        except Exception as e:
            return {"valid": False, "reason": str(e)}
    
    def register_device(self):
        """ডিভাইস রেজিস্টার"""
        try:
            url = f"{self.base_url}/devices/{self.hwid}.json"
            
            data = {
                "hwid": self.hwid,
                "hostname": platform.node(),
                "system": platform.system(),
                "machine": platform.machine(),
                "timestamp": datetime.now().isoformat(),
                "status": "pending"
            }
            
            response = requests.put(url, json=data, timeout=10)
            return response.status_code == 200
            
        except:
            return False

# ================================================================
# 🛡️ অ্যান্টি-ব্যান ডেটাবেস
# ================================================================

USER_AGENTS = [
    "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.6613.146 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; Pixel 9 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.6613.146 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.6533.119 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-F946B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.122 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; Xiaomi14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.6613.146 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; OnePlus12) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.6533.119 Mobile Safari/537.36",
]

BROWSER_PROFILES = [
    "Chrome 128", "Firefox 130", "Safari 18", "Edge 128",
    "Brave 1.68", "Opera 115", "Vivaldi 6.9", "Samsung Browser 26"
]

LANGUAGES = ["en-US", "en-GB", "de-DE", "fr-FR", "es-ES", "it-IT", "pt-BR", "ja-JP", "zh-CN", "ru-RU"]

SCREEN_RESOLUTIONS = [
    "1920x1080", "1366x768", "1536x864", "1440x900",
    "2560x1440", "1280x720", "3840x2160", "2400x1080",
    "2960x1440", "2340x1080", "2778x1284", "2532x1170"
]

TIMEZONES = [
    "UTC", "America/New_York", "Europe/London", "Europe/Berlin",
    "Asia/Dubai", "Asia/Tokyo", "Australia/Sydney", "Asia/Kolkata",
    "America/Los_Angeles", "Europe/Paris", "Asia/Singapore"
]

GLOBAL_SMARTPHONES = [
    "iPhone 16 Pro Max", "iPhone 16 Pro", "iPhone 16 Plus", "iPhone 16",
    "iPhone 15 Pro Max", "iPhone 15 Pro", "iPhone 15 Plus", "iPhone 15",
    "iPhone 14 Pro Max", "iPhone 14 Pro", "iPhone SE (4th Gen)",
    "Samsung Galaxy S25 Ultra", "Samsung Galaxy S25+", "Samsung Galaxy S25",
    "Samsung Galaxy S24 Ultra", "Samsung Galaxy S24+", "Samsung Galaxy S24",
    "Samsung Galaxy Z Fold 6", "Samsung Galaxy Z Flip 6",
    "Samsung Galaxy A75", "Samsung Galaxy A55", "Samsung Galaxy A35",
    "Google Pixel 9 Pro XL", "Google Pixel 9 Pro", "Google Pixel 9",
    "Google Pixel 8 Pro", "Google Pixel 8", "Google Pixel Fold 2",
    "Xiaomi 15 Pro", "Xiaomi 15", "Xiaomi 14 Ultra", "Xiaomi 14",
    "Redmi Note 14 Pro+", "Redmi Note 14 Pro", "POCO X7 Pro", "POCO F6",
    "OnePlus 13", "OnePlus 13R", "OnePlus 12", "OnePlus Open 2",
    "Vivo X200 Pro", "Vivo X200", "Vivo V40 Pro", "iQOO 13 Pro",
    "Oppo Find X8 Pro", "Oppo Find X8", "Oppo Reno 12 Pro",
    "Realme GT 6 Pro", "Realme GT 6", "Realme 13 Pro+",
    "Motorola Edge 60 Pro", "Motorola Razr 60 Ultra", "Moto G Power 2026",
    "Sony Xperia 1 VII", "Sony Xperia 1 VI", "Sony Xperia 10 VII",
    "Asus ROG Phone 9 Pro", "Asus Zenfone 12 Ultra",
    "Huawei P80 Pro", "Huawei Mate 70 Pro", "Honor Magic 7 Pro",
    "Nothing Phone (3)", "Infinix GT 30 Pro", "Tecno Phantom V Fold 3"
]

# ================================================================
# 🛡️ অ্যান্টি-ব্যান ক্লাস
# ================================================================

class AntiBanPro:
    @staticmethod
    def get_random_ua():
        return random.choice(USER_AGENTS)
    
    @staticmethod
    def get_random_browser():
        return random.choice(BROWSER_PROFILES)
    
    @staticmethod
    def get_random_language():
        return random.choice(LANGUAGES)
    
    @staticmethod
    def get_random_resolution():
        return random.choice(SCREEN_RESOLUTIONS)
    
    @staticmethod
    def get_random_timezone():
        return random.choice(TIMEZONES)
    
    @staticmethod
    def get_random_model():
        return random.choice(GLOBAL_SMARTPHONES)
    
    @staticmethod
    def generate_spoofed_headers():
        ua = AntiBanPro.get_random_ua()
        lang = AntiBanPro.get_random_language()
        
        headers = {
            "User-Agent": ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": f"{lang},en-US;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": str(random.choice([0, 1])),
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        return headers
    
    @staticmethod
    def generate_spoofed_mac():
        return ':'.join(['{:02x}'.format(random.randint(0, 255)) for _ in range(6)])
    
    @staticmethod
    def generate_spoofed_imei():
        return ''.join(random.choices(string.digits, k=15))

# ================================================================
# 📱 ডিভাইস জেনারেটর
# ================================================================

class DeviceGeneratorPro:
    @staticmethod
    def generate_device_info():
        model = AntiBanPro.get_random_model()
        user = f"u0_a{random.randint(100, 999)}"
        letters = ''.join(random.choices(string.ascii_uppercase, k=4))
        numbers = ''.join(random.choices(string.digits, k=6))
        device_id = f"{letters}.{numbers}.0{random.randint(10, 99)}"
        android_version = random.choice(["15", "14", "13"])
        sdk_level = random.choice([35, 34, 33])
        
        return {
            "model": model,
            "user": user,
            "device_id": device_id,
            "android_version": android_version,
            "sdk_level": sdk_level,
            "browser": AntiBanPro.get_random_browser(),
            "language": AntiBanPro.get_random_language(),
            "resolution": AntiBanPro.get_random_resolution(),
            "timezone": AntiBanPro.get_random_timezone(),
            "headers": AntiBanPro.generate_spoofed_headers(),
            "mac": AntiBanPro.generate_spoofed_mac(),
            "imei": AntiBanPro.generate_spoofed_imei(),
        }

# ================================================================
# 🔥 মেইন ইঞ্জিন
# ================================================================

class UltimateIPHiderPro:
    def __init__(self):
        self.old_ip = ""
        self.counter = 0
        self.failure_count = 0
        self.running = True
        self.stats = {
            "total": 0,
            "success": 0,
            "fail": 0,
            "unique_ips": set(),
            "start_time": datetime.now()
        }
        self.device_gen = DeviceGeneratorPro()
        self.hwid = HWIDSystem.generate_hwid()
        self.license = FirebaseLicense()
        
    def check_tor(self) -> bool:
        try:
            cmd = f"curl --max-time 3 --socks5-hostname {CONFIG['tor_host']}:{CONFIG['tor_port']} -s http://ip-api.com/json/"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=4)
            return result.returncode == 0 and result.stdout.strip()
        except:
            return False
    
    def start_tor(self):
        try:
            os.system("pkill tor 2>/dev/null")
            time.sleep(CONFIG["tor_restart_delay"])
            os.system("tor > /dev/null 2>&1 &")
            time.sleep(CONFIG["tor_restart_delay"] + 2)
            return self.check_tor()
        except:
            return False
    
    def change_tor_ip(self):
        try:
            os.system("pkill -HUP tor 2>/dev/null")
            time.sleep(0.5)
            return True
        except:
            return False
    
    def get_ip_and_country(self):
        for attempt in range(CONFIG["max_retries"]):
            try:
                cmd = f"curl --max-time 5 --socks5-hostname {CONFIG['tor_host']}:{CONFIG['tor_port']} -s http://ip-api.com/json/"
                output = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL, timeout=6).decode('utf-8').strip()
                
                if output:
                    data = json.loads(output)
                    ip = data.get("query")
                    country = data.get("country", "Unknown")
                    city = data.get("city", "Unknown")
                    region = data.get("regionName", "Unknown")
                    isp = data.get("isp", "Unknown")
                    
                    if ip and ip != "Unknown":
                        return ip, country, city, region, isp
                        
            except:
                time.sleep(CONFIG["retry_delay"])
            
        return None, None, None, None, None
    
    def check_license(self):
        print("\033[1;33m[🔑] Checking license...\033[0m")
        self.license.register_device()
        result = self.license.check_license()
        
        if result.get("valid", False):
            print(f"\033[1;32m[✅] License Valid!\033[0m")
            print(f"\033[1;36m📛 Name: {result.get('name', 'Unknown')}\033[0m")
            print(f"\033[1;36m👥 Group: {result.get('group', 'Unknown')}\033[0m")
            print(f"\033[1;36m📅 Expiry: {result.get('expiry', 'Never')}\033[0m\n")
            return True
        else:
            reason = result.get('reason', 'Unknown')
            print(f"\033[1;31m[❌] License Invalid: {reason}\033[0m")
            
            if reason == "Expired":
                print("\033[1;33m[⚠️] Your license has expired! Contact admin.\033[0m")
            elif reason == "Inactive":
                print("\033[1;33m[⚠️] License not activated! Contact admin with HWID.\033[0m")
            elif reason == "Not Found":
                print("\033[1;33m[⚠️] Device not registered! Contact admin.\033[0m")
            
            print(f"\033[1;33m📋 Your HWID: {self.hwid}\033[0m")
            return False
    
    def show_banner(self):
        os.system("clear" if os.name != "nt" else "cls")
        
        print("\033[1;36m" + "="*70 + "\033[0m")
        print("\033[1;31m" + "🔥"*25 + "\033[0m")
        print("\033[1;33m" + " " * 8 + "IP + DEVICE ROTATE v6.0 - ANTI-BAN PRO" + " " * 8 + "\033[0m")
        print("\033[1;35m" + " " * 10 + "🛡️ SECURITY - 100% TOR ✅" + " " * 10 + "\033[0m")
        print("\033[1;31m" + "🔥"*25 + "\033[0m")
        print("")
        print(f"\033[1;36m👨‍💻 Developer\033[0m : \033[1;32mMR. SANTO PRO\033[0m")
        print(f"\033[1;36m🏆 Team\033[0m        : \033[1;33mFIRE OTP SQUAD\033[0m")
        print(f"\033[1;36m🔑 HWID\033[0m         : \033[1;33m{self.hwid}\033[0m")
        print(f"\033[1;36m🔄 Rotation\033[0m      : \033[1;37mEvery {CONFIG['rotation_interval']} seconds\033[0m")
        print(f"\033[1;36m🛡️ Anti-Ban\033[0m      : \033[1;32mENABLED ✅\033[0m")
        print(f"\033[1;36m⏰ Uptime\033[0m        : \033[1;34m24/7/365\033[0m")
        print("")
        print("\033[1;31m" + "─"*70 + "\033[0m")
        print("\033[1;31m⚠️  Press Ctrl + C to Stop\033[0m")
        print("\033[1;31m" + "─"*70 + "\033[0m\n")
    
    def show_rotation(self, device_info, ip, country, city, region, isp):
        current_time = datetime.now().strftime("%I:%M:%S %p")
        uptime = str(datetime.now() - self.stats["start_time"]).split('.')[0]
        
        total = self.stats["total"] or 1
        success_rate = (self.stats["success"] / total * 100)
        
        print("\033[1;37m" + "╔" + "═"*68 + "╗" + "\033[0m")
        print(f"\033[1;33m ⚡ ROTATION #{self.counter}\033[0m \033[1;37m|\033[0m \033[1;32m✓ SUCCESS\033[0m \033[1;37m|\033[0m \033[1;34m{current_time}\033[0m")
        print(f"\033[1;37m ⏰ Uptime: {uptime}\033[0m")
        print("\033[1;37m" + "╠" + "═"*68 + "╣" + "\033[0m")
        
        print(f" \033[1;35m📱 Model\033[0m        \033[1;37m:\033[0m \033[1;32m{device_info['model'][:35]}\033[0m")
        print(f" \033[1;33m🔑 Device ID\033[0m     \033[1;37m:\033[0m \033[1;36m{device_info['device_id']}\033[0m")
        print(f" \033[1;34m👤 User\033[0m          \033[1;37m:\033[0m \033[1;33m{device_info['user']}\033[0m")
        print(f" \033[1;32m🤖 Android\033[0m       \033[1;37m:\033[0m \033[1;35m{device_info['android_version']} (SDK {device_info['sdk_level']})\033[0m")
        print(f" \033[1;36m🌐 Browser\033[0m       \033[1;37m:\033[0m \033[1;30m{device_info['browser']}\033[0m")
        print(f" \033[1;33m📝 Language\033[0m      \033[1;37m:\033[0m \033[1;30m{device_info['language']}\033[0m")
        print(f" \033[1;31m📌 MAC\033[0m           \033[1;37m:\033[0m \033[1;30m{device_info['mac']}\033[0m")
        
        print("\033[1;37m" + "╠" + "═"*68 + "╣" + "\033[0m")
        
        print(f" \033[1;32m🌐 IP Address\033[0m    \033[1;37m:\033[0m \033[1;32m{ip} ✅\033[0m")
        print(f" \033[1;33m🌍 Country\033[0m       \033[1;37m:\033[0m \033[1;33m{country}\033[0m")
        print(f" \033[1;34m🏙️ City\033[0m           \033[1;37m:\033[0m \033[1;36m{city}\033[0m")
        print(f" \033[1;35m📌 Region\033[0m        \033[1;37m:\033[0m \033[1;30m{region}\033[0m")
        print(f" \033[1;36m📡 ISP\033[0m           \033[1;37m:\033[0m \033[1;30m{isp[:30]}\033[0m")
        print(f" \033[1;35m🕐 Timezone\033[0m       \033[1;37m:\033[0m \033[1;30m{device_info['timezone']}\033[0m")
        print(f" \033[1;36m📱 Resolution\033[0m     \033[1;37m:\033[0m \033[1;30m{device_info['resolution']}\033[0m")
        
        print("\033[1;37m" + "╠" + "═"*68 + "╣" + "\033[0m")
        
        bar_length = 45
        filled = int(bar_length * success_rate / 100)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        print(f" \033[1;37m📊 Success Rate:\033[0m \033[1;32m{success_rate:.1f}%\033[0m")
        print(f" \033[1;37m   [{bar}] \033[1;32m{self.stats['success']}\033[0m/\033[1;37m{self.stats['total']}\033[0m")
        print(f" \033[1;37m   🔄 Total: {self.stats['total']} | 🌐 Unique: {len(self.stats['unique_ips'])} | ❌ Failed: {self.stats['fail']}\033[0m")
        
        print("\033[1;37m" + "╚" + "═"*68 + "╝" + "\033[0m\n")
        
        print(f"\033[1;30m┌─[ MR. SANTO PRO | HWID: {self.hwid[:8]}... ]────────────────────┐\033[0m")
        print(f"\033[1;30m│ 🔐 SECURED BY FIRE OTP SQUAD │ v6.0 │ ANTI-BAN PRO ✅ │\033[0m")
        print(f"\033[1;30m└────────────────────────────────────────────────────────────────────┘\033[0m\n")
    
    def run(self):
        signal.signal(signal.SIGINT, self.signal_handler)
        self.show_banner()
        
        if not self.check_license():
            print("\n\033[1;31m[❌] Invalid License! Exiting...\033[0m")
            print(f"\033[1;33m📋 Contact Admin with HWID: {self.hwid}\033[0m")
            time.sleep(5)
            return
        
        print("\033[1;33m[⏳] Starting Tor... Please wait...\033[0m")
        
        if not self.check_tor():
            self.start_tor()
            time.sleep(2)
        
        max_wait = 30
        wait_time = 0
        while wait_time < max_wait:
            if self.check_tor():
                print("\033[1;32m[✅] Tools is ready! Starting rotations...\033[0m\n")
                break
            time.sleep(2)
            wait_time += 2
        
        if wait_time >= max_wait:
            print("\033[1;31m[❌] Tools failed to start. Please check your connection.\033[0m")
            return
        
        while self.running:
            try:
                if not self.check_tor():
                    print("\033[1;33m[⚠️] Tools disconnected! Restarting...\033[0m")
                    self.start_tor()
                    time.sleep(1)
                    continue
                
                self.change_tor_ip()
                
                if CONFIG["random_delay"]:
                    delay = CONFIG["rotation_interval"] + random.uniform(-1.5, 1.5)
                    time.sleep(max(2, delay))
                else:
                    time.sleep(CONFIG["rotation_interval"])
                
                ip_info = self.get_ip_and_country()
                self.counter += 1
                self.stats["total"] += 1
                
                if ip_info and ip_info[0]:
                    current_ip, country, city, region, isp = ip_info
                    
                    if current_ip != self.old_ip:
                        self.stats["success"] += 1
                        self.stats["unique_ips"].add(current_ip)
                        self.failure_count = 0
                        
                        device_info = self.device_gen.generate_device_info()
                        self.show_rotation(device_info, current_ip, country, city, region, isp)
                        self.old_ip = current_ip
                    else:
                        print(f"\033[1;33m[⏳] Same IP... Waiting for next rotation...\033[0m")
                        
                else:
                    self.failure_count += 1
                    self.stats["fail"] += 1
                    print(f"\033[1;31m[❌] Rotation #{self.counter} failed! (Attempt {self.failure_count})\033[0m")
                    
                    if self.failure_count >= CONFIG["max_failures"]:
                        print("\033[1;33m[🔄] Restarting Tor...\033[0m")
                        self.start_tor()
                        self.failure_count = 0
                    
            except Exception as e:
                print(f"\033[1;31m[❌] Error: {e}\033[0m")
                time.sleep(CONFIG["retry_delay"])
    
    def signal_handler(self, sig, frame):
        print("\n\033[1;31m" + "═"*70 + "\033[0m")
        print("\033[1;33m🛑 Shutting down...\033[0m")
        print(f"\033[1;36m📊 Final Stats:\033[0m")
        print(f"   🔄 Total Rotations: {self.stats['total']}")
        print(f"   ✅ Successful: {self.stats['success']}")
        print(f"   ❌ Failed: {self.stats['fail']}")
        print(f"   🌐 Unique IPs: {len(self.stats['unique_ips'])}")
        
        uptime = str(datetime.now() - self.stats["start_time"]).split('.')[0]
        print(f"   ⏰ Uptime: {uptime}")
        
        print("\033[1;32m👨‍💻 Thank you for using TOOLS v6.0!\033[0m")
        print("\033[1;31m" + "═"*70 + "\033[0m")
        self.running = False
        sys.exit(0)

# ================================================================
# 🚀 মেইন এক্সিকিউশন
# ================================================================

if __name__ == "__main__":
    try:
        print("\033[1;32m")
        print("""
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║  ████████╗ ██████╗  ██████╗ ██╗     ███████╗                    ║
║  ╚══██╔══╝██╔═══██╗██╔═══██╗██║     ██╔════╝                    ║
║     ██║   ██║   ██║██║   ██║██║     ███████╗                    ║
║     ██║   ██║   ██║██║   ██║██║     ╚════██║                    ║
║     ██║   ╚██████╔╝╚██████╔╝███████╗███████║                    ║
║     ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚══════╝                    ║
║                                                                   ║
║  ┌─────────────────────────────────────────────────────────────┐  ║
║  │  🔥 TOOLS v6.0 - ANTI-BAN PRO 🔥                         │  ║
║  │  👨‍💻 Developer: MR. SANTO PRO                            │  ║
║  │  🏆 TEAM: FIRE OTP SQUAD                                 │  ║
║  │  🛡️ ANTI-BAN: MAXIMUM PRO SECURITY                      │  ║
║  │  🔑 LICENSE SYSTEM ACTIVE                                │  ║
║  │  ⏰ 24/7/365 UPTIME - 100% TOR ✅                       │  ║
║  └─────────────────────────────────────────────────────────────┘  ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
        """)
        time.sleep(1)
        
        app = UltimateIPHiderPro()
        app.run()
        
    except KeyboardInterrupt:
        print("\n\033[1;31m[!] Stopped by user\033[0m")
    except Exception as e:
        print(f"\033[1;31m[!] Fatal Error: {e}\033[0m")
        time.sleep(5)

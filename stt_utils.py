import os
import json
import queue
import threading
import time
import sounddevice as sd
from vosk import Model, KaldiRecognizer, SetLogLevel

SetLogLevel(-1)

class SpeechRecognizer:
    def __init__(self, callback):
        self.callback = callback
        self.q = queue.Queue()
        self.running = True
        self.last_trigger_time = 0  # 用于防止同句话反复触发
        
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
        """带有 2 秒冷却时间的触发逻辑，防止流式识别疯狂重复触发"""
        now = time.time()
        if text and now - self.last_trigger_time > 2.0:
            self.last_trigger_time = now
            self.callback(text)

    def _run(self):
        try:
            # blocksize 从 8000 改为 4000（约 0.25 秒），大幅降低延迟
            with sd.RawInputStream(samplerate=16000, blocksize=4000, device=None, dtype='int16',
                                   channels=1, callback=self._audio_callback):
                while self.running:
                    data = self.q.get()
                    
                    # 1. 获取流式识别结果（说到一半就能识别出来）
                    if self.rec.AcceptWaveform(data):
                        # 句子结束的最终结果
                        result = json.loads(self.rec.Result())
                        text = result.get("text", "").replace(" ", "")
                        self._check_and_trigger(text)
                    else:
                        # 句子进行中的实时结果（比如刚说到“谢”就能识别）
                        partial = json.loads(self.rec.PartialResult())
                        text = partial.get("partial", "").replace(" ", "")
                        self._check_and_trigger(text)
                        
        except Exception as e:
            print(f"语音识别线程出错: {e}")

    def stop(self):
        self.running = False
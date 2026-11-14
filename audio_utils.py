import numpy as np
from config import CFG, MIC_ENABLED if 'MIC_ENABLED' in globals() else CFG["mic"]["enabled"]

try:
    import sounddevice as sd
    HAS_AUDIO = True
except ImportError:
    HAS_AUDIO = False
    print("警告: 未安装 sounddevice 或 numpy，麦克风功能将被禁用。")

MIC_ENABLED = CFG["mic"]["enabled"] and HAS_AUDIO
current_volume = 0.0

def audio_callback(indata, frames, time_info, status):
    global current_volume
    if status:
        pass # 忽略流警告
    # 计算音量 RMS（均方根）
    volume = np.linalg.norm(indata) / np.sqrt(len(indata))
    # 平滑处理，避免瞬间突变
    current_volume = current_volume * 0.7 + volume * 0.3

def start_mic():
    if not MIC_ENABLED:
        return None
    try:
        stream = sd.InputStream(callback=audio_callback, channels=1, samplerate=44100)
        stream.start()
        print("麦克风监听已启动")
        return stream
    except Exception as e:
        print(f"麦克风启动失败: {e}")
        return None

def stop_mic(stream):
    if stream:
        stream.stop()
        stream.close()

def get_volume():
    return current_volume
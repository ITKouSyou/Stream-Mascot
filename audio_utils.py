import numpy as np
from config import CFG

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
        pass 
    
    # 计算音量 RMS（均方根）
    volume = np.linalg.norm(indata) / np.sqrt(len(indata))
    
    # 放大音量系数 (适配普通说话声音)
    volume = volume * 20.0 
    volume = min(volume, 1.0) # 限制最大不超过 1.0

    # 平滑处理：声音变大时反应快（Attack），变小时回落慢（Release）
    if volume > current_volume:
        current_volume = current_volume * 0.3 + volume * 0.7
    else:
        current_volume = current_volume * 0.8 + volume * 0.2

def start_mic():
    if not MIC_ENABLED:
        return None
    try:
        # 可以尝试修改 device 参数来切换麦克风，默认使用系统默认麦克风
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
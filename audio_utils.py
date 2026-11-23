import numpy as np
import time
import threading
import config
import warnings
from config import CFG

# 【新增】屏蔽底层降噪库的除零警告
warnings.filterwarnings("ignore", message="invalid value encountered in divide", category=RuntimeWarning)

try:
    import sounddevice as sd
    HAS_AUDIO = True
except ImportError:
    HAS_AUDIO = False

try:
    import librosa
    import noisereduce as nr
    HAS_LIBROSA = True
except ImportError:
    HAS_LIBROSA = False

MIC_ENABLED = CFG["global"]["mic"]["enabled"] and HAS_AUDIO
current_volume = 0.0
is_singing = False

_thread = None
_stop_event = threading.Event()
_stream = None
_current_device_name = None
_audio_buffer = []
MAX_BUFFER_SIZE = 22050
_last_data_time = time.time()

_last_calc_time = 0.0
_sing_counter = 0
_last_sing_time = 0.0

_state_lock = threading.Lock()

def get_all_input_devices():
    if not HAS_AUDIO: return [(-1, "系统默认设备")]
    try:
        devices = sd.query_devices()
        result = [(-1, "系统默认设备 (跟随 Windows 切换)")]
        seen_names = set()
        ignore_keywords = ["Microsoft 声音映射器", "主声音捕获驱动程序", "Sound Mapper", "Primary Sound Capture", "默认", "Default"]
        
        for i, d in enumerate(devices):
            if d['max_input_channels'] > 0:
                name = d['name']
                if any(kw in name for kw in ignore_keywords):
                    continue
                if name not in seen_names:
                    seen_names.add(name)
                    result.append((i, name))
        return result
    except Exception:
        return [(-1, "系统默认设备")]

def audio_callback(indata, frames, time_info, status):
    global current_volume, _audio_buffer, _last_data_time
    if status: pass
    
    _last_data_time = time.time()
    _audio_buffer.extend(indata[:, 0].astype(np.float32))
    if len(_audio_buffer) > MAX_BUFFER_SIZE:
        _audio_buffer = _audio_buffer[-MAX_BUFFER_SIZE:]
        
    volume = np.linalg.norm(indata) / np.sqrt(len(indata))
    volume = min(volume * 20.0, 1.0)
    if volume > current_volume:
        current_volume = current_volume * 0.3 + volume * 0.7
    else:
        current_volume = current_volume * 0.8 + volume * 0.2

def _audio_manager(stop_event):
    global _stream, _last_data_time, _audio_buffer, _current_device_name, current_volume
    global is_singing, _sing_counter
    
    while not stop_event.is_set():
        cfg_mic = config.CFG["global"]["mic"]
        target_device_id = cfg_mic.get("device_id", -1)
        
        actual_device = None
        device_name = "默认"
        try:
            if target_device_id != -1:
                info = sd.query_devices(target_device_id)
                actual_device = target_device_id
                device_name = info['name']
            else:
                info = sd.query_devices(kind='input')
                actual_device = None
                device_name = info['name']
        except Exception:
            target_device_id = -1
            try:
                info = sd.query_devices(kind='input')
                device_name = info['name']
            except:
                device_name = "Unknown"
            actual_device = None

        if _stream is not None and _current_device_name != device_name:
            try:
                _stream.stop()
                _stream.close()
            except: pass
            _stream = None
            with _state_lock:
                current_volume = 0.0
                is_singing = False
                _sing_counter = 0
                _audio_buffer = []
            stop_event.wait(0.5)

        if _stream is None:
            if device_name == "Unknown":
                stop_event.wait(1.0)
                continue
                
            try:
                _stream = sd.InputStream(device=actual_device, callback=audio_callback, channels=1, samplerate=44100, blocksize=1024)
                _stream.start()
                _current_device_name = device_name
                print(f"[音频系统] 麦克风监听已启动，当前设备: {_current_device_name}")
                _last_data_time = time.time()
                with _state_lock:
                    _audio_buffer = []
                    for _ in range(int(44100 * 0.1)): 
                        _audio_buffer.append(0.0)
            except Exception:
                stop_event.wait(1.0)
            continue

        if time.time() - _last_data_time > 2.0:
            print("[音频系统] 音频流中断，正在尝试重连...")
            try:
                _stream.stop()
                _stream.close()
            except: pass
            _stream = None
            with _state_lock:
                current_volume = 0.0
                _audio_buffer = []
                is_singing = False
                _sing_counter = 0
            
        stop_event.wait(0.5)

def start_mic():
    global _thread, _stop_event, is_singing, _sing_counter, current_volume, _audio_buffer
    if not MIC_ENABLED: return None
    
    if _thread is not None and _thread.is_alive():
        _stop_event.set()
        _thread.join(timeout=2.0)
        
    with _state_lock:
        is_singing = False
        _sing_counter = 0
        current_volume = 0.0
        _audio_buffer = []
        
    _stop_event = threading.Event()
    _thread = threading.Thread(target=_audio_manager, args=(_stop_event,), daemon=True)
    _thread.start()
    
    def _warmup():
        try:
            dummy_audio = np.zeros(16000, dtype=np.float32)
            librosa.piptrack(y=dummy_audio, sr=44100, fmin=80, fmax=1000)
            if config.CFG["global"]["mic"].get("denoise", True):
                nr.reduce_noise(y=dummy_audio, sr=44100)
        except: pass
    threading.Thread(target=_warmup, daemon=True).start()
    
    return _thread

def stop_mic(stream_thread):
    global _thread, _stop_event, _stream, is_singing, _sing_counter
    if _thread is not None:
        _stop_event.set()
        _thread.join(timeout=2.0)
        _thread = None
        
    if _stream:
        try:
            _stream.stop()
            _stream.close()
        except: pass
        _stream = None
        
    with _state_lock:
        is_singing = False
        _sing_counter = 0
        current_volume = 0.0

def get_volume():
    return current_volume

def update_singing_state(is_typing, is_clicking):
    global is_singing, _last_calc_time, _sing_counter, _audio_buffer, _last_sing_time
    
    if _stream is None or not HAS_LIBROSA or not MIC_ENABLED:
        with _state_lock:
            _sing_counter = 0
            is_singing = False
        return

    now = time.time()
    if now - _last_calc_time < 0.5: return
    _last_calc_time = now
    
    if is_typing or is_clicking:
        with _state_lock:
            _sing_counter = max(_sing_counter - 1, 0)
            if _sing_counter < 6: is_singing = False
        return

    sensitivity = config.CFG["global"].get("singing_sensitivity", 50.0)
    use_denoise = config.CFG["global"]["mic"].get("denoise", True)
    
    with _state_lock:
        buf_copy = list(_audio_buffer)
        vol = current_volume
    
    if vol > 0.08 and len(buf_copy) > 8000:
        try:
            y = np.array(buf_copy, dtype=np.float32)
            if use_denoise:
                y_denoised = nr.reduce_noise(y=y, sr=44100, stationary=False)
                # 【新增】安全校验：如果降噪结果里包含 NaN，说明除零了，退回到原音频
                if np.isnan(y_denoised).any():
                    y_denoised = y
            else:
                y_denoised = y
                
            pitches, magnitudes = librosa.piptrack(y=y_denoised, sr=44100, fmin=80, fmax=1000)
            f0_seq = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                mag = magnitudes[index, t]
                if 80 < pitch < 1000 and mag > 0.1:
                    f0_seq.append(pitch)
                    
            if len(f0_seq) > 15:
                pitch_diffs = np.abs(np.diff(f0_seq))
                stable_ratio = np.sum(pitch_diffs < 5.0) / len(pitch_diffs)
                required_ratio = max(0.16, 1.0 - (sensitivity / 120.0))
                with _state_lock:
                    if stable_ratio > required_ratio:
                        _sing_counter = min(_sing_counter + 2, 12)
                        _last_sing_time = now
                    else:
                        _sing_counter = max(_sing_counter - 2, 0)
        except Exception:
            pass
    else:
        with _state_lock:
            _sing_counter = max(_sing_counter - 2, 0)
            
    with _state_lock:
        if now - _last_sing_time > 1.5:
            _sing_counter = 0
            
        is_singing = _sing_counter >= 6

def get_is_singing():
    with _state_lock:
        return is_singing
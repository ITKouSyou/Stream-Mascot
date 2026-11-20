import os
import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import config
import webbrowser
import shutil
from audio_utils import get_all_input_devices

CONFIG_FILE = "config.json"

class SettingsWindow:
    def __init__(self, on_save_callback, on_interact_callback):
        self.on_save = on_save_callback
        self.on_interact = on_interact_callback
        
        self.cfg = config.load_config()
        self.active_profile_name = self.cfg["active_profile"]
        self.temp_images = {}
        
        self.root = tk.Tk()
        self.root.title("Stream-Mascot 设置")
        self.root.geometry("700x800")
        self.root.configure(bg="#2b2b2b")
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)

        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background='#2b2b2b', borderwidth=0)
        style.configure('TNotebook.Tab', background='#3c3f41', foreground='white', padding=[15, 5], font=('微软雅黑', 10))
        style.map('TNotebook.Tab', background=[('selected', '#4b6eaf')])
        style.configure('TFrame', background='#2b2b2b')
        style.configure('TLabel', background='#2b2b2b', foreground='#cccccc', font=('微软雅黑', 10))
        style.configure('Title.TLabel', foreground='white', font=('微软雅黑', 12, 'bold'))
        style.configure('TCheckbutton', background='#2b2b2b', foreground='white', font=('微软雅黑', 10))
        
        top_frame = tk.Frame(self.root, bg="#1e1e1e", pady=10, padx=10)
        top_frame.pack(fill=tk.X)
        
        tk.Label(top_frame, text="当前方案:", bg="#1e1e1e", fg="white", font=('微软雅黑', 10, 'bold')).pack(side=tk.LEFT)
        self.profile_var = tk.StringVar(value=self.active_profile_name)
        self.profile_combo = ttk.Combobox(top_frame, textvariable=self.profile_var, state="readonly", width=20)
        self.profile_combo['values'] = list(self.cfg["profiles"].keys())
        self.profile_combo.pack(side=tk.LEFT, padx=10)
        self.profile_combo.bind("<<ComboboxSelected>>", self.on_profile_change)
        
        tk.Button(top_frame, text="+ 新建", command=self.create_profile, bg="#4b6eaf", fg="white", relief="flat").pack(side=tk.LEFT, padx=5)
        tk.Button(top_frame, text="- 删除", command=self.delete_profile, bg="#a33", fg="white", relief="flat").pack(side=tk.LEFT)

        btn_frame = tk.Frame(self.root, bg="#2b2b2b")
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        tk.Button(btn_frame, text="仅保存（不重启）", command=self.apply_only, bg="#555555", fg="white", font=('微软雅黑', 10), relief="flat", width=15).pack(side=tk.LEFT)
        tk.Button(btn_frame, text="保存并重启", command=self.save_and_reload, bg="#4b6eaf", fg="white", font=('微软雅黑', 10, 'bold'), relief="flat", width=15).pack(side=tk.RIGHT)
        tk.Button(btn_frame, text="取消", command=self.root.destroy, bg="#555555", fg="white", font=('微软雅黑', 10), relief="flat", width=10).pack(side=tk.RIGHT, padx=10)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.tab_global = ttk.Frame(self.notebook)
        self.tab_char = ttk.Frame(self.notebook)
        self.tab_keywords = ttk.Frame(self.notebook)
        self.tab_action = ttk.Frame(self.notebook)
        self.tab_about = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_global, text='全局设置')
        self.notebook.add(self.tab_char, text='角色与表情')
        self.notebook.add(self.tab_keywords, text='语音词库')
        self.notebook.add(self.tab_action, text='快捷互动')
        self.notebook.add(self.tab_about, text='关于与教程')

        self.build_global_tab()
        self.build_char_tab()
        self.build_keywords_tab()
        self.build_action_tab()
        self.build_about_tab()

        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)
        self.load_profile_to_ui()

    def format_path(self, path):
        if not path: return "未选择"
        if len(path) > 35:
            return path[:15] + "..." + path[-15:]
        return path

    def on_profile_change(self, event=None):
        self.active_profile_name = self.profile_var.get()
        self.temp_images = {}
        self.load_profile_to_ui()

    def create_profile(self):
        new_name = simpledialog.askstring("新建方案", "请输入方案名称:", parent=self.root)
        if not new_name: return
        if new_name in self.cfg["profiles"]:
            messagebox.showwarning("提示", "方案名称已存在！")
            return
        
        new_prof = json.loads(json.dumps(config.DEFAULT_PROFILE))
        new_prof["name"] = new_name
        
        self.cfg["profiles"][new_name] = new_prof
        self.profile_combo['values'] = list(self.cfg["profiles"].keys())
        self.profile_var.set(new_name)
        self.on_profile_change()

    def delete_profile(self):
        if len(self.cfg["profiles"]) <= 1:
            messagebox.showwarning("提示", "至少需要保留一个方案！")
            return
        
        if messagebox.askyesno("确认", f"确定要删除方案「{self.active_profile_name}」吗？"):
            del self.cfg["profiles"][self.active_profile_name]
            self.active_profile_name = list(self.cfg["profiles"].keys())[0]
            self.profile_combo['values'] = list(self.cfg["profiles"].keys())
            self.profile_var.set(self.active_profile_name)
            self.on_profile_change()

    def build_global_tab(self):
        # 【核心修复】加入 Canvas 和 Scrollbar 实现滚动
        canvas = tk.Canvas(self.tab_global, bg="#2b2b2b", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.tab_global, orient="vertical", command=canvas.yview)
        
        # 绑定鼠标滚轮
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        
        # 包含所有控件的内部 Frame
        scrollable_frame = ttk.Frame(canvas, padding=15)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        global_cfg = self.cfg["global"]
        frame = scrollable_frame # 把原本加在 frame 上的控件都重定向到 scrollable_frame

        ttk.Label(frame, text="窗口缩放比例", style='Title.TLabel').pack(anchor=tk.W, pady=(10, 5))
        ttk.Label(frame, text="解释：控制桌宠在屏幕上的显示大小，默认 1.0。修改后需重启才能看到变化。", wraplength=600).pack(anchor=tk.W)
        self.var_scale = tk.DoubleVar(value=global_cfg.get("scale", 1.0))
        tk.Scale(frame, variable=self.var_scale, from_=0.5, to=2.5, resolution=0.1, orient=tk.HORIZONTAL, 
                 bg="#2b2b2b", fg="white", highlightthickness=0, length=400).pack(anchor=tk.W, pady=5)

        self.var_always_on_top = tk.BooleanVar(value=global_cfg.get("always_on_top", True))
        ttk.Checkbutton(frame, text="窗口置顶显示 (取消勾选后，点击其他软件时桌宠会被盖住)", variable=self.var_always_on_top).pack(anchor=tk.W, pady=(10, 0))

        # ===== 音频设备配置 =====
        ttk.Label(frame, text="音频输入设备", style='Title.TLabel').pack(anchor=tk.W, pady=(15, 5))
        ttk.Label(frame, text="解释：如果系统自动切换失效，可以在这里手动锁定你的麦克风。", wraplength=600).pack(anchor=tk.W)
        
        self.devices = get_all_input_devices()
        device_names = [d[1] for d in self.devices]
        self.var_device = tk.StringVar()
        
        current_dev_id = global_cfg["mic"].get("device_id", -1)
        current_dev_name = "系统默认设备 (跟随 Windows 切换)"
        for d_id, d_name in self.devices:
            if d_id == current_dev_id:
                current_dev_name = d_name
                break
        self.var_device.set(current_dev_name)
        
        self.device_combo = ttk.Combobox(frame, textvariable=self.var_device, values=device_names, state="readonly", width=60)
        self.device_combo.pack(anchor=tk.W, pady=5)

        self.var_denoise = tk.BooleanVar(value=global_cfg["mic"].get("denoise", True))
        ttk.Checkbutton(frame, text="启用 AI 降噪 (过滤风扇等底噪，防止误触唱歌)", variable=self.var_denoise).pack(anchor=tk.W, pady=(5, 0))

        ttk.Label(frame, text="麦克风触发阈值", style='Title.TLabel').pack(anchor=tk.W, pady=(15, 5))
        ttk.Label(frame, text="解释：数值越小越容易触发嘴巴动作，建议 0.1 - 0.25 之间。", wraplength=600).pack(anchor=tk.W)
        self.var_mic_threshold = tk.DoubleVar(value=global_cfg["mic"]["threshold"])
        tk.Scale(frame, variable=self.var_mic_threshold, from_=0.01, to=0.5, resolution=0.01, orient=tk.HORIZONTAL, 
                 bg="#2b2b2b", fg="white", highlightthickness=0, length=400).pack(anchor=tk.W, pady=5)

        ttk.Label(frame, text="唱歌判定灵敏度 (1-100)", style='Title.TLabel').pack(anchor=tk.W, pady=(15, 5))
        ttk.Label(frame, text="解释：数值越大越容易触发唱歌摇摆。如果普通说话经常变成唱歌，请直接拉到 80-100。", wraplength=600).pack(anchor=tk.W)
        self.var_singing_sens = tk.DoubleVar(value=global_cfg.get("singing_sensitivity", 50.0))
        tk.Scale(frame, variable=self.var_singing_sens, from_=10.0, to=100.0, resolution=1.0, orient=tk.HORIZONTAL, 
                 bg="#2b2b2b", fg="white", highlightthickness=0, length=400).pack(anchor=tk.W, pady=5)

        self.var_mic_enabled = tk.BooleanVar(value=global_cfg["mic"]["enabled"])
        ttk.Checkbutton(frame, text="启用麦克风互动 (说话嘴型/唱歌摇摆)", variable=self.var_mic_enabled).pack(anchor=tk.W, pady=(15, 0))

    def build_char_tab(self):
        frame = ttk.Frame(self.tab_char, padding=15)
        frame.pack(fill=tk.BOTH, expand=True)

        self.var_show_code_face = tk.BooleanVar()
        ttk.Checkbutton(frame, text="使用自带的颜文字表情 (如果关闭，请上传对应的表情图片)", variable=self.var_show_code_face).pack(anchor=tk.W, pady=(0, 15))

        base_frame = tk.LabelFrame(frame, text="基础角色图片 (normal)", bg="#2b2b2b", fg="#4b6eaf", font=('微软雅黑', 10, 'bold'))
        base_frame.pack(fill=tk.X, pady=5)
        
        self.lbl_char_path = tk.Label(base_frame, text="未选择", bg="#2b2b2b", fg="#aaaaaa", anchor="w")
        self.lbl_char_path.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        
        tk.Button(base_frame, text="选择图片", command=lambda: self.select_image("character_path", self.lbl_char_path), bg="#555", fg="white", relief="flat").pack(side=tk.RIGHT, padx=5)
        tk.Button(base_frame, text="恢复默认白猫", command=self.clear_char_image, bg="#a33", fg="white", relief="flat").pack(side=tk.RIGHT)

        self.custom_face_frame = tk.Frame(frame, bg="#2b2b2b")
        self.custom_face_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.face_labels = {}
        emotions = [("heart", "爱心眼"), ("angry", "生气"), ("cry", "哭泣"), ("surprised", "震惊"), ("speechless", "无语")]
        
        for key, name in emotions:
            sub = tk.Frame(self.custom_face_frame, bg="#2b2b2b")
            sub.pack(fill=tk.X, pady=2)
            tk.Label(sub, text=f"{name} 状态:", bg="#2b2b2b", fg="white", width=10, anchor="w").pack(side=tk.LEFT)
            
            lbl = tk.Label(sub, text="未选择", bg="#2b2b2b", fg="#aaaaaa", anchor="w")
            self.face_labels[key] = lbl
            
            tk.Button(sub, text="清除", command=lambda k=key: self.clear_face_image(k), bg="#555", fg="white", relief="flat").pack(side=tk.RIGHT, padx=5)
            tk.Button(sub, text="上传", command=lambda k=key, l=lbl: self.select_image(f"expressions.{k}", l), bg="#555", fg="white", relief="flat").pack(side=tk.RIGHT)
            
            lbl.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def clear_char_image(self):
        self.lbl_char_path.config(text="未选择", fg="#aaaaaa")
        if not hasattr(self, 'temp_images'): self.temp_images = {}
        self.temp_images["character_path"] = ""
        self.var_show_code_face.set(True)

    def clear_face_image(self, key):
        lbl = self.face_labels.get(key)
        if not lbl: return
        lbl.config(text="未选择", fg="#aaaaaa")
        if not hasattr(self, 'temp_images'): self.temp_images = {}
        self.temp_images[f"expressions.{key}"] = ""

    def select_image(self, path_key, label_widget):
        file_path = filedialog.askopenfilename(title="选择图片", filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif")])
        if not file_path: return
        
        filename = os.path.basename(file_path)
        dest_path = os.path.join(config.CUSTOM_DIR, filename)
        try:
            shutil.copy(file_path, dest_path)
            rel_path = os.path.join(config.CUSTOM_DIR, filename).replace("\\", "/")
            
            if not hasattr(self, 'temp_images'): self.temp_images = {}
            self.temp_images[path_key] = rel_path
            
            if label_widget:
                label_widget.config(text=self.format_path(rel_path), fg="#4b6eaf")
        except Exception as e:
            messagebox.showerror("错误", f"复制图片失败: {e}")

    def build_keywords_tab(self):
        self.kw_frame = ttk.Frame(self.tab_keywords, padding=10)
        self.kw_frame.pack(fill=tk.BOTH, expand=True)
        self.listboxes = {}
        self.rebuild_keywords_ui()

    def rebuild_keywords_ui(self):
        for widget in self.kw_frame.winfo_children():
            widget.destroy()
        
        self.listboxes = {}
        prof = self.cfg["profiles"][self.active_profile_name]
        show_code = prof.get("show_code_face", True)

        emotions = {
            "heart": "♥ 爱心眼", "angry": "╬ 生气", "cry": "ಥ 哭泣", "surprised": "⊙ 震惊", "speechless": "￣ 无语"
        }
        
        msg_text = "当前为自定义表情模式，请为每种状态配置触发词。" if not show_code else "当前为颜文字模式，请配置触发词。"
        tk.Label(self.kw_frame, text=msg_text, bg="#2b2b2b", fg="#4b6eaf").grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))

        for idx, (key, label_text) in enumerate(emotions.items()):
            col = idx % 2
            row = (idx // 2) + 1
            sub_frame = tk.LabelFrame(self.kw_frame, text=label_text, bg="#2b2b2b", fg="#4b6eaf", font=('微软雅黑', 10, 'bold'))
            sub_frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            self.kw_frame.grid_columnconfigure(col, weight=1)

            lb = tk.Listbox(sub_frame, height=4, bg="#3c3f41", fg="white", selectbackground="#4b6eaf")
            lb.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            self.listboxes[key] = lb
            
            for kw in prof["keywords"].get(key, []):
                lb.insert(tk.END, kw)

            op_frame = tk.Frame(sub_frame, bg="#2b2b2b")
            op_frame.pack(fill=tk.X, padx=5, pady=5)
            entry = tk.Entry(op_frame, bg="#1e1e1e", fg="white", insertbackground="white", width=10)
            entry.pack(side=tk.LEFT, padx=(0, 5))
            tk.Button(op_frame, text="+", width=2, bg="#4b6eaf", fg="white", relief="flat",
                      command=lambda k=key, e=entry, l=lb: self.add_keyword(k, e, l)).pack(side=tk.LEFT, padx=2)
            tk.Button(op_frame, text="-", width=2, bg="#a33", fg="white", relief="flat",
                      command=lambda k=key, l=lb: self.remove_keyword(k, l)).pack(side=tk.LEFT)

    def add_keyword(self, emotion, entry_widget, listbox):
        word = entry_widget.get().strip()
        if not word: return
        for k, lb in self.listboxes.items():
            if word in lb.get(0, tk.END):
                messagebox.showwarning("提示", f"关键词「{word}」已在其他表情中存在！")
                return
        listbox.insert(tk.END, word)
        entry_widget.delete(0, tk.END)

    def remove_keyword(self, emotion, listbox):
        sel = listbox.curselection()
        if not sel: return
        if listbox.size() <= 1:
            messagebox.showwarning("提示", "至少保留一个触发词！")
            return
        listbox.delete(sel[0])

    def build_action_tab(self):
        frame = ttk.Frame(self.tab_action, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(frame, text="手动触发互动", style='Title.TLabel').pack(anchor=tk.W, pady=(10, 15))
        
        def create_btn(text, action):
            tk.Button(frame, text=text, bg="#3c3f41", fg="white", font=('微软雅黑', 11), relief="flat", width=25,
                      command=lambda: self.on_interact(action)).pack(pady=6)

        create_btn("比个心 (♥ω♥)", "heart")
        create_btn("生气了 (╬▔皿▔)", "angry")
        create_btn("委屈哭泣 (ಥ_ಥ)", "cry")
        create_btn("震惊 (⊙_⊙)", "surprised")
        create_btn("无语出汗 (￣_￣)", "speechless")
        create_btn("恢复原状", "normal")

    def build_about_tab(self):
        frame = ttk.Frame(self.tab_about, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(frame, text=f"Stream-Mascot 直播桌宠 v{config.__version__}", style='Title.TLabel').pack(anchor=tk.W, pady=(0, 10))
        desc = "一个纯 Python + Pygame 编写的虚拟挂件。支持全局键鼠监听、麦克风语音联动以及离线语音识别。"
        tk.Label(frame, text=desc, wraplength=630, justify=tk.LEFT, bg="#2b2b2b", fg="#aaaaaa").pack(anchor=tk.W, pady=5)

        ttk.Label(frame, text="作者信息", style='Title.TLabel').pack(anchor=tk.W, pady=(15, 5))
        def open_link(url): webbrowser.open_new(url)
        
        tk.Label(frame, text="作者：ITKouSyou", bg="#2b2b2b", fg="white", font=('微软雅黑', 10, 'bold')).pack(anchor=tk.W)
        
        gf = tk.Frame(frame, bg="#2b2b2b")
        gf.pack(anchor=tk.W, fill=tk.X, pady=2)
        tk.Label(gf, text="GitHub：", bg="#2b2b2b", fg="#cccccc").pack(side=tk.LEFT)
        gl = tk.Label(gf, text="https://github.com/ITKouSyou/Stream-Mascot", bg="#2b2b2b", fg="#4b6eaf", underline=True, cursor="hand2")
        gl.pack(side=tk.LEFT)
        gl.bind("<Button-1>", lambda e: open_link("https://github.com/ITKouSyou/Stream-Mascot"))

    def load_profile_to_ui(self):
        prof = self.cfg["profiles"][self.active_profile_name]
        self.var_show_code_face.set(prof.get("show_code_face", True))
        
        char_path = prof.get("character_path", "")
        self.lbl_char_path.config(text=self.format_path(char_path) if char_path else "未选择", fg="#4b6eaf" if char_path else "#aaaaaa")
        
        for k, lbl in self.face_labels.items():
            path = prof.get("expressions", {}).get(k, "")
            lbl.config(text=self.format_path(path) if path else "未选择", fg="#4b6eaf" if path else "#aaaaaa")
            
        self.rebuild_keywords_ui()

    def _write_config(self):
        self.cfg["global"]["scale"] = round(self.var_scale.get(), 1)
        self.cfg["global"]["always_on_top"] = self.var_always_on_top.get()
        self.cfg["global"]["singing_sensitivity"] = round(self.var_singing_sens.get(), 1)
        self.cfg["global"]["mic"]["enabled"] = self.var_mic_enabled.get()
        self.cfg["global"]["mic"]["threshold"] = round(self.var_mic_threshold.get(), 2)
        self.cfg["global"]["mic"]["denoise"] = self.var_denoise.get()
        
        selected_name = self.var_device.get()
        selected_id = -1
        for d_id, d_name in self.devices:
            if d_name == selected_name:
                selected_id = d_id
                break
        self.cfg["global"]["mic"]["device_id"] = selected_id
        
        self.cfg["active_profile"] = self.profile_var.get()
        prof = self.cfg["profiles"][self.active_profile_name]
        prof["show_code_face"] = self.var_show_code_face.get()
        
        if hasattr(self, 'temp_images'):
            for key, val in self.temp_images.items():
                if key == "character_path":
                    prof["character_path"] = val
                elif key.startswith("expressions."):
                    exp_key = key.split(".")[1]
                    prof["expressions"][exp_key] = val
                    
        for k, lb in self.listboxes.items():
            prof["keywords"][k] = list(lb.get(0, tk.END))

        config.save_config(self.cfg)

    def apply_only(self):
        try:
            self._write_config()
            messagebox.showinfo("成功", "配置已保存！下次启动或重新加载时生效。")
        except Exception as e:
            messagebox.showerror("错误", f"无法保存配置：{e}")

    def save_and_reload(self):
        try:
            self._write_config()
            self.root.destroy()
            self.on_save()
        except Exception as e:
            messagebox.showerror("错误", f"无法保存配置：{e}")

    def show(self):
        self.root.mainloop()
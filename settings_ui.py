import os
import json
import tkinter as tk
from tkinter import ttk, messagebox
import config
import webbrowser  # 新增：用于打开浏览器链接

CONFIG_FILE = "config.json"

class SettingsWindow:
    def __init__(self, on_save_callback, on_interact_callback):
        self.on_save = on_save_callback
        self.on_interact = on_interact_callback
        
        self.root = tk.Tk()
        self.root.title("Stream-Mascot 设置")
        self.root.geometry("600x780")
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
        
        btn_frame = tk.Frame(self.root, bg="#2b2b2b")
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        
        tk.Button(btn_frame, text="仅保存（不重启）", command=self.apply_only, bg="#555555", fg="white", font=('微软雅黑', 10), relief="flat", width=15).pack(side=tk.LEFT)
        tk.Button(btn_frame, text="保存并重启", command=self.save_and_reload, bg="#4b6eaf", fg="white", font=('微软雅黑', 10, 'bold'), relief="flat", width=15).pack(side=tk.RIGHT)
        tk.Button(btn_frame, text="取消", command=self.root.destroy, bg="#555555", fg="white", font=('微软雅黑', 10), relief="flat", width=10).pack(side=tk.RIGHT, padx=10)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.tab_config = ttk.Frame(self.notebook)
        self.tab_keywords = ttk.Frame(self.notebook)
        self.tab_action = ttk.Frame(self.notebook)
        self.tab_about = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_config, text='基本设置')
        self.notebook.add(self.tab_keywords, text='语音词库')
        self.notebook.add(self.tab_action, text='快捷互动')
        self.notebook.add(self.tab_about, text='关于与教程')

        self.build_config_tab()
        self.build_keywords_tab()
        self.build_action_tab()
        self.build_about_tab()

        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)

    def build_config_tab(self):
        frame = ttk.Frame(self.tab_config, padding=15)
        frame.pack(fill=tk.BOTH, expand=True)
        cfg = config.load_config()

        ttk.Label(frame, text="窗口缩放比例", style='Title.TLabel').pack(anchor=tk.W, pady=(10, 5))
        ttk.Label(frame, text="解释：控制桌宠在屏幕上的显示大小，默认 1.0。修改后需重启才能看到变化。", wraplength=530).pack(anchor=tk.W)
        self.var_scale = tk.DoubleVar(value=cfg.get("scale", 1.0))
        tk.Scale(frame, variable=self.var_scale, from_=0.5, to=2.5, resolution=0.1, orient=tk.HORIZONTAL, 
                 bg="#2b2b2b", fg="white", highlightthickness=0, length=400).pack(anchor=tk.W, pady=5)

        ttk.Label(frame, text="麦克风触发阈值", style='Title.TLabel').pack(anchor=tk.W, pady=(20, 5))
        ttk.Label(frame, text="解释：数值越小越容易触发说话动作，建议 0.1 - 0.25 之间。如果发现猫猫经常无端张嘴，请调大这个值。", wraplength=530).pack(anchor=tk.W)
        self.var_mic_threshold = tk.DoubleVar(value=cfg["mic"]["threshold"])
        tk.Scale(frame, variable=self.var_mic_threshold, from_=0.01, to=0.5, resolution=0.01, orient=tk.HORIZONTAL, 
                 bg="#2b2b2b", fg="white", highlightthickness=0, length=400).pack(anchor=tk.W, pady=5)

        ttk.Label(frame, text="嘴巴张合速度", style='Title.TLabel').pack(anchor=tk.W, pady=(20, 5))
        ttk.Label(frame, text="解释：数值越大，说话时嘴巴开合的频率越快，默认为 10。", wraplength=530).pack(anchor=tk.W)
        self.var_mouth_speed = tk.IntVar(value=cfg["mic"].get("mouth_speed", 10))
        tk.Scale(frame, variable=self.var_mouth_speed, from_=1, to=20, orient=tk.HORIZONTAL, 
                 bg="#2b2b2b", fg="white", highlightthickness=0, length=400).pack(anchor=tk.W, pady=5)

        self.var_mic_enabled = tk.BooleanVar(value=cfg["mic"]["enabled"])
        ttk.Checkbutton(frame, text="启用麦克风互动 (关闭后不再识别声音和触发语音表情)", variable=self.var_mic_enabled).pack(anchor=tk.W, pady=(20, 0))

    def build_keywords_tab(self):
        frame = ttk.Frame(self.tab_keywords, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        cfg = config.load_config()
        self.keyword_vars = {}
        self.listboxes = {}

        emotions = {
            "heart": "♥ 爱心眼",
            "angry": "╬ 生气",
            "cry": "ಥ 哭泣",
            "surprised": "⊙ 震惊",
            "speechless": "￣ 无语"
        }

        for idx, (key, label_text) in enumerate(emotions.items()):
            col = idx % 2
            row = idx // 2
            
            sub_frame = tk.LabelFrame(frame, text=label_text, bg="#2b2b2b", fg="#4b6eaf", font=('微软雅黑', 10, 'bold'), bd=1)
            sub_frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            frame.grid_columnconfigure(col, weight=1)

            lb = tk.Listbox(sub_frame, height=4, bg="#3c3f41", fg="white", selectbackground="#4b6eaf", font=('微软雅黑', 10), bd=0)
            lb.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            self.listboxes[key] = lb
            
            for kw in cfg["keywords"][key]:
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
        if not word:
            return
        
        for k, lb in self.listboxes.items():
            if word in lb.get(0, tk.END):
                messagebox.showwarning("提示", f"关键词「{word}」已经在 [{k}] 表情中存在，不能重复！")
                return
                
        listbox.insert(tk.END, word)
        entry_widget.delete(0, tk.END)

    def remove_keyword(self, emotion, listbox):
        selection = listbox.curselection()
        if not selection:
            messagebox.showinfo("提示", "请先在列表中点击选中要删除的词。")
            return
        
        if listbox.size() <= 1:
            messagebox.showwarning("提示", "每个表情至少需要保留一个触发词！")
            return
            
        listbox.delete(selection[0])

    def build_action_tab(self):
        frame = ttk.Frame(self.tab_action, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="手动触发互动", style='Title.TLabel').pack(anchor=tk.W, pady=(10, 15))
        
        def create_btn(text, action):
            tk.Button(frame, text=text, bg="#3c3f41", fg="white", font=('微软雅黑', 11), relief="flat", width=25,
                      command=lambda: self.trigger_action(action)).pack(pady=6)

        create_btn("比个心 (♥ω♥)", "heart")
        create_btn("生气了 (╬▔皿▔)", "angry")
        create_btn("委屈哭泣 (ಥ_ಥ)", "cry")
        create_btn("震惊 (⊙_⊙)", "surprised")
        create_btn("无语出汗 (￣_￣)", "speechless")
        create_btn("恢复原状", "normal")

    def build_about_tab(self):
        frame = ttk.Frame(self.tab_about, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Stream-Mascot 直播桌宠", style='Title.TLabel').pack(anchor=tk.W, pady=(0, 10))
        
        desc = "一个纯 Python + Pygame 编写的虚拟挂件。支持全局键鼠监听、麦克风语音联动以及离线语音识别表情互动。"
        tk.Label(frame, text=desc, wraplength=530, justify=tk.LEFT, bg="#2b2b2b", fg="#aaaaaa", font=('微软雅黑', 10)).pack(anchor=tk.W, pady=5)

        # ======== 新增：作者信息 ========
        ttk.Label(frame, text="作者信息", style='Title.TLabel').pack(anchor=tk.W, pady=(15, 5))
        
        # 点击链接打开浏览器的函数
        def open_link(url):
            webbrowser.open_new(url)

        author_frame = tk.Frame(frame, bg="#2b2b2b")
        author_frame.pack(anchor=tk.W, fill=tk.X, pady=2)

        tk.Label(author_frame, text="作者：", bg="#2b2b2b", fg="#cccccc", font=('微软雅黑', 10)).pack(side=tk.LEFT)
        tk.Label(author_frame, text="ITKouSyou", bg="#2b2b2b", fg="#ffffff", font=('微软雅黑', 10, 'bold')).pack(side=tk.LEFT)

        bili_frame = tk.Frame(frame, bg="#2b2b2b")
        bili_frame.pack(anchor=tk.W, fill=tk.X, pady=2)
        tk.Label(bili_frame, text="B站主页：", bg="#2b2b2b", fg="#cccccc", font=('微软雅黑', 10)).pack(side=tk.LEFT)
        bili_link = tk.Label(bili_frame, text="https://space.bilibili.com/7243785", bg="#2b2b2b", fg="#4b6eaf", font=('微软雅黑', 10, 'underline'), cursor="hand2")
        bili_link.pack(side=tk.LEFT)
        bili_link.bind("<Button-1>", lambda e: open_link("https://space.bilibili.com/7243785"))

        github_frame = tk.Frame(frame, bg="#2b2b2b")
        github_frame.pack(anchor=tk.W, fill=tk.X, pady=2)
        tk.Label(github_frame, text="GitHub：", bg="#2b2b2b", fg="#cccccc", font=('微软雅黑', 10)).pack(side=tk.LEFT)
        github_link = tk.Label(github_frame, text="https://github.com/ITKouSyou/Stream-Mascot", bg="#2b2b2b", fg="#4b6eaf", font=('微软雅黑', 10, 'underline'), cursor="hand2")
        github_link.pack(side=tk.LEFT)
        github_link.bind("<Button-1>", lambda e: open_link("https://github.com/ITKouSyou/Stream-Mascot"))

        # ================================

        ttk.Label(frame, text="快捷键操作", style='Title.TLabel').pack(anchor=tk.W, pady=(15, 5))
        shortcuts = [
            "• 鼠标左键：拖拽桌宠 / 点击按钮",
            "• 鼠标右键：呼出菜单",
            "• F8 键：开启/关闭鼠标穿透",
            "• Esc 键：退出程序"
        ]
        for s in shortcuts:
            tk.Label(frame, text=s, bg="#2b2b2b", fg="#cccccc", font=('微软雅黑', 10)).pack(anchor=tk.W)

    def trigger_action(self, action):
        self.on_interact(action)

    def _write_config(self):
        cfg = config.load_config()
        cfg["scale"] = round(self.var_scale.get(), 1)
        cfg["mic"]["enabled"] = self.var_mic_enabled.get()
        cfg["mic"]["threshold"] = round(self.var_mic_threshold.get(), 2)
        cfg["mic"]["mouth_speed"] = self.var_mouth_speed.get()
        
        new_keywords = {}
        for k, lb in self.listboxes.items():
            new_keywords[k] = list(lb.get(0, tk.END))
        cfg["keywords"] = new_keywords

        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)

    def apply_only(self):
        try:
            self._write_config()
            messagebox.showinfo("保存成功", "配置已保存！下次启动或重新加载时生效。")
        except Exception as e:
            messagebox.showerror("保存失败", f"无法保存配置：{e}")

    def save_and_reload(self):
        try:
            self._write_config()
            self.root.destroy()
            self.on_save()
        except Exception as e:
            messagebox.showerror("保存失败", f"无法保存配置：{e}")

    def show(self):
        self.root.mainloop()
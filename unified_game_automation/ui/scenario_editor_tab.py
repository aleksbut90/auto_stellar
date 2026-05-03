"""
Scenario Editor Tab — редактор сценариев (ПОЛНОСТЬЮ ИСПРАВЛЕН)
"""

import os
import sys
import json
import time
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog

from core.scenario_engine import ScenarioEngine


class ScenarioEditorTab:
    def __init__(self, parent_frame, main_window):
        self.parent_frame = parent_frame
        self.main_window = main_window

        self.scenarios = []
        self.engine = None
        self.is_running = False
        self.selected_scenario_idx = None
        self._updating_threshold = False

        self.create_ui()

    def create_ui(self):
        main_frame = ttk.Frame(self.parent_frame, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # ====== СЕКЦИЯ 1: Управление ======
        control_section = ttk.LabelFrame(main_frame, text="🎮 Управление ботом", padding="15")
        control_section.pack(fill=tk.X, pady=(0, 15))

        buttons_frame = ttk.Frame(control_section)
        buttons_frame.pack(fill=tk.X)

        self.btn_start = ttk.Button(buttons_frame, text="▶️  Запустить (цикл)", command=self.start_bot)
        self.btn_start.pack(side=tk.LEFT, padx=(0, 10))

        self.btn_run_once = ttk.Button(buttons_frame, text="🚀 Запустить один раз", command=self.run_once)
        self.btn_run_once.pack(side=tk.LEFT, padx=(0, 10))

        self.btn_stop = ttk.Button(buttons_frame, text="⏹️  Остановить", command=self.stop_bot, state=tk.DISABLED)
        self.btn_stop.pack(side=tk.LEFT, padx=(0, 20))

        self.status_var = tk.StringVar(value="⚪ Бот остановлен")
        ttk.Label(control_section, textvariable=self.status_var, font=self.main_window.heading_font).pack(anchor=tk.W, pady=(5, 0))

        # ====== СЕКЦИЯ 2: Сценарии ======
        scenarios_section = ttk.LabelFrame(main_frame, text="📋 Сценарии", padding="15")
        scenarios_section.pack(fill=tk.X, pady=(0, 15))

        scenario_buttons = ttk.Frame(scenarios_section)
        scenario_buttons.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(scenario_buttons, text="➕ Добавить сценарий", command=self.add_scenario).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(scenario_buttons, text="🗑️  Удалить", command=self.delete_scenario).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(scenario_buttons, text="💾 Сохранить", command=self.save_scenarios).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(scenario_buttons, text="📂 Загрузить", command=self.load_scenarios_file).pack(side=tk.LEFT)

        self.scenario_listbox = tk.Listbox(scenarios_section, height=8,
                                           font=self.main_window.default_font,
                                           selectmode=tk.SINGLE, exportselection=False)
        self.scenario_listbox.pack(fill=tk.X, pady=(0, 10))
        self.scenario_listbox.bind('<<ListboxSelect>>', self.on_scenario_selected)

        # ====== СЕКЦИЯ 3: Редактор сценария ======
        self.editor_section = ttk.LabelFrame(main_frame, text="✏️  Редактор сценария", padding="15")
        self.editor_section.pack(fill=tk.BOTH, expand=True)

        name_frame = ttk.Frame(self.editor_section)
        name_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(name_frame, text="Название:", font=self.main_window.default_font, width=12).pack(side=tk.LEFT)
        self.scenario_name_var = tk.StringVar()
        ttk.Entry(name_frame, textvariable=self.scenario_name_var, width=40, font=self.main_window.default_font).pack(side=tk.LEFT)

        self.enabled_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(name_frame, text="Включён", variable=self.enabled_var).pack(side=tk.LEFT, padx=(20, 0))

        # Триггер
        trigger_frame = ttk.LabelFrame(self.editor_section, text="🔍 Триггер", padding="10")
        trigger_frame.pack(fill=tk.X, pady=(0, 10))

        type_frame = ttk.Frame(trigger_frame)
        type_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(type_frame, text="Тип:", width=12).pack(side=tk.LEFT)
        self.trigger_type_var = tk.StringVar(value="template")
        ttk.Combobox(type_frame, textvariable=self.trigger_type_var, width=20,
                     values=["template", "pixel_color"], state="readonly").pack(side=tk.LEFT)

        template_frame = ttk.Frame(trigger_frame)
        template_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(template_frame, text="Шаблон:", width=12).pack(side=tk.LEFT)
        self.template_path_var = tk.StringVar()
        ttk.Entry(template_frame, textvariable=self.template_path_var, width=50).pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
        ttk.Button(template_frame, text="📂", command=self.browse_template).pack(side=tk.LEFT)
        ttk.Button(template_frame, text="📸 Выделить", command=self.capture_template).pack(side=tk.LEFT)

        templates_list_frame = ttk.Frame(trigger_frame)
        templates_list_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Label(templates_list_frame, text="Шаблоны:", width=12).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(templates_list_frame, text="➕ Добавить", command=self.add_template).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(templates_list_frame, text="🗑️  Удалить", command=self.remove_template).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(templates_list_frame, text="⬆️  Вверх", command=self.move_template_up).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(templates_list_frame, text="⬇️  Вниз", command=self.move_template_down).pack(side=tk.LEFT)

        self.templates_listbox = tk.Listbox(trigger_frame, height=3, font=("Consolas", 9), exportselection=False)
        self.templates_listbox.pack(fill=tk.X, pady=(5, 0))

        settings_frame = ttk.Frame(trigger_frame)
        settings_frame.pack(fill=tk.X)
        ttk.Label(settings_frame, text="Порог:", width=12).pack(side=tk.LEFT)
        self.threshold_var = tk.DoubleVar(value=0.70)
        ttk.Spinbox(settings_frame, from_=0.5, to=0.95, increment=0.05,
                    textvariable=self.threshold_var, width=6).pack(side=tk.LEFT, padx=(0, 20))
        self.threshold_var.trace_add('write', self._on_threshold_change)

        ttk.Label(settings_frame, text="Область поиска:").pack(side=tk.LEFT)
        self.search_area_var = tk.StringVar(value="Весь экран")
        ttk.Label(settings_frame, textvariable=self.search_area_var).pack(side=tk.LEFT)
        ttk.Button(settings_frame, text="📏 Выделить", command=self.select_search_area).pack(side=tk.LEFT)

        ttk.Button(trigger_frame, text="🧪 Тестировать триггер", command=self.test_trigger).pack(anchor=tk.E, pady=(5, 0))

        # Действия
        actions_frame = ttk.LabelFrame(self.editor_section, text="🎯 Действия", padding="10")
        actions_frame.pack(fill=tk.BOTH, expand=True)

        actions_row1 = ttk.Frame(actions_frame)
        actions_row1.pack(fill=tk.X, pady=(0, 5))
        ttk.Button(actions_row1, text="➕ Движение мыши", command=lambda: self.add_action("mouse_move")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(actions_row1, text="➕ Клик ЛКМ", command=lambda: self.add_action("mouse_click")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(actions_row1, text="➕ Клик ПКМ", command=lambda: self.add_action("mouse_right_click")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(actions_row1, text="➕ Зажать ЛКМ", command=lambda: self.add_action("mouse_down", button="left")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(actions_row1, text="➕ Отпустить ЛКМ", command=lambda: self.add_action("mouse_up", button="left")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(actions_row1, text="➕ Зажать ПКМ", command=lambda: self.add_action("mouse_down", button="right")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(actions_row1, text="➕ Отпустить ПКМ", command=lambda: self.add_action("mouse_up", button="right")).pack(side=tk.LEFT, padx=(0, 5))

        actions_row2 = ttk.Frame(actions_frame)
        actions_row2.pack(fill=tk.X, pady=(0, 5))
        ttk.Button(actions_row2, text="➕ Клавиша", command=lambda: self.add_action("key_press")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(actions_row2, text="➕ Зажать клавишу", command=lambda: self.add_action("key_down")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(actions_row2, text="➕ Отпустить клавишу", command=lambda: self.add_action("key_up")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(actions_row2, text="➕ Комбинация", command=lambda: self.add_action("key_combo")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(actions_row2, text="➕ Пауза", command=lambda: self.add_action("wait")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(actions_row2, text="🗑️  Удалить действие", command=self.delete_action).pack(side=tk.LEFT)

        self.actions_listbox = tk.Listbox(actions_frame, height=6, font=("Consolas", 10),
                                          selectmode=tk.SINGLE, exportselection=False)
        self.actions_listbox.pack(fill=tk.BOTH, expand=True)

        repeat_frame = ttk.Frame(actions_frame)
        repeat_frame.pack(fill=tk.X, pady=(5, 0))
        self.repeat_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(repeat_frame, text="Повторять весь сценарий", variable=self.repeat_var).pack(side=tk.LEFT, padx=(0, 20))
        ttk.Label(repeat_frame, text="Задержка (сек):").pack(side=tk.LEFT)
        self.delay_var = tk.DoubleVar(value=1.0)
        ttk.Spinbox(repeat_frame, from_=0.1, to=30.0, increment=0.5,
                    textvariable=self.delay_var, width=6).pack(side=tk.LEFT)

        # Idle секция
        idle_section = ttk.LabelFrame(main_frame, text="💤 Действия при бездействии", padding="15")
        idle_section.pack(fill=tk.X, pady=(15, 0))

        idle_desc = ttk.Label(idle_section, text="Выполняются, если ни один триггер не сработал",
                              font=("Segoe UI", 9), foreground="gray")
        idle_desc.pack(anchor=tk.W, pady=(0, 10))

        idle_buttons = ttk.Frame(idle_section)
        idle_buttons.pack(fill=tk.X, pady=(0, 5))

        ttk.Button(idle_buttons, text="➕ Клик", command=lambda: self.add_idle_action("mouse_click")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(idle_buttons, text="➕ ПКМ", command=lambda: self.add_idle_action("mouse_right_click")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(idle_buttons, text="➕ Движение мыши", command=self.add_idle_mouse_move).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(idle_buttons, text="➕ Зажать ЛКМ", command=lambda: self.add_idle_action("mouse_down")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(idle_buttons, text="➕ Отпустить ЛКМ", command=lambda: self.add_idle_action("mouse_up")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(idle_buttons, text="➕ Пауза", command=lambda: self.add_idle_action("wait")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(idle_buttons, text="➕ Клавиша", command=self.add_idle_key_action).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(idle_buttons, text="🗑️  Удалить", command=self.remove_idle_action).pack(side=tk.LEFT, padx=(0, 20))

        self.idle_delay_var = tk.DoubleVar(value=2.0)
        ttk.Label(idle_buttons, text="Интервал:").pack(side=tk.LEFT)
        ttk.Spinbox(idle_buttons, from_=0.5, to=60.0, increment=0.5,
                    textvariable=self.idle_delay_var, width=6).pack(side=tk.LEFT)

        self.idle_actions_listbox = tk.Listbox(idle_section, height=3, font=("Consolas", 10), exportselection=False)
        self.idle_actions_listbox.pack(fill=tk.X)

        self.idle_actions = []

    # ==================== ЯДРО: SAVE / LOAD ====================
    def _sync_ui_to_scenario(self):
        """Сохранить текущие значения из UI в выбранный сценарий"""
        idx = self.selected_scenario_idx
        if idx is None or idx >= len(self.scenarios):
            return

        scenario = self.scenarios[idx]
        scenario['name'] = self.scenario_name_var.get()
        scenario['enabled'] = self.enabled_var.get()
        scenario['repeat'] = self.repeat_var.get()
        scenario['delay'] = self.delay_var.get()
        scenario['trigger']['type'] = self.trigger_type_var.get()
        scenario['trigger']['threshold'] = self.threshold_var.get()

        # Шаблоны
        if scenario.get('templates'):
            scenario['trigger']['template'] = scenario['templates'][0]
            scenario['trigger']['templates'] = scenario['templates']
        elif self.template_path_var.get():
            scenario['trigger']['template'] = self.template_path_var.get()
            scenario['trigger']['templates'] = [self.template_path_var.get()]

        # Область поиска
        sa_text = self.search_area_var.get()
        if sa_text != "Весь экран":
            try:
                coords = sa_text.strip('()').split(',')
                x, y = int(coords[0].strip()), int(coords[1].strip())
                wh = coords[2].strip().split('x')
                w, h = int(wh[0]), int(wh[1])
                scenario['trigger']['search_area'] = [x, y, w, h]
            except:
                pass

    def _load_scenario_to_ui(self, idx):
        """Загрузить данные сценария по индексу в UI"""
        if idx is None or idx >= len(self.scenarios):
            return

        scenario = self.scenarios[idx]
        trigger = scenario.get('trigger', {})
        actions = scenario.get('actions', [])

        self._updating_threshold = True
        self.scenario_name_var.set(scenario.get('name', ''))
        self.enabled_var.set(scenario.get('enabled', True))
        self.repeat_var.set(scenario.get('repeat', True))
        self.delay_var.set(scenario.get('delay', 1.0))
        self.trigger_type_var.set(trigger.get('type', 'template'))
        self.threshold_var.set(trigger.get('threshold', 0.70))

        templates = trigger.get('templates', [])
        if not templates and trigger.get('template'):
            tpl = trigger['template']
            templates = [tpl] if isinstance(tpl, str) else tpl
        scenario['templates'] = templates

        self.template_path_var.set(templates[0] if templates else '')
        self._updating_threshold = False

        sa = trigger.get('search_area', [0, 0, 0, 0])
        self.search_area_var.set(f"({sa[0]}, {sa[1]}, {sa[2]}x{sa[3]})" if sum(sa) > 0 else "Весь экран")

        self.refresh_templates_list()
        self.actions_listbox.delete(0, tk.END)
        for i, action in enumerate(actions):
            self.actions_listbox.insert(tk.END, f"{i+1}. {self._action_to_string(action)}")

    def on_scenario_selected(self, event=None):
        """Обработчик выбора сценария в списке"""
        sel = self.scenario_listbox.curselection()
        if not sel:
            return

        new_idx = sel[0]
        old_idx = self.selected_scenario_idx

        # Если переключились на другой сценарий -> сохраняем старый
        if old_idx is not None and old_idx != new_idx:
            self._sync_ui_to_scenario()

        self.selected_scenario_idx = new_idx
        self._load_scenario_to_ui(new_idx)

    def refresh_scenario_list(self, sync=True):
        """Только перерисовывает список. НЕ вызывает sync."""
        self.scenario_listbox.delete(0, tk.END)
        for s in self.scenarios:
            status = "✅" if s.get('enabled', True) else "❌"
            self.scenario_listbox.insert(tk.END, f"{status} {s['name']}")

        if self.selected_scenario_idx is not None and self.selected_scenario_idx < len(self.scenarios):
            self.scenario_listbox.selection_set(self.selected_scenario_idx)

    # ==================== УПРАВЛЕНИЕ СЦЕНАРИЯМИ ====================
    def add_scenario(self):
        self._sync_ui_to_scenario()  # Сохраняем текущее

        scenario = {
            'name': f'Сценарий_{len(self.scenarios) + 1}',
            'enabled': True,
            'trigger': {'type': 'template', 'template': '', 'threshold': 0.70, 'search_area': [0, 0, 0, 0]},
            'actions': [],
            'repeat': True,
            'delay': 1.0
        }
        self.scenarios.append(scenario)
        new_idx = len(self.scenarios) - 1

        self.refresh_scenario_list(sync=False)
        self.scenario_listbox.selection_set(new_idx)
        # on_scenario_selected сработает автоматически через <<ListboxSelect>>

    def delete_scenario(self):
        self._sync_ui_to_scenario()
        idx = self.selected_scenario_idx
        if idx is None or idx >= len(self.scenarios):
            messagebox.showwarning("Нет выбора", "Сначала выбери сценарий из списка!")
            return

        if messagebox.askyesno("Удалить", f"Удалить '{self.scenarios[idx]['name']}'?"):
            self.scenarios.pop(idx)
            self.selected_scenario_idx = None
            self.refresh_scenario_list(sync=False)

            if self.scenarios:
                self.scenario_listbox.selection_set(0)
            else:
                # Очистка UI если сценариев не осталось
                self.scenario_name_var.set('')
                self.enabled_var.set(True)
                self.repeat_var.set(True)
                self.delay_var.set(1.0)
                self.trigger_type_var.set('template')
                self.threshold_var.set(0.70)
                self.template_path_var.set('')
                self.search_area_var.set('Весь экран')
                self.templates_listbox.delete(0, tk.END)
                self.actions_listbox.delete(0, tk.END)

    # ==================== ШАБЛОНЫ ====================
    def add_template(self):
        sel = self.scenario_listbox.curselection()
        if not sel: return messagebox.showwarning("Нет выбора", "Сначала выбери сценарий!")
        path = filedialog.askopenfilename(title="Выбери шаблон", filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp"), ("All", "*.*")])
        if path:
            scenario = self.scenarios[sel[0]]
            scenario.setdefault('templates', []).append(path)
            self.refresh_templates_list()

    def remove_template(self):
        sel_tpl = self.templates_listbox.curselection()
        sel_scn = self.scenario_listbox.curselection()
        if not sel_scn or not sel_tpl: return messagebox.showwarning("Нет выбора", "Выбери сценарий и шаблон!")
        self.scenarios[sel_scn[0]]['templates'].pop(sel_tpl[0])
        self.refresh_templates_list()

    def move_template_up(self):
        sel = self.templates_listbox.curselection()
        sel_scn = self.scenario_listbox.curselection()
        if not sel_scn or not sel or sel[0] == 0: return
        idx = sel[0]
        tpl_list = self.scenarios[sel_scn[0]]['templates']
        tpl_list[idx], tpl_list[idx-1] = tpl_list[idx-1], tpl_list[idx]
        self.templates_listbox.selection_set(idx - 1)
        self.refresh_templates_list()

    def move_template_down(self):
        sel = self.templates_listbox.curselection()
        sel_scn = self.scenario_listbox.curselection()
        if not sel_scn or not sel: return
        idx = sel[0]
        tpl_list = self.scenarios[sel_scn[0]]['templates']
        if idx >= len(tpl_list) - 1: return
        tpl_list[idx], tpl_list[idx+1] = tpl_list[idx+1], tpl_list[idx]
        self.templates_listbox.selection_set(idx + 1)
        self.refresh_templates_list()

    def refresh_templates_list(self):
        self.templates_listbox.delete(0, tk.END)
        sel = self.scenario_listbox.curselection()
        if not sel: return
        templates = self.scenarios[sel[0]].get('templates', [])
        for i, tpl in enumerate(templates):
            self.templates_listbox.insert(tk.END, f"{i+1}. {os.path.basename(tpl)}")
        if templates:
            self.template_path_var.set(templates[0])

    # ==================== ДЕЙСТВИЯ ====================
    def _action_to_string(self, action):
        t = action.get('type', 'unknown')
        if t == 'mouse_move': return f"🖱️  Движение ({action.get('x', 0.5):.3f}, {action.get('y', 0.5):.3f})"
        if t == 'mouse_click': return "🖱️  Клик ЛКМ"
        if t == 'mouse_right_click': return "🖱️  Клик ПКМ"
        if t == 'mouse_down': return f"🖱️  Зажать {'ПКМ' if action.get('button')=='right' else 'ЛКМ'}"
        if t == 'mouse_up': return f"🖱️  Отпустить {'ПКМ' if action.get('button')=='right' else 'ЛКМ'}"
        if t == 'key_press': return f"⌨️  Нажать '{action.get('key', '')}'"
        if t == 'key_down': return f"⌨️  Зажать '{action.get('key', '')}'"
        if t == 'key_up': return f"⌨️  Отпустить '{action.get('key', '')}'"
        if t == 'key_combo': return f"⌨️  Комбинация: {'+'.join(action.get('keys', []))}"
        if t == 'wait': return f"⏱️  Пауза {action.get('duration', 0.5)}с"
        return f"❓ {t}"

    def add_action(self, action_type, button=None):
        sel = self.scenario_listbox.curselection()
        if not sel: return messagebox.showwarning("Нет выбора", "Сначала выбери сценарий!")
        scenario = self.scenarios[sel[0]]
        actions = scenario.setdefault('actions', [])

        if action_type == 'mouse_move':
            self.main_window.update_status("🖱️  Перемести мышь и нажми ЛКМ...")
            self.main_window.root.config(cursor="crosshair")
            def capture():
                try:
                    import mouse, pyautogui, win32api
                    mouse.wait(button='left')
                    x, y = pyautogui.position()
                    sw, sh = win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1)
                    actions.append({'type': 'mouse_move', 'x': round(max(0, min(1, x/sw)), 3), 'y': round(max(0, min(1, y/sh)), 3), 'duration': 0.1})
                    self.main_window.root.config(cursor="")
                    self._load_scenario_to_ui(sel[0])
                except Exception as e:
                    self.main_window.update_status(f"❌ Ошибка: {e}")
                    self.main_window.root.config(cursor="")
            threading.Thread(target=capture, daemon=True).start()
        elif action_type in ('mouse_click', 'mouse_right_click'):
            actions.append({'type': action_type})
        elif action_type in ('mouse_down', 'mouse_up'):
            b = button or simpledialog.askstring("Кнопка", "left/right/middle?", initialvalue="left")
            if b: actions.append({'type': action_type, 'button': b})
        elif action_type in ('key_press', 'key_down', 'key_up'):
            key = simpledialog.askstring("Клавиша", "Введите клавишу:")
            if key:
                key = key.strip().upper() if key.lower().startswith('f') and key[1:].isdigit() else key.lower()
                actions.append({'type': action_type, 'key': key})
        elif action_type == 'key_combo':
            combo = simpledialog.askstring("Комбинация", "Введите через + (например: ctrl+shift+p):")
            if combo:
                keys = [k.strip().upper() if k.strip().lower().startswith('f') else k.strip().lower() for k in combo.split('+')]
                actions.append({'type': action_type, 'keys': keys})
        elif action_type == 'wait':
            actions.append({'type': 'wait', 'duration': 0.5})

        self._load_scenario_to_ui(sel[0])

    def delete_action(self):
        idx = self.selected_scenario_idx
        if idx is None or idx >= len(self.scenarios): return messagebox.showwarning("Нет выбора", "Выбери сценарий!")
        sel_act = self.actions_listbox.curselection()
        if not sel_act: return messagebox.showwarning("Нет выбора", "Выбери действие!")
        self.scenarios[idx]['actions'].pop(sel_act[0])
        self._load_scenario_to_ui(idx)

    def _on_threshold_change(self, *args):
        if getattr(self, '_updating_threshold', False): return
        self._sync_ui_to_scenario()

    # ==================== IDLE ДЕЙСТВИЯ ====================
    def add_idle_action(self, action_type):
        if action_type == 'wait': self.idle_actions.append({'type': 'wait', 'duration': 1.0})
        elif action_type == 'mouse_down': self.idle_actions.append({'type': 'mouse_down', 'button': 'left'})
        elif action_type == 'mouse_up': self.idle_actions.append({'type': 'mouse_up', 'button': 'left'})
        else: self.idle_actions.append({'type': action_type, 'button': 'left' if action_type=='mouse_click' else 'right'})
        self.refresh_idle_actions_list()

    def add_idle_mouse_move(self):
        self.main_window.update_status("🖱️  Перемести мышь и нажми ЛКМ...")
        self.main_window.root.config(cursor="crosshair")
        def capture():
            try:
                import mouse, pyautogui, win32api
                mouse.wait(button='left')
                x, y = pyautogui.position()
                sw, sh = win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1)
                self.idle_actions.append({'type': 'mouse_move', 'x': round(max(0, min(1, x/sw)), 3), 'y': round(max(0, min(1, y/sh)), 3), 'duration': 0.1})
                self.main_window.root.config(cursor="")
                self.refresh_idle_actions_list()
            except Exception as e:
                self.main_window.update_status(f"❌ Ошибка: {e}")
                self.main_window.root.config(cursor="")
        threading.Thread(target=capture, daemon=True).start()

    def add_idle_key_action(self):
        key = simpledialog.askstring("Клавиша", "Введите клавишу:")
        if key:
            key = key.strip().upper() if key.lower().startswith('f') else key.lower()
            self.idle_actions.append({'type': 'key_press', 'key': key})
            self.refresh_idle_actions_list()

    def remove_idle_action(self):
        sel = self.idle_actions_listbox.curselection()
        if not sel: return messagebox.showwarning("Нет выбора", "Выбери действие!")
        self.idle_actions.pop(sel[0])
        self.refresh_idle_actions_list()

    def refresh_idle_actions_list(self):
        self.idle_actions_listbox.delete(0, tk.END)
        for i, a in enumerate(self.idle_actions):
            t = a['type']
            if t == 'mouse_click': d = "🖱️  Клик ЛКМ"
            elif t == 'mouse_right_click': d = "🖱️  Клик ПКМ"
            elif t == 'mouse_move': d = f"🖱️  Движение ({a.get('x', 0.5):.3f}, {a.get('y', 0.5):.3f})"
            elif t == 'mouse_down': d = "🖱️  Зажать ЛКМ"
            elif t == 'mouse_up': d = "🖱️  Отпустить ЛКМ"
            elif t == 'key_press': d = f"⌨️  Нажать {a.get('key', '?')}"
            elif t == 'wait': d = f"⏱️  Пауза {a.get('duration', 1.0)}с"
            else: d = t
            self.idle_actions_listbox.insert(tk.END, f"{i+1}. {d}")

    # ==================== ВЗАИМОДЕЙСТВИЕ С ЭКРАНОМ ====================
    def browse_template(self):
        path = filedialog.askopenfilename(title="Выбери шаблон", filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp"), ("All", "*.*")])
        if path:
            self.template_path_var.set(path)
            sel = self.scenario_listbox.curselection()
            if sel:
                self.scenarios[sel[0]].setdefault('templates', []).append(path)
                self.refresh_templates_list()

    def capture_template(self):
        self.main_window.update_status("📸 Выдели область портала...")
        def on_area_selected(area):
            left, top, width, height = area
            from PIL import ImageGrab
            import datetime
            os.makedirs("templates", exist_ok=True)
            name = self.scenario_name_var.get().strip() or "template"
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            def transliterate(text):
                m = {'А':'A','Б':'B','В':'V','Г':'G','Д':'D','Е':'E','Ё':'Yo','Ж':'Zh','З':'Z','И':'I','Й':'Y','К':'K','Л':'L','М':'M','Н':'N','О':'O','П':'P','Р':'R','С':'S','Т':'T','У':'U','Ф':'F','Х':'Kh','Ц':'Ts','Ч':'Ch','Ш':'Sh','Щ':'Sch','Ъ':'','Ы':'Y','Ь':'','Э':'E','Ю':'Yu','Я':'Ya','а':'a','б':'b','в':'v','г':'g','д':'d','е':'e','ё':'yo','ж':'zh','з':'z','и':'i','й':'y','к':'k','л':'l','м':'m','н':'n','о':'o','п':'p','р':'r','с':'s','т':'t','у':'u','ф':'f','х':'kh','ц':'ts','ч':'ch','ш':'sh','щ':'sch','ъ':'','ы':'y','ь':'','э':'e','ю':'yu','я':'ya',' ':'_','-':'_'}
                r = ''.join(m.get(c, c) for c in text)
                while '__' in r: r = r.replace('__', '_')
                return r.strip('_')
            save_path = f"templates/{transliterate(f'{name}_{ts}')}_trigger.png"
            ImageGrab.grab(bbox=(left, top, left+width, top+height)).save(save_path)
            self.template_path_var.set(save_path)
            sel = self.scenario_listbox.curselection()
            if sel:
                self.scenarios[sel[0]].setdefault('templates', []).append(save_path)
                self.refresh_templates_list()
            self.main_window.update_status(f"✅ Шаблон сохранён: {save_path}")
        self.main_window.define_ocr_area(on_area_selected)

    def select_search_area(self):
        self.main_window.update_status("📏 Выдели область поиска...")
        def on_area_selected(area):
            left, top, width, height = area
            sel = self.scenario_listbox.curselection()
            if sel:
                self.scenarios[sel[0]]['trigger']['search_area'] = [left, top, width, height]
                self.search_area_var.set(f"({left}, {top}, {width}x{height})")
            self.main_window.update_status(f"✅ Область поиска задана")
        self.main_window.define_ocr_area(on_area_selected)

    def test_trigger(self):
        sel = self.scenario_listbox.curselection()
        if not sel: return messagebox.showwarning("Нет выбора", "Выбери сценарий!")
        self._sync_ui_to_scenario()
        trigger = self.scenarios[sel[0]].get('trigger', {})
        engine = ScenarioEngine()
        res = engine._check_trigger(trigger)
        if res['found']:
            messagebox.showinfo("✅ Триггер сработал!", f"Совпадение: {res['confidence']:.1%}\nПозиция: ({res['screen_x']}, {res['screen_y']})")
        else:
            messagebox.showwarning("❌ Не сработал", f"Лучшее: {res.get('best_match', 0):.1%}")

    # ==================== СОХРАНЕНИЕ / ЗАГРУЗКА / ЗАПУСК ====================
    def save_scenarios(self):
        self._sync_ui_to_scenario()
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if path:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump({'scenarios': self.scenarios, 'idle_actions': self.idle_actions, 'idle_delay': self.idle_delay_var.get()}, f, indent=2, ensure_ascii=False)
            messagebox.showinfo("✅ Сохранено", f"Сценарии сохранены:\n{path}")

    def load_scenarios_file(self):
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if not path: return
        try:
            with open(path, 'r', encoding='utf-8') as f: data = json.load(f)
            if isinstance(data, dict):
                self.scenarios = data.get('scenarios', [])
                self.idle_actions = data.get('idle_actions', [])
                self.idle_delay_var.set(data.get('idle_delay', 2.0))
            elif isinstance(data, list):
                self.scenarios = data
            for s in self.scenarios:
                if 'steps' in s:
                    if s['steps']:
                        s['trigger'] = s['steps'][0].get('trigger', {})
                        s['actions'] = s['steps'][0].get('actions', [])
                    del s['steps']
                s['enabled'] = True
                if not s.get('name', '').strip(): s['name'] = 'Сценарий'
            self.selected_scenario_idx = None
            self.refresh_scenario_list(sync=False)
            self.refresh_idle_actions_list()
            if self.scenarios:
                self.scenario_listbox.selection_set(0)
            messagebox.showinfo("✅ Загружено", f"Загружено {len(self.scenarios)} сценариев")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки: {e}")

    def start_bot(self):
        if not self.scenarios: return messagebox.showwarning("Нет сценариев", "Сначала создай сценарий!")
        self._sync_ui_to_scenario()
        for s in self.scenarios:
            if 'steps' in s: del s['steps']
            s['enabled'] = True
        self.engine = ScenarioEngine()
        self.engine.load_scenarios(self.scenarios)
        self.engine.idle_actions = self.idle_actions
        self.engine.idle_delay = self.idle_delay_var.get()
        self.is_running = True
        self.btn_start.config(state=tk.DISABLED); self.btn_run_once.config(state=tk.DISABLED); self.btn_stop.config(state=tk.NORMAL)
        self.status_var.set("▶️  Бот работает (цикл)...")
        self.engine.start(self.update_status)

    def run_once(self):
        if not self.scenarios: return messagebox.showwarning("Нет сценариев", "Сначала создай сценарий!")
        self._sync_ui_to_scenario()
        for s in self.scenarios:
            if 'steps' in s: del s['steps']
            s['enabled'] = True
            s['repeat'] = False
        self.engine = ScenarioEngine()
        self.engine.load_scenarios(self.scenarios)
        self.engine.idle_actions = self.idle_actions
        self.engine.idle_delay = self.idle_delay_var.get()
        self.is_running = True
        self.btn_start.config(state=tk.DISABLED); self.btn_run_once.config(state=tk.DISABLED); self.btn_stop.config(state=tk.NORMAL)
        self.status_var.set("🚀 Бот работает (один раз)...")
        self.engine.start(self.update_status)

    def stop_bot(self):
        if self.engine: self.engine.stop()
        self.is_running = False
        self.btn_start.config(state=tk.NORMAL); self.btn_run_once.config(state=tk.NORMAL); self.btn_stop.config(state=tk.DISABLED)
        self.status_var.set("⏹️  Бот остановлен")

    def update_status(self, message):
        self.status_var.set(f"▶️  {message}")


if __name__ == "__main__":
    print("Scenario Editor — используйте через главное приложение")
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import os
import sys
import threading
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item
from core.logger import logger # logger 임포트 추가

# Appearance Settings
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class AgentGUI:
    def __init__(self, config_manager=None):
        print(">>> Modern GUI 초기화 시작...")
        self.config = config_manager
        self.root = ctk.CTk()
        self.root.withdraw() # 일단 숨겨서 초기 깜빡임 방지
        self.root.title("School-Doc Genie Agent v1.0")
        self.root.geometry("1000x700")
        self.root.protocol('WM_DELETE_WINDOW', self._on_closing)

        # State
        self.is_monitoring = False
        self.batch_files = []
        
        # Tray Icon Setup (Python 3.13 호환성 문제로 임시 비활성화)
        self.tray_icon = None

        # UI Components
        self._build_sidebar()
        self._build_main_view()
        self._build_history_view()
        self._build_settings_view()
        
        # Default view
        self.show_view("main")

        # 모든 컴포넌트 배치 완료 후 부드럽게 표시
        self.root.after(10, self.root.deiconify)
        self.root.after(20, self.root.focus_force)

    def _setup_dnd(self):
        try:
            import windnd
            def on_drop(filenames):
                try:
                    # filenames는 byte 문자열의 리스트로 올 수 있으므로 디코딩 필요
                    files = [f.decode('cp949') if isinstance(f, bytes) else f for f in filenames]
                    
                    # UI 업데이트는 반드시 메인 스레드에서 thread-safe하게 실행
                    self.root.after(0, lambda: self._handle_drop_ui(files))
                except Exception as e:
                    logger.error(f"Drop handling error: {e}")
            
            # windnd 라이브러리는 버전에 따라 함수명이 다를 수 있음
            hook_success = False
            for func_name in ['hook_dropfiles', 'hook_dropfile', 'hook']:
                if hasattr(windnd, func_name):
                    try:
                        getattr(windnd, func_name)(self.root, on_drop)
                        logger.info(f"DnD hooked via windnd.{func_name}")
                        hook_success = True
                        break
                    except Exception as e:
                        logger.error(f"windnd.{func_name} failed: {e}")
            
            if not hook_success:
                logger.error("windnd 모듈에서 작동하는 hook 함수를 찾을 수 없습니다.")
        except ImportError:
            print(">>> windnd 라이브러리가 없어 드래그 앤 드롭을 지원하지 않습니다.")
        except Exception as e:
            print(f">>> DnD 설정 중 오류: {e}")

    def _setup_tray(self):
        try:
            def create_image():
                # 간단한 아이콘 생성
                width, height = 64, 64
                image = Image.new('RGB', (width, height), (30, 136, 229))
                dc = ImageDraw.Draw(image)
                dc.text((20, 15), "G", fill="white")
                return image

            def run_tray_icon():
                # Python 3.13에서는 스레드 내부에서의 GIL 관리가 더욱 중요함
                try:
                    self.tray_icon.run()
                except Exception as e:
                    logger.error(f"Tray icon thread error: {e}")

            menu = (item('열기', self._show_window), item('종료', self._exit_app))
            self.tray_icon = pystray.Icon("school_doc_genie", create_image(), "School-Doc Genie", menu)
            
            # 별도 데몬 스레드에서 실행
            tray_thread = threading.Thread(target=run_tray_icon, daemon=True)
            tray_thread.start()
            logger.info("Tray icon started in background thread.")
        except Exception as e:
            logger.error(f"Failed to setup tray: {e}")

    def _show_window(self):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def _handle_drop_ui(self, files):
        """드롭된 파일들을 UI 목록에 추가 (Thread-safe)"""
        self.batch_files.extend(files)
        self._update_batch_list()
        self.show_view("main")

    def _on_closing(self):
        # Tray Icon 비활성화로 인해 창 닫기 = 프로그램 종료
        self._exit_app()

    def _exit_app(self):
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.destroy()
        sys.exit(0)

    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self.root, width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        
        ctk.CTkLabel(self.sidebar, text="School-Doc", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)
        
        self.btn_main = ctk.CTkButton(self.sidebar, text="📂 문서 분석", command=lambda: self.show_view("main"), corner_radius=10)
        self.btn_main.pack(pady=10, padx=20)
        
        self.btn_history = ctk.CTkButton(self.sidebar, text="📜 분석 기록", command=lambda: self.show_view("history"), corner_radius=10)
        self.btn_history.pack(pady=10, padx=20)

        # 비교 대상 저장용
        self.selected_comparison = []
        
        self.btn_settings = ctk.CTkButton(self.sidebar, text="⚙️ 환경 설정", command=lambda: self.show_view("settings"), corner_radius=10)
        self.btn_settings.pack(pady=10, padx=20)
        
        ctk.CTkLabel(self.sidebar, text="v1.0 Premium", font=ctk.CTkFont(size=10)).pack(side="bottom", pady=20)

    def _build_main_view(self):
        self.view_main = ctk.CTkFrame(self.root, corner_radius=0, fg_color="transparent")
        
        # Header & Engine Selector
        header_frame = ctk.CTkFrame(self.view_main, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(30, 0))
        
        ctk.CTkLabel(header_frame, text="실시간 문서 분석", font=ctk.CTkFont(size=24, weight="bold")).pack(side="left")
        
        # UI 초기값 설정 (단순 로드)
        # self._sync_engine_ui() - 삭제

        # Batch Area
        self.batch_frame = ctk.CTkFrame(self.view_main, corner_radius=15)
        self.batch_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        self.batch_list_container = ctk.CTkScrollableFrame(self.batch_frame, height=200)
        self.batch_list_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 안내 문구 (파일이 없을 때 표시)
        self.empty_label = ctk.CTkLabel(self.batch_list_container, 
                                        text="분석할 파일을 드래그하거나 [파일 추가] 버튼을 눌러주세요.\n현재 일괄 처리 및 폴더 감시 모드를 지원합니다.",
                                        text_color="gray")
        self.empty_label.pack(pady=50)

        # Action Buttons
        btn_box = ctk.CTkFrame(self.view_main, fg_color="transparent")
        btn_box.pack(fill="x", padx=30, pady=(0, 30))
        
        ctk.CTkButton(btn_box, text="➕ 파일 추가", command=self._add_files_to_batch, width=150, fg_color="#2ecc71", hover_color="#27ae60").pack(side="left", padx=10)
        ctk.CTkButton(btn_box, text="🚀 일괄 분석 시작", command=self._start_batch_analysis, width=200).pack(side="right", padx=10)
        
        self.monitor_btn = ctk.CTkButton(btn_box, text="👁️ 폴더 감시 시작", command=self._toggle_monitor, width=150, fg_color="#f39c12", hover_color="#e67e22")
        self.monitor_btn.pack(side="right", padx=10)

        # Progress Area (Hidden by default)
        self.progress_frame = ctk.CTkFrame(self.view_main, fg_color="transparent")
        self.progress_frame.pack(fill="x", padx=40, pady=(0, 20))
        
        self.progress_label = ctk.CTkLabel(self.progress_frame, text="", font=ctk.CTkFont(size=12))
        self.progress_label.pack(anchor="w")
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, width=800)
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", pady=5)
        self.progress_bar.pack_forget() # Initially hidden

    def _build_history_view(self):
        self.view_history = ctk.CTkFrame(self.root, corner_radius=0, fg_color="transparent")
        
        header = ctk.CTkFrame(self.view_history, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(30, 10))
        
        ctk.CTkLabel(header, text="분석 아카이브", font=ctk.CTkFont(size=24, weight="bold")).pack(side="left")
        
        # Search & Compare Buttons
        btn_row = ctk.CTkFrame(header, fg_color="transparent")
        btn_row.pack(side="right")
        
        self.btn_compare = ctk.CTkButton(btn_row, text="⚖️ 문서 비교 (0/2)", width=120, fg_color="#e74c3c", command=self._start_comparison)
        self.btn_compare.pack(side="left", padx=5)

        self.search_entry = ctk.CTkEntry(btn_row, placeholder_text="📄 검색...", width=200)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", lambda e: self._refresh_history_ui())

        self.history_container = ctk.CTkScrollableFrame(self.view_history, corner_radius=15)
        self.history_container.pack(fill="both", expand=True, padx=30, pady=(0, 30))

    def _build_settings_view(self):
        self.view_settings = ctk.CTkFrame(self.root, corner_radius=0, fg_color="transparent")
        ctk.CTkLabel(self.view_settings, text="시스템 설정", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=30, padx=30, anchor="w")
        
        s_container = ctk.CTkScrollableFrame(self.view_settings, corner_radius=15)
        s_container.pack(fill="both", expand=True, padx=30, pady=(0, 30))

        # AI Provider Choice
        ctk.CTkLabel(s_container, text="AI 분석 엔진 선택", font=ctk.CTkFont(weight="bold")).pack(pady=(10, 5), anchor="w", padx=20)
        self.ai_provider = ctk.CTkSegmentedButton(s_container, values=["Gemini 3.0 Flash", "Ollama (Local)"], command=self._on_provider_change)
        self.ai_provider.pack(fill="x", padx=20, pady=5)
        
        # Settings Content Container (to maintain fixed order)
        self.settings_content_frame = ctk.CTkFrame(s_container, fg_color="transparent")
        self.settings_content_frame.pack(fill="x", padx=20, pady=10)

        # Gemini Settings
        self.gemini_frame = ctk.CTkFrame(self.settings_content_frame, fg_color="transparent")
        ctk.CTkLabel(self.gemini_frame, text="Gemini API Key").pack(anchor="w")
        self.entry_api_key = ctk.CTkEntry(self.gemini_frame, placeholder_text="API Key를 입력하세요", show="*", width=400)
        self.entry_api_key.pack(fill="x", pady=5)
        
        # Ollama Settings
        self.ollama_frame = ctk.CTkFrame(self.settings_content_frame, fg_color="transparent")
        ctk.CTkLabel(self.ollama_frame, text="Ollama Server URL").pack(anchor="w")
        self.entry_ollama_url = ctk.CTkEntry(self.ollama_frame, placeholder_text="http://localhost:11434")
        self.entry_ollama_url.pack(fill="x", pady=5)
        ctk.CTkLabel(self.ollama_frame, text="Model Name").pack(anchor="w")
        self.entry_ollama_model = ctk.CTkEntry(self.ollama_frame, placeholder_text="llama3")
        self.entry_ollama_model.pack(fill="x", pady=5)

        # Monitor Settings
        ctk.CTkLabel(s_container, text="자동 감시 폴더 설정", font=ctk.CTkFont(weight="bold")).pack(pady=(20, 5), anchor="w", padx=20)
        monitor_box = ctk.CTkFrame(s_container, fg_color="transparent")
        monitor_box.pack(fill="x", padx=20, pady=5)
        self.entry_monitor_path = ctk.CTkEntry(monitor_box, placeholder_text="분석할 폴더를 선택하세요")
        self.entry_monitor_path.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkButton(monitor_box, text="찾기", width=80, command=self._browse_monitor_folder).pack(side="right")

        # Save Button
        ctk.CTkButton(s_container, text="설정 저장 및 적용", command=self._save_all_settings).pack(pady=30)

        # Load current state
        self._load_settings_into_ui()

    def show_view(self, view_name):
        for v in [self.view_main, self.view_history, self.view_settings]:
            v.pack_forget()
        
        if view_name == "main":
            self.view_main.pack(fill="both", expand=True)
        elif view_name == "history":
            self.view_history.pack(fill="both", expand=True)
            self._refresh_history_ui()
        elif view_name == "settings":
            self.view_settings.pack(fill="both", expand=True)

    def _load_settings_into_ui(self):
        if not self.config: return
        
        # 레거시 이름 호환성 처리
        current_provider = self.config.get_config("ai_provider", "Gemini 3.0 Flash")
        if current_provider == "Gemini API":
            current_provider = "Gemini 3.0 Flash"
            
        self.ai_provider.set(current_provider)
        self._on_provider_change(current_provider)
        
        self.entry_api_key.insert(0, self.config.get_api_key() or "")
        self.entry_ollama_url.insert(0, self.config.get_config("ollama_url", "http://localhost:11434"))
        self.entry_ollama_model.insert(0, self.config.get_config("ollama_model", "exaone3.5:2.4b"))
        self.entry_monitor_path.insert(0, self.config.get_config("monitor_folder", ""))

    def _on_provider_change(self, value):
        # UI 순서와 가시성을 완벽하게 제어
        if "Gemini" in value:
            self.ollama_frame.pack_forget()
            self.gemini_frame.pack(fill="x")
        else:
            self.gemini_frame.pack_forget()
            self.ollama_frame.pack(fill="x")

    def _save_all_settings(self):
        if not self.config: return
        self.config.set_api_key(self.entry_api_key.get().strip())
        self.config.set_config("ai_provider", self.ai_provider.get())
        self.config.set_config("ollama_url", self.entry_ollama_url.get().strip())
        
        # 모델명 안전 처리 (사용자 실수 방지)
        raw_model = self.entry_ollama_model.get().strip()
        # exaone3.5.2.4b -> exaone3.5:2.4b 자동 보정
        if "exaone" in raw_model.lower() and ":" not in raw_model and raw_model.count(".") >= 2:
            fixed_model = raw_model.replace("3.5.", "3.5:")
            logger.info(f"Auto-corrected model name: {raw_model} -> {fixed_model}")
            raw_model = fixed_model
            # UI에도 반영
            self.entry_ollama_model.delete(0, tk.END)
            self.entry_ollama_model.insert(0, raw_model)
            
        self.config.set_config("ollama_model", raw_model)
        self.config.set_config("monitor_folder", self.entry_monitor_path.get().strip())
        
        self.root.focus_set() # 저장 후 포커스 해제
        
        selected_p = self.ai_provider.get()
        display_model = "Gemini 3.0 Flash" if "Gemini" in selected_p else raw_model
        messagebox.showinfo("성공", f"설정이 저장되었습니다.\n엔진: {selected_p}\n모델: {display_model}")

    def _browse_monitor_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.entry_monitor_path.delete(0, tk.END)
            self.entry_monitor_path.insert(0, path)

    def _add_files_to_batch(self):
        files = filedialog.askopenfilenames(title="분석할 파일 선택")
        if files:
            self.batch_files.extend(files)
            self._update_batch_list()

    def _update_batch_list(self):
        # 기존 리스트 클리어
        for widget in self.batch_list_container.winfo_children():
            widget.destroy()
            
        if not self.batch_files:
            self.empty_label = ctk.CTkLabel(self.batch_list_container, 
                                            text="분석할 파일을 드래그하거나 [파일 추가] 버튼을 눌러주세요.\n현재 일괄 처리 및 폴더 감시 모드를 지원합니다.",
                                            text_color="gray")
            self.empty_label.pack(pady=50)
            return

        for i, f in enumerate(self.batch_files):
            row = ctk.CTkFrame(self.batch_list_container, fg_color="transparent")
            row.pack(fill="x", pady=2)
            
            # 파일명
            ctk.CTkLabel(row, text=f"• {os.path.basename(f)}", anchor="w").pack(side="left", padx=10, fill="x", expand=True)
            
            # 삭제 버튼
            remove_btn = ctk.CTkButton(row, text="✕", width=30, height=24, 
                                        fg_color="#e74c3c", hover_color="#c0392b",
                                        command=lambda idx=i: self._remove_from_batch(idx))
            remove_btn.pack(side="right", padx=10)

    def _remove_from_batch(self, index):
        if 0 <= index < len(self.batch_files):
            del self.batch_files[index]
            self._update_batch_list()

    def _start_batch_analysis(self):
        if not self.batch_files:
            messagebox.showwarning("알림", "분석할 파일을 먼저 추가해 주세요.")
            return
        # handler is injected from agent_main.py
        if hasattr(self, 'batch_handler'):
            self.batch_handler(self.batch_files)
            self.batch_files = []
            self._update_batch_list()

    def _toggle_monitor(self):
        if self.is_monitoring:
            if hasattr(self, 'monitor_stop_handler'):
                self.monitor_stop_handler()
            self.monitor_btn.configure(text="👁️ 폴더 감시 시작", fg_color="#f39c12")
            self.is_monitoring = False
        else:
            path = self.entry_monitor_path.get().strip()
            if not path or not os.path.exists(path):
                messagebox.showwarning("경고", "올바른 감시 폴더를 설정해 주세요.")
                return
            if hasattr(self, 'monitor_start_handler'):
                self.monitor_start_handler(path)
            self.monitor_btn.configure(text="🛑 감시 중지", fg_color="#e74c3c")
            self.is_monitoring = True

    def _refresh_history_ui(self):
        for widget in self.history_container.winfo_children():
            widget.destroy()
        
        if hasattr(self, 'history_fetcher'):
            data = self.history_fetcher()
            query = self.search_entry.get().lower()
            
            for item in data:
                title = item.get("analysis", {}).get("title", "").lower()
                filename = item.get("filename", "").lower()
                
                if query in title or query in filename:
                    self._create_history_card(item)

    def _create_history_card(self, item):
        card = ctk.CTkFrame(self.history_container, corner_radius=10)
        card.pack(fill="x", padx=10, pady=5)
        
        # 1. 상세 보기 버튼을 오른쪽에 배치
        btn_detail = ctk.CTkButton(card, text="상세 보기", width=80, command=lambda: self._show_record_detail(item))
        btn_detail.pack(side="right", padx=(5, 15), pady=10)

        # 2. 삭제 버튼 (X)
        btn_delete = ctk.CTkButton(card, text="✕", width=30, height=30, fg_color="#e74c3c", hover_color="#c0392b", 
                                   command=lambda: self._delete_history_item(item))
        btn_delete.pack(side="right", padx=(5, 5), pady=10)

        # 2. 체크박스 배치
        cb = ctk.CTkCheckBox(card, text="", width=20, command=lambda: self._on_compare_select(item, cb))
        cb.pack(side="left", padx=10)
        
        # 3. 정보 텍스트 영역 (나머지 공간 차지)
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True)

        title = item.get("analysis", {}).get("title", "Unknown")
        # 제목 클릭 시 상세 보기 열리도록 바인딩
        lbl_title = ctk.CTkLabel(info_frame, text=title, font=ctk.CTkFont(weight="bold"), cursor="hand2")
        lbl_title.pack(anchor="w", padx=5, pady=(5, 0))
        lbl_title.bind("<Button-1>", lambda e: self._show_record_detail(item))

        # 긴 파일명/날짜 텍스트가 버튼을 밀어내지 않도록 wraplength 설정
        meta_text = f"📅 {item.get('timestamp')} | {item.get('filename')}"
        lbl_meta = ctk.CTkLabel(info_frame, text=meta_text, font=ctk.CTkFont(size=10), text_color="gray", 
                               justify="left", wraplength=500)
        lbl_meta.pack(anchor="w", padx=5, pady=(0, 5))
        lbl_meta.bind("<Button-1>", lambda e: self._show_record_detail(item))

    def _delete_history_item(self, item):
        if not hasattr(self, 'delete_handler'): return
        
        filename = item.get("filename", "Unknown")
        if messagebox.askyesno("기록 삭제", f"'{filename}' 분석 기록을 정말 삭제하시겠습니까?"):
            if self.delete_handler(item.get("timestamp"), item.get("filename")):
                self._refresh_history_ui()

    def _on_compare_select(self, item, cb):
        if cb.get():
            if len(self.selected_comparison) >= 2:
                cb.deselect()
                messagebox.showwarning("알림", "최대 2개의 문서만 비교 가능합니다.")
                return
            self.selected_comparison.append(item)
        else:
            if item in self.selected_comparison:
                self.selected_comparison.remove(item)
        
        self.btn_compare.configure(text=f"⚖️ 문서 비교 ({len(self.selected_comparison)}/2)")

    def _start_comparison(self):
        if len(self.selected_comparison) != 2:
            messagebox.showwarning("알림", "비교할 두 개의 문서를 체크박스로 선택해 주세요.")
            return
        
        doc_a = self.selected_comparison[0]
        doc_b = self.selected_comparison[1]
        
        comp_win = ctk.CTkToplevel(self.root)
        comp_win.title("AI 문서 비교 분석")
        comp_win.geometry("800x600")
        
        # 팝업 가림 방지
        comp_win.attributes("-topmost", True)
        comp_win.after(100, lambda: comp_win.attributes("-topmost", False))
        comp_win.lift()
        comp_win.focus_force()
        
        ctk.CTkLabel(comp_win, text="⚖️ 두 문서 비교 결과", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)
        
        result_box = ctk.CTkTextbox(comp_win, width=750, height=450)
        result_box.pack(padx=20, pady=10)
        result_box.insert("0.0", "AI가 두 문서를 비교 중입니다... 잠시만 기다려 주세요.")
        
        def run_comp():
            if hasattr(self, 'compare_handler'):
                res = self.compare_handler(doc_a['full_content'], doc_b['full_content'])
                result_box.delete("0.0", tk.END)
                result_box.insert("0.0", res)
        
        threading.Thread(target=run_comp, daemon=True).start()

    # Legacy Compatibility Methods (Modified for CTAk)
    def show_message(self, title, message, is_error=False):
        if is_error:
            messagebox.showerror(title, message)
        else:
            messagebox.showinfo(title, message)

    def show_disclaimer(self) -> bool:
        # Simplfied for modern UI
        res = messagebox.askyesno("이용 약관 동의", "School-Doc Genie Intelligent Hybrid 에이전트 이용 약관에 동의하십니까?\n(로컬 처리 및 서버 스테이트리스 원칙 준수)")
        if res: self.root.deiconify()
        return res

    def show_main_menu(self):
        # Already handled by CTAk tabs, but kept for agent_main loop compatibility
        self._show_window()
        self.root.mainloop()
        return "exit" # Default behavior

    def _show_record_detail(self, record):
        # Toplevel for detail analysis
        detail_win = ctk.CTkToplevel(self.root)
        detail_win.title(f"상세 분석 - {record['filename']}")
        detail_win.geometry("900x850")
        
        # 팝업 가림 방지 로직
        detail_win.attributes("-topmost", True)
        detail_win.after(100, lambda: detail_win.attributes("-topmost", False))
        detail_win.lift()
        detail_win.focus_force()
        
        # 1. Metadata Header (데이터 수집 정보)
        meta_frame = ctk.CTkFrame(detail_win, fg_color="transparent")
        meta_frame.pack(fill="x", padx=30, pady=(20, 10))
        
        analysis = record.get('analysis', {})
        ctk.CTkLabel(meta_frame, text=analysis.get('title', '제목 없음'), font=ctk.CTkFont(size=22, weight="bold")).pack(anchor="w")
        
        info_str = f"📅 날짜: {analysis.get('date', '미추출')}  |  📄 문서번호: {analysis.get('doc_number', '미추출')}"
        ctk.CTkLabel(meta_frame, text=info_str, font=ctk.CTkFont(size=13), text_color="#3498db").pack(anchor="w", pady=5)

        # 2. Main Content
        tabview = ctk.CTkTabview(detail_win, width=840, height=450)
        tabview.pack(padx=20, pady=10)
        
        tab_sum = tabview.add("핵심 요약 & 조치")
        tab_raw = tabview.add("원본 텍스트")
        
        # Summary & Actions Tab
        sum_txt = ctk.CTkTextbox(tab_sum, width=800, height=380)
        sum_txt.pack(padx=10, pady=10)
        
        summary = analysis.get('summary', '요약 정보가 없습니다.')
        actions = "\n".join([f"• {a}" for a in analysis.get('action_items', [])])
        sum_txt.insert("0.0", f"【 핵심 요약 】\n{summary}\n\n【 조치 사항 및 일정 】\n{actions}")
        sum_txt.configure(state="disabled")
        
        # Raw Content Tab
        raw_txt = ctk.CTkTextbox(tab_raw, width=800, height=380)
        raw_txt.pack(padx=10, pady=10)
        raw_txt.insert("0.0", record.get('full_content', '내용 없음'))
        raw_txt.configure(state="disabled")

        # 3. AI Chat Interface (저장 기능 포함)
        chat_frame = ctk.CTkFrame(detail_win, corner_radius=15, fg_color="#34495e")
        chat_frame.pack(fill="x", padx=30, pady=10)
        
        ctk.CTkLabel(chat_frame, text="💬 이 문서에 대해 무엇이든 물어보세요 (AI Chat)", text_color="white", font=ctk.CTkFont(weight="bold")).pack(pady=(10, 5))
        
        # 이전 채팅 내역 표시 영역
        history_box = ctk.CTkTextbox(chat_frame, height=150, width=800, fg_color="#2c3e50", text_color="white")
        if record.get("chat_history"):
            history_box.pack(padx=15, pady=5)
            for chat in record["chat_history"]:
                history_box.insert("end", f"Q: {chat['query']}\nA: {chat['answer']}\n{'-'*40}\n")
            history_box.configure(state="disabled")
            history_box.see("end")

        chat_input_row = ctk.CTkFrame(chat_frame, fg_color="transparent")
        chat_input_row.pack(fill="x", padx=15, pady=(0, 15))
        
        chat_entry = ctk.CTkEntry(chat_input_row, placeholder_text="예: 이 공문의 예산 지원 자격이 뭐야?", height=40)
        chat_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        chat_entry.focus_set() # 창이 열리면 바로 타이핑 가능하게 포커스
        
        def send_chat(event=None): # 엔터키 이벤트 대응을 위해 event 매개변수 추가
            query = chat_entry.get().strip()
            if not query: return
            
            chat_entry.delete(0, tk.END)
            ans_win = ctk.CTkToplevel(detail_win)
            ans_win.title("AI 답변")
            ans_win.geometry("500x400")
            
            # 팝업 가림 방지 (답변 창에도 적용)
            ans_win.attributes("-topmost", True)
            ans_win.after(100, lambda: ans_win.attributes("-topmost", False))
            ans_win.lift()
            ans_win.focus_force()
            
            ans_box = ctk.CTkTextbox(ans_win, width=460, height=350)
            ans_box.pack(padx=20, pady=20)
            ans_box.insert("0.0", "AI가 생각 중입니다... 잠시만 기다려 주세요.")
            
            def perform_ai_call():
                if hasattr(self, 'chat_handler'):
                    answer = self.chat_handler(record.get('full_content', ''), query)
                    # 창이 아직 존재하는지 확인
                    if ans_win.winfo_exists():
                        ans_box.configure(state="normal")
                        ans_box.delete("0.0", tk.END)
                        ans_box.insert("0.0", f"Q: {query}\n\n{answer}")
                        ans_box.configure(state="disabled")
                    
                    # 채팅 내역 저장 요청
                    if hasattr(self, 'chat_save_handler'):
                        self.chat_save_handler(record.get('timestamp'), record.get('filename'), query, answer)
            
            threading.Thread(target=perform_ai_call, daemon=True).start()

        # 엔터키 바인딩
        chat_entry.bind("<Return>", send_chat)
        ctk.CTkButton(chat_input_row, text="질문하기", width=100, command=send_chat, fg_color="#2ecc71").pack(side="right")

        # 4. Action Buttons (행정 편의)
        conv_frame = ctk.CTkFrame(detail_win, fg_color="transparent")
        conv_frame.pack(fill="x", padx=30, pady=(0, 20))
        
        ctk.CTkButton(conv_frame, text="📋 관련 근거 복사", command=lambda: self._copy_reference(record), width=180, fg_color="#3498db").pack(side="left", padx=10)
        ctk.CTkButton(conv_frame, text="📅 일정 추출 (.ics)", command=lambda: self._export_ics(record), width=180, fg_color="#9b59b6").pack(side="left", padx=10)

    def _copy_reference(self, record):
        from datetime import datetime
        title = record['analysis'].get('title', '문서 분석')
        ts = record.get('timestamp', '')
        try:
            # 보수적으로 형식이 다를 수 있으므로 체크
            if " " in ts: # 2025-12-31 13:37:58 형태
                date_part = ts.split(" ")[0].replace("-", ".")
            else:
                date_part = datetime.now().strftime("%Y.%m.%d")
        except:
            date_part = datetime.now().strftime("%Y.%m.%d")
        
        ref_text = f"관련: {title}({date_part}.)"
        self.root.clipboard_clear()
        self.root.clipboard_append(ref_text)
        self.root.update()
        messagebox.showinfo("복사 완료", f"클립보드에 복사되었습니다:\n{ref_text}")

    def _export_ics(self, record):
        try:
            from icalendar import Calendar, Event
            from datetime import datetime, timedelta
            import webbrowser
            import os
            import re
            import tkinter as tk
        except ImportError:
            messagebox.showerror("오류", "icalendar 라이브러리가 필요합니다.\npip install icalendar를 실행해 주세요.")
            return

        actions = record['analysis'].get('action_items', [])
        if not actions:
            messagebox.showwarning("알림", "추출할 조치 사항이 없습니다.")
            return

        # 1. 일정 추출 로직
        date_pattern = re.compile(r'(\d{4}[-./])?(\d{1,2})[-./월]\s*(\d{1,2})일?')
        extracted_events = []
        
        for action in actions:
            event_date = datetime.now()
            match = date_pattern.search(action)
            is_detected = False
            if match:
                try:
                    month = int(match.group(2))
                    day = int(match.group(3))
                    year = int(match.group(1).strip('-./')) if match.group(1) else datetime.now().year
                    event_date = datetime(year, month, day)
                    is_detected = True
                except: pass
            
            extracted_events.append({
                "date": event_date.strftime("%Y-%m-%d"),
                "summary": action,
                "is_detected": is_detected,
                "raw_dt": event_date
            })

        # 2. 미리보기 창 띄우기
        preview_win = ctk.CTkToplevel(self.root)
        preview_win.title("캘린더 일정 미리보기")
        preview_win.geometry("600x500")
        preview_win.attributes("-topmost", True)
        preview_win.grab_set()

        ctk.CTkLabel(preview_win, text="📅 추출된 일정 목록", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=15)
        
        scroll_frame = ctk.CTkScrollableFrame(preview_win, width=550, height=300)
        scroll_frame.pack(padx=20, pady=10, fill="both", expand=True)

        for item in extracted_events:
            row = ctk.CTkFrame(scroll_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)
            
            date_color = "#2ecc71" if item["is_detected"] else "#e67e22"
            detect_tag = "[감지]" if item["is_detected"] else "[오늘]"
            
            date_lbl = ctk.CTkLabel(row, text=f"{item['date']} {detect_tag}", text_color=date_color, font=ctk.CTkFont(weight="bold"), width=120)
            date_lbl.pack(side="left", padx=5)
            
            summary_lbl = ctk.CTkLabel(row, text=item['summary'], anchor="w", wraplength=380, justify="left")
            summary_lbl.pack(side="left", padx=5, fill="x", expand=True)

        def proceed_save():
            preview_win.destroy()
            
            cal = Calendar()
            cal.add('prodid', '-//School-Doc Genie//')
            cal.add('version', '2.0')
            
            for item in extracted_events:
                event = Event()
                event.add('summary', f"[학교] {item['summary']}")
                event.add('dtstart', item['raw_dt'])
                event.add('dtend', item['raw_dt'] + timedelta(hours=1))
                cal.add_component(event)

            save_path = filedialog.asksaveasfilename(defaultextension=".ics", 
                                                   initialfile=f"{record['analysis'].get('title', '일정')}_일정.ics",
                                                   title="캘린더 파일 저장")
            if save_path:
                with open(save_path, 'wb') as f:
                    f.write(cal.to_ical())
                
                self.root.clipboard_clear()
                self.root.clipboard_append(save_path)
                self.root.update()
                
                if messagebox.askyesno("구글 캘린더 등록", 
                                      f"{len(extracted_events)}개의 일정이 생성되었습니다.\n\n파일 경로가 클립보드에 복사되었습니다!\n\n지금 구글 캘린더 '가져오기' 페이지를 열까요?"):
                    webbrowser.open("https://calendar.google.com/calendar/u/0/r/settings/export")
                    os.startfile(os.path.dirname(os.path.abspath(save_path)))

        btn_frame = ctk.CTkFrame(preview_win, fg_color="transparent")
        btn_frame.pack(fill="x", pady=20)
        ctk.CTkButton(btn_frame, text="취소", command=preview_win.destroy, fg_color="gray").pack(side="left", padx=50)
        ctk.CTkButton(btn_frame, text="ICS 파일로 저장", command=proceed_save).pack(side="right", padx=50)

    def show_preview(self, filename: str, content: str) -> str:
        # Modal preview
        preview_win = ctk.CTkToplevel(self.root)
        preview_win.title("최종 검토")
        preview_win.geometry("800x700")
        
        # 팝업 가림 방지
        preview_win.attributes("-topmost", True)
        preview_win.after(100, lambda: preview_win.attributes("-topmost", False))
        preview_win.lift()
        preview_win.focus_force()
        preview_win.grab_set()
        
        
        ctk.CTkLabel(preview_win, text=f"🔍 {filename} 분석 전 검토", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        editor = ctk.CTkTextbox(preview_win, width=750, height=550)
        editor.pack(padx=20, pady=10)
        editor.insert("0.0", content)
        
        res = {"content": None}
        def submit():
            res["content"] = editor.get("0.0", tk.END).strip()
            preview_win.destroy()
        
        def cancel():
            preview_win.destroy()
            
        btn_frame = ctk.CTkFrame(preview_win, fg_color="transparent")
        btn_frame.pack(fill="x", pady=20)
        ctk.CTkButton(btn_frame, text="취소", command=cancel, width=100, fg_color="gray").pack(side="left", padx=50)
        ctk.CTkButton(btn_frame, text="심층 분석 요청", command=submit, width=200).pack(side="right", padx=50)
        
        self.root.wait_window(preview_win)
        return res["content"]

    def set_analysis_progress(self, filename, text_len=0, is_start=True, provider="Gemini 3.0 Flash"):
        if is_start:
            self.progress_bar.pack(fill="x", pady=5)
            self.progress_bar.start() 
            
            # 파일명이 너무 길면 생략 처리 (예: "매우긴파일명..." )
            display_name = filename if len(filename) <= 30 else filename[:27] + "..."
            
            # 예상 시간 계산 (공급자별 차등)
            if "Ollama" in provider:
                estimated_sec = max(30, int(text_len / 500 * 25))
            else:
                estimated_sec = 10
            
            min_val = estimated_sec // 60
            sec_val = estimated_sec % 60
            
            msg = f"⏳ '{display_name}' 분석 중...\n({provider} 사용 중, 예상 소요 시간: "
            if min_val > 0:
                msg += f"{min_val}분 "
            msg += f"{sec_val}초)"
            
            # wraplength를 추가하여 텍스트가 잘리지 않게 함
            self.progress_label.configure(text=msg, justify="left")
        else:
            self.progress_bar.stop()
            self.progress_bar.set(1.0)
            self.progress_label.configure(text="✅ 분석이 완료되었습니다.")
            self.root.after(3000, lambda: self.progress_bar.pack_forget())
            self.root.after(3000, lambda: self.progress_label.configure(text=""))

if __name__ == "__main__":
    gui = AgentGUI()
    gui.show_window()
    gui.root.mainloop()

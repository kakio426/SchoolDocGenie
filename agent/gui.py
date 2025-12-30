
import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog, ttk
import os

class AgentGUI:
    def __init__(self):
        print(">>> GUI 초기화 시작...")
        self.root = tk.Tk()
        self.root.title("School-Doc Agent")
        self.root.geometry("600x500")
        self.root.withdraw() # 처음엔 크기만 잡고 숨김
        
        # 스타일 설정
        self.style = ttk.Style()
        self.style.configure('TButton', font=('Malgun Gothic', 10))
        self.style.configure('TLabel', font=('Malgun Gothic', 10))

    def show_disclaimer(self) -> bool:
        """법적 고지 사항을 표시"""
        self.root.deiconify() # 창 보이기
        self.root.attributes('-topmost', True) # 최상단
        self._center_window(self.root)
        
        # 제목
        tk.Label(self.root, text="School-Doc Genie 이용 약관", font=('Malgun Gothic', 14, 'bold')).pack(pady=10)

        # 약관 내용
        txt = scrolledtext.ScrolledText(self.root, width=70, height=18, font=('Malgun Gothic', 9))
        txt.pack(padx=10, pady=5)
        
        disclaimer_text = """
[School-Doc Genie Intelligent Hybrid 에이전트 이용 약관]

1. [운영 모델: BYOK (Bring Your Own Key)]
   - 본 프로그램은 사용자가 직접 발급한 Google Gemini API Key를 사용합니다.
   - AI 분석 및 채팅 사용에 따른 API 할당량 소모는 사용자의 책임입니다.

2. [데이터 처리 및 보안]
   - [로컬 처리]: 문서 변환(HWP 등)과 개인정보 마스킹은 사용자의 PC 내에서만 수행됩니다.
   - [스테이트리스 전송]: 비식별화된 텍스트는 AI 분석을 위해 전송되나, 서버에 저장되지 않고 즉시 휘발됩니다.
   - [로컬 저장]: 모든 분석 기록은 사용자의 PC 내에만 암호화 및 로컬 저장됩니다.

3. [AI 지능형 기능 안내]
   - 본 에이전트는 AI 요약, 액션 아이템 추출, 문서 채팅(Q&A), 문서 비교 기능을 제공합니다.
   - AI는 기술적 한계로 인해 사실과 다른 답변을 낼 수 있으므로, 업무 활용 시 반드시 원본과 대조하십시오.

4. [사용자 책임 고지]
   - 사용자는 전송 전 '미리보기'를 통해 비식별화 상태를 직접 최전선에서 검토해야 합니다.
   - 검토 소홀로 인한 사고 및 프로그램 활용 결과에 대한 모든 책임은 사용자 본인에게 있습니다.

위 내용을 모두 숙지하였으며, 지능형 에이전트 서비스 이용에 동의합니다.
        """
        txt.insert(tk.END, disclaimer_text)
        txt.config(state='disabled')

        result = {'agreed': False}
        
        def on_agree():
            result['agreed'] = True
            self.root.quit() # 메인루프 탈출용
            
        def on_cancel():
            self.root.destroy()
            import sys
            sys.exit(0)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=15)
        
        tk.Button(btn_frame, text="동의하지 않음 (종료)", command=on_cancel, width=20).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="동의합니다 (시작)", command=on_agree, width=20, bg='#ddffdd', font=('Malgun Gothic', 10, 'bold')).pack(side=tk.LEFT, padx=10)

        self.root.lift()
        self.root.focus_force()
        print(">>> [확인] 화면에 '이용 약관' 창이 떴습니다!")
        
        self.root.mainloop() # 동의할 때까지 대기
        
        # 동의 후에는 다음 창을 위해 일단 다시 숨김
        if result['agreed']:
            self.root.attributes('-topmost', False) # 상단 고정 해제
            self._clear_root()
            self.root.withdraw()
        return result['agreed']

    def show_preview(self, filename: str, content: str) -> str:
        """프리뷰 창 표시"""
        self.root.deiconify()
        self.root.geometry("800x700")
        self._center_window(self.root)
        self.root.attributes('-topmost', True)

        header_frame = tk.Frame(self.root, bg='#f0f8ff', pady=10)
        header_frame.pack(fill=tk.X)
        tk.Label(header_frame, text="🔍 전송 전 최종 검토", font=('Malgun Gothic', 12, 'bold'), bg='#f0f8ff').pack()

        editor = scrolledtext.ScrolledText(self.root, font=('Malgun Gothic', 11))
        editor.pack(expand=True, fill=tk.BOTH, padx=15, pady=10)
        editor.insert(tk.END, content)

        btn_frame = tk.Frame(self.root, pady=15)
        btn_frame.pack(fill=tk.X)

        result = {'content': None}

        def on_submit():
            result['content'] = editor.get("1.0", tk.END).strip()
            self.root.quit()

        def on_cancel():
            self.root.quit()

        tk.Button(btn_frame, text="취소", command=on_cancel, width=15).pack(side=tk.LEFT, padx=20)
        tk.Button(btn_frame, text="✅ AI 분석 시작", command=on_submit, width=25, bg='#007bff', fg='white').pack(side=tk.RIGHT, padx=20)

        self.root.mainloop()
        self.root.withdraw()
        self._clear_root()
        return result['content']

    def show_settings_popup(self, current_key: str = "") -> str:
        """API Key 설정 팝업"""
        self.root.deiconify()
        self.root.geometry("500x350")
        self._center_window(self.root)
        self.root.attributes('-topmost', True)
        
        tk.Label(self.root, text="⚙️ 에이전트 설정", font=('Malgun Gothic', 14, 'bold')).pack(pady=20)
        
        tk.Label(self.root, text="Google Gemini API Key를 입력해주세요:", font=('Malgun Gothic', 10)).pack(pady=5)
        
        key_entry = tk.Entry(self.root, width=50, font=('Courier New', 10), show='*')
        key_entry.pack(pady=10, padx=20)
        if current_key:
            key_entry.insert(0, current_key)
            
        def open_guide():
            import webbrowser
            webbrowser.open("https://aistudio.google.com/app/apikey")
            
        tk.Button(self.root, text="🔑 API Key 발급 가이드 (무료)", command=open_guide, fg='blue', cursor='hand2', relief=tk.FLAT).pack(pady=5)

        result = {'key': None}

        def on_save():
            val = key_entry.get().strip()
            if not val:
                messagebox.showwarning("경고", "API Key를 입력해야 사용 가능합니다.")
                return
            result['key'] = val
            self.root.quit()

        tk.Button(self.root, text="저장하고 시작하기", command=on_save, bg='#007bff', fg='white', width=20, font=('Malgun Gothic', 10, 'bold')).pack(pady=30)

        self.root.mainloop()
        self.root.withdraw()
        self._clear_root()
        return result['key']

    def show_history(self, history_data: list):
        """로컬 히스토리 보기 팝업 (AI Summary 중심 Card-based UI)"""
        import re
        history_win = tk.Toplevel(self.root)
        history_win.title("📜 로컬 분석 아카이브")
        history_win.geometry("900x750")
        self._center_window(history_win)
        history_win.configure(bg='#f4f7f9')
        history_win.attributes('-topmost', True) 

        # Header
        header_frame = tk.Frame(history_win, bg='#1a237e', pady=25)
        header_frame.pack(fill=tk.X)
        tk.Label(header_frame, text="로컬 분석 아카이브", font=('Malgun Gothic', 20, 'bold'), bg='#1a237e', fg='white').pack()
        tk.Label(header_frame, text="서버에 저장되지 않은, 선생님 PC만의 공문 분석 기록고입니다.", font=('Malgun Gothic', 10), bg='#1a237e', fg='#c5cae9').pack()

        # Canvas for scrolling
        container = tk.Frame(history_win, bg='#f4f7f9')
        container.pack(expand=True, fill=tk.BOTH, padx=25, pady=20)
        
        canvas = tk.Canvas(container, bg='#f4f7f9', highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#f4f7f9')

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=840)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        if not history_data:
            tk.Label(scrollable_frame, text="분석된 공문이 없습니다.", font=('Malgun Gothic', 11), fg='gray', bg='#f4f7f9', pady=100).pack()
        
        selected_indices = []

        def toggle_select(idx, item):
            if idx in selected_indices:
                selected_indices.remove(idx)
            else:
                if len(selected_indices) >= 2:
                    messagebox.showwarning("알림", "최대 2개의 문서만 비교 가능합니다.")
                    return False
                selected_indices.append(idx)
            return True

        for idx, item in enumerate(history_data):
            card = tk.Frame(scrollable_frame, bg='white', relief=tk.FLAT, pady=18, padx=25)
            card.pack(fill=tk.X, pady=12, padx=10)
            card.configure(highlightbackground="#d1d9e6", highlightthickness=1)

            # Checkbox for comparison
            var = tk.BooleanVar()
            cb = tk.Checkbutton(card, variable=var, bg='white', command=lambda i=idx, it=item: toggle_select(i, it))
            cb.pack(side=tk.LEFT, anchor='n', padx=(0, 10))

            content_frame = tk.Frame(card, bg='white')
            content_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

            analysis = item.get("analysis", {})
            title = analysis.get("title", "제목 없음")
            dt = item.get("timestamp", "")
            
            # Title
            tk.Label(content_frame, text=title, font=('Malgun Gothic', 15, 'bold'), bg='white', fg='#1a237e', wraplength=700, justify=tk.LEFT).pack(anchor='w')
            # Meta
            tk.Label(content_frame, text=f"📅 {dt}  |  📂 {item.get('filename')}", font=('Malgun Gothic', 9), bg='white', fg='#78909c').pack(anchor='w', pady=(2, 10))
            
            # AI Summary
            summary = analysis.get("summary", "")
            if not summary:
                snip = item.get("content_snippet", "")
                snip = re.sub(r'#+\s*HWP\s*변환\s*결과', '', snip)
                snip = re.sub(r'[|#\-_]', ' ', snip).strip()
                summary = f"[자동 요약 미사용 문서] {snip[:200]}..."

            summ_box = tk.Label(content_frame, text=summary, font=('Malgun Gothic', 10), bg='#ffffff', fg='#37474f', 
                                pady=12, padx=12, wraplength=700, justify=tk.LEFT, relief=tk.SOLID, borderwidth=1)
            summ_box.pack(fill=tk.X, pady=(0, 10))
            
            if analysis.get("summary"):
                summ_box.configure(highlightbackground="#4caf50", highlightthickness=1)
            else:
                summ_box.configure(highlightbackground="#e3f2fd", highlightthickness=1)

            # Footer
            footer = tk.Frame(content_frame, bg='white')
            footer.pack(fill=tk.X)
            
            kw_f = tk.Frame(footer, bg='white')
            kw_f.pack(side=tk.LEFT)
            for kw in (analysis.get("keywords") or [])[:5]:
                tk.Label(kw_f, text=f"#{kw}", font=('Malgun Gothic', 8, 'bold'), bg='#e8eaf6', fg='#3f51b5', padx=6, pady=2).pack(side=tk.LEFT, padx=3)

            def open_d(r): return lambda: self._show_record_detail(r)
            tk.Button(footer, text="정밀 분석 및 조치사항 보기 →", command=open_d(item), relief=tk.FLAT, font=('Malgun Gothic', 9, 'bold'), fg='#1a237e', bg='white', cursor='hand2').pack(side=tk.RIGHT)

        def on_compare():
            if len(selected_indices) != 2:
                messagebox.showwarning("알림", "비교할 두 개의 문서를 선택해주세요.")
                return
            doc_a = history_data[selected_indices[0]]
            doc_b = history_data[selected_indices[1]]
            self._show_comparison_window(doc_a, doc_b)

        bottom_btn_frame = tk.Frame(history_win, bg='#f4f7f9', pady=20)
        bottom_btn_frame.pack(fill=tk.X)
        
        tk.Button(bottom_btn_frame, text="⚖️ 선택한 두 문서 비교하기 (AI 분석)", command=on_compare, bg='#673ab7', fg='white', 
                  width=40, font=('Malgun Gothic', 11, 'bold'), pady=10).pack(side=tk.LEFT, padx=50)
        
        tk.Button(bottom_btn_frame, text="닫기", command=history_win.destroy, width=15, bg='#455a64', fg='white', 
                  font=('Malgun Gothic', 10, 'bold'), pady=10).pack(side=tk.RIGHT, padx=50)
        
        history_win.lift()

    def _show_comparison_window(self, doc_a, doc_b):
        """두 문서 비교 분석창"""
        compare_win = tk.Toplevel(self.root)
        compare_win.title("⚖️ 신구 대조 및 변경사항 분석")
        compare_win.geometry("900x800")
        self._center_window(compare_win)
        compare_win.attributes('-topmost', True)
        compare_win.configure(bg='white')

        # Header
        header = tk.Frame(compare_win, bg='#311b92', pady=20)
        header.pack(fill=tk.X)
        tk.Label(header, text="신구 대조 및 변경사항 분석", font=('Malgun Gothic', 18, 'bold'), bg='#311b92', fg='white').pack()
        
        # Subtitle
        sub = tk.Frame(compare_win, bg='white', pady=10)
        sub.pack(fill=tk.X, padx=30)
        tk.Label(sub, text=f"대조군 A: {doc_a['analysis'].get('title')}", font=('Malgun Gothic', 10), bg='white', fg='gray').pack(side=tk.LEFT)
        tk.Label(sub, text=" vs ", font=('Malgun Gothic', 10, 'bold'), bg='white').pack(side=tk.LEFT)
        tk.Label(sub, text=f"실험군 B: {doc_b['analysis'].get('title')}", font=('Malgun Gothic', 10), bg='white', fg='#1a237e').pack(side=tk.LEFT)

        # Result Area
        res_area = scrolledtext.ScrolledText(compare_win, font=('Malgun Gothic', 11), bg='#fff9c4', padx=20, pady=20)
        res_area.pack(expand=True, fill=tk.BOTH, padx=30, pady=20)
        res_area.insert(tk.END, "AI 분석 중입니다... 잠시만 기다려주세요.")
        res_area.config(state='disabled')

        def run_compare():
            if hasattr(self, 'compare_handler'):
                res = self.compare_handler(doc_a.get('full_content'), doc_b.get('full_content'))
                res_area.config(state='normal')
                res_area.delete("1.0", tk.END)
                res_area.insert(tk.END, res)
                res_area.config(state='disabled')

        compare_win.after(500, run_compare)
        
        tk.Button(compare_win, text="닫기", command=compare_win.destroy, bg='#1a237e', fg='white', width=20, pady=10).pack(pady=15)

    def _show_record_detail(self, record):
        """상세 보고서 (Summary + Action Items)"""
        detail_win = tk.Toplevel(self.root)
        detail_win.title("📄 AI 정밀 분석 보고서")
        detail_win.geometry("850x850")
        self._center_window(detail_win)
        detail_win.attributes('-topmost', True)
        detail_win.configure(bg='white')
        
        analysis = record.get("analysis", {})
        
        # Header
        header = tk.Frame(detail_win, bg='white', pady=25, padx=40)
        header.pack(fill=tk.X)
        tk.Label(header, text=analysis.get('title'), font=('Malgun Gothic', 20, 'bold'), bg='white', fg='#1a237e', wraplength=750, justify=tk.LEFT).pack(anchor='w')
        tk.Label(header, text=f"문서번호: {analysis.get('doc_number') or '없음'} | 일자: {analysis.get('date') or '미상'}", font=('Malgun Gothic', 10), bg='white', fg='#90a4ae').pack(anchor='w', pady=5)
        
        container = tk.Frame(detail_win, bg='white', padx=40)
        container.pack(expand=True, fill=tk.BOTH)

        # 1. Action Items (Highlight)
        actions = analysis.get("action_items", [])
        if actions:
            a_frame = tk.Frame(container, bg='#fff8e1', pady=15, padx=20, relief=tk.SOLID, borderwidth=1)
            a_frame.pack(fill=tk.X, pady=(0, 20))
            tk.Label(a_frame, text="✅ 조치 및 강조 사항", font=('Malgun Gothic', 12, 'bold'), bg='#fff8e1', fg='#f57f17').pack(anchor='w')
            for a in actions:
                tk.Label(a_frame, text=f"• {a}", font=('Malgun Gothic', 10), bg='#fff8e1', justify=tk.LEFT, wraplength=700).pack(anchor='w', padx=10, pady=2)

        # 2. AI Summary
        tk.Label(container, text="📝 핵심 요약", font=('Malgun Gothic', 12, 'bold'), bg='white', fg='#1a237e').pack(anchor='w', pady=(0, 5))
        s_txt = tk.Text(container, font=('Malgun Gothic', 11, 'italic' if not analysis.get('summary') else 'normal'), 
                        bg='#f8f9fa', height=7, relief=tk.FLAT, padx=15, pady=15)
        s_txt.pack(fill=tk.X, pady=(0, 20))
        
        summary_val = analysis.get("summary", "").strip()
        if not summary_val:
            summary_val = "해당 문서는 AI 요약 정보가 포함되지 않은 예전 기록이거나, 분석 중 오류가 발생했습니다."
            
        s_txt.insert(tk.END, summary_val)
        s_txt.config(state='disabled')

        # 3. Full Content (Original)
        tk.Label(container, text="📄 원본 내용 (비식별화 완료)", font=('Malgun Gothic', 12, 'bold'), bg='white', fg='#1a237e').pack(anchor='w', pady=(0, 5))
        o_txt = scrolledtext.ScrolledText(container, font=('Consolas', 10), bg='#fafafa', height=10)
        o_txt.pack(fill=tk.BOTH, expand=True)
        o_txt.insert(tk.END, record.get("full_content", ""))
        o_txt.config(state='disabled')
        
        btn_frame = tk.Frame(detail_win, bg='white', pady=15)
        btn_frame.pack(fill=tk.X)
        
        tk.Button(btn_frame, text="💬 문서에 대해 질문하기 (Chat)", command=lambda: self._show_chat_window(record), 
                  bg='#4caf50', fg='white', width=30, pady=12, font=('Malgun Gothic', 10, 'bold')).pack(side=tk.LEFT, padx=40)
        
        tk.Button(btn_frame, text="닫기", command=detail_win.destroy, bg='#1a237e', fg='white', width=20, pady=12, font=('Malgun Gothic', 10, 'bold')).pack(side=tk.RIGHT, padx=40)
        detail_win.lift()
        detail_win.focus_force()

    def _show_chat_window(self, record):
        """AI와 문서 기반 대화 창"""
        chat_win = tk.Toplevel(self.root)
        chat_win.title(f"💬 {record.get('filename')} - AI 채팅")
        chat_win.geometry("500x650")
        self._center_window(chat_win)
        chat_win.attributes('-topmost', True)
        chat_win.configure(bg='#f8f9fa')

        # Chat History
        chat_area = scrolledtext.ScrolledText(chat_win, font=('Malgun Gothic', 10), bg='white', state='disabled', padx=10, pady=10)
        chat_area.pack(expand=True, fill=tk.BOTH, padx=15, pady=15)

        def append_msg(role, msg):
            chat_area.config(state='normal')
            tag = "ai" if role == "AI" else "user"
            chat_area.insert(tk.END, f"[{role}]\n", tag)
            chat_area.insert(tk.END, f"{msg}\n\n")
            chat_area.config(state='disabled')
            chat_area.see(tk.END)

        append_msg("AI", "이 문서에 대해 궁금한 점을 물어보세요! (예: 제출 기한이 언제야?, 예산은 얼마야?)")

        # Input Area
        input_frame = tk.Frame(chat_win, bg='#f8f9fa', pady=10)
        input_frame.pack(fill=tk.X, padx=15)
        
        entry = tk.Entry(input_frame, font=('Malgun Gothic', 11))
        entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))
        
        def send_query():
            query = entry.get().strip()
            if not query: return
            entry.delete(0, tk.END)
            append_msg("나", query)
            
            # API 호출을 위해 외부 핸들러가 필요함 (agent_main.py에서 주입받아야 함)
            if hasattr(self, 'chat_handler'):
                ans = self.chat_handler(record.get('full_content'), query)
                append_msg("AI", ans)
            else:
                append_msg("AI", "죄송합니다. 채팅 기능이 현재 활성화되지 않았습니다.")

        tk.Button(input_frame, text="전송", command=send_query, bg='#1a237e', fg='white', width=8).pack(side=tk.RIGHT)
        entry.bind("<Return>", lambda e: send_query())

        chat_win.focus_force()

    def show_main_menu(self) -> str:
        """메인 대시보드 메뉴"""
        self.root.deiconify()
        # 중요: 메인메뉴는 다른 창을 가리면 안되므로 topmost 해제
        self.root.attributes('-topmost', False) 
        self.root.geometry("500x480")
        self._center_window(self.root)
        
        # UI Code same as before...
        tk.Label(self.root, text="🏫 School-Doc Genie Agent", font=('Malgun Gothic', 16, 'bold'), fg='#007bff').pack(pady=25)
        btn_style = {'width': 30, 'font': ('Malgun Gothic', 11), 'pady': 10}
        result = {'choice': 'exit'}
        def set_choice(c):
            result['choice'] = c
            self.root.quit()

        tk.Button(self.root, text="📄 새 문서 분석 시작", command=lambda: set_choice('process'), bg='#e3f2fd', **btn_style).pack(pady=10)
        tk.Button(self.root, text="📜 로컬 분석 기록 보기 (Premium)", command=lambda: set_choice('history'), **btn_style).pack(pady=10)
        tk.Button(self.root, text="⚙️ 설정 (API Key 변경)", command=lambda: set_choice('settings'), **btn_style).pack(pady=10)
        tk.Button(self.root, text="❌ 프로그램 종료", command=lambda: set_choice('exit'), **btn_style).pack(pady=10)
        tk.Label(self.root, text="v0.5.0 Intelligent Hybrid", font=('Arial', 8), fg='gray').pack(side=tk.BOTTOM, pady=10)

        self.root.mainloop()
        self._clear_root()
        return result['choice']

    def select_file(self):
        self.root.deiconify()
        file_path = filedialog.askopenfilename(title="파일 선택")
        self.root.withdraw()
        return file_path

    def show_message(self, title, message, is_error=False):
        if is_error:
            messagebox.showerror(title, message)
        else:
            messagebox.showinfo(title, message)
            
    def _center_window(self, win):
        win.update_idletasks()
        width = win.winfo_width()
        height = win.winfo_height()
        x = (win.winfo_screenwidth() // 2) - (width // 2)
        y = (win.winfo_screenheight() // 2) - (height // 2)
        win.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    def _clear_root(self):
        """메인 창의 모든 위젯 삭제 (Bug Fix: Check if root exists)"""
        try:
            if not self.root.winfo_exists():
                return
            for widget in self.root.winfo_children():
                widget.destroy()
        except Exception:
            pass # 이미 죽었으면 무시

if __name__ == "__main__":
    gui = AgentGUI()
    if gui.show_disclaimer():
        res = gui.show_preview("테스트.hwp", "내용샘플")
        print(f"Result: {res}")


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
[School-Doc Genie 하이브리드 에이전트 이용 약관]

1. [개인정보 처리 방침]
   - 본 프로그램은 사용자의 PC에서 문서를 텍스트로 변환하고 비식별화(마스킹)합니다.
   - 원순 파일은 서버에 전송되거나 저장되지 않습니다.

2. [사용자 책임 고지]
   - 사용자는 서버로 전송하기 전, 반드시 '미리보기' 기능을 통해 직접 확인해야 합니다.
   - 검토 소홀로 인한 사고의 모든 책임은 사용자 본인에게 있습니다.

위 내용을 숙지하였으며 준수에 동의합니다.
        """
        txt.insert(tk.END, disclaimer_text)
        txt.config(state='disabled')

        result = {'agreed': False}
        
        def on_agree():
            result['agreed'] = True
            self.root.quit() # 메인루프 탈출용
            
        def on_cancel():
            self.root.destroy()
            os._exit(0)

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
        tk.Button(btn_frame, text="✅ 서버 전송", command=on_submit, width=25, bg='#007bff', fg='white').pack(side=tk.RIGHT, padx=20)

        self.root.mainloop()
        self.root.withdraw()
        self._clear_root()
        return result['content']

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
        """메인 창의 모든 위젯 삭제 (다음 화면 준비)"""
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    gui = AgentGUI()
    if gui.show_disclaimer():
        res = gui.show_preview("테스트.hwp", "내용샘플")
        print(f"Result: {res}")

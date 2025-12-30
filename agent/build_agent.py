
import subprocess
import sys
import os

def build():
    print("🚀 School-Doc Genie 에이전트 빌드를 시작합니다...")
    
    # 빌드할 파일 경로
    main_file = "agent_main.py"
    
    # PyInstaller 명령어 조합
    # --onefile: 단일 실행 파일로 생성
    # --name: 실행 파일 이름
    # --clean: 빌드 전 캐시 삭제
    # --add-data: 필요한 경우 데이터 파일 포함 (현재는 없음)
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", "SchoolDocAgent",
        "--clean",
        main_file
    ]
    
    try:
        subprocess.check_call(cmd)
        print("\n" + "="*50)
        print("✅ 빌드 성공!")
        print(f"실행 파일 위치: {os.path.join(os.getcwd(), 'dist', 'SchoolDocAgent.exe')}")
        print("="*50)
    except subprocess.CalledProcessError as e:
        print(f"❌ 빌드 실패: {e}")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    build()

import os
import json
from pathlib import Path
from cryptography.fernet import Fernet
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class ConfigManager:
    """사용자 설정을 암호화하여 로컬에 저장하는 클래스"""
    
    def __init__(self, config_path: Path = None):
        if config_path:
            self.config_path = config_path
        else:
            # 기본 경로는 사용자 홈 디렉토리 또는 에이전트 실행 경로
            self.config_path = Path("agent_config.enc")
            
        self._key = self._get_or_create_master_key()
        self._fernet = Fernet(self._key)

    def _get_or_create_master_key(self):
        """머신 고유의 마스터 키 생성 (간이 보안)"""
        # 실제로는 사용자 비밀번호를 받거나 OS 보안 키체인을 쓰는게 좋음
        # 여기서는 PC 이름과 사용자 이름을 조합하여 고정 키 생성
        import platform
        import getpass
        
        salt = b'school-doc-genie-salt' # 고정 솔트
        machine_seed = (platform.node() + getpass.getuser()).encode()
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(machine_seed))

    def _save_settings(self, settings: dict):
        """설정 딕셔너리를 암호화하여 저장"""
        data = json.dumps(settings).encode()
        encrypted_data = self._fernet.encrypt(data)
        with open(self.config_path, "wb") as f:
            f.write(encrypted_data)

    def _load_settings(self) -> dict:
        """암호화된 설정을 복호화하여 딕셔너리로 반환"""
        if not self.config_path.exists():
            return {}
        try:
            with open(self.config_path, "rb") as f:
                encrypted_data = f.read()
            decrypted_data = self._fernet.decrypt(encrypted_data)
            return json.loads(decrypted_data.decode())
        except Exception:
            return {}

    def set_api_key(self, api_key: str):
        settings = self._load_settings()
        settings['gemini_api_key'] = api_key
        self._save_settings(settings)

    def get_api_key(self) -> str:
        return self._load_settings().get('gemini_api_key')

    def set_config(self, key: str, value):
        """임의의 설정값 저장"""
        settings = self._load_settings()
        settings[key] = value
        self._save_settings(settings)

    def get_config(self, key: str, default=None):
        """임의의 설정값 가져오기"""
        return self._load_settings().get(key, default)

    def has_api_key(self) -> bool:
        return self.get_api_key() is not None

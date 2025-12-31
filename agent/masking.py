
import re

class MaskingService:
    def __init__(self, whitelist: list = None):
        self.whitelist = whitelist or []
        
        # 정규표현식 패턴 정의
        self.patterns = {
            # 주민등록번호: 000000-0000000 -> 000000-*******
            "resident_number": re.compile(r'\d{6}-\d{7}'),
            
            # 전화번호: 010-0000-0000 -> 010-****-****
            "phone": re.compile(r'01[016789]-?\d{3,4}-?\d{4}'),
            
            # 이메일: user@example.com -> u***@example.com
            "email": re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'),
            
            # 이름 (간단한 버전): 2~4글자 한글 (조사 제외 등 복잡한 로직은 추후 고도화)
            "name": re.compile(r'([가-힣]{2,4})\s*(?:선생님|교사|학부모|귀하)')
        }

    def mask_pii(self, text: str) -> str:
        """agent_main.py에서 기대하는 비식별화 메서드 명칭"""
        return self.mask_text(text)

    def mask_text(self, text: str) -> str:
        if not text:
            return ""

        masked = text
        
        # 1. 주민번호 마스킹 (█ 사용)
        masked = self.patterns["resident_number"].sub(lambda m: m.group()[:7] + "███████", masked)
        
        # 2. 전화번호 마스킹
        def mask_phone(m):
            phone = m.group()
            nums = re.findall(r'\d', phone)
            if len(nums) >= 10:
                # 010-1234-5678 -> 010-████-5678
                return phone.replace("".join(nums[3:7]), "████")
            return phone
            
        masked = self.patterns["phone"].sub(mask_phone, masked)
        
        # 3. 이메일 마스킹 -> 실무용으로 마스킹 제외 (사용자 요청)
        # masked = self.patterns["email"].sub(mask_email, masked)
        
        # 4. 이름 마스킹 (선생님, 교사 등 직위와 결합된 경우)
        def mask_name(m):
            name = m.group(1)
            # 홍길동 -> 홍█동, 이순신 -> 이█신
            if len(name) >= 3:
                return name[0] + "█" + name[2:] + m.group().replace(name, "")
            elif len(name) == 2:
                return name[0] + "█" + m.group().replace(name, "")
            return m.group()

        masked = self.patterns["name"].sub(mask_name, masked)
        
        return masked

if __name__ == "__main__":
    service = MaskingService()
    sample = "교사 홍길동 선생님 (010-1234-5678, test@gmail.com, 900101-1234567)"
    print(f"Original: {sample}")
    print(f"Masked:   {service.mask_text(sample)}")

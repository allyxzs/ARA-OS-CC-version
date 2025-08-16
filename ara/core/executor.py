import subprocess
import tempfile
from pathlib import Path
import sys

class SafeExecutor:
    def __init__(self, timeout=10, memory_limit=100):
        self.timeout = timeout
        self.memory_limit = memory_limit

    def run(self, code: str) -> tuple:
        try:
            with tempfile.NamedTemporaryFile(
                mode='w', suffix='.py', 
                delete=False, encoding='utf-8'
            ) as tmp:
                tmp.write(code)
                tmp_path = tmp.name
            
            result = subprocess.run(
                [sys.executable, tmp_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=self.timeout
            )
            return (result.returncode == 0, result.stdout + result.stderr)
        except Exception as e:
            return (False, f"Erro na execução: {str(e)}")
        finally:
            try:
                Path(tmp_path).unlink(missing_ok=True)
            except:
                pass

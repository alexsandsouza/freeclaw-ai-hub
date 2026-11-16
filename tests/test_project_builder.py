import importlib.util
import io
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "local-engine"
spec = importlib.util.spec_from_file_location("proposal_parser", ROOT / "proposal_parser.py")
parser = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parser)

class BuilderTests(unittest.TestCase):
    def test_extract_multiple_files(self):
        md = '### Arquivo: src/main.py\n```python\nprint("ok")\n```\n\n### Arquivo: tests/test_main.py\n```python\nassert 1 == 1\n```'
        files = parser.extract_files(md)
        self.assertEqual(sorted(files), ["src/main.py", "tests/test_main.py"])
        self.assertIn('print("ok")', files["src/main.py"])
        binary = parser.build_zip(files)
        with zipfile.ZipFile(io.BytesIO(binary)) as archive:
            self.assertIn("REVIEW_REQUIRED.md", archive.namelist())
            self.assertIn("tests/test_main.py", archive.namelist())

    def test_refuse_path_traversal(self):
        for name in ["src/../evil.py","/tmp/pwn.py","src\\evil.py","other/evil.py","src/foo.sh","C:/tmp/a.py"]:
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    parser.safe_path(name)

    def test_reject_duplicate_and_no_code(self):
        self.assertRaises(ValueError,parser.extract_files,"Apenas um plano, sem blocos de arquivo")
        md = '### Arquivo: src/a.py\n```python\nx=1\n```\n### Arquivo: src/a.py\n```python\nx=2\n```'
        self.assertRaises(ValueError, parser.extract_files, md)

    def test_secrets_blocked(self):
        md = '### Arquivo: src/a.py\n```python\nk="nvapi-' + ('a' * 25) + '"\n```'
        self.assertRaises(ValueError,parser.extract_files,md)

    def test_missing_fenced_python(self):
        self.assertRaises(ValueError, parser.extract_files, '### Arquivo: src/a.py\nprint("not fenced")')

if __name__ == "__main__":
    unittest.main()

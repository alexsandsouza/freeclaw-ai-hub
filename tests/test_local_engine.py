import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ENGINE = Path(__file__).resolve().parents[1] / "local-engine" / "engine.py"
spec = importlib.util.spec_from_file_location("freeclaw_engine", ENGINE)
engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)

class EngineTests(unittest.TestCase):
    def test_valid_document(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "spec.md"
            f.write_text("# PRD\nRF-001", encoding="utf8")
            self.assertIn("RF-001", engine.load_specification(f))

    def test_secret_blocked(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "spec.md"
            f.write_text("nvapi-" + "x" * 30)
            with self.assertRaises(ValueError):
                engine.load_specification(f)

    def test_messages(self):
        m = engine.make_messages("Create plan", "RF-001")
        self.assertEqual(len(m), 2)
        self.assertIn("RF-001", m[1]["content"])

    def test_mock_nvidia(self):
        class Response:
            def __enter__(self): return self
            def __exit__(self, *args): return None
            def read(self, *args): return b'{"choices":[{"message":{"content":"Draft proposal"}}]}'
        with patch.object(engine.urllib.request, "urlopen", return_value=Response()):
            answer = engine.call_nvidia("test", "sample/model", engine.make_messages("Plan", "RF-001"))
        self.assertEqual(answer, "Draft proposal")

if __name__ == "__main__":
    unittest.main()

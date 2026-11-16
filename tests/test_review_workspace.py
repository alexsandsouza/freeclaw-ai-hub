import importlib.util
import io
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "local-engine"
sys.path.insert(0, str(ROOT))
spec = importlib.util.spec_from_file_location("review_workspace", ROOT / "review_workspace.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class WorkspaceTests(unittest.TestCase):
    def test_compare_new_and_modified_without_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "src").mkdir()
            original = root / "src" / "main.py"
            original.write_text("print('original')\n", encoding="utf-8")
            files = {"src/main.py":"print('proposed')\n", "tests/test_main.py":"assert True\n"}
            diff = mod.compare_files(root,files)
            self.assertEqual(diff["src/main.py"]["status"],"alterado")
            self.assertEqual(diff["tests/test_main.py"]["status"],"novo")
            self.assertIn("-print('original')", diff["src/main.py"]["diff"])
            self.assertEqual(original.read_text(encoding="utf-8"), "print('original')\n")
            self.assertFalse((root / "tests").exists())

    def test_selective_zip_export(self):
        files={"src/main.py":"print('safe')\n","tests/test_main.py":"assert 1\n"}
        data=mod.export_selected(files,["src/main.py"])
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            self.assertIn("src/main.py",z.namelist())
            self.assertNotIn("tests/test_main.py",z.namelist())
        self.assertEqual(set(mod.read_proposal_zip(data)),{"src/main.py"})

    def test_invalid_selections(self):
        with self.assertRaises(ValueError):
            mod.export_selected({"src/main.py":"pass\n"},["src/other.py"])
        with self.assertRaises(ValueError):
            mod.export_selected({"src/main.py":"pass\n"},[])

    def test_refuse_symlink_escape(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            outside=root/"outside"
            outside.mkdir()
            (root/"src").symlink_to(outside, target_is_directory=True)
            with self.assertRaises(ValueError):
                mod.compare_files(root,{"src/main.py":"pass\n"})

    def test_reject_traversal_in_zip(self):
        buf=io.BytesIO()
        with zipfile.ZipFile(buf,"w") as z:
            z.writestr("../bad.py","print('bad')")
        with self.assertRaises(ValueError):
            mod.read_proposal_zip(buf.getvalue())

    def test_reject_zip_bomb_member(self):
        buf=io.BytesIO()
        with zipfile.ZipFile(buf,"w",compression=zipfile.ZIP_DEFLATED) as z:
            z.writestr("src/big.py","x"*100_001)
        with self.assertRaises(ValueError):
            mod.read_proposal_zip(buf.getvalue())

if __name__ == "__main__":
    unittest.main()

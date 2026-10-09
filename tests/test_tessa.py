import hashlib
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import tessa  # noqa: E402

SCRIPT = os.path.join(ROOT, "tessa.py")
CONTENT = b"hello world\n"
SHA256 = hashlib.sha256(CONTENT).hexdigest()


def run(*args, stdin=""):
    return subprocess.run(
        [sys.executable, SCRIPT, *args], input=stdin, capture_output=True, text=True
    )


class TessaTests(unittest.TestCase):
    def setUp(self):
        fd, self.path = tempfile.mkstemp()
        with os.fdopen(fd, "wb") as f:
            f.write(CONTENT)
        self.addCleanup(os.remove, self.path)

    def test_compute_hash_matches_hashlib(self):
        self.assertEqual(tessa.compute_hash(self.path, "sha256"), SHA256)

    def test_normalize_accepts_prefix_and_case(self):
        self.assertEqual(
            tessa.normalize_expected_hash(f"SHA256:{SHA256.upper()}", "sha256"), SHA256
        )

    def test_normalize_rejects_bad_input(self):
        for bad in ("", "xyz", SHA256[:-1]):
            with self.assertRaises(ValueError):
                tessa.normalize_expected_hash(bad, "sha256")

    def test_match_exit_0(self):
        self.assertEqual(run("-f", self.path, "-e", SHA256).returncode, 0)

    def test_mismatch_exit_1(self):
        self.assertEqual(run("-f", self.path, "-e", "0" * 64).returncode, 1)

    def test_malformed_expected_exit_2(self):
        r = run("-f", self.path, "-e", "abc")
        self.assertEqual(r.returncode, 2)
        self.assertIn("characters", r.stderr)

    def test_missing_file_exit_2_on_stderr(self):
        r = run("-f", "/nonexistent/file", "-g")
        self.assertEqual(r.returncode, 2)
        self.assertIn("not found", r.stderr)
        self.assertNotIn("not found", r.stdout)

    def test_quiet_generate_prints_only_hash(self):
        r = run("-f", self.path, "-g", "-q")
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), SHA256)

    def test_quiet_compare_prints_nothing(self):
        r = run("-f", self.path, "-e", SHA256, "-q")
        self.assertEqual((r.returncode, r.stdout), (0, ""))

    def test_no_ansi_when_piped(self):
        self.assertNotIn("\033", run("-f", self.path, "-e", SHA256).stdout)

    def test_flag_misuse_exit_2(self):
        self.assertEqual(run("-e", SHA256).returncode, 2)
        self.assertEqual(run("-g").returncode, 2)
        self.assertEqual(run("-f", self.path, "-g", "-e", SHA256).returncode, 2)
        self.assertEqual(run("-f", self.path).returncode, 2)

    def test_eof_in_menu_exits_cleanly(self):
        r = run(stdin="")
        self.assertEqual(r.returncode, 0)
        self.assertNotIn("Traceback", r.stderr)


if __name__ == "__main__":
    unittest.main()

"""BUG1142/YKT910 independent API literal/role oracle, never Production-derived expected."""
from pathlib import Path
import unittest


class ApiLiteralOracleTest(unittest.TestCase):
    def test_api_clone_contains_only_independent_api_terminal_literal_and_role(self):
        root=Path(__file__).resolve().parents[2]
        test=(root/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/bootstrap/ApiTerminalCaptureTest.java').read_text()
        production=(root/'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/bootstrap/ApiTerminalCapture.java').read_text()
        self.assertIn('"API process stopped\\nAPI fixed PT native capture complete\\n"',test)
        self.assertNotIn('WEB',test);self.assertNotIn('Web',test)
        self.assertIn('ServiceConfigFiles.Service.API',production)
        self.assertNotIn('ServiceConfigFiles.Service.WEB',production)
        web=(root/'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/bootstrap/WebTerminalCaptureTest.java').read_text()
        self.assertIn('"WEB process stopped\\nWEB fixed PT native capture complete\\n"',web)


if __name__=='__main__':unittest.main()

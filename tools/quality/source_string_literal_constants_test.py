"""Independent literal/private-field planning fixtures; proposal never authorizes application."""
import pathlib
import hashlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
JDK = pathlib.Path('/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin')


class LiteralProposal(unittest.TestCase):
    def run_fixture(self, fixture, relative='Fixture.java', duplicate_request=False):
        with tempfile.TemporaryDirectory(prefix='pgpt-literal-constants-') as folder:
            base = pathlib.Path(folder); source = base / 'original'; source.mkdir(); classes = base / 'tool'; classes.mkdir()
            target = source / relative; target.write_text(fixture); before = target.read_bytes()
            lines = fixture.splitlines(); selected = next((i, text.index('"request"') + 1) for i, text in enumerate(lines, 1) if '"request"' in text)
            request = f'{relative}\t{selected[0]}\t{selected[1]}\n'
            requests = base / 'requests.tsv'; requests.write_text(request * (2 if duplicate_request else 1))
            compiled = subprocess.run([str(JDK / 'javac'), '-Xlint:all', '-Werror', '-d', str(classes), str(ROOT / 'tools/quality/IsolatedSourceOutput.java'), str(ROOT / 'tools/quality/SourcePrivateFieldRename.java'), str(ROOT / 'tools/quality/SourceStringLiteralConstants.java'), str(ROOT / 'tools/quality/SourceStringLiteralProof.java')], capture_output=True, text=True, timeout=30)
            self.assertEqual(0, compiled.returncode, compiled.stderr)
            out = base / 'candidate'
            run = subprocess.run([str(JDK / 'java'), '-cp', str(classes), 'SourceStringLiteralConstants', str(source), '', str(requests), str(out)], capture_output=True, text=True, timeout=30)
            self.assertEqual(before, target.read_bytes())
            if duplicate_request:
                self.assertNotEqual(0, run.returncode); self.assertFalse(out.exists()); return '', run.stdout
            self.assertEqual(0, run.returncode, run.stderr)
            candidate = (out / relative).read_text()
            plan = base / 'plan.tsv'; plan.write_text(run.stdout)
            proof_command = [str(JDK / 'java'), '-cp', str(classes), 'SourceStringLiteralProof', str(source), str(out), '', str(plan)]
            proof = subprocess.run(proof_command, capture_output=True, text=True, timeout=30)
            self.assertEqual(0, proof.returncode, proof.stderr)
            self.assertIn('FULL_SEMANTIC_ABI_VALUES_IDENTICAL\t1', proof.stdout)
            if 'CONSTANT\t' in run.stdout:
                expected_hash = hashlib.sha256('request'.encode('utf-16-be')).hexdigest()
                self.assertIn(expected_hash, run.stdout)
                for tampered in [candidate.replace('"request"', '"changed"', 1), candidate.replace('String b()', 'Object b()', 1)]:
                    self.assertNotEqual(candidate, tampered)
                    (out / relative).write_text(tampered)
                    negative = subprocess.run(proof_command, capture_output=True, text=True, timeout=30)
                    self.assertNotEqual(0, negative.returncode)
                (out / relative).write_text(candidate)
            built = base / 'built'; built.mkdir()
            actual = subprocess.run([str(JDK / 'javac'), '-Xlint:all', '-Werror', '-d', str(built), str(out / relative)], capture_output=True, text=True, timeout=30)
            self.assertEqual(0, actual.returncode, actual.stderr)
            if 'public static void main' in fixture:
                execution = subprocess.run([str(JDK / 'java'), '-cp', str(built), 'Fixture'], capture_output=True, text=True, timeout=30)
                self.assertEqual(0, execution.returncode, execution.stderr)
                self.assertEqual('request/request/request/request', execution.stdout)
            return candidate, run.stdout

    def test_existing_field_forward_reference_nested_record_and_collision(self):
        fixture = '''class Fixture {
 static final String LITERAL_REQUEST = "collision";
 static final String EARLY = "request";
 String a() {return "request";}
 String b() {return "request";}
 record Nested(int n) {String c(){return "request";}}
 public static void main(String[] a){System.out.print(EARLY+"/"+new Fixture().a()+"/"+new Fixture().b()+"/"+new Nested(1).c());}
}'''
        candidate, report = self.run_fixture(fixture)
        self.assertIn('private static final java.lang.String LITERAL_REQUEST_VALUE = "request";', candidate)
        self.assertEqual(1, candidate.count('"request"'))
        self.assertIn('PROPOSED_ONLY\t1', report)

    def test_record_and_header_comments_are_preserved(self):
        fixture = '''/* { not a body */ record Fixture(int n) /* header { comment */ {
 String a() {return "request";}
 String b() {return "request";}
 String c() {return "request";}
 String d() {return "request";}
}'''
        candidate, report = self.run_fixture(fixture)
        self.assertTrue(candidate.startswith('/* { not a body */ record Fixture(int n) /* header { comment */ {'))
        self.assertEqual(1, candidate.count('"request"'))

    def test_interface_held_and_duplicate_request_rejected(self):
        fixture = 'interface Fixture {String a="request",b="request",c="request",d="request";}\n'
        candidate, report = self.run_fixture(fixture)
        self.assertEqual(fixture, candidate); self.assertIn('HELD', report); self.assertIn('PROPOSED_ONLY\t0', report)
        self.run_fixture('class Fixture {String a="request",b="request",c="request",d="request";}\n', duplicate_request=True)


if __name__ == '__main__':
    unittest.main()

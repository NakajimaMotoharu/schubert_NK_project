"""Check the architecture report against six self-owned synthetic JARs."""

import hashlib
import os
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TOOLCHAIN = ROOT.parent / "toolchain"
JAVA = TOOLCHAIN / "jdk-25.0.4/bin"
TOOL = ROOT / "tools/quality/architecture/ModuleDependencyAudit.java"
MODULES = ("api", "batch", "bootstrap", "protocol", "storage", "web")
DEPENDENCIES = (
    (TOOLCHAIN / "architecture/archunit-1.4.2/archunit-1.4.2.jar",
     "6d8adf69a3f109ebe1b395764feb07f919e9e0e2ab5e2ea141d2e6251ba7d17f"),
    (TOOLCHAIN / "m2/repository/org/slf4j/slf4j-api/2.0.18/slf4j-api-2.0.18.jar",
     "44508fd1576500688c790b190acdd16fec4f8c79a3e0b900afd70503cf055f55"),
)


class ModuleDependencyReportTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        work = Path(cls.enterClassContext(tempfile.TemporaryDirectory(prefix="pgpt-arch-report-")))
        sources = []
        for module in MODULES:
            type_name = module.capitalize() + "Marker"
            source = work / (type_name + ".java")
            source.write_text(f"package synthetic; public interface {type_name} {{}}\n")
            sources.append((module, type_name, source))
        sink = work / "InterruptedReport.java"
        sink.write_text(
            """import java.io.IOException;
import java.io.OutputStream;
import java.io.PrintStream;

public final class InterruptedReport {
  public static void main(String[] args) throws IOException {
    var original = System.out;
    System.setOut(new PrintStream(new OutputStream() {
      private int remaining = 30;

      @Override
      public void write(int value) throws IOException {
        if (remaining == 0) throw new IOException("synthetic report sink");
        remaining--;
        original.write(value);
        original.flush();
      }
    }));
    ModuleDependencyAudit.main(args);
  }
}
"""
        )
        for dependency, expected in DEPENDENCIES:
            if hashlib.sha256(dependency.read_bytes()).hexdigest() != expected:
                raise ValueError("pinned architecture test dependency differs")
        classpath = os.pathsep.join(str(dependency) for dependency, _ in DEPENDENCIES)
        subprocess.run(
            [JAVA / "javac", "--release", "25", "-proc:none", "-cp", classpath, "-d", work,
             TOOL, sink, *(source for _, _, source in sources)],
            check=True, capture_output=True, timeout=45,
        )
        cls.java = [JAVA / "java", "-cp", f"{work}{os.pathsep}{classpath}"]
        cls.jars = []
        for module, type_name, _ in sources:
            member = f"synthetic/{type_name}.class"
            jar = work / f"{module}.jar"
            with zipfile.ZipFile(jar, "x") as archive:
                archive.write(work / member, member)
            cls.jars.append(f"{module}={jar}")

    def run_report(self, launch_class):
        return subprocess.run([*self.java, launch_class, *self.jars],
                              capture_output=True, timeout=45, check=False)

    def test_complete_report_lists_the_six_inputs_and_no_violations(self):
        result = self.run_report("ModuleDependencyAudit")
        self.assertEqual(0, result.returncode, result.stderr)
        rows = result.stdout.decode("ascii").splitlines()
        self.assertEqual("ARCHUNIT\t1.4.2\t6\t6", rows[0])
        self.assertEqual([f"MODULE\t{module}\t1" for module in MODULES], rows[1:7])
        self.assertTrue(rows[-1].startswith("INSPECTED\t"))
        self.assertFalse(any(row.startswith("FINDING\t") for row in rows))

    def test_interrupted_report_cannot_return_success(self):
        result = self.run_report("InterruptedReport")
        self.assertEqual(30, len(result.stdout), result.stdout)
        self.assertNotIn(b"INSPECTED", result.stdout)
        self.assertEqual(1, result.returncode, result.stderr)
        self.assertIn(b"architecture audit output incomplete", result.stderr)

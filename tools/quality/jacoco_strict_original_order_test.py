"""Independent writer-order vectors for the Java and Python strict coverage readers."""

import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import tempfile
import unittest

from jacoco_readonly_exec_subset import decode


REPOSITORY = Path(__file__).resolve().parents[2]
BIN = REPOSITORY.parent / 'toolchain/jdk-25.0.4/bin'
TOOL = REPOSITORY / 'tools/quality/jacoco/UnfilteredCodeMeasurement.java'
COMPILE_PROOF = (
    REPOSITORY / 'evidence/01_PT/018_NK-OPS-001/evidence'
    / 'PG31432-generated-code-supplemental-tool-v1/compile.json'
)
JAVA_MAIN = 'org.jacoco.core.internal.analysis.UnfilteredCodeMeasurement'
NAME = 'orderfixture/One'
SECOND = 'orderfixture/Two'
HEADER = bytes.fromhex('01 c0c0 1007')
SESSION = bytes.fromhex('10 0003 52554e') + struct.pack('>qq', 1000, 1001)


def class_crc(physical):
    """Calculate the documented CRC64 over the original Java 25 class bytes."""
    crc = 0
    for byte in physical:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ (0xd800000000000000 if crc & 1 else 0)
    return crc


def class_record(name, crc):
    encoded = name.encode('ascii')
    return b'\x11' + struct.pack('>QH', crc, len(encoded)) + encoded + b'\x01\x01'


class StrictOriginalOrderTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        work = cls.enterClassContext(tempfile.TemporaryDirectory(prefix='pgpt-exec-order-'))
        cls.directory = Path(work)
        pins = json.loads(COMPILE_PROOF.read_bytes())['dependencies']
        for item in pins:
            content = Path(item['path']).read_bytes()
            if hashlib.sha256(content).hexdigest() != item['sha256']:
                raise ValueError('pinned JaCoCo/ASM dependency differs')
        classpath = os.pathsep.join(item['path'] for item in pins)
        fixture = cls.directory / 'One.java'
        fixture.write_text(
            'package orderfixture; public interface One { default int value() { return 7; } }\n'
        )
        other = cls.directory / 'Two.java'
        other.write_text(
            'package orderfixture; public interface Two { default int value() { return 9; } }\n'
        )
        subprocess.run(
            [BIN / 'javac', '--release', '25', '-Xlint:all', '-Werror', '-proc:none',
             '-cp', classpath, '-d', cls.directory, TOOL, fixture, other],
            check=True, capture_output=True, timeout=30,
        )
        cls.target = cls.directory / (NAME + '.class')
        cls.crc = class_crc(cls.target.read_bytes())
        cls.entry = class_record(NAME, cls.crc)
        cls.second = cls.directory / (SECOND + '.class')
        cls.second_crc = class_crc(cls.second.read_bytes())
        cls.command = [BIN / 'java', '-cp', f'{cls.directory}{os.pathsep}{classpath}', JAVA_MAIN]

    def measure(self, raw, *targets, strict=True):
        execution = self.directory / (self._testMethodName + '.exec')
        execution.write_bytes(raw)
        flags = ['--strict-original-exec'] if strict else []
        return subprocess.run(
            [*self.command, *flags, execution, *(targets or (self.target,))],
            capture_output=True, timeout=30,
        )

    def test_session_then_class_keeps_target_identity(self):
        raw = HEADER + SESSION + self.entry
        self.assertEqual([0], decode(raw, {NAME})['classes'][NAME]['hitProbeIds'])
        result = self.measure(raw)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn(f'CLASS\t{NAME}\t{self.crc:016x}\ttrue\t1\t'.encode(), result.stdout)

    def test_session_without_class_retains_unmeasured_target(self):
        raw = HEADER + SESSION
        self.assertEqual({}, decode(raw, set())['classes'])
        result = self.measure(raw)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn(f'CLASS\t{NAME}\t{self.crc:016x}\tfalse\t1\t'.encode(), result.stdout)

    def test_class_before_session_is_rejected_by_both_strict_readers(self):
        raw = HEADER + self.entry + SESSION
        with self.subTest(reader='Python'):
            with self.assertRaisesRegex(ValueError, 'execution class before original session'):
                decode(raw, {NAME})
        with self.subTest(reader='Java'):
            result = self.measure(raw)
            self.assertEqual(1, result.returncode, result.stdout)
            self.assertIn(b'execution class before original session', result.stderr)
            self.assertEqual(b'', result.stdout)
        with self.subTest(reader='Java legacy'):
            self.assertEqual(0, self.measure(raw, strict=False).returncode)

    def test_unselected_class_before_session_is_also_rejected(self):
        raw = HEADER + class_record('orderfixture/Other', self.crc ^ 1) + SESSION + self.entry
        with self.subTest(reader='Python'):
            with self.assertRaisesRegex(ValueError, 'execution class before original session'):
                decode(raw, {NAME})
        with self.subTest(reader='Java'):
            result = self.measure(raw)
            self.assertEqual(1, result.returncode, result.stdout)
            self.assertIn(b'execution class before original session', result.stderr)
            self.assertEqual(b'', result.stdout)

    def test_crc006_later_class_crc_mismatch_leaves_no_measurement(self):
        raw = HEADER + SESSION + self.entry + class_record(SECOND, self.second_crc ^ 1)
        for strict in (True, False):
            with self.subTest(strict=strict):
                result = self.measure(raw, self.target, self.second, strict=strict)
                self.assertEqual(1, result.returncode, result.stderr)
                self.assertIn(b'execution/class CRC mismatch', result.stderr)
                self.assertEqual(b'', result.stdout)

    def test_crc007_later_duplicate_target_leaves_no_measurement(self):
        raw = HEADER + SESSION + self.entry
        for strict in (True, False):
            with self.subTest(strict=strict):
                result = self.measure(raw, self.target, self.target, strict=strict)
                self.assertEqual(1, result.returncode, result.stderr)
                self.assertIn(b'duplicate class input', result.stderr)
                self.assertEqual(b'', result.stdout)

    def test_crc008_complete_output_preserves_requested_order_and_counters(self):
        raw = HEADER + SESSION + self.entry + class_record(SECOND, self.second_crc)
        result = self.measure(raw, self.second, self.target)
        self.assertEqual(0, result.returncode, result.stderr)
        rows = [tuple(line.split('\t')) for line in result.stdout.decode('ascii').splitlines()]
        self.assertEqual(
            [('CLASS', SECOND), ('METHOD', SECOND), ('CLASS', NAME), ('METHOD', NAME)],
            [row[:2] for row in rows],
        )
        for record, crc, method in ((rows[0], self.second_crc, rows[1]), (rows[2], self.crc, rows[3])):
            self.assertEqual((f'{crc:016x}', 'true', '1'), record[2:5])
            self.assertEqual(('value', '()I'), method[2:4])
            self.assertIn('INSTRUCTION:0:2', record)
            self.assertIn('LINE:0:1', record)
            self.assertIn('BRANCH:0:0', record)
            self.assertIn('METHOD:0:1', record)
            self.assertIn('CLASS:0:1', record)


if __name__ == '__main__':
    unittest.main(verbosity=2)

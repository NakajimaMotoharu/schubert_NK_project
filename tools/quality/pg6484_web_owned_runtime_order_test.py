"""Reader checks against compile-only fixtures; never calls Production code or certifies PT."""
import struct
import subprocess
import unittest
import pg6484_web_owned_runtime_order as subject
from classfile_field_flags import fields


class Structure(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Preserved unsuccessful Testcompile source has completed Main compile, not a PT PASS.
        cls.cp = subject.W/'pg6480-web-owned-component-v2/source/src/schubert-nk-web/target/classes'
        cls.data = (cls.cp/(subject.CLS.replace('.', '/')+'.class')).read_bytes()
        def read(verbose):
            return subprocess.check_output([str(subject.TC/'jdk-25.0.4/bin/javap'), '-p', '-v' if verbose else '-c', '-s', '-classpath', str(cls.cp), subject.CLS], text=True)
        cls.raw, cls.verbose = read(False), read(True)

    def test_actual_compiled_shape_and_five_flag_negatives(self):
        result = subject.analyze(self.raw, self.verbose, self.data)
        self.assertTrue(result['fixedDefaultFourBindings'])
        self.assertEqual(6, len(result['immediateCaptures']))
        for name in (*subject.FLAGS, 'ownerLock'):
            changed = bytearray(self.data); item = fields(self.data)[name.encode()]
            struct.pack_into('>H', changed, item['offset'], 0x0002)
            with self.assertRaisesRegex(ValueError, 'five private volatile'):
                subject.analyze(self.raw, self.verbose, bytes(changed))

    def test_missing_default_reference_or_monitor_rejected(self):
        with self.assertRaisesRegex(ValueError, 'fixed Production method reference'):
            subject.analyze(self.raw, self.verbose.replace('LinuxDirectoryCalls.create:', 'Unrelated.create:'), self.data)
        with self.assertRaisesRegex(ValueError, 'same private ownerLock'):
            subject.analyze(self.raw.replace('monitorenter', 'nop'), self.verbose, self.data)

    def test_bootstrap_numbers_resolve_but_real_target_change_is_not_waived(self):
        old = subject.W/'pg6466-nio-collision-selected-v1/source'/subject.JAR
        def read(verbose):
            return subprocess.check_output([str(subject.TC/'jdk-25.0.4/bin/javap'), '-p', '-v' if verbose else '-c', '-s', '-classpath', str(old), subject.CLS], text=True)
        before, after = subject.methods(read(False)), subject.methods(self.raw)
        old_verbose = read(True)
        for key in before:
            if key.startswith('  '+subject.CLS+'(') or ' void start()' in key: continue
            self.assertEqual(subject.resolved_body(before[key], old_verbose), subject.resolved_body(after[key], self.verbose), key)
        ready = next(k for k in before if ' boolean ready()' in k)
        modified = self.verbose.replace('WebManagementServer.ready:()Z', 'WebManagementServer.unrelated:()Z')
        self.assertNotEqual(self.verbose, modified)
        self.assertNotEqual(subject.resolved_body(before[ready], old_verbose), subject.resolved_body(after[ready], modified))


if __name__ == '__main__': unittest.main()

import inspect
import unittest
import pg3294_protocol_directional_oracle as subject


class DirectionalOracleToolTest(unittest.TestCase):
    def test_exact_real_dto_mutation_swaps_both_directions_without_wire_key_loss(self):
        raw = (subject.ROOT / subject.FILES[2]).read_text()
        changed = subject.mutate_dto(raw)
        self.assertIn('Map.entry("Username", TypedFieldValues.text(password))', changed)
        self.assertIn('Map.entry("Password", TypedFieldValues.text(username))', changed)
        self.assertIn('TypedFieldValues.requiredString(fields, "Password"),\n        TypedFieldValues.requiredString(fields, "Username")', changed)
        self.assertNotEqual(raw, changed)
        with self.assertRaises(ValueError):
            subject.mutate_dto(raw.replace('"Username"', '"missing"'))

    def test_stable_wrong_bytes_does_not_change_real_file_and_payload_compiles(self):
        path = subject.ROOT / subject.FILES[3]; original = path.read_text()
        changed = subject.mutate_bytes(original)
        self.assertIn("data[0] = (byte) 'X'", changed)
        self.assertEqual(original, path.read_text())
        with self.assertRaises(ValueError):
            subject.mutate_bytes('missing anchor')
        code = 'INPUT={}\n' + '\n'.join(inspect.getsource(f) for f in [subject.require, subject.swap_once, subject.mutate_dto, subject.mutate_bytes, subject.fixed_jdk, subject.launcher_path]) + '\n' + subject.SERVER
        compile(code, '<fixed two independent oracles>', 'exec')
        self.assertNotIn('javaagent', code)

    def test_server_jdk_is_bound_to_original_actual_java_home(self):
        base = subject.Path('/home/mini/schubert-nk-pgpt')
        home = str(base / 'tools/jdk-25.0.4')
        self.assertEqual(base / 'tools/jdk-25.0.4/bin', subject.fixed_jdk([home], base))
        for homes in [[], [home, home], [str(base / 'toolchain/jdk-25.0.4')], ['/foreign/jdk'], [None]]:
            with self.subTest(homes=homes), self.assertRaises(ValueError):
                subject.fixed_jdk(homes, base)
        for name in ['JAVA_TOOL_OPTIONS', 'JDK_JAVA_OPTIONS', '_JAVA_OPTIONS']:
            self.assertIn(name, subject.SERVER)

    def test_exact_same_engine_version_launcher_not_application_classpath_guess(self):
        repo = subject.Path('/qualified/m2')
        engine = repo / 'org/junit/platform/junit-platform-engine/1.2.3/junit-platform-engine-1.2.3.jar'
        self.assertEqual(repo / 'org/junit/platform/junit-platform-launcher/1.2.3/junit-platform-launcher-1.2.3.jar', subject.launcher_path([engine], repo))
        for engines in [[], [engine, engine], [subject.Path('/foreign/1.2.3/junit-platform-engine-1.2.3.jar')], [engine.with_name('junit-platform-engine-9.9.jar')]]:
            with self.subTest(engines=engines), self.assertRaises(ValueError):
                subject.launcher_path(engines, repo)


if __name__ == '__main__':
    unittest.main()

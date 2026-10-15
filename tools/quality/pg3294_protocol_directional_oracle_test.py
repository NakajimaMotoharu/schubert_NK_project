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
        code = 'INPUT={}\n' + '\n'.join(inspect.getsource(f) for f in [subject.require, subject.swap_once, subject.mutate_dto, subject.mutate_bytes]) + '\n' + subject.SERVER
        compile(code, '<fixed two independent oracles>', 'exec')
        self.assertNotIn('javaagent', code)


if __name__ == '__main__':
    unittest.main()

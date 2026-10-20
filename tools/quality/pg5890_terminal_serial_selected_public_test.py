import unittest
import pg5890_terminal_serial_selected_public as target


class Complete83ProjectionGenerationTest(unittest.TestCase):
    def test_both_output_counts_and_six_real_design_identities(self):
        raw=target.reader_source()
        self.assertEqual(2,raw.count("'tests':83"));self.assertNotIn("'tests':81",raw)
        self.assertIn('range(1,7)',raw);self.assertIn('sum(map(len,actual.values()))==83',raw)
        self.assertEqual(6,len(target.TERMINAL_CASES))
        self.assertIn('pg5880-terminal-serial83-v1',raw);self.assertIn('PG5882-terminal-serial-static-v1',raw)
        self.assertNotIn('Popen',raw);self.assertNotIn('subprocess.run',raw)


if __name__=='__main__':unittest.main()

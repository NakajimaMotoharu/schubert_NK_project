import ast
import unittest
from pg1025_cold_owned_native import source

class NativeBinding(unittest.TestCase):
    def test_current_cold_paths_source_modes_and_reservation(self):
        raw=source();ast.parse(raw)
        self.assertIn("sys.argv[1]in ('stage','verify')",raw)
        self.assertIn('cbca8738-3b24-4090-b77c-bf029677cdd6',raw)
        self.assertNotIn('cc9ed874',raw);self.assertNotIn('execute',raw)
        self.assertIn("'genuineParentAccepted':False",raw)
        self.assertIn('Pg1023ColdOwnedReadback '+"'+action",raw)
        self.assertIn('pg1024-cold-readback-frozen-v1.safe.json',raw)
        self.assertLess(raw.index("'.begin.safe.json'"),raw.index("if action=='stage':"))
        self.assertIn("open('x')",raw)
    def test_all_payload_hashes_and_newonly_guest_stage(self):
        raw=source()
        self.assertIn('assert not os.path.lexists(root)',raw)
        self.assertIn("set(FILES)|{'payload-sha256.json'}",raw)
        self.assertIn('hashlib.sha256((root/name).read_bytes()).hexdigest()==digest',raw)
        self.assertIn('os.chmod(f,0o400)',raw)
        self.assertIn("json.loads((root/'payload-sha256.json').read_text())==FILES",raw)
        self.assertIn('pg1025-stage-v1.exit',raw)
        self.assertNotIn('pg978',raw)

if __name__=='__main__':unittest.main()

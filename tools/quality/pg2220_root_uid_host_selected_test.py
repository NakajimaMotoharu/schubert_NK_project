import unittest
from pyflakes.api import check
from pg2220_root_uid_host_selected import SERVER


class FrozenMainSelection(unittest.TestCase):
    def test_whole_server_no_native_mix_or_main_compile(self):
        self.assertEqual(0,check('INPUT={}\n'+SERVER,'<actual new selected server>'))
        for text in ['source-full-PG2124','PG2220-selected-v1',"INPUT['full']['jarHashes'][m]",
          "INPUT['full']['qualificationInputs'][m]['exec']","fixture_hashes",'Pg2220RootUidLauncher',
          "'tests':'1'",'classByteMismatch','*hosts,str(execfile)',"'MainRecompiled':False"]:
            self.assertIn(text,SERVER)
        self.assertNotIn('PG1590',SERVER);self.assertNotIn('PG1618',SERVER)
        self.assertNotIn("'mvn'",SERVER)
        self.assertNotIn('src/main',SERVER)


if __name__=='__main__':unittest.main()

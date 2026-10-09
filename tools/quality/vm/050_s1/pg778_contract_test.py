"""Full generated namespace and literal stop sequence/fault reuse; old fixtures independently bound."""
import ast
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch
import pg778_sources as p

R=Path(__file__).resolve().parent


def namespace():
    module=types.ModuleType('pg778_owned');module.__file__=str(R/'pg778_owned.py')
    with patch.dict(sys.modules,{'dbus':types.SimpleNamespace()}):exec(compile(p.helper(),'<actual fixed helper>','exec'),module.__dict__)
    return module


class Test(unittest.TestCase):
    def test_namespace_complete_fieldsets_and_source_cohort(self):
        h=namespace();self.assertEqual(18,len(h.FIELDS));self.assertEqual(27,len(h.FIELDS_CONFIGURATION))
        self.assertEqual(4,len(h.EXPECTED));self.assertEqual(('3063762','2dd9f106319e4c79995c8d6880c3f1a6',13884944),h.EXPECTED['schubert-nk-api.service'])
        self.assertIn('80594db5e3a5588a26b05be729e80a40f750a44230f34c3e025f923f365ddba4',p.helper())
        j=p.java();self.assertIn('RootFailedStartRecovery.retirePair',j);self.assertIn('var refs=new References',j)
        self.assertLess(j.index('helper("terminal")'),j.index('files.revoke(invalid,permit)'))
        self.assertLess(j.index('files.revoke(invalid,permit)'),j.index('RootFailedStartRecovery.quarantinePair'))
        self.assertLess(j.index('refs.release();'),j.index('db.rollback();schema.rollback();phase="DATABASE_SCOPE_CLOSE"'))
        for value in ('Pg496','PG493','0.1.0-PG489','ZERO existing intents'):self.assertNotIn(value,j)
        ast.parse(p.helper())

    def test_independent_current_stop_fault_fixture(self):
        raw=p.bind((R/'pg496_timeout_owned_test.py').read_text()).replace('import pg778_timeout_owned as h','import pg778_owned as h')
        for old,new in [('4113865','3072633'),('b656fdfe067a4cb8a542708750af019c','b9c8ad2fabf244939367171499e0eac9'),('25667027','13889925'),('4108080','3066272'),('1dedba9e9ee648fb94eca6232385e018','b49fd80a49a9408e8b8e13dd52f733b5'),('25663790','13886491'),('4105598','3063762'),('730085ab1173444b83c9bf2c8127c94e','2dd9f106319e4c79995c8d6880c3f1a6'),('25662174','13884944'),('3939714','2841798'),('12360e619aa7445684692c59badc7c51','47c9e398cfc043dfa7504bedbe486269'),('25552139','13746502')]:raw=raw.replace(old,new)
        # Golden is an independent old-fault vector rebound to captured public actor literals.
        # No guest, Production or network is called; stop itself is an event stub.
        with patch.dict(sys.modules,{'pg778_owned':namespace()}):exec(compile(raw,'<current literal stopfault oracle>','exec'),{'__name__':'literal_oracle'})


if __name__=='__main__':unittest.main()

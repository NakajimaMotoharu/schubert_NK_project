"""Full generated sources bind literal source/current64 and genuine normal terminal."""
import ast
import copy
import unittest
from pyflakes.api import check,checkPath
import pg4752_new_current_admission_image as admission
import pg4754_new_current_terminal as terminal


class NewAdmission(unittest.TestCase):
    def binding(self):return {'boot':'79a3260ae16d42bf942ab914ed144c28','invocation':'b414b0e1e5ac47e8b5fb8c5ae3d94348','job':'209474','start':188006981413,'run':'fff841d9-2554-4680-b17d-9548bfa79cbb','cutoff':'2026-10-16T22:12:38.570783Z','activation':'7ab6c953-b2fc-47ae-be96-26a3196ca76d','rootPid':860231}

    def test_same_actual_admission_shape_and_no_old_source_credit(self):
        raw=admission.payload(self.binding());self.assertEqual(0,check(raw,'<full image>'))
        self.assertIn(admission.SOURCE,raw);self.assertIn(admission.BOM,raw)
        self.assertIn("'nativeExecEntries':64",raw);self.assertIn('!=64',raw)
        self.assertNotIn(admission.previous.SOURCE,raw);self.assertNotIn(admission.previous.ONCE,raw)
        self.assertNotIn('os.system',raw);self.assertNotIn('systemctl',raw)
        self.assertEqual(0,checkPath(admission.__file__))

    def test_terminal_binds_this_generation_observer_and_budget(self):
        raw=terminal.payload(self.binding());self.assertEqual(0,check(raw,'<full genuine terminal>'))
        self.assertIn(admission.SOURCE,raw);self.assertIn(admission.BOM,raw)
        self.assertIn(terminal.TERM,raw);self.assertNotIn('pg4560-parent-watch-v1',raw)
        self.assertIn('1800',raw);self.assertIn('genuineRootDone',raw)
        compile(raw,'<genuine>','exec');ast.parse(raw)
        self.assertEqual(0,checkPath(terminal.__file__));self.assertEqual(0,checkPath(__file__))

    def test_literal_full11_lossless_projection_and_foreign_schema_rejection(self):
        units={str(i):{'MainPID':'0','ControlPID':'0','Job':''}for i in range(10)}
        value={'backup':{'backup-path':['literal']},'configuration':{n:{}for n in units},'extraDurable':{'credentials':{'key-path':['literal']},'oldProofs':{'proof-path':['literal']}},'originals':{'original-path':['literal']},'pid1':{},'rows':{str(i):[]for i in range(24)},'runtime':{},'startup':{},'unitFilesActual':{'unit-path':['literal']},'units':units,'native':{str(i)+'.exec':{}for i in range(64)}}
        publication={'unitFilesActual':copy.deepcopy(value['unitFilesActual'])};original=copy.deepcopy(value)
        projected=admission.project(value,publication)
        self.assertEqual({'originals':value['originals'],'backup':value['backup'],**value['extraDurable']},projected['durable']);self.assertEqual(original,value)
        for change in [lambda v:v.pop('rows'),lambda v:v.update(database={}),lambda v:v.update(rows=None),lambda v:v['native'].pop('0.exec'),lambda v:v['units']['0'].update(MainPID='2'),lambda v:v.update(extraDurable={})]:
            bad=copy.deepcopy(value);change(bad)
            with self.assertRaises(ValueError):admission.project(bad,publication)


if __name__=='__main__':unittest.main()

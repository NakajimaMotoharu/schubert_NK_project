import tempfile
import unittest
import zipfile
from pathlib import Path
from pyflakes.api import check
from pg2406_question_signed_candidate import verify_delta, verify_web_resource, main_source, RESOURCE


class Candidate(unittest.TestCase):
    def test_current_main_all1643_literal_identity_and_negative(self):
        values = {m:{} for m in ['protocol','storage','bootstrap','api','web','batch']}
        values['batch'] = {str(i):'a'*64 for i in range(1643)}
        self.assertEqual(1643, verify_delta(values, values))
        changed = {**values, 'batch':{**values['batch'], '0':'b'*64}}
        with self.assertRaises(ValueError):
            verify_delta(values, changed)
        with self.assertRaises(ValueError):
            verify_delta(None, values)

    def test_independent_old_and_new_approved_resource_bytes(self):
        import subprocess
        root = Path(__file__).resolve().parents[2]
        relative = 'src/schubert-nk-web/src/main/resources/' + RESOURCE
        old = subprocess.check_output(['git','show','3b7f3567b:'+relative],cwd=root)
        new = subprocess.check_output(['git','show','cdbc07cdf:'+relative],cwd=root)
        with tempfile.TemporaryDirectory(prefix='pg2406-resource-') as temp:
            a,b,c = [Path(temp)/n for n in ['old.jar','new.jar','foreign.jar']]
            for p, content, extra in [(a,old,b'fixed'),(b,new,b'fixed'),(c,new,b'foreign')]:
                with zipfile.ZipFile(p,'w') as jar:
                    jar.writestr(RESOURCE,content);jar.writestr('literal-other',extra)
            verify_web_resource(a,b)
            for p in [a,c]:
                with self.assertRaises(ValueError):
                    verify_web_resource(a,p)

    def test_full_host_entry_complete_globals_and_no_guest_action(self):
        import pg2406_question_signed_candidate as current
        raw = main_source()
        prelude = ('import os,subprocess,json,hashlib,shutil,datetime\nfrom pathlib import Path\n'
                   'from pg2406_question_signed_candidate import W,P,T,OLD,OLD_SOURCE,OLD_BOM,NEXT,FROZEN,SIG,validate_gate,verify_delta,receive\n'
                   'from pg1638_api_signed_candidate import require,sha,artifacts,MODULES,class_inventory\n'
                   'PRODUCTION="fixed"\n__file__="fixed"\n')
        self.assertEqual(0, check(prelude + raw,'<entry complete namespace>'))
        namespace = {**current.prior.__dict__,'OLD':current.OLD,'NEXT':current.NEXT,
                     'SIG':current.SIG,'FROZEN':current.FROZEN,'PRODUCTION':current.production()}
        exec(compile(raw,'<full host entry>','exec'),namespace)
        for value in ['PG2406','PG2126','3637','web/web.jar', 'changedResources']:
            self.assertIn(value,raw)
        self.assertNotIn('StartUnit(',raw)
        self.assertNotIn('StopUnit(',raw)


if __name__ == '__main__':
    unittest.main()

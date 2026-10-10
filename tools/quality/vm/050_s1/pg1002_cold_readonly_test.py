"""Cold-only observation boundaries; no historical success/native resurrection."""
import ast
import unittest
from pg1002_cold_readonly import payload

class ColdTest(unittest.TestCase):
    def test_fixed_current_source_and_after_image_no_business_command(self):
        s=payload();ast.parse(s)
        self.assertIn("manifest['source']['commit']==SOURCE",s)
        self.assertNotIn('gitCommit',s)
        self.assertIn('c76227aee0b0c82877c750db53115c004aeef8e99f0c8f3682b94fbd1a56ff32',s)
        self.assertIn("require(rows==old['rows']",s)
        self.assertIn("'fullColdPreparationAccepted':False",s)
        self.assertIn("'oldTmpfsSuccessfullyRetired':False",s)
        self.assertIn("'full32ColdConfigurationAccepted':False",s)
        self.assertNotIn("'systemctl','start'",s)
        self.assertNotIn("'systemctl','stop'",s)
        self.assertFalse("'pg_restore'"in s)

    def test_cold_rejects_warm_actor_or_unknown_history(self):
        nodes=ast.parse(payload()).body
        fn=next(x for x in nodes if isinstance(x,ast.FunctionDef)and x.name=='cold')
        env={};exec(compile(ast.Module(body=[fn],type_ignores=[]),'<cold fixture>','exec'),env)
        v={'LoadState':'loaded','ActiveState':'inactive','SubState':'dead','MainPID':'0','ControlPID':'0',
           'Job':'','InvocationID':'','Result':'success','KillMode':'control-group','SendSIGKILL':'no',
           'ExecMainCode':'0','ExecMainStatus':'0','ExecMainStartTimestampMonotonic':'0','ExecMainExitTimestampMonotonic':'0'}
        self.assertTrue(env['cold'](v))
        for key in v:
            changed={**v,key:'unknown'};self.assertFalse(env['cold'](changed))

if __name__=='__main__':unittest.main()

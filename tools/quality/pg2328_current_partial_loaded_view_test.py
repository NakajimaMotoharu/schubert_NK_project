import unittest
from copy import deepcopy
from pg2328_current_partial_loaded_view_post import payload,admitted_configuration


class LoadedView(unittest.TestCase):
    def test_exact_two_fields_all_other_fields_unchanged_and_every_foreign_refusal(self):
        row={str(i):''for i in range(30)};row.update(ExecStart='old',DropInPaths='fixed')
        unit='schubert-nk-morning-controller.service';old={unit:row,'ordinary':dict(row)}
        new={unit:{**row,'ExecStart':'new','DropInPaths':'fixed /run/systemd/system/schubert-nk-morning-controller.service.d/zz-pg2316-once-resume.conf'},'ordinary':dict(row)}
        def parse(value):return ('/usr/bin/java','fixed'+(' --resume 91f5484b-9702-4c7c-97f3-dd5110a853f9'if value=='new'else''),'no','n/a','n/a','0','(null)','0/0')
        self.assertTrue(admitted_configuration(old,new,parse))
        self.assertFalse(admitted_configuration(old,old,parse))
        self.assertFalse(admitted_configuration(None,new,parse))
        self.assertFalse(admitted_configuration(old,None,parse))
        for name in new:
            for key in new[name]:
                changed=deepcopy(new);changed[name][key]='unknown'
                if key=='ExecStart':self.assertFalse(admitted_configuration(old,changed,lambda x:None))
                else:self.assertFalse(admitted_configuration(old,changed,parse))
        raw=payload()
        self.assertIn("'normalReloadAccepted':False",raw)
        self.assertNotIn("['systemctl','daemon-reload']",raw)


if __name__=='__main__':unittest.main()

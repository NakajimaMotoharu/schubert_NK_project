"""Literal independent declarations, all fields and each auxiliary bound are checked."""
import unittest
from pg1948_reload_closed_configuration import reload_configuration_same,RESET_UNITS,CLOSED


class Reload(unittest.TestCase):
    def test_declared_and_closed_only_for_eight_known_units(self):
        old={f'field{i}':'fixed'for i in range(31)};old['ExecStart']='old'
        new={**old,'ExecStart':'closed'}
        vectors={'old':('/bin/service','--fixed',False,'date1','date2','123','exited','10'),'closed':('/bin/service','--fixed',False,*CLOSED)}
        parse=vectors.get
        for unit in RESET_UNITS:self.assertTrue(reload_configuration_same(unit,old,new,parse))
        for unit in ['foreign','schubert-nk-bootstrap-admin.service','schubert-nk-inbox-inspector.service']:
            self.assertFalse(reload_configuration_same(unit,old,new,parse));self.assertTrue(reload_configuration_same(unit,old,old,parse))
        for key in old:
            if key!='ExecStart':self.assertFalse(reload_configuration_same('caddy.service',old,{**new,key:'changed'},parse))
        for index in range(8):
            bad=list(vectors['closed']);bad[index]='foreign';vectors['bad']=tuple(bad)
            self.assertFalse(reload_configuration_same('caddy.service',old,{**new,'ExecStart':'bad'},parse))
        for bad in [None,{},dict(list(old.items())[:-1]),{**old,'extra':'x'},{**old,'field0':None}]:
            self.assertFalse(reload_configuration_same('caddy.service',old,bad,parse))
        self.assertFalse(reload_configuration_same('caddy.service',old,{**new,'ExecStart':'unknown'},parse))


if __name__=='__main__':unittest.main()

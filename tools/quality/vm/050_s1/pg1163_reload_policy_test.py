import copy
import unittest
from pg1163_reload_policy import configuration,MORNING,WRONG


class ReloadTest(unittest.TestCase):
    def test_full_literal_display_and_settings(self):
        old='{ path=/usr/bin/java ; argv[]=/usr/bin/java literal ; ignore_errors=no ; start_time=[Sat 2026-10-10 12:40:25 UTC] ; stop_time=[Sat 2026-10-10 13:10:25 UTC] ; pid=242818 ; code=exited ; status=143 }'
        reset='{ path=/usr/bin/java ; argv[]=/usr/bin/java literal ; ignore_errors=no ; start_time=[n/a] ; stop_time=[n/a] ; pid=0 ; code=(null) ; status=0/0 }'
        base={MORNING:{'ExecStart':old,'DropInPaths':'/etc/systemd/system/x/pg477-native-coverage.conf','Other':'fixed'},'artemis.service':{'ExecStart':old,'DropInPaths':'','Other':'fixed'}}
        self.assertTrue(configuration(base,copy.deepcopy(base),False))
        current=copy.deepcopy(base)
        for v in current.values():v['ExecStart']=reset
        current[MORNING]['DropInPaths']=WRONG+' '+base[MORNING]['DropInPaths']
        self.assertTrue(configuration(base,current,True))
        for changed in [reset.replace('argv[]=/usr/bin/java literal','argv[]=/usr/bin/java foreign'),reset.replace('ignore_errors=no','ignore_errors=yes'),reset.replace('pid=0','pid=242818'),reset.replace('status=0/0','status=143'),reset.replace('code=(null)','code=exited')]:
            bad=copy.deepcopy(current);bad['artemis.service']['ExecStart']=changed
            with self.assertRaises(ValueError):configuration(base,bad,True)
        bad=copy.deepcopy(current);bad['artemis.service']['Other']='changed'
        with self.assertRaises(ValueError):configuration(base,bad,True)
        bad=copy.deepcopy(current);bad[MORNING]['DropInPaths']=base[MORNING]['DropInPaths']+' '+WRONG
        with self.assertRaises(ValueError):configuration(base,bad,True)
        for name in ['pg1160-once-resume.conf','pg477-native-coverage.conf']:
            self.assertLess(name,'zz-pg1160-once-resume.conf')


if __name__=='__main__':unittest.main()

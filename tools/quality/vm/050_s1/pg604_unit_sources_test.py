"""Independent literal observed full source profile; never generated from subject constants."""
import copy
import unittest
from pg604_unit_sources import sources

GOLDEN={
 'caddy.service':{'FragmentPath':'/usr/lib/systemd/system/caddy.service','DropInPaths':'/etc/systemd/system/caddy.service.d/schubert-nk-startup-policy.conf'},
 'schubert-nk-web.service':{'FragmentPath':'/etc/systemd/system/schubert-nk-web.service','DropInPaths':'/etc/systemd/system/schubert-nk-web.service.d/zz-pg471-native193.conf'},
 'schubert-nk-api.service':{'FragmentPath':'/etc/systemd/system/schubert-nk-api.service','DropInPaths':'/etc/systemd/system/schubert-nk-api.service.d/pg406-root-coverage.conf /etc/systemd/system/schubert-nk-api.service.d/zz-pg471-native193.conf'},
 'schubert-nk-cleanup.service':{'FragmentPath':'/etc/systemd/system/schubert-nk-cleanup.service','DropInPaths':'/etc/systemd/system/schubert-nk-cleanup.service.d/pg390-native-coverage.conf'},
 'schubert-nk-inbox-inspector.service':{'FragmentPath':'/etc/systemd/system/schubert-nk-inbox-inspector.service','DropInPaths':''},
 'schubert-nk-expiry-cleanup.service':{'FragmentPath':'/etc/systemd/system/schubert-nk-expiry-cleanup.service','DropInPaths':'/etc/systemd/system/schubert-nk-expiry-cleanup.service.d/pg394-native-coverage.conf'},
 'schubert-nk-backup.service':{'FragmentPath':'/etc/systemd/system/schubert-nk-backup.service','DropInPaths':'/etc/systemd/system/schubert-nk-backup.service.d/pg390-native-coverage.conf'},
 'artemis.service':{'FragmentPath':'/etc/systemd/system/artemis.service','DropInPaths':''},
 'schubert-nk-morning-controller.service':{'FragmentPath':'/etc/systemd/system/schubert-nk-morning-controller.service','DropInPaths':'/etc/systemd/system/schubert-nk-morning-controller.service.d/pg477-native-coverage.conf'},
 'schubert-nk-bootstrap-admin.service':{'FragmentPath':'/etc/systemd/system/schubert-nk-bootstrap-admin.service','DropInPaths':''}}


class SourceProfile(unittest.TestCase):
    def test_normal_vendor_local_and_all_eight_dropins(self):
        actual=sources(copy.deepcopy(GOLDEN))
        self.assertEqual(18,len(actual))
        self.assertIn('/usr/lib/systemd/system/caddy.service',actual)
        self.assertNotIn('/etc/systemd/system/caddy.service',actual)
        self.assertIn('/etc/systemd/system/schubert-nk-api.service.d/pg406-root-coverage.conf',actual)
        reordered=copy.deepcopy(GOLDEN)
        reordered['schubert-nk-api.service']['DropInPaths']=' '.join(reversed(reordered['schubert-nk-api.service']['DropInPaths'].split()))
        self.assertEqual(actual,sources(reordered))

    def test_every_unit_missing_null_foreign_and_drop_change(self):
        for unit in GOLDEN:
            for change in('missing','null','fragment','extra_field','drop_null','drop_extra','drop_missing'):
                bad=copy.deepcopy(GOLDEN)
                if change=='missing':del bad[unit]
                elif change=='null':bad[unit]=None
                elif change=='fragment':bad[unit]['FragmentPath']='/etc/foreign'
                elif change=='extra_field':bad[unit]['Foreign']=True
                elif change=='drop_null':bad[unit]['DropInPaths']=None
                elif change=='drop_extra':bad[unit]['DropInPaths']+=' /etc/foreign.conf'
                else:
                    if not bad[unit]['DropInPaths']:continue
                    bad[unit]['DropInPaths']=''
                with self.subTest(unit=unit,change=change),self.assertRaises(ValueError):sources(bad)
        bad=copy.deepcopy(GOLDEN);bad['caddy.service']['DropInPaths']+=' '+bad['caddy.service']['DropInPaths']
        with self.assertRaises(ValueError):sources(bad)
        bad=copy.deepcopy(GOLDEN);bad['Foreign.service']=bad['caddy.service']
        with self.assertRaises(ValueError):sources(bad)
        for value in(None,{},[]):
            with self.assertRaises(ValueError):sources(value)


if __name__=='__main__':unittest.main()

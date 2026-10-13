import copy
import unittest
from pyflakes.api import check
from pg2208_current_newboot_cold_sources import BOOT
import pg2242_newboot_fresh_day_full_seal as p


class CurrentFullSeal(unittest.TestCase):
    def test_exact_frozen_schema_and_whole_emitted_current_guards(self):
        current={'boot':BOOT,'source':'3b7f3567b54f91f3a9dbeb859e8dd77e8353a2c8','manifestSha256':'62213f357c9dab3b00b557549426b091a03ace6557a62f4410999a02028a332c','units':{str(i):{}for i in range(10)},'configuration':{},'rows':{str(i):[]for i in range(24)},'durable':{k:{}for k in ['backup','originals','credentials','oldProofs']},'unitFiles':{'public-unit':{'metadata':[1]*9,'sha256':'c'*64}},'maintenance':[]}
        frozen={'current':current,'runtime':{},'systemdRuntime':{},'ordinaryNoargs':True,'newJstDate':'2026-10-14','existingSuccessfulInspectorStepsForDate':0,'availableBytes':{},'requiredGuestWriteAndCloseBytes':805306368}
        result=p.normalize_frozen(frozen)
        self.assertEqual([1]*9+['c'*64],result['unitFilesActual']['public-unit'])
        for field in frozen:
            bad=copy.deepcopy(frozen);del bad[field]
            with self.assertRaises(ValueError):p.normalize_frozen(bad)
        for field,value in [('boot','oldboot'),('source','old'),('manifestSha256','old'),('rows',{}),('durable',{})]:
            bad=copy.deepcopy(frozen);bad['current'][field]=value
            with self.assertRaises(ValueError):p.normalize_frozen(bad)
        binding={'boot':BOOT.replace('-',''),'rootPid':123,'invocation':'1'*32,'start':1000000,'job':'123','run':'11111111-1111-4111-8111-111111111111','activation':'22222222-2222-4222-8222-222222222222','cutoff':'2026-10-13T15:01:00Z'}
        raw=p.payload(binding,'a'*64,'b'*64)
        self.assertEqual(0,check(raw,'<entire emitted current seal>'))
        for value in [p.SLOT,'pg2227-newboot-fresh-day-once-v1','pg2238-newboot-before-selectors-v1','normalize_frozen(json.loads(before_raw))','0.1.0-PG2126','currentFourOwnedLive','sqlOracleQualified']:
            self.assertIn(value,raw)
        self.assertNotIn('3d69f5af',raw)
        self.assertIn("'02bddddf-9cd3-4668-9d67-7561232fc4e4'",raw) # immutable negative, not live data
        self.assertNotIn('systemctl start',raw)


if __name__=='__main__':unittest.main()

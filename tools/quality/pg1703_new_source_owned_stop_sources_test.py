"""Independent frozen role fixtures; source generation grants no stop authority."""
import json
import unittest
from unittest.mock import patch
import pg1703_new_source_owned_stop_sources as subject


class StopSourceTest(unittest.TestCase):
    def test_whole_generated_helpers_are_bound_to_fixture_roles(self):
        seal,done=self.fixture()
        with patch.object(subject,'context',return_value=(seal['privateBeforeSha256'],seal['observedOwned'],done['receipt'],seal['doneEndUtc'])):
            generated=subject.sources()
        self.assertEqual(14,len(generated))
        combined='\n'.join(generated.values())
        for v in ['02e941b9-1c52-4018-a193-63dd00b269af','fe43e94b1fbf4886bb4ab3922fd16f9c',
                  'pg1702-new-source-completed-seal-v1','0.1.0-PG1638','66941284515','68741284515']:
            self.assertIn(v,combined)
        for v in ['pg1609','Pg1609','0.1.0-PG1544','38365395523','40165395523',
                  '0be226b1-bbb7-43d3-aa9e-59d0bda70f9a']:
            self.assertNotIn(v,combined)

    def fixture(self):
        owned={unit:[pid,inv,7700000,'a'*64]for unit,pid,inv in [
            ('caddy.service','303003','a'*32),('schubert-nk-web.service','303002','b'*32),
            ('schubert-nk-api.service','303001','c'*32),('artemis.service','303000','d'*32)]}
        done={'actualExit':0,'source':'2741c4546afad6c1e8b6efbd53dfb58144edf7bb',
              'receipt':{'endMonotonicUs':68541284515,'elapsedSeconds':1600}}
        seal={'actualExit':0,'productionSource':'2741c4546afad6c1e8b6efbd53dfb58144edf7bb',
              'sqlOracleQualified':True,'currentFourOwnedLive':True,'privateBeforeSha256':'f'*64,
              'observedOwned':owned,'genuineCompletion':done['receipt'],'doneEndUtc':'2026-10-12T14:46:00Z'}
        return seal,done

    def test_join_and_bad_source_role_identity_completion_rejected(self):
        seal,done=self.fixture()
        def read(path): return json.dumps(seal if path.name=='manifest.safe.json' else done).encode()
        with patch('pathlib.Path.read_bytes',read):
            self.assertEqual('f'*64,subject.context()[0])
            raw=subject.bind("PG1544 pg1609 Pg1609 pg1608-current-observation-full-seal-v3 256734 994fd53232ee426d9ca93a2f311bda53 38365395523 39951854181 40165395523 71184 204695")
            self.assertEqual('PG1638 pg1703 Pg1703 pg1702-new-source-completed-seal-v1 303001 '+'c'*32+' 66941284515 68541284515 68741284515 106924 302199',raw)
            for key,bad in [('productionSource','old'),('sqlOracleQualified',False),('currentFourOwnedLive',None),
                            ('privateBeforeSha256','bad'),('genuineCompletion',{}),('doneEndUtc',None)]:
                original=seal[key];seal[key]=bad
                with self.subTest(key=key),self.assertRaises(ValueError):subject.context()
                seal[key]=original
            for field,bad in [(0,'0'),(1,'foreign'),(2,True),(3,None)]:
                identity=seal['observedOwned']['caddy.service'];original=identity[field];identity[field]=bad
                with self.subTest(field=field),self.assertRaises(ValueError):subject.context()
                identity[field]=original
            for end in [True,None,66941284515,68741284516]:
                done['receipt']['endMonotonicUs']=end
                with self.subTest(end=end),self.assertRaises(ValueError):subject.context()


if __name__=='__main__':unittest.main()

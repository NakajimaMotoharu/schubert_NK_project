import copy
import hashlib
import json
import unittest
from pg1259_fresh_backup_manifest_oracle import verify,FILES,VERSIONS

class IndependentFreshBackupManifestTest(unittest.TestCase):
    def setUp(self):
        self.run='9f651096-aef9-4fba-90b0-a653e99f035a';self.cut='2026-10-10T20:03:22.718197Z'
        self.profile=dict(zip(VERSIONS,['pgpt-r2','0.1.0-SNAPSHOT','028','ubuntu-26.04','25.0.4','18.6','2.56.0','1.2.1']))
        self.files={n:{'size':len(b),'sha256':hashlib.sha256(b).hexdigest()}for n,b in zip(FILES,[b'dump-vector',b'config-vector',b'age-cipher-vector'])}
        self.recipient=hashlib.sha256(b'independent-public-recipient\n').hexdigest()
        began='2026-10-10T20:03:27.141566Z';finish='2026-10-10T20:03:31.559039Z'
        self.manifest={'format':'NKBACKUP1','database':'schubert_nk','runId':self.run,'cutoff':self.cut,'startedAt':began,'contentFinishedAt':finish,'databaseStep':{'id':625,'attempt':1,'startedAt':began},'configurationStep':{'id':626,'attempt':1,'startedAt':began},'versions':self.profile,'recipientSha256':self.recipient,'files':self.files}
        self.rows=[]
        for i,(step,count,size)in enumerate([('BACKUP_DB',1,self.files[FILES[0]]['size']),('BACKUP_CONFIG',2,sum(self.files[n]['size']for n in FILES[1:]))]):
            self.rows.append({'id':625+i,'attempt':1,'run_id':self.run,'business_date':'2026-10-11','step':step,'started_at':began.replace('Z','+00:00'),'ended_at':'2026-10-10T20:03:32.000000+00:00','status':'SUCCESS','target_count':count,'success_count':count,'failure_count':0,'byte_count':size,'error_code':None,'error_summary':None})

    def raw(self,m):return(json.dumps(m,separators=(',',':'))+'\n').encode('ascii')
    def check(self,raw=None,rows=None,physical=None):
        return verify(raw if raw is not None else self.raw(self.manifest),physical if physical is not None else self.files,self.profile,rows if rows is not None else self.rows,self.run,self.cut,self.recipient)

    def test_independent_normal_and_all_handle_or_file_negative_cases(self):
        result=self.check();self.assertEqual(result['directoryName'],'20261011-050327-'+self.run)
        self.assertEqual(result['configurationBytes'],30);self.assertEqual(result['totalArchiveBytes'],41)
        for field,value in [('database','foreign'),('runId','343a5a1b-d064-47d5-88c2-31c36d7ba7a4'),('cutoff','2026-10-10T12:40:27.396847Z'),('recipientSha256','a'*64),('contentFinishedAt','2026-10-10T20:03:26.000000Z')]:
            m=copy.deepcopy(self.manifest);m[field]=value
            with self.assertRaises(ValueError):self.check(self.raw(m))
        for key in ['databaseStep','configurationStep']:
            for field,value in [('id',True),('attempt',0),('startedAt','2026-10-10T20:03:27Z')]:
                m=copy.deepcopy(self.manifest);m[key][field]=value
                with self.assertRaises(ValueError):self.check(self.raw(m))
        for field,value in [('id',True),('attempt',2),('status','FAILED'),('failure_count',1),('byte_count',0),('business_date','2026-10-10'),('error_code','FAIL')]:
            rows=copy.deepcopy(self.rows);rows[0][field]=value
            with self.assertRaises(ValueError):self.check(rows=rows)
        with self.assertRaises(ValueError):self.check(rows=self.rows[:1])
        for raw in [self.raw(self.manifest)+b'\n',self.raw(self.manifest).replace(b',',b', ',1),self.raw(self.manifest).replace(b'\n',b'\r\n'),self.raw(self.manifest).replace(b'"format":',b'"format":null,"format":',1),b'\xef\xbb\xbf'+self.raw(self.manifest),b'',b'{}\n']:
            with self.assertRaises(ValueError):self.check(raw)
        m=copy.deepcopy(self.manifest);m['files'][FILES[0]]['sha256']='F'*64
        with self.assertRaises(ValueError):self.check(self.raw(m))
        physical=copy.deepcopy(self.files);physical[FILES[0]]['size']+=1
        with self.assertRaises(ValueError):self.check(physical=physical)

if __name__=='__main__':unittest.main()

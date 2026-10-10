"""Literal approved fresh Backup fixture, independent hashes/DB postconditions."""
import copy
import hashlib
import json
import stat
import unittest
from pg1121_fresh_backup_oracle import qualify


class BackupOracleTest(unittest.TestCase):
    def fixture(self):
        root='/srv/schubert-nk/backup'
        run='343a5a1b-d064-47d5-88c2-31c36d7ba7a4'
        cutoff='2026-10-10T12:40:27.396847Z'
        folder=root+'/20261010-214033-'+run
        profile=dict(host='fixture',app='0.1.0-PG1068',schema='028',os='26.04',
                     jdk='25.0.4',postgresql='18.6',artemis='2.56.0',age='1.3.1')
        recipient=b'age1-public-fixture\n'
        data={folder+'/schubert_nk.dump':b'PGDMP-fixture',
              folder+'/config.tar':b'toy-config',
              folder+'/credentials.tar.age':b'age-encryption.org/v1\nxyz'}
        claims={
            'schubert_nk.dump':dict(size=13,sha256=hashlib.sha256(b'PGDMP-fixture').hexdigest()),
            'config.tar':dict(size=10,sha256=hashlib.sha256(b'toy-config').hexdigest()),
            'credentials.tar.age':dict(size=25,sha256=hashlib.sha256(b'age-encryption.org/v1\nxyz').hexdigest())}
        manifest=dict(format='NKBACKUP1',database='schubert_nk',runId=run,cutoff=cutoff,
            startedAt='2026-10-10T12:40:33.000000Z',contentFinishedAt='2026-10-10T12:40:35.000000Z',
            databaseStep=dict(id=101,attempt=1,startedAt='2026-10-10T12:40:31.000000Z'),
            configurationStep=dict(id=102,attempt=1,startedAt='2026-10-10T12:40:32.000000Z'),
            versions=copy.deepcopy(profile),recipientSha256=hashlib.sha256(b'age1-public-fixture\n').hexdigest(),
            files=claims)
        data[folder+'/MANIFEST.json']=(json.dumps(manifest,separators=(',',':'))+'\n').encode()
        old={root:dict(metadata=[1,10,992,977,stat.S_IFDIR|0o700,2,0,10,10],sha256=None)}
        current=copy.deepcopy(old);current[root]['metadata'][5:]=[3,4096,20,20]
        current[folder]=dict(metadata=[1,11,992,977,stat.S_IFDIR|0o700,2,4096,20,20],sha256=None)
        for index,(name,raw)in enumerate(data.items()):
            uid=992 if name.endswith('.dump')else 0;gid=977 if uid else 0
            current[name]=dict(metadata=[1,30+index,uid,gid,stat.S_IFREG|0o600,1,len(raw),20,20],
                               sha256=hashlib.sha256(raw).hexdigest())
        rows=[]
        for step,id,count,size,started in [('BACKUP_DB',101,1,13,'2026-10-10T12:40:31Z'),
                                         ('BACKUP_CONFIG',102,2,35,'2026-10-10T12:40:32Z')]:
            rows.append(dict(step=step,id=id,attempt=1,run_id=run,business_date='2026-10-10',
                status='SUCCESS',error_code=None,error_summary=None,target_count=count,
                success_count=count,failure_count=0,byte_count=size,started_at=started,
                ended_at='2026-10-10T12:40:36Z'))
        return [run,cutoff,old,current,rows,profile,recipient,(992,977),data.__getitem__],data,manifest,folder

    def test_two_success_counts_hashes_and_old_backup_retained(self):
        args,_,_,_=self.fixture();result=qualify(*args)
        self.assertTrue(result['freshBackupTwoSuccessVerified'])
        self.assertEqual(result['newBundleEntries'],5)
        self.assertTrue(result['contentDigestDbCountersBound'])
        self.assertFalse(result['formalAccepted'])
        # Old successful Backup pairs remain in the same table and must not
        # be reused as current handles or counted as current duplicates.
        old=copy.deepcopy(args[4]);old[0]['run_id']=old[1]['run_id']='old-run'
        args[4]=old+args[4]
        self.assertTrue(qualify(*args)['freshBackupTwoSuccessVerified'])
        args[6]=args[6].strip()
        with self.assertRaises(ValueError):qualify(*args)

    def test_manifest_binding_version_bytes_and_unknown_negative(self):
        for key,bad in [('format','WRONG'),('database','other'),('runId','old'),
                        ('cutoff','2026-10-09T12:40:27.396847Z'),
                        ('startedAt','2026-10-10T12:40:33Z'),
                        ('recipientSha256','0'*64),('versions',{}),('files',{})]:
            args,data,manifest,folder=self.fixture();manifest[key]=bad
            raw=(json.dumps(manifest,separators=(',',':'))+'\n').encode()
            data[folder+'/MANIFEST.json']=raw
            v=args[3][folder+'/MANIFEST.json'];v['metadata'][6]=len(raw);v['sha256']=hashlib.sha256(raw).hexdigest()
            with self.subTest(key=key),self.assertRaises(ValueError):qualify(*args)
        args,_,_,folder=self.fixture();args[3][folder+'/unknown']={}
        with self.assertRaises(ValueError):qualify(*args)

    def test_row_pair_status_counter_null_duplicate_and_old_mode(self):
        for key,bad in [('status','SKIPPED'),('run_id','old'),('business_date','2026-10-11'),
                        ('target_count',2),('target_count',True),('failure_count',1),
                        ('byte_count',0),('error_code','ALREADY_SUCCESSFUL'),
                        ('ended_at','2026-10-10T12:40:34Z')]:
            args,_,_,_=self.fixture();args[4][0][key]=bad
            with self.subTest(key=key),self.assertRaises(ValueError):qualify(*args)
        args,_,_,_=self.fixture();args[4].append(copy.deepcopy(args[4][0]))
        with self.assertRaises(ValueError):qualify(*args)
        args,_,_,_=self.fixture();args[4].append(None)
        with self.assertRaises(ValueError):qualify(*args)
        args,_,_,_=self.fixture();args[3]['/srv/schubert-nk/backup']['metadata'][4]=stat.S_IFDIR|0o755
        with self.assertRaises(ValueError):qualify(*args)

    def test_inode_owner_mode_digest_cipher_header_and_null_inputs(self):
        for key,index,bad in [('dump',2,0),('dump',4,stat.S_IFREG|0o644),('config',2,992),
                              ('dir',4,stat.S_IFDIR|0o755)]:
            args,_,_,folder=self.fixture()
            name=folder if key=='dir'else folder+('/schubert_nk.dump'if key=='dump'else'/config.tar')
            args[3][name]['metadata'][index]=bad
            with self.assertRaises(ValueError):qualify(*args)
        for index in [2,3,4,5,6,7]:
            args,_,_,_=self.fixture();args[index]=None
            with self.assertRaises(ValueError):qualify(*args)
        args,data,manifest,folder=self.fixture()
        path=folder+'/credentials.tar.age';data[path]=b'x'*25
        args[3][path]['sha256']=hashlib.sha256(data[path]).hexdigest()
        manifest['files']['credentials.tar.age']['sha256']=args[3][path]['sha256']
        raw=(json.dumps(manifest,separators=(',',':'))+'\n').encode();data[folder+'/MANIFEST.json']=raw
        args[3][folder+'/MANIFEST.json']['sha256']=hashlib.sha256(raw).hexdigest()
        with self.assertRaises(ValueError):qualify(*args)

    def test_seven_generations_oldest_retired_with_private_preservation(self):
        args,data,_,new_folder=self.fixture()
        root='/srv/schubert-nk/backup';old=args[2];now=args[3]
        old[root]['metadata'][5:]=[9,4096,10,10]
        now[root]['metadata'][5:]=[9,4096,20,20]
        retired_folder=None
        for index in range(7):
            folder=root+'/old-'+str(index)
            old[folder]=dict(metadata=[1,100+index,992,977,stat.S_IFDIR|0o700,2,4096,10,10],sha256=None)
            for n,name in enumerate(['MANIFEST.json','schubert_nk.dump','config.tar','credentials.tar.age']):
                raw=(json.dumps({'startedAt':'2026-10-08T12:00:0'+str(index)+'.000000Z'})+'\n').encode()if name=='MANIFEST.json'else b'old-byte'
                old[folder+'/'+name]=dict(metadata=[1,200+index*10+n,0,0,stat.S_IFREG|0o600,1,len(raw),10,10],
                                         sha256=hashlib.sha256(raw).hexdigest())
                data[folder+'/'+name]=raw
            if index==0:retired_folder=folder
            else:
                for path,value in old.items():
                    if path==folder or path.startswith(folder+'/'):now[path]=copy.deepcopy(value)
        proof={'folder':retired_folder,'startedAt':'2026-10-08T12:00:00.000000Z',
               'privateProofSha256':'c'*64,
               'files':{name:dict(size=old[retired_folder+'/'+name]['metadata'][6],
                                 sha256=old[retired_folder+'/'+name]['sha256'],
                                 originalMetadata=copy.deepcopy(old[retired_folder+'/'+name]['metadata']))
                        for name in ['MANIFEST.json','schubert_nk.dump','config.tar','credentials.tar.age']}}
        result=qualify(*args,retired=proof)
        self.assertEqual(result['retiredEntriesPrivatelyPreserved'],5)
        self.assertEqual(result['retiredProofSha256'],'c'*64)
        with self.assertRaises(ValueError):qualify(*args)
        bad=copy.deepcopy(proof);bad['startedAt']='2026-10-10T12:00:00.000000Z'
        with self.assertRaises(ValueError):qualify(*args,retired=bad)
        bad=copy.deepcopy(proof);bad['files']['config.tar']['sha256']='0'*64
        with self.assertRaises(ValueError):qualify(*args,retired=bad)


if __name__=='__main__':unittest.main()

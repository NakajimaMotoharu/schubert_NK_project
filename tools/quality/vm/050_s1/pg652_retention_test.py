"""Literal new-success/skip/byte/retention normal and tamper vectors."""
import copy
import hashlib
import json
import stat
import unittest
from pg652_retention_oracle import validate,STEPS,ROOT
from pg652_capture_retention import payload


def fixture():
    run='aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee';cutoff='2026-10-08T21:33:22.000000Z'
    old={'schubert.batch_runs':[]};old.update({f'schubert.t{i}':[]for i in range(23)})
    for i in range(482):old['schubert.batch_runs'].append({'id':i+1,'run_id':'prior','step':'BACKUP_DB','status':'SUCCESS','business_date':'2026-10-08','attempt':1})
    today=[dict(id=483+i,run_id='prior-today',step=s,status='SUCCESS',business_date='2026-10-09',attempt=1)for i,s in enumerate(STEPS)]
    today +=[dict(id=493+i,run_id='e492',step=s,status='SUCCESS',business_date='2026-10-09',attempt=2)for i,s in enumerate(STEPS[:2])]
    today +=[dict(id=495+i,run_id='e492',step=s,status='SKIPPED',business_date='2026-10-09',attempt=3 if i<2 else 2)for i,s in enumerate(STEPS)]
    for r in today[:10]:r['run_id']='3a53b979-fa01-47dd-92a6-7b26affcfb5c'
    old['schubert.batch_runs']+=today;new=copy.deepcopy(old)
    files={'schubert_nk.dump':b'literal dump','config.tar':b'literal config','credentials.tar.age':b'literal cipher'}
    for i,s in enumerate(STEPS):
        backup=i<2;count,size=(1,len(files['schubert_nk.dump']))if i==0 else(2,len(files['config.tar'])+len(files['credentials.tar.age']))if i==1 else(0,0)
        new['schubert.batch_runs'].append(dict(id=505+i,run_id=run,step=s,status='SUCCESS'if backup else'SKIPPED',business_date='2026-10-09',attempt=4 if backup else 3,started_at='2026-10-08T21:33:23.000000Z',ended_at='2026-10-08T21:33:26.000000Z'if backup else'2026-10-08T21:33:23.000000Z',target_count=count,success_count=count,failure_count=0,byte_count=size,error_code=None if backup else'ALREADY_SUCCESSFUL',error_summary=None if backup else'step already successful for business date',expiry_cutoff_at=None,expiry_before_count=None,expiry_after_count=None))
    m=dict(format='NKBACKUP1',database='schubert_nk',runId=run,cutoff=cutoff,startedAt='2026-10-08T21:33:24.000000Z',contentFinishedAt='2026-10-08T21:33:25.000000Z',databaseStep={'id':505,'attempt':4,'startedAt':'2026-10-08T21:33:23.000000Z'},configurationStep={'id':506,'attempt':4,'startedAt':'2026-10-08T21:33:23.000000Z'},versions={'host':'pgpt-r2','app':'0.1.0-SNAPSHOT','schema':'028','os':'ubuntu-26.04','jdk':'25.0.4','postgresql':'18.6','artemis':'2.56.0','age':'1.2.1'},recipientSha256='1'*64,files={k:{'size':len(v),'sha256':hashlib.sha256(v).hexdigest()}for k,v in files.items()})
    raw=(json.dumps(m,separators=(',',':'))+'\n').encode();metadata=[28,1,992,977,stat.S_IFDIR|0o700,15,100,1,1]
    before={ROOT:{'metadata':metadata,'sha256':None}}
    for i in range(8):
        name=f'old{i}';before[ROOT+'/'+name]={'metadata':metadata[:],'sha256':None}
        for file in ('MANIFEST.json',*files):before[ROOT+'/'+name+'/'+file]={'metadata':[28,10+i,0,0,stat.S_IFREG|0o600,1,3,1,1],'sha256':'old-fixed'}
    for i in range(5):before[ROOT+f'/protected{i}']={'metadata':metadata[:],'sha256':None}
    after={k:copy.deepcopy(v)for k,v in before.items()if not any(k==ROOT+'/'+n or k.startswith(ROOT+'/'+n+'/')for n in ('old0','old1'))}
    after[ROOT]['metadata'][5]=14
    bundle=ROOT+'/20261009-063324-'+run;after[bundle]={'metadata':metadata[:],'sha256':None}
    for name,v in {'MANIFEST.json':raw,**files}.items():after[bundle+'/'+name]={'metadata':[28,100,0,0,stat.S_IFREG|0o600,1,len(v),1,1],'sha256':hashlib.sha256(v).hexdigest()}
    expected={'eligibleUpperBound':8,'maximumEligibleAfterNew':9,'retentionLimit':7,'expectedRetentionDeletes':2,'expectedDeleted':['old0','old1']}
    return [old,new,before,after,expected,raw,files,('NKRUN1\n'+run+'\n'+cutoff+'\n').encode(),{'lower':'2026-10-08T21:33:00Z','upper':'2026-10-08T21:35:00Z'}]


class Retention(unittest.TestCase):
    def test_literal_two_success_eight_skip_and_two_oldest(self):
        result=validate(*fixture());self.assertEqual(result['retentionDeleted'],2);self.assertEqual(result['eligibleAfter'],7)
        self.assertFalse(result['parentDoneAccepted'])

    def test_null_tampered_rows_files_old_backup_and_extra_source(self):
        for kind in ('oldrow','newcount','attempt','skipstatus','skipaudit','counter','otherdb','file','oldbyte','protected','extra','link','anchor','manifest'):
            a=fixture()
            if kind=='oldrow':a[1]['schubert.batch_runs'][0]['status']='FAILED'
            if kind=='newcount':a[1]['schubert.batch_runs'].pop()
            if kind=='attempt':a[1]['schubert.batch_runs'][-1]['attempt']=4
            if kind=='skipstatus':a[1]['schubert.batch_runs'][-1]['status']='SUCCESS'
            if kind=='skipaudit':a[1]['schubert.batch_runs'][-1]['expiry_before_count']=0
            if kind=='counter':a[1]['schubert.batch_runs'][-1]['target_count']=1
            if kind=='otherdb':a[1]['schubert.t0']=[None]
            if kind=='file':a[6]['config.tar']=b'tampered'
            if kind=='oldbyte':a[3][ROOT+'/old2/config.tar']['sha256']='foreign'
            if kind=='protected':a[3].pop(ROOT+'/protected0')
            if kind=='extra':a[3][ROOT+'/unknown']={}
            if kind=='link':a[3][ROOT]['metadata'][5]=13
            if kind=='anchor':a[7]=None
            if kind=='manifest':a[5]+=b'\n'
            with self.subTest(kind=kind),self.assertRaises(ValueError):validate(*a)

    def test_readonly_current_generation_and_all_row_windows(self):
        v=payload();compile(v,'<current retention capture>','exec')
        for x in ('1826480','095f6d1d7f8442b7b2b44ae59a4314f5','107901545407','pg650-fresh-parent-v2','==514','<=514','pg652-retention-post-v1','summary=env[',"['retention']",'pg_restore', 'n==rows()'):
            self.assertIn(x,v)
        for x in ('daemon-reload','.unlink(',"['systemctl','start'","['systemctl','stop'"):
            self.assertNotIn(x,v)


if __name__=='__main__':unittest.main()

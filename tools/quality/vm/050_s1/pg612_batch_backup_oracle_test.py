"""Independent SS341 literal vectors, never Production encode/step results."""
import copy,hashlib,json,unittest
from pg612_batch_backup_oracle import validate
class Test(unittest.TestCase):
 def setUp(self):
  self.old={'schubert.batch_runs':[]};self.old.update({str(n):[]for n in range(23)});self.new=copy.deepcopy(self.old)
  self.files={'schubert_nk.dump':b'PGDMP-literal','config.tar':b'config-literal','credentials.tar.age':b'cipher-literal'}
  self.oracle={'expected':{s:[]for s in ('notifications','questions','auth_sessions','login_ip_attempts','web_http_sessions','schubert.mq_outbox','schubert_web_session.web_log_outbox','app_logs','web_receipt_references','batch_runs','schubert.inbox_inspection_progress','schubert.log_cleanup_progress')},'inboxExpectedDeleted':[]}
  self.oracle['expected']['web_http_sessions']=[str(n) for n in range(229)]
  steps=['BACKUP_DB','BACKUP_CONFIG','CLEAN_NOTIFICATION','CLEAN_QUESTION','CLEAN_SESSION','CLEAN_INBOX_OUTBOX','CLEAN_LOG','CLEAN_BATCH_RUN','CLEAN_TRANSFER','CLEAN_EXPIRY']
  for i,s in enumerate(steps):
   count=1 if s=='BACKUP_DB'else 2 if s=='BACKUP_CONFIG'else 229 if s=='CLEAN_SESSION'else 0
   size=len(self.files['schubert_nk.dump'])if s=='BACKUP_DB'else len(self.files['config.tar'])+len(self.files['credentials.tar.age'])if s=='BACKUP_CONFIG'else 0
   self.new['schubert.batch_runs'].append({'id':i+1,'attempt':1,'step':s,'run_id':'3a53b979-fa01-47dd-92a6-7b26affcfb5c','business_date':'2026-10-09','status':'SUCCESS','target_count':count,'success_count':count,'failure_count':0,'byte_count':size,'error_code':None,'error_summary':None,'started_at':'2026-10-08T15:32:47.000000Z','ended_at':'2026-10-08T15:32:56.000000Z'})
   self.new['schubert.batch_runs'][-1].update(expiry_cutoff_at='2026-10-01T15:32:46.368375Z'if s=='CLEAN_EXPIRY'else None,expiry_before_count=0 if s=='CLEAN_EXPIRY'else None,expiry_after_count=0 if s=='CLEAN_EXPIRY'else None)
  self.m={'format':'NKBACKUP1','database':'schubert_nk','runId':'3a53b979-fa01-47dd-92a6-7b26affcfb5c','cutoff':'2026-10-08T15:32:46.368375Z','startedAt':'2026-10-08T15:32:48.000000Z','contentFinishedAt':'2026-10-08T15:32:55.000000Z','databaseStep':{'id':1,'attempt':1,'startedAt':'2026-10-08T15:32:47.000000Z'},'configurationStep':{'id':2,'attempt':1,'startedAt':'2026-10-08T15:32:47.000000Z'},'versions':{'host':'pgpt-r2','app':'0.1.0-SNAPSHOT','schema':'028','os':'ubuntu-26.04','jdk':'25.0.4','postgresql':'18.6','artemis':'2.56.0','age':'1.2.1'},'recipientSha256':'a'*64,'files':{n:{'size':len(b),'sha256':hashlib.sha256(b).hexdigest()}for n,b in self.files.items()}}
 def raw(self,m=None):return(json.dumps(self.m if m is None else m,separators=(',',':'))+'\n').encode('ascii')
 def test_literal_success_and_exact_bytes(self):
  got=validate(self.old,self.new,self.oracle,self.raw(),self.files);self.assertTrue(got['independentTenStepsVerified']);self.assertEqual(got['stepCounts']['BACKUP_CONFIG'],2)
  for changed in (b' ',b'\r\n',b'foreign'):
   with self.assertRaises((ValueError,KeyError,TypeError)):validate(self.old,self.new,self.oracle,self.raw()+changed,self.files)
 def test_all_rows_null_foreign_duplicate_and_counts(self):
  for field,value in [('run_id','foreign'),('step','unknown'),('status','SKIPPED'),('target_count',True),('success_count',1),('failure_count',1),('byte_count',1),('attempt',2),('business_date','2026-10-07'),('error_code','x'),('started_at',None),('ended_at','2026-10-08T04:03:00Z')]:
   bad=copy.deepcopy(self.new);bad['schubert.batch_runs'][-1][field]=value
   with self.assertRaises((ValueError,KeyError,TypeError)):validate(self.old,bad,self.oracle,self.raw(),self.files)
  for rows in (None,[],self.new['schubert.batch_runs'][:-1],self.new['schubert.batch_runs']+[self.new['schubert.batch_runs'][-1]]):
   bad=copy.deepcopy(self.new);bad['schubert.batch_runs']=rows
   with self.assertRaises((ValueError,KeyError,TypeError)):validate(self.old,bad,self.oracle,self.raw(),self.files)
 def test_manifest_identity_size_hash_order_null(self):
  for field,value in [('runId','foreign'),('cutoff','foreign'),('versions',None),('recipientSha256',None),('contentFinishedAt','2026-10-08T04:03:09Z')]:
   bad=copy.deepcopy(self.m);bad[field]=value
   with self.assertRaises((ValueError,KeyError,TypeError)):validate(self.old,self.new,self.oracle,self.raw(bad),self.files)
  for field in ('id','attempt','startedAt'):
   for value in (None,True,'foreign'):
    bad=copy.deepcopy(self.m);bad['databaseStep'][field]=value
    with self.assertRaises((ValueError,KeyError,TypeError)):validate(self.old,self.new,self.oracle,self.raw(bad),self.files)
  for name in self.files:
   bad=copy.deepcopy(self.m);bad['files'][name]['sha256']='b'*64
   with self.assertRaises(ValueError):validate(self.old,self.new,self.oracle,self.raw(bad),self.files)
   bad=copy.deepcopy(self.m);bad['files'][name]['size']=True
   with self.assertRaises(ValueError):validate(self.old,self.new,self.oracle,self.raw(bad),self.files)
if __name__=='__main__':unittest.main()

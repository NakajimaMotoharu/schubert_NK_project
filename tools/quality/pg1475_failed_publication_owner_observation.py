"""Current failed publication-only cohort/PID1 observation; mutation authority0."""
import inspect
import pg1464_failed_current_capture as previous

JOURNAL=r'''
 observations={}
 for unit in ['artemis.service','schubert-nk-cleanup.service','schubert-nk-expiry-cleanup.service']:
  state=units[unit];inv=state['InvocationID'];require(re.fullmatch('[0-9a-f]{32}',inv) is not None)
  raw=command(['journalctl','--boot='+BOOT.replace('-',''),'_PID=1','UNIT='+unit,'INVOCATION_ID='+inv,'-o','json','--no-pager'],1048576)
  records=[json.loads(line)for line in raw.splitlines()]
  require(1<=len(records)<=6 and all(r.get('_BOOT_ID')==BOOT.replace('-','')and r.get('_PID')=='1'and r.get('_UID')=='0'and r.get('UNIT')==unit and r.get('INVOCATION_ID')==inv for r in records))
  starts=[r for r in records if r.get('MESSAGE_ID')=='7d4958e842da4a758f6c1cdc7b36dcc5'and r.get('JOB_TYPE')=='start']
  done=[r for r in records if r.get('MESSAGE_ID')=='39f53479d3a045ac8e11786248231fbf'and r.get('JOB_TYPE')=='start'and r.get('JOB_RESULT')=='done']
  require(len(done)==1)
  if unit=='artemis.service':
   require(state['Type']=='simple' and len(starts)==0 and len(records)==1 and done[0]['JOB_ID']=='13935')
   require(within_root_period(int(state['ExecMainStartTimestampMonotonic']),int(done[0]['__MONOTONIC_TIMESTAMP'])))
  else:
   require(state['Type']=='oneshot'and len(starts)==1 and len(records)==2 and starts[0]['JOB_ID']==done[0]['JOB_ID'])
   require(within_root_period(int(starts[0]['__MONOTONIC_TIMESTAMP']),int(done[0]['__MONOTONIC_TIMESTAMP'])))
  require(5711141318<int(state['ExecMainStartTimestampMonotonic'])<7511141318)
  if unit!='artemis.service':require(state['MainPID']==state['ControlPID']=='0'and state['Job']==''and state['ActiveState']=='active'and state['SubState']=='exited'and state['ExecMainCode']=='1'and state['ExecMainStatus']=='0')
  observations[unit]={'pid1':records,'startingJob':starts[0]['JOB_ID'] if starts else None,'doneJob':done[0]['JOB_ID'],'invocation':inv,'rootOriginalDataCorrelationOnly':True,'missingStartingNotInvented':True}
 startup=runtime['startup'];rootPath='/run/schubert-nk/startup'
 require(set(startup)=={rootPath,rootPath+'/epoch.current',rootPath+'/b6e5cc96-3279-4cb8-a7f5-6584a3ac62c4.permit',rootPath+'/permit-start.intent'})
 # No owner/launch is invented and no already INVALID generation is rewritten.
 require(not any('.owner' in n or '.launch' in n or '.API.start.intent' in n or '.WEB.start.intent' in n for n in startup))
'''


def within_root_period(start,done):
    return type(start)is int and type(done)is int and 5711141318<start<done<7511141318


def payload():
    raw=previous.payload().replace('pg1464-failed-current-capture-v1','pg1475-failed-publication-owner-v1').replace('PG1464-failed-current-capture-v1','PG1475-failed-publication-owner-v1')
    raw=raw.replace('def snapshot():',inspect.getsource(within_root_period)+'\ndef snapshot():',1)
    marker=" return {'source':SOURCE,'boot':BOOT,'manifestSha256':BOM"
    assert raw.count(marker)==1
    raw=raw.replace(marker,JOURNAL+" return {'pid1CohortObservations':observations,'source':SOURCE,'boot':BOOT,'manifestSha256':BOM",1)
    compile(raw,'<current failed publication observation>','exec');return raw


def main():
    entry=inspect.getsource(previous.main).replace('pg1464-failed-current-capture-v1','pg1475-failed-publication-owner-v1')
    namespace={**previous.__dict__,'payload':payload}
    exec(compile(entry,'<new-only current owner transport>','exec'),namespace)
    return namespace['main']()


if __name__=='__main__':raise SystemExit(main())

"""One current readonly comparison of all18 properties/cost, under ten refs. No Root start."""
import inspect
import pg4214_quiescent_ten_ref_observation as previous
import pg4216_same_peer_observer_manager as manager

SLOT='pg4218-same-peer-observer-benchmark-v1'


def payload():
    raw=previous.payload().replace(previous.SLOT,SLOT)
    marker="with metadata_refs(manager,bus,tuple(old['units'])):\n"
    if raw.count(marker)!=1:raise ValueError('one real Ref scope required')
    prefix=raw[:raw.index(marker)]+'\nMANAGER_SOURCE='+repr(inspect.getsource(manager))+'\n'
    return prefix+marker+''.join(' '+line+'\n'for line in BODY.splitlines())+"\nvalue['newTenMetadataRefsNormalClose']=True\n(save/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value))\n"


BODY=r'''
import time,resource
native={};exec(MANAGER_SOURCE,native)
signed={};exec(SIGNED_SOURCE,signed)
materials=[{'path':str(p),'size':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for p in [pin,signature]]
require(signed['verify'](str(root),data['artifacts'],raw,materials)is True)
before=snapshot();require(not before['actors']and not before['flocks']and not before['database']['peers']and not before['database']['locks'])
configuration=config();require(all(CONFIG_CONTRACT['same'](old['configuration'][u],v,exec_record)for u,v in configuration.items()))
FIELDS18='Id,LoadState,ActiveState,SubState,Job,MainPID,ControlPID,InvocationID,Type,Restart,RemainAfterExit,Result,ExecMainCode,ExecMainStatus,ExecMainStartTimestampMonotonic,ExecMainExitTimestampMonotonic,KillMode,SendSIGKILL'
def slow(unit):
 text=command(['/usr/bin/systemctl','show',unit,'--property='+FIELDS18],1048576).decode();value={}
 for line in text.splitlines():
  k,v=line.split('=',1);require(k not in value);value[k]=v
 require(set(value)==set(FIELDS18.split(',')));return value
def cpu_children():
 r=resource.getrusage(resource.RUSAGE_CHILDREN);return round((r.ru_utime+r.ru_stime)*1000000000)
def measure(read):
 start=time.monotonic_ns();cpu=time.process_time_ns();children=cpu_children();value=read()
 return value,{'wallNanos':time.monotonic_ns()-start,'selfCpuNanos':time.process_time_ns()-cpu,'childCpuNanos':cpu_children()-children}
reader=native['NativeReader']();samples={'systemctl':[],'samePeer':[]};observations=[]
try:
 for n in range(20):
  for unit in ['schubert-nk-morning-controller.service','schubert-nk-api.service','schubert-nk-web.service','caddy.service']:
   expected,a=measure(lambda:slow(unit));actual,b=measure(lambda:reader.read(unit));require(expected==actual)
   samples['systemctl'].append(a);samples['samePeer'].append(b);observations.append({'round':n,'unit':unit,'expected':expected,'actual':actual})
finally:reader.close()
after=snapshot();require(before==after and configuration==config());require(signed['verify'](str(root),data['artifacts'],raw,materials)is True)
encoded=json.dumps({'before':before,'after':after,'configuration':configuration,'observations':observations,'samples':samples},sort_keys=True).encode()
with(save/'observed.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(encoded);f.flush();os.fsync(f.fileno())
totals={name:{key:sum(v[key]for v in rows)for key in ['wallNanos','selfCpuNanos','childCpuNanos']}for name,rows in samples.items()}
value={'actualExit':0,'source':data['source']['commit'],'BOM':sha,'boot':boot,'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'privateSha256':hashlib.sha256(encoded).hexdigest(),'perTransportReadCount':80,'fieldsPerRead':18,'all1440ValuesSame':True,'totals':totals,
 'allOriginalDataAndSourceSame':True,'all32DeclarationsSame':True,'samePeerBusNormalClose':True,'stateChangingActions':0,
 'rootTimeoutCauseProved':False,'authorityIssued':False,'formalAccepted':False}
'''


def main():
    ns={**vars(__import__('pg4210_quiescent_current_read')),'SLOT':SLOT,'payload':payload}
    exec(compile(inspect.getsource(ns['main']),'<bounded manager benchmark>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())

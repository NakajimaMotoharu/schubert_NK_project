"""Independent seven finite phases/new187 and all11 preserved data; never a Root start."""
import ast
import builtins
import hashlib
import inspect
import json
import os
import subprocess
import symtable
from pyflakes.api import check
import pg3794_hygiene_publication_post as legacy
import pg4540_failed_current_publication_sources as role
from pg1446_current_cold_stage import W,P,SSH
from pg4434_current_candidate_admission_read import authenticate_host
from pg1674_critical_management_gate import management_gate
from pg4442_failed_current_view_qualification import strict_equal,journal_rows

SLOT='pg4552-failed-current-publication-post-v1'


def check_embedded_namespace(block,outer):
    def defined(table):
        return {s.get_name()for s in table.get_symbols()if s.is_assigned()or s.is_imported()or s.is_namespace()}
    table=symtable.symtable(block,'<actual embedded finite verifier>','exec')
    available=defined(symtable.symtable(outer,'<actual full post>','exec'))|defined(table)|set(dir(builtins))
    referenced=set()
    def visit(t):
        for s in t.get_symbols():
            if s.is_global()and s.is_referenced():referenced.add(s.get_name())
        for child in t.get_children():visit(child)
    visit(table);missing=referenced-available
    if missing:raise ValueError('undefined embedded globals: '+','.join(sorted(missing)))
    return True


def publication_checks():
    raw=inspect.getsource(legacy.publication).replace('pg3788_ordinary_publication_contract','pg4540_ordinary_publication_contract')
    ns={**vars(legacy),'role':role};exec(compile(raw,'<all seven independent phase checks>','exec'),ns)
    result=ns['publication']()
    old='genuineParentNormalWarningOriginal=true\\ncurrentManagerGc=true\\n'
    if result.count(old)!=1:raise ValueError('one independent failed-data completion receipt')
    result=result.replace(old,'genuineParentNormalWarningOriginal=false\\ncurrentManagerGc=false\\nfailedParent143DataOnly=true\\n',1)
    result=result.replace("all(after[k]==old_after[k]for k in old_after if k!='startup')","all(strict_equal(after[k],old_after[k])for k in old_after if k!='startup')")
    result=result.replace('require(json.loads(pub_before)==old_after)','require(strict_equal(json.loads(pub_before),old_after))')
    old='startsStopsReloadsEpochWrites0=true\\noldUnknownNormalized=false'
    if result.count(old)!=1:raise ValueError('one truthful independent publication write receipt')
    return result.replace(old,'startsStopsReloadsBusinessWrites0=true\\ncanonicalInvalidEpochWritten=true\\noldUnknownNormalized=false',1)


def reader_prefix():
    encoded=(W/'pg4482-bound-configuration-pair-read-v1/payload.private.py').read_bytes()
    if hashlib.sha256(encoded).hexdigest()!='f2cac6424e371314b6c7661b520bb78a1584510e20faf0da40af6870507b7376':raise ValueError('fixed full19/32/24 reader')
    raw=encoded.decode();marker="os.umask(0o077);save=base/'pg4482-bound-configuration-pair-read-v1'"
    if raw.count(marker)!=1:raise ValueError('one data-only prelude before old owner capture')
    prefix=raw[:raw.index(marker)]
    replacements={role.CURRENT:role.SOURCE,role.CURRENT_BOM:role.BOM,"data['release']=='0.1.0-PG3976'":"data['release']=='0.1.0-PG4432'","pg3976-manifest.sig":"pg4432-manifest.sig"}
    for old,new in replacements.items():
        if old not in prefix:raise ValueError('one new-current verifier binding')
        prefix=prefix.replace(old,new)
    return prefix


BODY=r'''
import dbus,pathlib
os.umask(0o077);save=base/'pg4552-failed-current-publication-post-v1';require(not os.path.lexists(save));save.mkdir(mode=0o700)
def save_private(name,value):
 encoded=json.dumps(value,sort_keys=True).encode();require(len(encoded)<=67108864)
 with(save/name).open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(encoded);f.flush();os.fsync(f.fileno())
 fd=os.open(save,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:os.fsync(fd)
 finally:os.close(fd)
 return hashlib.sha256(encoded).hexdigest()
def metadata9(s):return(s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
def strict(path,mode,bound):
 s=path.lstat();require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,mode,1)and not os.listxattr(path)and s.st_size<=bound)
 value=path.read_bytes();require(len(value)==s.st_size and metadata9(path.lstat())==metadata9(s));return value
expected_raw=(base/'pg4440-failed-full-image-diagnosis-v1/canonical-first11.private.json').read_bytes()
require(hashlib.sha256(expected_raw).hexdigest()=='8e000cbabdde5c903c5c6b48e875fe4b104ee54520e0b19a233a959c510d00ff');expected=json.loads(expected_raw)
after={k:v for k,v in expected.items()if k!='native'};require(len(after)==10)
bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager');refs=[]
try:
 for unit in sorted(expected['units']):manager.LoadUnit(unit);manager.RefUnit(unit);refs.append(unit)
 require(len(refs)==10)
 exec(PUBLICATION_CHECKS)
 journal_contract={};exec(JOURNAL_SOURCE,journal_contract)
 def capture(label):
  value=snapshot();save_private(label+'-raw8.private.json',value)
  cfg=config();save_private(label+'-config.private.json',cfg)
  journal_raw=command(['/usr/bin/journalctl','--boot='+boot.replace('-',''),'_PID=1','UNIT=schubert-nk-morning-controller.service','INVOCATION_ID=bbcdb69957764d489a9c757b441542fd','-o','json','--no-pager'],4194304)
  save_private(label+'-journal-raw.private.json',{'hex':journal_raw.hex()});journal=journal_rows(journal_raw)
  files={}
  for name in expected['unitFilesActual']:
   p=Path(name);files[name]=metadata(p)+[hashlib.sha256(p.read_bytes()).hexdigest()]
  durable=value['durable']
  full={'units':value['units'],'configuration':cfg,'rows':value['database']['rows'],'pid1':journal,'startup':value['startup'],
   'originals':durable['originals'],'backup':durable['backup'],'extraDurable':{k:durable[k]for k in expected['extraDurable']},
   'unitFilesActual':files,'runtime':value['runtime'],'native':value['native']}
  digest=save_private(label+'-full11.private.json',full)
  require(strict_equal(json.loads(journal_contract['project'](journal_raw)),journal))
  require(not value['actors']and not value['database']['peers']and not value['database']['locks']and not value['flocks'])
  require(strict_equal(full,expected)and len(full['rows'])==24 and sum(v.get('sha256')is not None for v in full['native'].values())==58)
  return full,digest
 first,first_sha=capture('first');second,second_sha=capture('second');require(strict_equal(first,second))
 parent=second['units']['schubert-nk-morning-controller.service'];require(parent['ActiveState']==parent['SubState']=='failed'and parent['Result']=='timeout'and parent['ExecMainCode']=='1'and parent['ExecMainStatus']=='143'and parent['InvocationID']=='bbcdb69957764d489a9c757b441542fd')
 require(hashlib.sha256(Path('/var/lib/schubert-nk/maintenance/attempts/8314450e-0dd5-4986-875c-81f73e1b50b2.done').read_bytes()).hexdigest()=='654073a05ac1101060b235c8dc1e058efb94f0884e4eb87613b7f182b199644a')
 require(hashlib.sha256(strict(signature,0o400,64)).hexdigest()=='d8df41162f3c281e79ffb6a85880481a41e4e5322cd289e841b18949c63440a2')
 require(manifest.read_bytes()==raw and current.resolve(strict=True)==root and boot==Path('/proc/sys/kernel/random/boot_id').read_text().strip())
finally:
 for unit in reversed(refs):manager.UnrefUnit(unit)
 bus.close()
value={'actualExit':0,'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'productionSource':data['source']['commit'],'candidateSource':data['source']['commit'],
 'candidateManifestSha256':sha,'boot':boot,'postSha256':second_sha,'firstFull11Sha256':first_sha,'sevenFinitePhasesVerified':True,'all24And32Unchanged':True,
 'whole187SignedArtifactBytesVerified':True,'allTenKernelEmpty':True,'allClientAdvisoryFlock0':True,'originalBackupNative58Preserved':True,
 'canonicalInvalidEpochApprovalCurrentAndOldLinkVerified':True,'unitBytesInodesConfigurationUnchanged':True,'newTenReferencesReturnedNormally':len(refs)==10,
 'unitExchangeAndReload':False,'newSourceParentNotStarted':True,'oldParent143DataOnly':True,'oldNativeNotAppliedToNewSource':True,'dbWrites':0,'signalsOrStarts':0,'formalAccepted':False}
save_private('manifest.safe.json',value);print(json.dumps(value))
'''


def payload():
    fixed=json.loads((W/'pg4548-frozen-v1.safe.json').read_bytes())
    if fixed['actualExit']!=0:raise ValueError('actual all24 current-JAR host compile0')
    sources=role.sources()
    result='PUBLICATION_FILES='+repr(fixed['fileHashes'])+'\nPUBLICATION_CHECKS='+repr(publication_checks())+'\nJOURNAL_SOURCE='+repr(sources['pg4540_stable_journal.py'])+'\n'+inspect.getsource(strict_equal)+'\n'+inspect.getsource(journal_rows)+'\n'+reader_prefix()+'\n'+BODY
    # Inline the actual verifier in the retained metadata scope. This exposes
    # its real globals to the ordinary whole-payload static check as well.
    marker=' exec(PUBLICATION_CHECKS)\n'
    if result.count(marker)!=1:raise ValueError('one retained-scope finite verifier boundary')
    result=result.replace(marker,''.join(' '+line+'\n'for line in publication_checks().splitlines()),1)
    if check(result,'<new187 full11 all seven phase independent post>'):raise ValueError('all emitted static0')
    check_embedded_namespace(publication_checks(),result)
    ast.parse(result);return result


def main():
    receipt=json.loads((W/'pg4544-activate-v1.safe.json').read_bytes())
    if receipt['actualExit']!=0 or receipt['sourceQualified']is not True or receipt['currentApprovalEpochChanged']is not True:raise ValueError('genuine original finite publication0 first')
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed independent source first')
    raw=payload();authenticate_host();os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);(out/'payload.private.py').write_text(raw)
    with management_gate(P/'current-management-critical.lock'):
        result=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw.encode(),capture_output=True,timeout=240)
    (out/'stdout.safe.json').write_bytes(result.stdout);(out/'stderr.private.log').write_bytes(result.stderr)
    value={'actualExit':result.returncode,'productionSource':role.SOURCE,'candidateManifestSha256':role.BOM,'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'formalAccepted':False}
    if result.returncode==0:value['result']=json.loads(result.stdout)
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return result.returncode


if __name__=='__main__':raise SystemExit(main())

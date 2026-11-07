"""Explicit index-frozen Test metadata only; own javac followed by parse, never Test compile/run."""
from pathlib import Path
import collections, datetime, hashlib, json, stat, subprocess, sys
import pg9666_pagination_static as c
R=Path(__file__).resolve().parents[4]
BASE=R/'evidence/01_PT/018_NK-OPS-001'
FREEZE=BASE/'evidence/PG22696-tracked-test-wait-inputs-v1'
OUT=BASE/'evidence/PG22698-tracked-test-wait-inventory-v1'
SLOT=R.parent/'pgpt-runs/PG379/pg22698-tracked-test-wait-inventory-v1'
TOOL=BASE/'input/243_TrackedTestWaitAstCheck.java'
BLOCK=('RootFailedStart','SnapshotKeyCloseWitness','pg9892_')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_bytes())
write=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def index():
    allowed={};excluded=[]
    for entry in subprocess.check_output(['git','ls-files','--stage','-z','--','src'],cwd=R).split(b'\0'):
        if not entry:continue
        meta,name=entry.decode().split('\t',1);mode,oid,stage=meta.split()
        if not name.endswith('.java') or '/src/test/java/' not in name:continue
        # Exclusion uses index metadata only; never stat/read/hash excluded source.
        if any(x in name for x in BLOCK) or mode!='100644' or stage!='0':
            excluded.append(dict(path=name,mode=mode,stage=stage,reason='PROTECTED_PATH_OR_NONREGULAR_INDEX'));continue
        assert name.startswith('src/') and '..' not in Path(name).parts
        allowed[name]=dict(mode=mode,gitBlob=oid)
    return dict(sorted(allowed.items())),sorted(excluded,key=lambda x:x['path'])
def checked_bytes(name,meta):
    assert not any(x in name for x in BLOCK)
    p=R/name;assert stat.S_ISREG(p.lstat().st_mode) and not p.is_symlink()
    for parent in p.parents:
        if parent==R:break
        assert not parent.is_symlink()
    data=p.read_bytes()
    oid=subprocess.check_output(['git','hash-object','--stdin'],cwd=R,input=data).decode().strip()
    assert oid==meta['gitBlob'],name
    return hashlib.sha256(data).hexdigest()
def main():
    names,excluded=index();assert len(names)==956 and len(excluded)==2
    if sys.argv[1:] == ['--freeze']:
        assert not FREEZE.exists();inputs={n:dict(v,sha256=checked_bytes(n,v)) for n,v in names.items()}
        FREEZE.mkdir();write(FREEZE/'manifest.json',dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),inputs=inputs,excludedBeforeIO=excluded,checkedSources=len(inputs),modules=dict(collections.Counter(n.split('/')[1] for n in inputs)),tool=dict(path=str(TOOL.relative_to(R)),sha256=sha(TOOL)),productTestsExecuted=0,newProductTests=0,newAcceptance=0));print(json.dumps(dict(frozen=len(inputs),excluded=len(excluded),manifestSha256=sha(FREEZE/'manifest.json'))));return
    assert not sys.argv[1:];assert not OUT.exists() and not SLOT.exists();f=load(FREEZE/'manifest.json');assert names=={n:{k:v[k] for k in ('mode','gitBlob')} for n,v in f['inputs'].items()} and excluded==f['excludedBeforeIO'];assert sha(TOOL)==f['tool']['sha256'];assert all(checked_bytes(n,v)==v['sha256'] for n,v in f['inputs'].items())
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()
    for p in [TOOL,Path(__file__),FREEZE/'manifest.json']:
        assert p.read_bytes()==subprocess.check_output(['git','show',head+':'+str(p.relative_to(R))],cwd=R)
    SLOT.mkdir();(SLOT/'source').mkdir();(SLOT/'classes').mkdir();mirror=SLOT/'source/TrackedTestWaitAstCheck.java';mirror.write_bytes(TOOL.read_bytes());c.SLOT=SLOT;jdk=R.parent/'toolchain/jdk-25.0.4/bin'
    stages={};stages['tool-javac']=c.step('tool-javac',[str(jdk/'javac'),'-proc:none','-encoding','UTF-8','-Xlint:all','-Werror','-d',str(SLOT/'classes'),str(mirror)],R);assert stages['tool-javac']['actualExit']==0 and not stages['tool-javac']['timedOut']
    stages['parse']=c.step('parse',[str(jdk/'java'),'-cp',str(SLOT/'classes'),'TrackedTestWaitAstCheck',str(R),*names],R,timeout=180);assert stages['parse']['actualExit']==0 and not stages['parse']['timedOut']
    rows=[line.split('\t') for line in (SLOT/'parse.stdout').read_text().splitlines()];assert sorted(x[1] for x in rows if x[0]=='FILE')==list(names)
    sites=[dict(kind=x[0],path=x[1],owner=x[2],method=x[3],receiver=x[4],name=x[5],arity=int(x[6]) if x[0]=='CALL' else None,line=int(x[7]),columnUtf16=int(x[8]),receiverClassification='UNKNOWN_NOT_YET_RESOLVED',sourceSha256=f['inputs'][x[1]]['sha256']) for x in rows if x[0] in ('CALL','REF')]
    assert all(checked_bytes(n,v)==v['sha256'] for n,v in f['inputs'].items());assert index()==(names,excluded)
    OUT.mkdir();files={}
    for name in ('tool-javac.stdout','tool-javac.stderr','tool-javac-exit.safe.json','parse.stdout','parse.stderr','parse-exit.safe.json'):
        (OUT/name).write_bytes((SLOT/name).read_bytes());files[name]=sha(OUT/name)
    write(OUT/'sites.json',sites);files['sites.json']=sha(OUT/'sites.json')
    m=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=head,productionCoreMain='7aed8eace7c844c2f79f2e39db766faf914890d5',frozenInputs=dict(path=str((FREEZE/'manifest.json').relative_to(R)),sha256=sha(FREEZE/'manifest.json')),inputHashes={n:v['sha256'] for n,v in f['inputs'].items()},checkedSources=len(names),excludedBeforeIO=excluded,methodInvocationSites=sum(s['kind']=='CALL' for s in sites),methodReferenceSites=sum(s['kind']=='REF' for s in sites),nameCounts=dict(collections.Counter(s['name'] for s in sites)),noArgumentInvocationCandidates=sum(s['kind']=='CALL' and s['arity']==0 for s in sites),allReceiverTypesUnresolved=True,noBlockingOrSafeInference=True,waitAuditOrLateralClosureComplete=False,sourceBytesUnchanged=True,productTestsExecuted=0,newProductTests=0,newSourceProofs=0,newAcceptance=0,wholeF03Accepted=False,whole451Accepted=False,effortRate=None,stages=stages,files=files,ownToolClassHashes={p.name:sha(p) for p in (SLOT/'classes').iterdir()},tool=dict(path=str(TOOL.relative_to(R)),sha256=sha(TOOL),mirrorSha256=sha(mirror)),producer=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(__file__)))
    write(OUT/'manifest.json',m);print(json.dumps({k:m[k] for k in ('actualExit','checkedSources','methodInvocationSites','methodReferenceSites','nameCounts','noArgumentInvocationCandidates')}))
if __name__=='__main__':main()

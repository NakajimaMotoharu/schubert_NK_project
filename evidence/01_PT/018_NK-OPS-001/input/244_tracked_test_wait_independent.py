"""Independent frozen-index/source/position checks; no original Test compilation/execution."""
from pathlib import Path
import collections,copy,datetime,hashlib,json,re,stat,subprocess
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';P=B/'evidence/PG22698-tracked-test-wait-inventory-v1';OUT=B/'evidence/PG22700-tracked-test-wait-independent-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_bytes())
PART=re.compile(r'(?P<comment>//[^\n]*|/\*[\s\S]*?\*/)|"""[\s\S]*?"""|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'')
def mask(text):
    def replace(m):
        value=''.join('\n' if c=='\n' else ' ' for c in m.group());return value if m.group('comment') else 'L'+value[1:]
    return PART.sub(replace,text)
def valid(site,text):
    if site['name'] not in ['get','join','await','wait','park','parkNanos','parkUntil'] or site['kind'] not in ['CALL','REF']:return False
    lines=text.splitlines(keepends=True);line=site['line'];column=site['columnUtf16']
    if type(line) is not int or type(column) is not int or not 0<line<=len(lines) or column<1:return False
    try:prefix=lines[line-1].encode('utf-16-le')[:(column-1)*2].decode('utf-16-le')
    except UnicodeError:return False
    at=sum(map(len,lines[:line-1]))+len(prefix);name=site['name']
    if text[at:at+len(name)]!=name:return False
    code=mask(text);tail=code[at+len(name):]
    if site['kind']=='REF':return site['arity'] is None and re.search(r'::\s*(?:<[^<>]*>\s*)?$',code[max(0,at-100):at]) is not None
    if type(site['arity']) is not int or site['arity']<0:return False
    match=re.match(r'\s*\(',tail)
    if not match:return False
    opening=at+len(name)+match.end()-1;depth=1;end=None
    for i in range(opening+1,len(code)):
        if code[i]=='(':depth+=1
        elif code[i]==')':
            depth-=1
            if depth==0:end=i;break
    if end is None:return False
    empty=not code[opening+1:end].strip();return empty==(site['arity']==0)
def main():
    assert not OUT.exists();m=load(P/'manifest.json');assert m['actualExit']==0;fpath=R/m['frozenInputs']['path'];assert sha(fpath)==m['frozenInputs']['sha256'];f=load(fpath);assert len(f['inputs'])==m['checkedSources']==956
    indexed={};excluded=[]
    for raw in subprocess.check_output(['git','ls-files','--stage','-z','--','src'],cwd=R).split(b'\0'):
        if not raw:continue
        meta,name=raw.decode().split('\t',1);mode,oid,stage=meta.split()
        if not name.endswith('.java') or '/src/test/java/' not in name:continue
        if any(x in name for x in ['RootFailedStart','SnapshotKeyCloseWitness','pg9892_']) or mode!='100644' or stage!='0':
            excluded.append(dict(path=name,mode=mode,stage=stage,reason='PROTECTED_PATH_OR_NONREGULAR_INDEX'));continue
        indexed[name]=(mode,oid)
    assert sorted(excluded,key=lambda x:x['path'])==f['excludedBeforeIO']==m['excludedBeforeIO'] and len(excluded)==2
    assert set(indexed)==set(f['inputs'])==set(m['inputHashes']);source={}
    for name,h in m['inputHashes'].items():
        assert not any(x in name for x in ['RootFailedStart','SnapshotKeyCloseWitness','pg9892_'])
        p=R/name;assert stat.S_ISREG(p.lstat().st_mode) and not p.is_symlink();data=p.read_bytes();assert hashlib.sha256(data).hexdigest()==h==f['inputs'][name]['sha256'];oid=subprocess.check_output(['git','hash-object','--stdin'],cwd=R,input=data).decode().strip();assert indexed[name]==(f['inputs'][name]['mode'],oid) and oid==f['inputs'][name]['gitBlob'];source[name]=data.decode()
    for name,h in m['files'].items():assert sha(P/name)==h
    for label,stage in m['stages'].items():
        assert stage==load(P/(label+'-exit.safe.json')) and stage['actualExit']==0 and not stage['timedOut']
        for stream in ['stdout','stderr']:assert sha(P/(label+'.'+stream))==stage[stream+'Sha256']
    cmd=m['stages']['parse']['command'];assert cmd[1]=='-cp' and cmd[3]=='TrackedTestWaitAstCheck' and cmd[4]==str(R) and cmd[5:]==sorted(source)
    slot=Path(cmd[2]).parent;assert slot==R.parent/'pgpt-runs/PG379/pg22698-tracked-test-wait-inventory-v1'
    assert {p.name:sha(p) for p in (slot/'classes').iterdir()}==m['ownToolClassHashes'];assert all(n.startswith('TrackedTestWaitAstCheck') and n.endswith('.class') for n in m['ownToolClassHashes'])
    j=m['stages']['tool-javac']['command'];assert j[1:8]==['-proc:none','-encoding','UTF-8','-Xlint:all','-Werror','-d',str(slot/'classes')] and j[8:]==[str(slot/'source/TrackedTestWaitAstCheck.java')]
    tool=R/m['tool']['path'];assert sha(tool)==m['tool']['sha256']==m['tool']['mirrorSha256']==sha(slot/'source/TrackedTestWaitAstCheck.java');code=tool.read_text()
    assert 'task.parse()' in code and not any(v in code for v in ['task.analyze(','task.generate(','Class.forName','newInstance(','System.getenv','System.load'])
    assert 'List.of("-proc:none", "--release", "25")' in code and 'node.getType().toString()' not in code and 'type(node.getType())' in code
    for tree in ['AnnotatedTypeTree','IdentifierTree','MemberSelectTree','ArrayTypeTree','PrimitiveTypeTree','ParameterizedTypeTree','WildcardTree']:assert tree in code
    rows=[x.split('\t') for x in (P/'parse.stdout').read_text().splitlines()];assert sorted(x[1] for x in rows if x[0]=='FILE')==sorted(source)
    assert all(x[0] in ['FILE','IMPORT','VAR','CALL','REF'] and x[1] in source for x in rows)
    # Java type/init output is structural identifiers; quotes/backslashes cannot be copied literals.
    assert all(not any(ch in x[5]+x[6] for ch in ['"',"'",'\\']) for x in rows if x[0]=='VAR')
    sites=load(P/'sites.json');raw=[x for x in rows if x[0] in ['CALL','REF']];assert len(sites)==len(raw)
    keys=set()
    for s,x in zip(sites,raw):
        assert (s['kind'],s['path'],s['owner'],s['method'],s['receiver'],s['name'])==tuple(x[:6])
        assert s['arity']==(int(x[6]) if x[0]=='CALL' else None) and s['line']==int(x[7]) and s['columnUtf16']==int(x[8])
        assert s['sourceSha256']==m['inputHashes'][s['path']] and s['receiverClassification']=='UNKNOWN_NOT_YET_RESOLVED'
        assert valid(s,source[s['path']]),(s['path'],s['line'],s['name'])
        key=(s['path'],s['line'],s['columnUtf16'],s['kind']);assert key not in keys;keys.add(key)
    calls=sum(s['kind']=='CALL' for s in sites);refs=len(sites)-calls;zero=sum(s['kind']=='CALL' and s['arity']==0 for s in sites)
    assert calls==m['methodInvocationSites'] and refs==m['methodReferenceSites'] and zero==m['noArgumentInvocationCandidates'] and dict(collections.Counter(s['name'] for s in sites))==m['nameCounts']
    sample=next(s for s in sites if s['kind']=='CALL');negative=[]
    for k,v in [('line',0),('columnUtf16',0),('name','missing'),('kind','OTHER'),('arity',1 if sample['arity']==0 else 0)]:
        b=copy.deepcopy(sample);b[k]=v;assert not valid(b,source[sample['path']]);negative.append(k)
    assert m['allReceiverTypesUnresolved'] and m['noBlockingOrSafeInference'] and not m['waitAuditOrLateralClosureComplete']
    OUT.mkdir();result=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=m['source'],productionCoreMain=m['productionCoreMain'],originalManifest=dict(path=str((P/'manifest.json').relative_to(R)),sha256=sha(P/'manifest.json')),checkedSources=len(source),excludedBeforeIO=excluded,verifiedSourceNamePositions=len(sites),methodInvocationSites=calls,methodReferenceSites=refs,independentlyVerifiedZeroArgVsNonzeroCalls=calls,nonzeroExactArityNumbersFromParserOnly=True,noArgumentInvocationCandidates=zero,nameCounts=m['nameCounts'],allReceiverTypesUnresolved=True,noBlockingOrSafeInference=True,waitAuditOrLateralClosureComplete=False,metadataNegativeGuards=negative,productTestsExecuted=0,newProductTests=0,newSourceProofs=0,newAcceptance=0,wholeF03Accepted=False,whole451Accepted=False,effortRate=None,sourceBytesUnchanged=True,verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(__file__),source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()))
    (OUT/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,sources=len(source),sites=len(sites),zeroArgCandidates=zero,manifestSha256=sha(OUT/'manifest.json'))))
if __name__=='__main__':main()

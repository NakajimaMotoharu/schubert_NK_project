"""BUG3188: explicit current safe byte union from seven qualified pure Web closures + Protocol176."""
from pathlib import Path
import datetime,hashlib,json,shutil,xml.etree.ElementTree as E,zipfile
import pgpt_closed_host_profile as policy
from pgpt_spotbugs_contract import canonical_plugin
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';runs=r.parent/'pgpt-runs/PG379';tc=r.parent/'toolchain'
ld=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
work=runs/'pg37782-pure-protocol-web-maxlow-v1';out=b/'evidence/PG37782-pure-protocol-web-maxlow-prepare-v1';assert not work.exists() and not out.exists()
sources={};byte_inputs={};scope_rows=[];deps={}
for number in (37470,37498,37522,37552,37702,37738,37772):
    matches=list((b/'evidence').glob('PG'+str(number)+'*'));assert len(matches)==1
    post_path=matches[0]/'manifest.json';post=ld(post_path);assert post['actualExit']==0 and not post['formalUpdated']
    ppath=r/post['prepare']['path'];assert sha(ppath)==post['prepare']['sha256'];p=ld(ppath);assert p['actualExit']==0
    websources={n:h for n,h in p['mainInputHashes'].items() if n.startswith('src/schubert-nk-web/src/main/java/')}
    assert websources
    for n,h in websources.items():
        policy.relative_name(n);assert sha(r/n)==h
        if n in sources:assert sources[n]==h
        sources[n]=h
    webbytes={n:h for n,h in p['physicalClassHashes'].items() if n.startswith('dev/codex/schubert/nk/web/')};assert webbytes
    for n,h in webbytes.items():
        policy.relative_name(n);source=Path(p['work'])/'component'/n;assert sha(source)==h
        if n in byte_inputs:assert byte_inputs[n]['sha256']==h
        else:byte_inputs[n]=dict(path=str(source),sha256=h)
    for n,h in p['toolDependencyHashes'].items():
        if '/toolchain/m2/repository/' not in n:continue
        if '/commons-logging/' in n and '/1.4.0/' not in n:continue
        assert sha(Path(n))==h
        if n in deps:assert deps[n]==h
        deps[n]=h
    scope_rows.append(dict(independentPost=ref(post_path),prepare=ref(ppath),originalUnitSource=post['source'],currentMainSourceHashes=websources,webPhysicalClassHashes=webbytes,oldExecChangedOrReplayed=False))
proto_path=b/'evidence/PG37688-web-enum-current-protocol176-v1/manifest.json';proto=ld(proto_path);assert proto['actualExit']==0 and len(proto['physicalClassHashes'])==176
for n,h in proto['inputHashes'].items():
    policy.relative_name(n);assert sha(r/n)==h
    if '/src/main/java/' in n:sources[n]=h
jar=Path(proto['jar']['path']);assert sha(jar)==proto['jar']['sha256']
with zipfile.ZipFile(jar) as archive:
    for n,h in proto['physicalClassHashes'].items():
        policy.relative_name(n);assert n.startswith('dev/codex/schubert/nk/protocol/') and n not in byte_inputs
        raw=archive.read(n);assert hashlib.sha256(raw).hexdigest()==h;byte_inputs[n]=dict(zipPath=str(jar),zipEntry=n,sha256=h)
assert all(n.startswith('dev/codex/schubert/nk/web/') or n.startswith('dev/codex/schubert/nk/protocol/') for n in byte_inputs)
assert not any(any(k in n for k in policy.DENIED) for n in byte_inputs)
# Match the actual current Web transitive commons-logging version. No alternate providers coexist.
current=ld(b/'evidence/PG37690-web-enum-eight-source-closure-v1/manifest.json')['sdkHashes'];deps.update(current)
assert len([n for n in deps if '/commons-logging/' in n])==1
providers={}
for n,h in deps.items():
    assert sha(Path(n))==h
    with zipfile.ZipFile(n) as archive:providers[n]='META-INF/services/java.sql.Driver' in archive.namelist()
assert not any(providers.values())
work.mkdir();out.mkdir();target=work/'target/classes';target.mkdir(parents=True)
for n,row in byte_inputs.items():
    dest=target/n;dest.parent.mkdir(parents=True,exist_ok=True)
    if 'zipPath' in row:
        with zipfile.ZipFile(row['zipPath']) as archive:dest.write_bytes(archive.read(row['zipEntry']))
    else:shutil.copyfile(row['path'],dest)
    assert sha(dest)==row['sha256']
ns='{http://maven.apache.org/POM/4.0.0}';E.register_namespace('',ns[1:-1]);pom=E.parse(runs/'pg37758-web-trace-current24-v1/pom.xml').getroot();ds=pom.find(ns+'dependencies');assert ds is not None;ds.clear()
for i,n in enumerate(sorted(deps)):
    d=E.SubElement(ds,ns+'dependency')
    for key,value in [('groupId','dev.codex.schubert.quality'),('artifactId','current-sdk-'+str(i)),('version','1'),('scope','system'),('systemPath',n)]:E.SubElement(d,ns+key).text=value
E.ElementTree(pom).write(work/'pom.xml',encoding='unicode',xml_declaration=True)
assert E.tostring(canonical_plugin((work/'pom.xml').read_text()))==E.tostring(canonical_plugin((r/'src/schubert-nk-web/pom.xml').read_text()))
actual={str(p.relative_to(target)):sha(p) for p in target.rglob('*.class')};assert actual=={n:v['sha256'] for n,v in byte_inputs.items()}
v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceCore='a013a6d676454082de3c59bc199e87f37fefe159',work=str(work),scopeRows=scope_rows,protocol=ref(proto_path),sourceHashes=sources,byteInputs=byte_inputs,physicalClassHashes=actual,dependencies=deps,classpathSqlDrivers=providers,analysisPomSha256=sha(work/'pom.xml'),analysisOnlyNoSourcesNoTestClasses=True,oldProductUnitExecsUnchanged=True,productCompileOrTestsExecuted=0,heldBinaryActions=0,actualRootVmDbNativeKeysAuthorityActions=0,formalUpdated=False,newAcceptance=0)
(out/'manifest.json').write_text(json.dumps(v,indent=2)+'\n');print(dict(actualExit=0,Protocol176=176,WebPhysical=len(actual)-176,safePhysicalTotal=len(actual),sourceCount=len(sources),wholeProofs=7,compiledOrTests=0))

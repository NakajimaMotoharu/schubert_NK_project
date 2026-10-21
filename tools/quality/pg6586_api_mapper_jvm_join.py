"""Bind84 explicit mapper/secondary calls to original Jar bytecode and aggregate line hits."""
import json
import re
import subprocess
import xml.etree.ElementTree as ET
from pg5940_private_lock_compile import ROOT, W, BASE, TC, sha
from pg6580_api_mapper_plan import spans

CALL=re.compile(r'(TemporaryInfrastructureException|AuthenticationInfrastructureException)\.(preserveFatal|attachSecondary)\(')


def jvm_calls(text):
    result=[]
    chunks=re.split(r'(?=^  (?:public|protected|private|static)\b[^\n]*[;{]$)',text,flags=re.M)
    for chunk in chunks:
        lines=[(int(bci),int(line)) for line,bci in re.findall(r'^\s+line (\d+): (\d+)$',chunk,re.M)]
        for bci,owner,method in re.findall(r'^\s+(\d+): invokestatic\s+.*// Method ([\w/$]+)\.(preserveFatal|attachSecondary):',chunk,re.M):
            preceding=[(offset,line) for offset,line in lines if offset<=int(bci)]
            if not preceding:raise ValueError('actual invocation must have original debug line')
            result.append(dict(method=method,owner=owner,line=max(preceding)[1],bci=int(bci),member=chunk.splitlines()[0].strip()))
    return result


def join_calls(source,bytecode,line_hits):
    catches=spans(source);rows=[];used=set()
    for match in CALL.finditer(source):
        line=source.count('\n',0,match.start())+1
        suffix='/'+match[1]
        hits=[(i,c) for i,c in enumerate(bytecode) if c['line']==line and c['method']==match[2] and c['owner'].endswith(suffix)]
        identities={(c.get('physicalClass'),c['member'],c['bci']) for _,c in hits}
        if not hits or len(identities)!=len(hits) or any(i in used for i,_ in hits):
            raise ValueError('distinct original JVM paths for exactly one source site')
        used.update(i for i,_ in hits)
        owning=[r for r in catches if r['bodyStart']<=match.start() and r['body'] and match.start()<r['body'][-1][2]]
        # Outbox retainFailure is a private method, not a catch; do not invent a catch variable.
        scope=max(owning,key=lambda r:r['bodyStart']) if owning else None
        rows.append(dict(line=line,port=match[1]+'.'+match[2],jvmPaths=[c for _,c in hits],
                         catchVariable=scope['var'] if scope else None,
                         catchLine=scope['line'] if scope else None,
                         aggregateLineCounter=line_hits.get(line),
                         perTestCausalityProved=False,accepted=False))
    if len(used)!=len(bytecode):raise ValueError('no unmatched original target JVM invocations')
    return rows


def main():
    qp=BASE/'PG6584-api-jdbc-domain-qualification-v1/manifest.json';q=json.loads(qp.read_bytes())
    private=W/'pg6584-api-jdbc-domain-qualification-v1/manifest.safe.json'
    if sha(private)!=q['privateManifestSha256'] or q['actualExit']!=0:raise ValueError('original256 qualification first')
    proof=json.loads(private.read_bytes());run=W/'pg6582-api-jdbc-domain-green-v1';snapshot=run/'source'
    if sha(run/'manifest.safe.json')!=q['originalManifestSha256']:raise ValueError('genuine original run')
    plan=json.loads((BASE/'PG6580-api-mapper-plan-v1/correction-v2.json').read_bytes());rows=[]
    jar=snapshot/'src/schubert-nk-api/target/schubert-nk-api-0.1.0-SNAPSHOT.jar'
    coverage=ET.parse(snapshot/'src/schubert-nk-api/target/site/jacoco/jacoco.xml').getroot()
    for file in plan['files']:
        path=file['path'];actual=(snapshot/path).read_text()
        if sha(snapshot/path)!=file['actualSha256'] or sha(ROOT/path)!=proof['allSourceHashes'][path]:raise ValueError('exact Main bytes')
        owner='api:'+path.split('/src/main/java/')[1][:-5]
        family=[p for p in proof['allPhysicalMainSha256'] if p==owner+'.class' or p.startswith(owner+'$')]
        bytecode=[]
        for physical in sorted(family):
            name=physical.split(':',1)[1][:-6].replace('/','.')
            command=[str(TC/'jdk-25.0.4/bin/javap'),'-classpath',str(jar),'-p','-c','-l',name]
            text=subprocess.check_output(command,text=True)
            bytecode.extend(dict(physicalClass=physical,**c) for c in jvm_calls(text))
        package,name=path.split('/src/main/java/')[1].rsplit('/',1)
        sourcefile=coverage.find("package[@name='"+package+"']/sourcefile[@name='"+name+"']")
        if sourcefile is None:raise ValueError('actual original source coverage present')
        hits={int(line.get('nr')):{k:int(line.get(k)) for k in ('ci','mi','cb','mb')} for line in sourcefile.findall('line')}
        rows.extend(dict(sourcePath=path,sourceSha256=sha(snapshot/path),**r) for r in join_calls(actual,bytecode,hits))
    if len(rows)!=84:raise ValueError('explicit72 mapper +12 secondary calls')
    value=dict(source=q['source'],qualificationSha256=sha(qp),actualExit=0,sites=84,rows=rows,
               hitSites=sum(bool(r['aggregateLineCounter'] and r['aggregateLineCounter']['ci']) for r in rows),
               perTestCausalityProved=False,acceptedSites=0,ptPassAdded=0,formalChanged=False,
               inputsUnchanged=True,toolsSourceSha256=sha(ROOT/'tools/quality/pg6586_api_mapper_jvm_join.py'))
    out=BASE/'PG6586-api-mapper-jvm-join-v1';out.mkdir()
    target=out/'manifest.json'
    with target.open('x') as stream:stream.write(json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
    print(json.dumps(dict(actualExit=0,source=q['source'],sites=84,hitSites=value['hitSites'],sha256=sha(target))))


if __name__=='__main__':main()

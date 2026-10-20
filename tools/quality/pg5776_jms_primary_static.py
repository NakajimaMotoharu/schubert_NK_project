"""Exact three same-identity guards; independently check all class bytes/ABI and static inputs."""
import json
import os
import subprocess
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from pg5540_snapshot_scratch_selected import ROOT,TC,sha
from pg5584_field_accessor_inspection import compile_only_artifacts
from pmd_diagnostic_identity import diagnostic_row

W=ROOT.parent/'pgpt-runs/PG379';SLOT='pg5776-jms-primary-static-v1'
PATHS={
 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/inbound/InboundTransactions.java':(('isolationFailure','protocolFailure'),('failure','rollbackFailure')),
 'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/messaging/ArtemisReplyConsumer.java':(('isolationFailure','protocolFailure'),)}
MODULES=('protocol','storage','bootstrap','api','web','batch')


def expected_source(path,before):
    for left,right in PATHS[path]:
        phrase=f'      {left}.addSuppressed({right});'
        if before.count(phrase)!=1:raise ValueError('one exact unguarded diagnostic append before change')
        before=before.replace(phrase,f'      if ({left} != {right}) {{\n        {left}.addSuppressed({right});\n      }}',1)
    return before


def guard_coverage(snapshot):
    values=[]
    for path,pairs in PATHS.items():
        module=path.split('/')[1];root=ET.parse(snapshot/('src/'+module+'/target/site/jacoco/jacoco.xml')).getroot();package,filename=path.split('/src/main/java/')[1].rsplit('/',1)
        sources=[s for p in root.findall('package')if p.get('name')==package for s in p.findall('sourcefile')if s.get('name')==filename]
        if len(sources)!=1:raise ValueError('exact actual sourcefile coverage')
        lines=(snapshot/path).read_text().splitlines()
        for left,right in pairs:
            match=[i+1 for i,s in enumerate(lines)if s.strip()==f'if ({left} != {right}) {{']
            if len(match)!=1:raise ValueError('exact new guard source line')
            counters=[s for s in sources[0].findall('line')if int(s.get('nr'))==match[0]]
            if len(counters)!=1 or counters[0].get('mb')!='0'or counters[0].get('cb')!='2':raise ValueError('actual both new identity branches must execute')
            values.append({'sourcePath':path,'line':match[0],'missedBranches':0,'coveredBranches':2,'guard':f'{left} != {right}'})
    return values


def main():
    path=W/'pg5774-jms-primary-green-v1/manifest.safe.json';v=json.loads(path.read_bytes());snapshot=path.parent/'source'
    if not(v['actualExit']==0 and v['selectedQualified']and(v['tests'],v['suites'])==(14,7)and not v['failedOrSkipped']):raise ValueError('actual normal finite14 green first')
    oldp=W/'pg5750-exception-static-v1/manifest.safe.json';old=json.loads(oldp.read_bytes());public=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5750-exception-static-v1/manifest.json'
    if sha(public)!='70e765032b899a377bd1067846d158496373aec901de559dc0baeaac2121d5d9'or sha(oldp)!=json.loads(public.read_bytes())['privateManifestSha256']:raise ValueError('original9463 static proof')
    sources={p.relative_to(snapshot).as_posix():sha(p)for p in snapshot.glob('src/*/src/main/java/**/*.java')}
    if len(sources)!=849 or set(sources)!=set(old['allSourceHashes'])or {p for p in sources if sources[p]!=old['allSourceHashes'][p]}!=set(PATHS):raise ValueError('exact two Main source changes')
    for name in PATHS:
        before=subprocess.check_output(['git','show',old['source']+':'+name],cwd=ROOT,text=True)
        if expected_source(name,before)!=(snapshot/name).read_text():raise ValueError('only three identity guards, no business/retry/oracle change')
    current=v['allPhysicalMainSha256'];classes={p.split('/')[1].removeprefix('schubert-nk-')+':'+p.split('/src/main/java/')[1][:-5]+'.class'for p in PATHS}
    if len(current)!=1664 or set(current)!=set(old['auxClassHashes'])or {k for k in current if current[k]!=old['auxClassHashes'][k]}!=classes:raise ValueError('exact two actual classes changed,1662 unchanged')
    jdk=TC/'jdk-25.0.4/bin';before_snapshot=W/'pg5748-exception-green-v1/source'
    for name in PATHS:
        module=name.split('/')[1];member=name.split('/src/main/java/')[1][:-5].replace('/','.')
        def signature(root):return subprocess.check_output([str(jdk/'javap'),'-p','-s','-classpath',str(root/('src/'+module+'/target/classes')),member],text=True)
        if signature(before_snapshot)!=signature(snapshot):raise ValueError('all fields/public/private descriptors preserved')
    for name in('pmd.xml','checkstyle.xml'):
        if sha(snapshot/'tools/quality/static'/name)!=sha(before_snapshot/'tools/quality/static'/name):raise ValueError('same rules, no exclusions')
    guards=guard_coverage(snapshot)
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);filelist=out/'all-main.txt';filelist.write_text(''.join(str(snapshot/p)+'\n'for p in sorted(sources)))
    tail=(W/'pg5750-exception-static-v1/aux-classpath.txt').read_text().splitlines()[6:]
    release=W/'pg5430-release-v1';bom=release/'RELEASE-MANIFEST.json'
    if sha(bom)!='85fbce34711ac798d1e71a3e3a8a7a54cc070e074ec1255047c4ac75ef18fbd6':raise ValueError('fixed third-party BOM')
    approved={str(release/r['path']):r['sha256']for r in json.loads(bom.read_bytes())['artifacts']if '/lib/'in r['path']and r['path'].endswith('.jar')and not os.path.basename(r['path']).startswith('schubert-nk-')};unique={}
    for name,digest in approved.items():unique.setdefault(digest,name)
    provided,_=compile_only_artifacts();approved.update({str(p):sha(p)for p in provided})
    if tail!=[*unique.values(),*map(str,provided)]or any(sha(Path(p))!=approved[p]for p in tail):raise ValueError('all actual immutable third-party/provided dependencies')
    tools=TC/'static-gates-20261015'
    if sha(tools/'record-fix-v1/pmd-record-1298.jar')!='4859fb956de018a843abe55ddb92b0a98921878b80525aaa2a77c5b5d8c2820c'or sha(tools/'checkstyle-14.3.0-all.jar')!='754e218ab1fcabb1e1c5f8530e9d3aa37636806c22987bb279dd907a6ee749b2':raise ValueError('pinned analyzers')
    aux=out/'aux-classpath.txt';aux.write_text('\n'.join([*(str(snapshot/('src/schubert-nk-'+m+'/target/classes'))for m in MODULES),*tail])+'\n')
    pmd=old['commands'][0].copy();cs=old['commands'][1].copy()
    for flag,val in [('--file-list',str(filelist)),('--aux-classpath','file:'+str(aux)),('--report-file',str(out/'pmd.xml')),('--rulesets',str(snapshot/'tools/quality/static/pmd.xml'))]:pmd[pmd.index(flag)+1]=val
    cs[cs.index('-c')+1]=str(snapshot/'tools/quality/static/checkstyle.xml');cs[cs.index('-o')+1]=str(out/'checkstyle.xml');cs[-1]='@'+str(filelist);exits=[]
    for name,command in(('pmd',pmd),('checkstyle',cs)):
        with(out/(name+'.private.log')).open('xb')as f:exits.append(subprocess.run(command,stdout=f,stderr=subprocess.STDOUT,timeout=180).returncode)
    tree=ET.parse(out/'pmd.xml').getroot();rows=[]
    for file in tree.findall('{*}file'):
        name=os.path.relpath(file.get('name'),snapshot)
        if name not in sources:raise ValueError('current source diagnostics only')
        for warning in file.findall('{*}violation'):rows.append(diagnostic_row(name,sources[name],warning,len(rows)+1))
    errors=len(tree.findall('.//{*}error'));cs_count=len(ET.parse(out/'checkstyle.xml').getroot().findall('.//error'));expected_counts=Counter(old['ruleCounts']);expected_counts['CompareObjectsWithEquals']+=3
    done=exits[0]in(0,4)and exits[1]==0 and errors==cs_count==0 and Counter(r['rule']for r in rows)==expected_counts and len({r['findingId']for r in rows})==len(rows)and all(sha(snapshot/p)==h for p,h in sources.items())
    value={'actualExit':0 if done else 1,'source':v['source'],'previousMainSource':old['source'],'changedSourcePaths':sorted(PATHS),'physicalMain':1664,'changedPhysicalClasses':sorted(classes),'unchangedPhysicalClasses':1662,'allFieldAndMethodDescriptorsUnchanged':True,'inputSourceFiles':849,'actualAuxClasses':1664,'pmdExit':exits[0],'pmdRawFindings':len(rows),'ruleCounts':dict(Counter(r['rule']for r in rows)),'pmdProcessingErrors':errors,'checkstyleExit':exits[1],'checkstyleFindings':cs_count,'newGuardsActualCoverage':guards,'selectedManifestSha256':sha(path),'pmdXmlSha256':sha(out/'pmd.xml'),'checkstyleXmlSha256':sha(out/'checkstyle.xml'),'commands':[pmd,cs],'allSourceHashes':sources,'auxClassHashes':current,'formalAccepted':False,'F03Accepted':False,'fullCoverageClaimed':False,'ptAlternativeCompleted':0,'vmActions':0}
    with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    projected={k:val for k,val in value.items()if k not in('commands','allSourceHashes','auxClassHashes')};projected['privateManifestSha256']=sha(out/'manifest.safe.json');target=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5776-jms-primary-static-v1';target.mkdir()
    for name,data in(('manifest.json',projected),('findings.json',rows)):
        with(target/name).open('x')as f:json.dump(data,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({k:projected[k]for k in('actualExit','source','changedPhysicalClasses','unchangedPhysicalClasses','pmdRawFindings','pmdProcessingErrors','checkstyleFindings','newGuardsActualCoverage','F03Accepted')}))
    return 0 if done else 1


if __name__=='__main__':raise SystemExit(main())

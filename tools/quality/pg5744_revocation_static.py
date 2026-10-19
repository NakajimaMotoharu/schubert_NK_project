"""Exact single-class PG delta, current six-module static analysis and actual codec coverage."""
import json
import os
import subprocess
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from pg5540_snapshot_scratch_selected import ROOT,TC,sha
from pg5742_revocation_selected import SLOT as SELECTED
from pg5584_field_accessor_inspection import compile_only_artifacts
from pmd_diagnostic_identity import diagnostic_row

SLOT='pg5744-revocation-static-v1'
MODULES=('protocol','storage','bootstrap','api','web','batch')
REL='src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/revocation/RevocationPayloadCodec.java'
MEMBER='dev/codex/schubert/nk/web/revocation/RevocationPayloadCodec'


def main():
    w=ROOT.parent/'pgpt-runs/PG379';path=w/SELECTED/'manifest.safe.json';v=json.loads(path.read_bytes());snapshot=path.parent/'source'
    if not(v['actualExit']==0 and v['selectedQualified']and(v['tests'],v['suites'])==(15,7)):raise ValueError('actual15 selected PT first')
    p=w/'pg5734-enum48-static-v1/manifest.safe.json';old=json.loads(p.read_bytes())
    public=ROOT/'evidence/01_PT/001_NK-PRO-001/evidence/provisional/PG5734-enum48-static-v1/manifest.json'
    if sha(public)!='81aa7ea5f48a0c93762d629f43bbdeeb8672a2379a69e175641499b680838e3a'or sha(p)!=json.loads(public.read_bytes())['privateManifestSha256']:raise ValueError('fixed original static proof')
    sources={p.relative_to(snapshot).as_posix():sha(p)for p in snapshot.glob('src/*/src/main/java/**/*.java')}
    if len(sources)!=849 or set(sources)!=set(old['allSourceHashes'])or [k for k in sources if sources[k]!=old['allSourceHashes'][k]]!=[REL]:raise ValueError('exact one changed Main source')
    before=subprocess.check_output(['git','show',old['source']+':'+REL],cwd=ROOT,text=True)
    phrase='previousVersion != null && version.equals(previousVersion)'
    if before.count(phrase)!=1 or before.replace(phrase,'version.equals(previousVersion)')!=(snapshot/REL).read_text():raise ValueError('only equivalent nullable String guard removed')
    current=v['allPhysicalMainSha256'];prior=old['auxClassHashes'];expected_class='web:'+MEMBER+'.class'
    if len(current)!=1664 or set(current)!=set(prior)or [k for k in current if current[k]!=prior[k]]!=[expected_class]:raise ValueError('exact one actual class delta,1663 unchanged')
    jdk=TC/'jdk-25.0.4/bin';cpold=w/'pg5732-enum48-selected-v2/source/src/schubert-nk-web/target/classes';cpnew=snapshot/'src/schubert-nk-web/target/classes'
    def signature(cp):return subprocess.check_output([str(jdk/'javap'),'-p','-s','-classpath',str(cp),MEMBER.replace('/','.')],text=True)
    if signature(cpold)!=signature(cpnew):raise ValueError('all fields and public/private method descriptors unchanged')
    for name in('pmd.xml','checkstyle.xml'):
        if sha(snapshot/'tools/quality/static'/name)!=sha(w/'pg5732-enum48-selected-v2/source/tools/quality/static'/name):raise ValueError('rules unchanged,no exclusions')
    coverage=snapshot/'src/schubert-nk-web/target/site/jacoco/jacoco.xml'
    classes=[c for c in ET.parse(coverage).getroot().findall('package/class')if c.get('name')==MEMBER]
    if len(classes)!=1:raise ValueError('exact target class coverage')
    counters={c.get('type'):{'covered':int(c.get('covered')),'missed':int(c.get('missed'))}for c in classes[0].findall('counter')}
    if not all(counters[k]['missed']==0 and counters[k]['covered']>0 for k in('LINE','METHOD','CLASS','BRANCH')):raise ValueError('target four real counters100')
    os.umask(0o077);out=w/SLOT;out.mkdir(mode=0o700);filelist=out/'all-main.txt';filelist.write_text(''.join(str(snapshot/p)+'\n'for p in sorted(sources)))
    oldcp=w/'pg5734-enum48-static-v1/aux-classpath.txt';tail=oldcp.read_text().splitlines()[6:]
    release=w/'pg5430-release-v1';bom=release/'RELEASE-MANIFEST.json'
    if sha(bom)!='85fbce34711ac798d1e71a3e3a8a7a54cc070e074ec1255047c4ac75ef18fbd6':raise ValueError('pinned third-party BOM')
    approved={str(release/r['path']):r['sha256']for r in json.loads(bom.read_bytes())['artifacts']if '/lib/'in r['path']and r['path'].endswith('.jar')and not os.path.basename(r['path']).startswith('schubert-nk-')}
    unique={}
    for name,digest in approved.items():unique.setdefault(digest,name)
    provided,_=compile_only_artifacts();approved.update({str(p):sha(p)for p in provided})
    if tail!=[*unique.values(),*map(str,provided)]or any(sha(Path(p))!=approved[p]for p in tail):raise ValueError('every actual unchanged third-party/provided artifact, no omissions')
    tools=TC/'static-gates-20261015'
    if sha(tools/'record-fix-v1/pmd-record-1298.jar')!='4859fb956de018a843abe55ddb92b0a98921878b80525aaa2a77c5b5d8c2820c'or sha(tools/'checkstyle-14.3.0-all.jar')!='754e218ab1fcabb1e1c5f8530e9d3aa37636806c22987bb279dd907a6ee749b2':raise ValueError('pinned analyzers and approved record patch')
    aux=out/'aux-classpath.txt';aux.write_text('\n'.join([*(str(snapshot/('src/schubert-nk-'+m+'/target/classes'))for m in MODULES),*tail])+'\n')
    pmd=old['commands'][0].copy();cs=old['commands'][1].copy()
    for flag,value in [('--file-list',str(filelist)),('--aux-classpath','file:'+str(aux)),('--report-file',str(out/'pmd.xml')),('--rulesets',str(snapshot/'tools/quality/static/pmd.xml'))]:pmd[pmd.index(flag)+1]=value
    cs[cs.index('-c')+1]=str(snapshot/'tools/quality/static/checkstyle.xml');cs[cs.index('-o')+1]=str(out/'checkstyle.xml');cs[-1]='@'+str(filelist)
    exits=[]
    for name,command in [('pmd',pmd),('checkstyle',cs)]:
        with(out/(name+'.private.log')).open('xb')as f:exits.append(subprocess.run(command,stdout=f,stderr=subprocess.STDOUT,timeout=180).returncode)
    tree=ET.parse(out/'pmd.xml').getroot();rows=[]
    for f in tree.findall('{*}file'):
        relative=os.path.relpath(f.get('name'),snapshot)
        if relative not in sources:raise ValueError('only current source diagnostics')
        for warning in f.findall('{*}violation'):rows.append(diagnostic_row(relative,sources[relative],warning,len(rows)+1))
    errors=len(tree.findall('.//{*}error'));cs_count=len(ET.parse(out/'checkstyle.xml').getroot().findall('.//error'))
    remaining=[r for r in rows if r['sourcePath']==REL and r['rule']=='UnusedNullCheckInEquals']
    done=exits[0]in(0,4)and exits[1]==0 and not errors and not cs_count and not remaining and len({r['findingId']for r in rows})==len(rows)and all(sha(snapshot/p)==h for p,h in sources.items())
    value={'actualExit':0 if done else 1,'source':v['source'],'previousMainSource':old['source'],'changedSourcePaths':[REL],'physicalMain':1664,'changedPhysicalClasses':[expected_class],'unchangedPhysicalClasses':1663,'allFieldAndMethodDescriptorsUnchanged':True,'inputSourceFiles':849,'actualAuxClasses':1664,'pmdExit':exits[0],'pmdRawFindings':len(rows),'ruleCounts':dict(Counter(r['rule']for r in rows)),'pmdProcessingErrors':errors,'checkstyleExit':exits[1],'checkstyleFindings':cs_count,'remainingTargetFindings':len(remaining),'targetCounters':counters,'targetFour100':True,'coverageXmlSha256':sha(coverage),'selectedManifestSha256':sha(path),'pmdXmlSha256':sha(out/'pmd.xml'),'checkstyleXmlSha256':sha(out/'checkstyle.xml'),'commands':[pmd,cs],'allSourceHashes':sources,'auxClassHashes':current,'formalAccepted':False,'F03Accepted':False,'fullCoverageClaimed':False,'ptAlternativeCompleted':0,'vmActions':0}
    with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    projected={k:val for k,val in value.items()if k not in('commands','allSourceHashes','auxClassHashes')};projected['privateManifestSha256']=sha(out/'manifest.safe.json')
    target=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5744-revocation-static-v1';target.mkdir(parents=True)
    for name,data in [('manifest.json',projected),('findings.json',rows)]:
        with(target/name).open('x')as f:json.dump(data,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({k:projected[k]for k in('actualExit','source','pmdRawFindings','pmdProcessingErrors','checkstyleFindings','remainingTargetFindings','targetCounters','F03Accepted')}))
    return 0 if done else 1


if __name__=='__main__':raise SystemExit(main())

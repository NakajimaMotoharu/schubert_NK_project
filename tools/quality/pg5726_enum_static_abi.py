"""PG static/ABI analysis only; PT count/coverage come from the separate completed protocol run."""
from collections import Counter
import hashlib
import json
import os
import re
import subprocess
import xml.etree.ElementTree as ET
from pg5724_semantic_enum_protocol import ROOT,TC,SLOT as PROTOCOL,BASE
from pg5584_field_accessor_inspection import compile_only_artifacts
from pmd_diagnostic_identity import diagnostic_row

W=ROOT.parent/'pgpt-runs/PG379'
SLOT='pg5726-semantic-enum-static-v1'
MODULES=('protocol','storage','bootstrap','api','web','batch')


def main():
    proof_path=W/PROTOCOL/'manifest.safe.json';proof=json.loads(proof_path.read_bytes())
    if not(proof['actualExit']==0 and proof['protocolFour100Qualified']and(proof['tests'],proof['suites'])==(88,18)):raise ValueError('actual separate protocol PT first')
    snapshot=proof_path.parent/'source';head=proof['source']
    if subprocess.check_output(['git','diff',head,'--','src','pom.xml','.mvn','mvnw','tools/quality/static'],cwd=ROOT):raise ValueError('same source before static analysis')
    before_path=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5716-current3908-cases/qualification.json';before=json.loads(before_path.read_bytes())
    if not(before['productionSource']==BASE and before['tests']==3908 and before['mainClasses']==1664):raise ValueError('old own-source class input only, not old success credit')
    old_snapshot=W/'pg5708-exec-generation-green-v1/source'
    roots={m:(snapshot if m=='protocol'else old_snapshot)/('src/schubert-nk-'+m+'/target/classes')for m in MODULES}
    aux={m+':'+p.relative_to(roots[m]).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for m in MODULES for p in roots[m].rglob('*.class')}
    expected={k:v for k,v in before['allPhysicalMainSha256'].items()if not k.startswith('protocol:')}
    expected.update({'protocol:'+k:v for k,v in proof['allPhysicalProtocolMainSha256'].items()})
    if aux!=expected or len(aux)!=1664:raise ValueError('all actual static auxiliary classes; no missing/foreign byte')
    changes=[p for p in subprocess.check_output(['git','diff','--name-only',BASE,head,'--','src'],cwd=ROOT,text=True).splitlines()if '/src/main/java/'in p]
    if len(changes)!=18 or any(not p.startswith('src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/semantic/')for p in changes):raise ValueError('only eighteen declared enum sources changed')
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);abi=[];jdk=TC/'jdk-25.0.4/bin'
    def command(argv,name):
        with(out/name).open('xb')as f:r=subprocess.run(argv,stdout=f,stderr=subprocess.STDOUT,timeout=180)
        return r.returncode
    for path in sorted(changes):
        old=subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT,text=True);new=(snapshot/path).read_text()
        required=old.replace('private final String wireValue;','private final String encodedValue;').replace('this.wireValue = wireValue;','this.encodedValue = wireValue;').replace('return wireValue;','return encodedValue;')
        if old.count('private final String wireValue;')!=1 or new!=required:raise ValueError('three private-only tokens, no method/literal/constant/ordering change')
        cls=path.split('/src/main/java/',1)[1][:-5].replace('/','.')
        left=subprocess.check_output([str(jdk/'javap'),'-p','-c','-classpath',str(old_snapshot/'src/schubert-nk-protocol/target/classes'),cls],text=True)
        right=subprocess.check_output([str(jdk/'javap'),'-p','-c','-classpath',str(roots['protocol']),cls],text=True)
        normalize=lambda text:re.sub(r'#\d+','<cp>',text.replace('encodedValue','wireValue'))
        if normalize(left)!=normalize(right):raise ValueError('all disassembled code and ABI equal after only private-field/constant-pool-reference normalization')
        abi.append({'class':cls,'sourcePath':path,'sourceSha256':hashlib.sha256(new.encode()).hexdigest(),'privateTokenEdits':3,'publicAndOpcodeContractUnchanged':True})
    release=W/'pg5430-release-v1';bom=(release/'RELEASE-MANIFEST.json').read_bytes()
    if hashlib.sha256(bom).hexdigest()!='85fbce34711ac798d1e71a3e3a8a7a54cc070e074ec1255047c4ac75ef18fbd6':raise ValueError('fixed third-party BOM')
    libraries={}
    for row in json.loads(bom)['artifacts']:
        if '/lib/'in row['path']and row['path'].endswith('.jar')and not os.path.basename(row['path']).startswith('schubert-nk-'):
            path=release/row['path']
            if hashlib.sha256(path.read_bytes()).hexdigest()!=row['sha256']:raise ValueError('actual fixed third-party bytes')
            libraries.setdefault(row['sha256'],path)
    provided,_=compile_only_artifacts();toolchain=ROOT.parent/'toolchain/static-gates-20261015'
    overlay=toolchain/'record-fix-v1/pmd-record-1298.jar';checkstyle=toolchain/'checkstyle-14.3.0-all.jar'
    if hashlib.sha256(overlay.read_bytes()).hexdigest()!='4859fb956de018a843abe55ddb92b0a98921878b80525aaa2a77c5b5d8c2820c'or hashlib.sha256(checkstyle.read_bytes()).hexdigest()!='754e218ab1fcabb1e1c5f8530e9d3aa37636806c22987bb279dd907a6ee749b2':raise ValueError('existing pinned analyzer/fix, no new suppression')
    files=sorted(snapshot.glob('src/*/src/main/java/**/*.java'))
    if len(files)!=849:raise ValueError('complete production input, no exclusions')
    sources={p.relative_to(snapshot).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in files}
    filelist=out/'all-main.txt';filelist.write_text(''.join(str(p)+'\n'for p in files))
    classpath=out/'aux-classpath.txt';classpath.write_text('\n'.join(map(str,[*roots.values(),*libraries.values(),*provided]))+'\n')
    pmdcp=os.pathsep.join(map(str,[overlay,*sorted((toolchain/'pmd-bin-7.28.0/lib').glob('*.jar'))]))
    pmd=[str(jdk/'java'),'-cp',pmdcp,'net.sourceforge.pmd.cli.PmdCli','check','--file-list',str(filelist),'--rulesets',str(snapshot/'tools/quality/static/pmd.xml'),'--use-version','java-25','--minimum-priority','5','--aux-classpath','file:'+str(classpath),'--no-cache','--format','xml','--report-file',str(out/'pmd.xml')]
    cs=[str(jdk/'java'),'-jar',str(checkstyle),'-c',str(snapshot/'tools/quality/static/checkstyle.xml'),'-f','xml','-o',str(out/'checkstyle.xml'),'@'+str(filelist)]
    pmd_exit=command(pmd,'pmd.private.log');cs_exit=command(cs,'checkstyle.private.log')
    tree=ET.parse(out/'pmd.xml').getroot();rows=[]
    for file in tree.findall('{*}file'):
        path=os.path.relpath(file.get('name'),snapshot)
        if path not in sources:raise ValueError('every finding belongs to this exact source')
        for warning in file.findall('{*}violation'):
            rows.append(diagnostic_row(path,sources[path],warning,len(rows)+1))
    errors=len(tree.findall('.//{*}error'));cs_count=len(ET.parse(out/'checkstyle.xml').getroot().findall('.//error'))
    remaining=[r for r in rows if r['rule']=='AvoidFieldNameMatchingMethodName'and r['sourcePath']in changes]
    done=pmd_exit in(0,4)and cs_exit==0 and errors==cs_count==0 and not remaining and all(hashlib.sha256((snapshot/p).read_bytes()).hexdigest()==h for p,h in sources.items())
    value={'actualExit':0 if done else 1,'source':head,'inputSourceFiles':849,'actualAuxClasses':1664,'auxFromCurrentProtocolAndUnchangedOtherModules':True,'freshWholeCompileClaimed':False,'protocolPtManifestSha256':hashlib.sha256(proof_path.read_bytes()).hexdigest(),'abi':abi,'pmdExit':pmd_exit,'pmdRawFindings':len(rows),'pmdProcessingErrors':errors,'ruleCounts':dict(Counter(r['rule']for r in rows)),'checkstyleExit':cs_exit,'checkstyleFindings':cs_count,'remainingTargetFindings':len(remaining),'target18StaticAndAbiQualified':done,'pmdXmlSha256':hashlib.sha256((out/'pmd.xml').read_bytes()).hexdigest(),'checkstyleXmlSha256':hashlib.sha256((out/'checkstyle.xml').read_bytes()).hexdigest(),'commands':[pmd,cs],'allSourceHashes':sources,'auxClassHashes':aux,'formalAccepted':False,'F03Accepted':False,'wholeCoverageAccepted':False,'executedPtAdded':0,'ptAlternativeCompleted':0,'vmActions':0}
    with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    public=ROOT/'evidence/01_PT/001_NK-PRO-001/evidence/provisional/PG5726-enum-static-v1';public.mkdir(parents=True)
    projected={k:v for k,v in value.items()if k not in('commands','allSourceHashes','auxClassHashes')}
    projected['privateManifestSha256']=hashlib.sha256((out/'manifest.safe.json').read_bytes()).hexdigest()
    for name,data in(('manifest.json',projected),('findings.json',rows)):
        with(public/name).open('x')as f:json.dump(data,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({k:projected[k]for k in('actualExit','source','inputSourceFiles','actualAuxClasses','pmdExit','pmdRawFindings','pmdProcessingErrors','checkstyleFindings','remainingTargetFindings','target18StaticAndAbiQualified','F03Accepted')}))
    return 0 if done else 1


if __name__=='__main__':raise SystemExit(main())

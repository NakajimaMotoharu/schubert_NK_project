"""Index every immutable PMD finding and original vendor rule; no exclusion or SAST rerun."""
import hashlib
import inspect
import json
import os
from pathlib import Path
import shlex
import subprocess
from lan_server import copy,run
from git_source_contract import last_main_source

ROOT=Path(__file__).resolve().parents[2]
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
BASE='/home/mini/schubert-nk-pgpt'


def require(value,reason):
    if not value:raise ValueError(reason)


def server(data):
    from collections import Counter
    import datetime
    import hashlib
    import io
    import json
    import os
    from pathlib import Path
    import xml.etree.ElementTree as E
    import zipfile

    os.umask(0o077);b=Path('/home/mini/schubert-nk-pgpt');out=b/'runs/PG3704-pmd-inventory-v1';out.mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    recovered=b/'runs/PG3700-static-source-recovery-v1/manifest.safe.json';require(sha(recovered)==data['recoveredManifestSha256'],'actual source recovery authority')
    v=json.loads(recovered.read_bytes());require(v['actualExit']==0 and v['all849ByteJoinVerified']and v['productionCandidateSource']==data['source'],'exact current static source')
    root=b/'runs/PG3692-hygiene-candidate-v1/candidate';report=b/'runs/PG3696-hygiene-pmd-v1/pmd.xml';require(sha(report)==v['pmd']['reportSha256'],'immutable actual2217 original report')
    require({str(p.relative_to(root)):sha(p)for p in root.glob('src/*/src/main/java/**/*.java')}==v['all849SourceSha256'],'all current849 input bytes')
    xml=E.parse(report).getroot();require(not xml.findall('.//{*}error'),'processing errors not findings')
    findings=[]
    for file in xml.findall('{*}file'):
        path=Path(file.get('name'));require(path.is_relative_to(root),'all finding coordinates stay in actual candidate source');relative=str(path.relative_to(root));require(relative in v['all849SourceSha256'],'source trace known')
        for node in file.findall('{*}violation'):
            attrs=dict(node.attrib);rule=attrs.pop('rule');row={'id':'PMD-'+str(len(findings)+1).zfill(4),'path':relative,'sourceSha256':v['all849SourceSha256'][relative],'rule':rule,'coordinates':attrs,'disposition':'UNCLASSIFIED','applicable':None,'reason':None,'testOrDesignEvidence':[]};findings.append(row)
    require(len(findings)==2217 and dict(Counter(x['rule']for x in findings))==v['pmd']['ruleCounts'],'all exact original findings/rule counts')
    distribution=b/'runs/PG3382-static-gate-v1/pmd-dist-7.28.0-bin.zip';require(sha(distribution)=='f974ba571f7bc01c73fffe11bade25fbc1f438698f9e9c00e416e8d65e9fbac2','exact original vendor distribution')
    with zipfile.ZipFile(distribution)as z:
        members=[n for n in z.namelist()if n.endswith('/pmd-java-7.28.0.jar')];require(len(members)==1,'single original Java rule library');library=z.read(members[0])
    rules={};wanted={x['rule']for x in findings}
    with zipfile.ZipFile(io.BytesIO(library))as z:
        for name in z.namelist():
            if not(name.startswith('category/java/')and name.endswith('.xml')):continue
            raw=z.read(name);catalog=E.fromstring(raw)
            for rule in catalog.findall('{*}rule'):
                key=rule.get('name')
                if key not in wanted:continue
                require(key not in rules,'unique actual original rule definition')
                description=rule.find('{*}description');properties=rule.find('{*}properties')
                rules[key]={'name':key,'resource':name,'resourceSha256':hashlib.sha256(raw).hexdigest(),'attributes':dict(rule.attrib),'description':''.join(description.itertext()).strip()if description is not None else'','priority':rule.findtext('{*}priority'),'propertiesXml':E.tostring(properties,encoding='unicode')if properties is not None else None}
    require(set(rules)==wanted,'every one of23 actual rule definitions present')
    (out/'findings.private.json').write_text(json.dumps(findings,sort_keys=True));(out/'vendor-rules.private.json').write_text(json.dumps(rules,sort_keys=True))
    result={'actualExit':0,'productionCandidateSource':data['source'],'operatorSource':data['head'],'rawFindings':2217,'rules':23,'processingErrors':0,'sourceFilesWithFindings':len({x['path']for x in findings}),'allFindingCoordinatesSourceBound':True,'dispositions':{'UNCLASSIFIED':2217},'applicableViolationCount':None,'suppressionAdded':False,'ruleChanges':False,'pmdReissued':False,'MainModified':False,'vmActions':0,'ruleCounts':v['pmd']['ruleCounts'],'findingsSha256':sha(out/'findings.private.json'),'vendorRulesSha256':sha(out/'vendor-rules.private.json'),'distributionSha256':sha(distribution),'javaRulesLibrarySha256':hashlib.sha256(library).hexdigest(),'formalAccepted':False,'F03Accepted':False,'recordedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    (out/'manifest.safe.json').write_text(json.dumps(result,sort_keys=True));result['serverManifestSha256']=sha(out/'manifest.safe.json');print(json.dumps(result))


def main():
    require(not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT),'clean current source before read-only inventory')
    recovered=json.loads((W/'pg3700-static-source-recovery-v1/manifest.safe.json').read_bytes());require(recovered['actualExit']==0,'actual full849 source recovered')
    source=last_main_source(ROOT);require(source==recovered['result']['productionCandidateSource'],'current Main still exactly diagnostic source')
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();data={'source':source,'head':head,'recoveredManifestSha256':recovered['result']['serverManifestSha256']}
    os.umask(0o077);out=W/'pg3704-pmd-applicability-inventory-v1';out.mkdir();payload=inspect.getsource(require)+'\n'+inspect.getsource(server)+'\nINPUT='+repr(data)+'\nserver(INPUT)\n';script=out/'inventory.private.py';script.write_text(payload)
    rc,_=run('test ! -e '+BASE+'/runs/PG3704-pmd-inventory-v1 && mkdir -m700 '+BASE+'/transfer/PG3704-pmd-inventory-v1',timeout=30);require(rc==0,'new-only classification inventory')
    rc,_=copy(script,BASE+'/transfer/PG3704-pmd-inventory-v1/',timeout=60);require(rc==0,'fixed read-only rule inventory payload')
    rc,output=run('python3 -B '+shlex.quote(BASE+'/transfer/PG3704-pmd-inventory-v1/inventory.private.py'),timeout=60);(out/'observer.private.log').write_text(output)
    value={'actualExit':rc,'productionCandidateSource':source,'payloadSha256':hashlib.sha256(payload.encode()).hexdigest(),'formalAccepted':False}
    if rc==0:value['result']=json.loads(next(x for x in reversed(output.splitlines())if x.startswith('{')))
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return rc


if __name__=='__main__':raise SystemExit(main())

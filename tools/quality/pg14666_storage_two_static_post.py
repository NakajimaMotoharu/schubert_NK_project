"""Independent original XML reconstruction for two Storage sources, no analyzer or Product rerun."""
from collections import Counter
import copy
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OUT=data.BASE/'PG14666-storage-two-static-post-v1'
PIN='4fb789834a8906d782f42acda3d8dc8a41cf403be5bb9938dbdfeacc025100a2'
CURRENT=data.BASE/'PG14664-storage-two-qualified-main-static-v1'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg14664-storage-two-qualified-main-static-v1'

def main():
    invocation=capture(__file__);assert not OUT.exists()
    m=data.read_checked(CURRENT/'manifest.json',PIN)
    begin=data.read_checked(SLOT/'begin.safe.json',m['beginSha256'])
    normal=data.read_checked(data.BASE/'PG14216-typed-marker-guard-six-compile-v1/manifest.json','1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3')
    assert m['source']==begin['source']==normal['source']==SOURCE
    assert m['actualExit']==0 and m['analysisComplete'] and not m['processingErrors'] and m['qualityGateExit']==1
    assert m['analysisScope']==begin['analysisScope']=='QUALIFIED_STORAGE_TWO_MAIN_ONLY_NOT_GLOBAL'
    assert m['sourceCount']==m['mainSourceCount']==2 and m['testSourceCount']==0
    selected=begin['selectedJavaHashes']
    expected_sources={"src/schubert-nk-storage/src/main/java/dev/codex/schubert/nk/storage/ResourceScope.java":"639d3e7a51ad7d4fd2b45a9d5b8f7536ece257f08b0db9955249704009d00bbf","src/schubert-nk-storage/src/main/java/dev/codex/schubert/nk/storage/ServiceCredentialId.java":"1d6f6922f1ed8ecdd2df6a3eddb62f059952ac43eeaa34f6a0aaa6cb4a58f2a7"}
    assert selected==expected_sources
    old=data.read_checked(data.BASE/'PG14226-typed-marker-guard-three-main-static-v1/manifest.json','0ae9027c8f4819697a6d6926b5b6723dc611c525690d98b0dccfc63259a4c293')
    old_begin=data.read_checked(data.ROOT.parent/'pgpt-runs/PG379/pg14226-typed-marker-guard-three-main-static-v1/begin.safe.json',old['beginSha256'])
    assert all(begin[k]==old_begin[k] for k in ['toolAndRuleHashes','dependencyHashes','testClassFileHashes','mainClassHashes','auxiliaryClasspath'])
    assert m['analysisToolchainPreviouslyPinned'] is True and m['previousToolchainManifestSha256']=='0ae9027c8f4819697a6d6926b5b6723dc611c525690d98b0dccfc63259a4c293'
    snapshot=Path(begin['snapshot']);assert {Path(v['path']).parents[3] for v in normal['jars'].values()}=={snapshot}
    assert (SLOT/'source-list.txt').read_text().splitlines()==[str(snapshot/p) for p in sorted(selected)]
    assert all(data.sha((snapshot/p).read_bytes())==data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items())
    assert all(normal['begin']['inputHashes'][p]==h for p,h in selected.items())
    for p,h in {**begin['testClassFileHashes'],**begin['dependencyHashes'],**begin['toolAndRuleHashes']}.items():
        assert data.sha(Path(p).read_bytes())==h
    rows=[];seen={};counts={}
    for tool,tag in [('pmd','violation'),('checkstyle','error')]:
        raw=(CURRENT/(tool+'.xml')).read_bytes();assert data.sha(raw)==m['reports'][tool]['sha256']
        root=ET.fromstring(raw);seen[tool]=set()
        assert not [x for x in root if x.tag.rpartition('}')[2] in ['error','configerror']]
        for file in root:
            if file.tag.rpartition('}')[2]!='file':continue
            path=Path(file.get('name')).relative_to(snapshot).as_posix();assert path in selected
            seen[tool].add(path)
            for node in file:
                assert node.tag.rpartition('}')[2]==tag
                attrs=dict(node.attrib);rule=attrs.get('rule',attrs.get('source','UNKNOWN'))
                assert not (tool=='checkstyle' and rule in ['com.puppycrawl.tools.checkstyle.Checker','com.puppycrawl.tools.checkstyle.TreeWalker'])
                rows.append(dict(tool=tool,path=path,sourceSha256=selected[path],module=path.split('/')[1].removeprefix('schubert-nk-'),kind='main',attributes=attrs,rule=rule,message=' '.join(''.join(node.itertext()).split()) if tool=='pmd' else attrs.get('message','')))
        local=[r for r in rows if r['tool']==tool]
        counts[tool]=dict(total=len(local),byModule=dict(sorted(Counter(r['module'] for r in local).items())),byKind=dict(sorted(Counter(r['kind'] for r in local).items())),byRule=dict(sorted(Counter(r['rule'] for r in local).items())),byPath=dict(sorted(Counter(r['path'] for r in local).items())))
        assert counts[tool]==m['counts'][tool] and len(local)==m['reports'][tool]['findings']
        stage=m['stages'][tool];assert not stage['timedOut']
        for suffix,field in [('stdout','stdoutSha256'),('stderr','stderrSha256')]:
            assert data.sha((SLOT/(tool+'.'+suffix)).read_bytes())==stage[field]
    assert seen['checkstyle']==set(selected) and m['stages']['pmd']['actualExit']==4 and m['stages']['checkstyle']['actualExit']==0
    assert rows==data.read_checked(CURRENT/'findings.json',m['findingsSha256'])
    assert counts['pmd']['total']==18 and counts['pmd']['byRule']=={'AvoidCatchingGenericException':8,'AvoidInstanceofChecksInCatchClause':10} and counts['checkstyle']['total']==0
    assert m['productTestsExecuted']==0 and not list(snapshot.glob('src/*/target/surefire-reports/TEST-*.xml'))
    def contract(value):
        expected=dict(source=SOURCE,actualExit=0,analysisComplete=True,analysisScope='QUALIFIED_STORAGE_TWO_MAIN_ONLY_NOT_GLOBAL',sourceCount=2,mainSourceCount=2,testSourceCount=0,counts=counts,qualityGateExit=1,processingErrors=[],productTestsExecuted=0,targetAppInvoked=False,externalActions=0,newAccepted=0,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None)
        if any(json.dumps(value.get(k),sort_keys=True)!=json.dumps(v,sort_keys=True) for k,v in expected.items()):raise ValueError('exact scoped analysis values required')
    contract(m);labels=[]
    vectors=[('source',lambda v:v.update(source='0'*40)),('scope',lambda v:v.update(analysisScope='GLOBAL')),('bool-count',lambda v:v.update(sourceCount=True)),('count',lambda v:v.update(mainSourceCount=3)),('raw-erased',lambda v:v['counts']['pmd'].update(total=0)),('gate-inflated',lambda v:v.update(qualityGateExit=0)),('processing',lambda v:v.update(processingErrors=[{'unknown':True}])),('Product',lambda v:v.update(productTestsExecuted=26)),('formal',lambda v:v.update(whole451Accepted=True)),('effort',lambda v:v.update(effortPercent=50))]
    for label,change in vectors:
        wrong=copy.deepcopy(m);change(wrong)
        try:contract(wrong)
        except ValueError:labels.append(label)
        else:raise ValueError('false static summary accepted')
    assert len(labels)==10
    verify(m['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,analysisManifestSha256=PIN,analysisReexecuted=False,analysisScope='QUALIFIED_STORAGE_TWO_MAIN_ONLY_NOT_GLOBAL',sourceHashes=selected,counts=counts,processingErrors=0,qualityGateExit=1,rawWarningsRetained=18,actualApplicableViolations=None,unclassifiedRows=18,metadataNegativeVectors=len(labels),nonVacuousLabels=labels,toolchainAndRuntimeByteIdenticalToPrior=True,sourcePrograms=2,productTestsExecuted=0,coverage=None,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()

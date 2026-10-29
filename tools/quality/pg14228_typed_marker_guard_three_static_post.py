"""Independent original XML reconstruction for changed three Main, no analyzer or Product rerun."""
from collections import Counter
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OUT=data.BASE/'PG14228-typed-marker-guard-three-static-post-v1'
PIN='0ae9027c8f4819697a6d6926b5b6723dc611c525690d98b0dccfc63259a4c293'
CURRENT=data.BASE/'PG14226-typed-marker-guard-three-main-static-v1'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg14226-typed-marker-guard-three-main-static-v1'

def main():
    invocation=capture(__file__);assert not OUT.exists()
    m=data.read_checked(CURRENT/'manifest.json',PIN)
    begin=data.read_checked(SLOT/'begin.safe.json',m['beginSha256'])
    normal=data.read_checked(data.BASE/'PG14216-typed-marker-guard-six-compile-v1/manifest.json','1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3')
    proof=data.read_checked(data.BASE/'PG14218-typed-marker-guard-source-post-v1/manifest.json','ce3dbfd768a78ef45481db15ecf7c599b00bcb90a5b0b84eac568a54d1dc1909')
    assert m['source']==begin['source']==normal['source']==proof['source']==SOURCE
    assert m['actualExit']==0 and m['analysisComplete'] and not m['processingErrors'] and m['qualityGateExit']==1
    assert m['analysisScope']==begin['analysisScope']=='CHANGED_THREE_MAIN_ONLY_NOT_GLOBAL'
    assert m['sourceCount']==m['mainSourceCount']==3 and m['testSourceCount']==0
    selected=begin['selectedJavaHashes'];assert set(selected)==set(proof['changedInputPaths'])
    snapshot=Path(begin['snapshot'])
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
                rows.append(dict(tool=tool,path=path,sourceSha256=selected[path],module='api',kind='main',attributes=attrs,rule=rule,message=' '.join(''.join(node.itertext()).split()) if tool=='pmd' else attrs.get('message','')))
        local=[r for r in rows if r['tool']==tool]
        counts[tool]=dict(total=len(local),byModule=dict(sorted(Counter(r['module'] for r in local).items())),byKind=dict(sorted(Counter(r['kind'] for r in local).items())),byRule=dict(sorted(Counter(r['rule'] for r in local).items())),byPath=dict(sorted(Counter(r['path'] for r in local).items())))
        assert counts[tool]==m['counts'][tool] and len(local)==m['reports'][tool]['findings']
        stage=m['stages'][tool];assert not stage['timedOut']
        for suffix,field in [('stdout','stdoutSha256'),('stderr','stderrSha256')]:
            assert data.sha((SLOT/(tool+'.'+suffix)).read_bytes())==stage[field]
    assert seen['checkstyle']==set(selected) and m['stages']['pmd']['actualExit']==4 and m['stages']['checkstyle']['actualExit']==0
    assert rows==data.read_checked(CURRENT/'findings.json',m['findingsSha256'])
    assert counts['pmd']['total']==18 and counts['pmd']['byRule']=={'AvoidCatchingGenericException':18} and counts['checkstyle']['total']==0
    assert m['productTestsExecuted']==0 and not list(snapshot.glob('src/*/target/surefire-reports/TEST-*.xml'))
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,analysisManifestSha256=PIN,analysisReexecuted=False,analysisScope='CHANGED_THREE_MAIN_ONLY_NOT_GLOBAL',sourceHashes=selected,counts=counts,processingErrors=0,qualityGateExit=1,rawWarningsRetained=18,actualApplicableViolations=None,productTestsExecuted=0,coverage=None,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()

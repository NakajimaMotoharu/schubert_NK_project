"""Independent current1821 source XML reassembly, full input byte checks and non-PASS quality proof."""
from collections import Counter
import copy
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg9906_user_query_oracle_source_post import jar_classes
from pg9978_plain_core_quality_post import test_classes

OUT = data.BASE/'PG13254-current-all-java-static-post-v1'
CURRENT = data.BASE/'PG13253-current-all-java-static-v2'
SLOT = data.ROOT.parent/'pgpt-runs/PG379/pg13253-current-all-java-static-v2'

def strict(value,reference):
    assert json.dumps(value,sort_keys=True) == json.dumps(reference,sort_keys=True)

def main():
    invocation = capture(__file__);assert not OUT.exists()
    m = data.read_checked(CURRENT/'manifest.json','751a5f536623faed78362b14e69da89f5fbdba305acf2b8c1bbbf0811021dbdf')
    begin = data.read_checked(SLOT/'begin.safe.json',m['beginSha256'])
    n = data.read_checked(data.BASE/'PG13242-business-delivery-literal-v1/manifest.json','73d770b42807892d7b39bdc6d7da6d45e73857c152cb6aace83c0387e3239496')
    assert begin['source'] == m['source'] == n['source'] == 'db33c6a371d3dbc8e84f70462e0e56351bbb18b4'
    assert m['actualExit'] == 0 and m['analysisComplete'] and m['qualityGateExit'] == 1 and not m['processingErrors']
    snapshot = Path(begin['snapshot']);selected = {p:sha for p,sha in n['begin']['inputHashes'].items() if p.startswith('src/') and '/java/' in p and p.endswith('.java')}
    assert begin['selectedJavaHashes'] == selected and len(selected) == 1821
    assert (SLOT/'source-list.txt').read_text().splitlines() == [str(snapshot/p) for p in sorted(selected)]
    assert sum('/src/main/java/' in p for p in selected) == 965 and sum('/src/test/java/' in p for p in selected) == 856
    assert all(data.sha((snapshot/p).read_bytes()) == sha == data.sha((data.ROOT/p).read_bytes()) for p,sha in begin['sourceInputHashes'].items())
    for p,sha in {**begin['testClassFileHashes'],**begin['dependencyHashes'],**begin['toolAndRuleHashes']}.items():assert data.sha(Path(p).read_bytes()) == sha
    assert len(jar_classes(n)) == 1843 and len(test_classes(n)) == 1974
    assert {role+':'+entry:sha for (role,entry),sha in jar_classes(n).items()} == begin['mainClassHashes']
    observed_rows = [];counts = {};seen = {}
    for tool in ['pmd','checkstyle']:
        raw = (CURRENT/(tool+'.xml')).read_bytes();assert data.sha(raw) == m['reports'][tool]['sha256']
        root = ET.fromstring(raw);seen[tool] = set()
        assert not [node for node in root if node.tag.rpartition('}')[2] in ['error','configerror']]
        for file in root:
            if file.tag.rpartition('}')[2] != 'file':continue
            path = str(Path(file.get('name')).relative_to(snapshot));assert path in selected;seen[tool].add(path)
            role = next(r for r in ['api','batch','bootstrap','protocol','storage','web'] if path.startswith('src/schubert-nk-'+r+'/'))
            kind = 'main' if '/src/main/java/' in path else 'test'
            for node in file:
                assert node.tag.rpartition('}')[2] == ('violation' if tool == 'pmd' else 'error')
                attrs = dict(node.attrib);rule = attrs.get('rule',attrs.get('source','UNKNOWN'))
                assert not (tool == 'checkstyle' and rule in ['com.puppycrawl.tools.checkstyle.Checker','com.puppycrawl.tools.checkstyle.TreeWalker'])
                observed_rows.append(dict(tool=tool,path=path,sourceSha256=selected[path],module=role,kind=kind,attributes=attrs,rule=rule,
                    message=' '.join(''.join(node.itertext()).split()) if tool == 'pmd' else attrs.get('message','')))
        rows = [row for row in observed_rows if row['tool'] == tool]
        counts[tool] = dict(total=len(rows),byModule=dict(sorted(Counter(row['module'] for row in rows).items())),byKind=dict(sorted(Counter(row['kind'] for row in rows).items())),
            byRule=dict(sorted(Counter(row['rule'] for row in rows).items())),byPath=dict(sorted(Counter(row['path'] for row in rows).items())))
        assert counts[tool] == m['counts'][tool] and len(rows) == m['reports'][tool]['findings']
        stage = m['stages'][tool];assert not stage['timedOut']
        assert data.sha((SLOT/(tool+'.stdout')).read_bytes()) == stage['stdoutSha256'] and data.sha((SLOT/(tool+'.stderr')).read_bytes()) == stage['stderrSha256']
    assert seen['checkstyle'] == set(selected)
    assert m['stages']['pmd']['actualExit'] == 4 and m['stages']['checkstyle']['actualExit'] == 0
    stored = data.read_checked(CURRENT/'findings.json',m['findingsSha256']);assert stored == observed_rows
    assert counts['pmd']['total'] == 8022 and counts['pmd']['byKind'] == dict(main=1502,test=6520) and counts['checkstyle']['total'] == 0
    reference = dict(source=m['source'],sourceCount=1821,mainSourceCount=965,testSourceCount=856,mainPhysicalClasses=1843,testPhysicalClasses=1974,
        pmdWarnings=8022,pmdMain=1502,pmdTest=6520,checkstyleWarnings=0,processingErrors=0,analysisComplete=True,qualityGateExit=1,
        trackedCatalogReference=8008,aggregateDifferenceNotNewDefectCount=14,actualViolationCount=None,productTestsExecuted=0,newAccepted=0,wholeF03Accepted=False,whole451Accepted=False)
    strict(reference,reference);labels = []
    for label,change in [('source',lambda x:x.update(source='0'*40)),('source-count',lambda x:x.update(sourceCount=1820)),('test-class-versus-PT',lambda x:x.update(testPhysicalClasses=1964)),
        ('catalog-as-measured',lambda x:x.update(pmdWarnings=8008)),('quality',lambda x:x.update(qualityGateExit=0)),('bool-counter',lambda x:x.update(productTestsExecuted=False)),
        ('PT',lambda x:x.update(productTestsExecuted=1821)),('violation-count',lambda x:x.update(actualViolationCount=8022)),('accepted',lambda x:x.update(newAccepted=1))]:
        bad = copy.deepcopy(reference);change(bad);assert json.dumps(bad,sort_keys=True) != json.dumps(reference,sort_keys=True)
        try:strict(bad,reference)
        except AssertionError:labels.append(label)
        else:raise AssertionError('false all-source quality claim accepted')
    verify(invocation);OUT.mkdir();data.write(OUT/'verification.json',reference)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=m['source'],invocation=invocation,analysisManifestSha256='751a5f536623faed78362b14e69da89f5fbdba305acf2b8c1bbbf0811021dbdf',
        verificationSha256=data.sha((OUT/'verification.json').read_bytes()),metadataNegativeVectors=len(labels),nonVacuousLabels=labels,sourceCount=1821,pmdWarnings=8022,checkstyleWarnings=0,
        analysisReexecuted=False,qualityGateExit=1,actualViolationCount=None,productTestsExecuted=0,newAccepted=0,wholeF03Accepted=False,whole451Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':main()

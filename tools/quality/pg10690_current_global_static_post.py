"""Independent complete-input/XML finding index; preserves raw failure and unclassified findings."""
from collections import Counter
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

OUT = data.BASE/'PG10690-current-global-static-post-v1'
SLOT = data.ROOT.parent/'pgpt-runs/PG379/pg10688-current-global-static-v1'


def finding_rows(raw,label,inputs):
    root = ET.fromstring(raw)
    if root.tag.rpartition('}')[2] != ('pmd' if label == 'pmd' else 'checkstyle'):
        raise ValueError('original scanner report root required')
    rows = []
    for file in root:
        if file.tag.rpartition('}')[2] != 'file':
            continue
        path = Path(file.attrib['name'])
        if not path.is_absolute() or not path.is_relative_to(data.ROOT):
            raise ValueError('exact public source coordinate required')
        relative = str(path.relative_to(data.ROOT))
        if relative not in inputs:
            raise ValueError('noninventory source, never read it')
        for node in file:
            if node.tag.rpartition('}')[2] != ('violation' if label == 'pmd' else 'error'):
                continue
            line = int(node.attrib['beginline'] if label == 'pmd' else node.attrib['line'])
            assert line > 0
            rows.append(dict(scanner=label,path=relative,inputSha256=inputs[relative],
                module=relative.split('/')[1],sourceKind='MAIN' if '/src/main/java/' in relative else 'TEST',
                rule=node.attrib['rule'] if label == 'pmd' else node.attrib['source'],
                line=line,attributes=dict(node.attrib),message=' '.join(''.join(node.itertext()).split()) if label == 'pmd' else node.attrib['message'],
                disposition='UNCLASSIFIED_NOT_AUTOMATIC_DEFECT_OR_PASS'))
    return rows,root


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    primary_path = data.BASE/'PG10688-current-global-static-v1/manifest.json'
    primary_raw = primary_path.read_bytes()
    primary = json.loads(primary_raw)
    assert primary['source'] == '370fd74f6f170a18bc1bf959aa9fceced0def15a' and primary['measurementCompleted'] is True
    assert primary['productTestsExecuted'] == 0 and not primary['productCodeExecuted'] and not primary['rulesChanged'] and not primary['suppressionsAdded']
    inputs = data.read_checked(primary_path.parent/'inputs.json',primary['inputsSha256'])
    normal_path = data.BASE/'PG10632-query-semantic-constant-compile-v1/manifest.json'
    normal = data.read_checked(normal_path,'8f29215a400d24a55ecabee90c74fb72a43525b740f129a12ae6053559701f87')
    wanted = {p:h for p,h in normal['begin']['inputHashes'].items() if p.startswith('src/schubert-nk-') and '/src/' in p and p.endswith('.java')}
    assert inputs == wanted and len(inputs) == 1810
    assert Counter('MAIN' if '/src/main/java/' in p else 'TEST' for p in inputs) == {'MAIN':965,'TEST':845}
    assert sum(p.endswith('/package-info.java') for p in inputs) == 37
    listing = (SLOT/'source-list.txt').read_bytes()
    assert data.sha(listing) == primary['sourceListSha256']
    assert listing.decode().splitlines() == [str(data.ROOT/p) for p in sorted(inputs)]
    snapshot = Path(primary['snapshot'])
    for p,h in inputs.items():
        assert data.sha((data.ROOT/p).read_bytes()) == data.sha((snapshot/p).read_bytes()) == h
    for path,digest in {**primary['dependencyHashes'],**primary['toolAndRuleHashes']}.items():
        assert data.sha(Path(path).read_bytes()) == digest
    rows,summary = [],{}
    for label in ('pmd','checkstyle'):
        raw = (primary_path.parent/(label+'.xml')).read_bytes()
        assert data.sha(raw) == primary['reports'][label]['sha256'] == data.sha((SLOT/(label+'.xml')).read_bytes())
        selected,root = finding_rows(raw,label,inputs)
        assert len(selected) == primary['reports'][label]['findings']
        errors = [n for n in root.iter() if n.tag.rpartition('}')[2] in ('error','configerror')] if label == 'pmd' else []
        assert len(errors) == primary['reports'][label]['processingErrors'] == 0
        step = primary['stages'][label]
        assert not step['timedOut']
        exit_record = json.loads((SLOT/(label+'-exit.safe.json')).read_bytes())
        assert exit_record == step
        for stream in ('stdout','stderr'):
            assert data.sha((SLOT/(label+'.'+stream)).read_bytes()) == step[stream+'Sha256']
        assert (step['actualExit'] == 0) == (not selected)
        summary[label] = dict(findings=len(selected),bySourceKind=dict(Counter(r['sourceKind'] for r in selected)),
            byRule=dict(Counter(r['rule'] for r in selected)),scannerExit=step['actualExit'],processingErrors=0)
        for row in selected:
            row['id'] = label.upper()+'-'+str(len(rows)+1).zfill(5)
            row['rowSha256'] = data.sha(json.dumps(row,sort_keys=True,ensure_ascii=False).encode())
            rows.append(row)
    gate = not rows
    assert primary['actualExit'] == (0 if gate else 1)
    for raw in ('<invalid/>','<pmd><file name="/outside.java"><violation rule="X" beginline="1"/></file></pmd>'):
        try:
            finding_rows(raw.encode(),'pmd',inputs)
        except ValueError:
            pass
        else:
            raise AssertionError('invalid source/report must be rejected without target read')
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'findings.json',rows)
    data.write(OUT/'manifest.json',dict(actualExit=0,metadataAuditCompleted=True,primaryStaticGateExit=primary['actualExit'],
        primaryManifestSha256=data.sha(primary_raw),source=primary['source'],invocation=invocation,
        sourcesChecked=1810,mainSources=965,testSources=845,packageInfoIncluded=37,summary=summary,
        findingCount=len(rows),findingsSha256=data.sha((OUT/'findings.json').read_bytes()),negativeMetadataVectors=2,
        productTestsExecuted=0,productCodeExecuted=False,coverage=None,wholeF03Accepted=False,
        externalActions=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0,primaryStaticGateExit=primary['actualExit'],summary=summary,
        manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()

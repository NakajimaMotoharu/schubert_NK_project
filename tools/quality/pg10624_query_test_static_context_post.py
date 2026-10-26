"""Independent original XML/line/hash binding of39 source judgments, not runtime PT."""
import copy
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

OUT = data.BASE/'PG10624-query-test-static-context-post-v1'


def require(condition,message):
    if not condition:
        raise ValueError(message)


def check(rows,original,texts,hashes):
    require(len(rows) == len(original) == 39,'all original39 rows required')
    for i,(row,finding) in enumerate(zip(rows,original),1):
        require(row['metadataId'] == f'STATIC-10622-{i:03d}','one-to-one metadata identity')
        require(row['originalFinding'] == finding,'raw XML finding immutable')
        path = row['path']
        require(path in texts and row['sourceSha256'] == hashes[path],'exact current source SHA')
        a,b = int(finding['beginline']),int(finding['endline'])
        span = '\n'.join(texts[path].splitlines()[a-1:b])
        require(row['sourceSpanSha256'] == data.sha(span.encode()),'exact source span')
        actionable = finding['rule'] == 'AvoidLiteralsInIfCondition'
        expected = 'ACTIONABLE_OPEN_BUG1853' if actionable else 'NOT_APPLICABLE_TO_EXACT_TEST_CONTEXT'
        require(row['disposition'] == expected and row['dynamicQualification'] is False,'source classification only; dynamic unproved')
        require(isinstance(row['reason'],str) and len(row['reason']) > 60,'explicit scoped source rationale')


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    manifest_path = data.BASE/'PG10622-query-test-static-context-v1/manifest.json'
    result = data.read_checked(manifest_path,'606712ec61dc8240a3a46c13002001a0badd213255b427a681300e1c6c944db9')
    rows = data.read_checked(manifest_path.parent/'judgments.json',result['judgmentsSha256'])
    static = data.read_checked(data.BASE/'PG10610-log-cleanup-literal-static-v1/manifest.json',
        'ece9dc5461f5cd2dd24a1a62c7a4bd3c9d236d8bec737fed23791401f4ceb8b5')
    raw_path = data.BASE/'PG10610-log-cleanup-literal-static-v1/pmd.xml'
    assert data.sha(raw_path.read_bytes()) == static['reports']['pmd']['sha256']
    original = []
    for node in ET.fromstring(raw_path.read_bytes()).iter():
        if node.tag.rpartition('}')[2] == 'file':
            path = Path(node.attrib['name']).relative_to(data.ROOT).as_posix()
            assert path in result['sourceHashes']
            for child in node:
                if child.tag.rpartition('}')[2] == 'violation':
                    finding = dict(child.attrib,message=' '.join(''.join(child.itertext()).split()))
                    original.append(finding)
    texts = {p:(data.ROOT/p).read_text() for p in result['sourceHashes']}
    assert all(data.sha(t.encode()) == result['sourceHashes'][p] for p,t in texts.items())
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in result['companionSourceHashes'].items())
    check(rows,original,texts,result['sourceHashes'])
    rejected = []
    edits = [
        ('source-sha',lambda r:r[0].update(sourceSha256='0'*64)),
        ('lost-row',lambda r:r.pop()),
        ('invented-dynamic',lambda r:r[0].update(dynamicQualification=True)),
        ('invented-applicability',lambda r:r[0].update(disposition='PASS'))]
    for label,edit in edits:
        changed = copy.deepcopy(rows)
        edit(changed)
        try:
            check(changed,original,texts,result['sourceHashes'])
        except ValueError:
            rejected.append(label)
        else:
            raise AssertionError('invalid source classification accepted')
    assert result['reviewed'] == 39 and result['contextNotApplicable'] == 34 and result['actionable'] == 5
    assert result['rawStaticExit'] == 1 and not result['actualExecutorShutdownLivenessProven']
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=result['source'],invocation=invocation,
        primaryManifestSha256=data.sha(manifest_path.read_bytes()),rawXmlSha256=data.sha(raw_path.read_bytes()),
        originalFindingRows=39,sourceSpans=39,sourceContextsNotApplicable=34,actionable=5,
        metadataNegativeVectors=rejected,rawStaticExit=1,remainingActionableBug='BUG1853',
        productTestsExecuted=0,coverage=None,actualExecutorShutdownLivenessProven=False,
        wholeF03Accepted=False,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()

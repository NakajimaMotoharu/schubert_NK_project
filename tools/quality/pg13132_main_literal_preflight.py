"""Source-only Main PG preflight: exact inverses and two original diagnostic removals."""
from collections import Counter
import json
import os
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg13131_main_literal_inverse import inverse, negative
import pg9666_pagination_static as runner

SLOT = data.ROOT.parent/'pgpt-runs/PG379/pg13132-main-literal-preflight-v1'
OUT = data.BASE/'PG13132-main-literal-preflight-v1'

def signature(attributes,message):
    return json.dumps({k:v for k,v in attributes.items() if k not in ['beginline','endline','begincolumn','endcolumn']},sort_keys=True),message

def main():
    invocation = capture(__file__);assert not SLOT.exists() and not OUT.exists()
    old = data.read_checked(data.BASE/'PG13130-main-literal-originals-v1/manifest.json','1ae8f6627fa5a7092106d5659601102a556915061e8c4950928086706e906c34')
    original = data.read_checked(data.BASE/'PG13130-main-literal-originals-v1/originals.json',old['originalsSha256'])
    normal = data.read_checked(data.BASE/'PG13106-snapshot-corrected-six-compile-v1/manifest.json','0d052046bbfe7586c491f1cb398566301fae8d958c0e2ae3e660d477961c12c7')
    h = data.read_checked(data.BASE/'PG13108-snapshot-corrected-host-v1/manifest.json','776be8fff9f5c812c557a02f2198313adf8f506f2f88fea1c809e200911b525a')
    paths = {r['path'] for r in original['sources']}
    hashes = {p:data.sha((data.ROOT/p).read_bytes()) for p in paths}
    inverses = {}; negatives = {}
    for row in original['sources']:
        text = (data.ROOT/row['path']).read_text()
        inverses[row['path']] = inverse(row['path'],row['text'],text)
        negatives[row['path']] = negative(row['path'],row['text'],text)
    assert {p for p,sha in normal['begin']['inputHashes'].items() if data.sha((data.ROOT/p).read_bytes()) != sha} == paths
    original_raw = (data.BASE/'PG10690-current-global-static-post-v1/findings.json').read_bytes()
    assert data.sha(original_raw) == original['originalFindingsSha256']
    expected = {path:Counter(signature(r['attributes'],r['message']) for r in json.loads(original_raw) if r['path'] == path and r['id'] not in ['PMD-02953','PMD-06175']) for path in paths}
    static = runner.TC/'static-gates-20261015';rules = data.ROOT/'tools/quality/static'
    pmd = [static/'record-fix-v1/pmd-record-1298.jar',*sorted((static/'pmd-bin-7.28.0/lib').glob('*.jar'))]
    tools = {str(p):data.sha(p.read_bytes()) for p in [*pmd,static/'checkstyle-14.3.0-all.jar',rules/'pmd.xml',rules/'checkstyle.xml']}
    deps = h['begin']['dependencyHashes'];assert all(data.sha(Path(p).read_bytes()) == sha for p,sha in deps.items())
    SLOT.mkdir();runner.SLOT = SLOT;listing = SLOT/'source-list.txt'
    with listing.open('x') as stream:stream.write(''.join(str(data.ROOT/p)+'\n' for p in sorted(paths)))
    java = str(runner.TC/'jdk-25.0.4/bin/java')
    stages = {
        'pmd':runner.step('pmd',[java,'-cp',os.pathsep.join(map(str,pmd)),'net.sourceforge.pmd.cli.PmdCli','check','--file-list',str(listing),'--rulesets',str(rules/'pmd.xml'),'--use-version','java-25','--minimum-priority','5','--aux-classpath',os.pathsep.join(deps),'--no-cache','--format','xml','--report-file',str(SLOT/'pmd.xml')],SLOT),
        'checkstyle':runner.step('checkstyle',[java,'-jar',str(static/'checkstyle-14.3.0-all.jar'),'-c',str(rules/'checkstyle.xml'),'-f','xml','-o',str(SLOT/'checkstyle.xml'),'@'+str(listing)],SLOT),
    }
    current = {path:Counter() for path in paths};actual_rows = []
    tree = ET.parse(SLOT/'pmd.xml').getroot()
    assert not [x for x in tree.iter() if x.tag.rpartition('}')[2] in ['error','configerror']]
    for file in tree:
        if file.tag.rpartition('}')[2] != 'file':continue
        path = str(Path(file.get('name')).relative_to(data.ROOT));assert path in paths
        for row in file:
            assert row.tag.rpartition('}')[2] == 'violation'
            current[path][signature(dict(row.attrib),row.text.strip())] += 1
            actual_rows.append(dict(path=path,attributes=dict(row.attrib),message=row.text.strip()))
    assert current == expected
    assert not [x for x in ET.parse(SLOT/'checkstyle.xml').getroot().iter() if x.tag == 'error']
    assert stages['pmd']['actualExit'] == (4 if actual_rows else 0) and stages['checkstyle']['actualExit'] == 0 and not any(x['timedOut'] for x in stages.values())
    assert all(data.sha((data.ROOT/p).read_bytes()) == sha for p,sha in hashes.items())
    assert all(data.sha(Path(p).read_bytes()) == sha for p,sha in {**tools,**deps}.items())
    verify(invocation);OUT.mkdir()
    for name in ['pmd','checkstyle']:
        with (OUT/(name+'.xml')).open('xb') as stream:stream.write((SLOT/(name+'.xml')).read_bytes())
    data.write(OUT/'manifest.json',dict(actualExit=0,baseSource=old['source'],source=None,invocation=invocation,
        candidateSourceHashes=hashes,originalTokenInverses=inverses,negativeVectors=negatives,
        removedOriginalFindingIds=['PMD-02953','PMD-06175'],retainedRawFindings=actual_rows,
        rawStatic=len(actual_rows),rawStaticGateExit=1 if actual_rows else 0,stages=stages,toolAndRuleHashes=tools,
        reports={name:data.sha((OUT/(name+'.xml')).read_bytes()) for name in ['pmd','checkstyle']},
        productTestsExecuted=0,dynamicPtStatus='NOT_EXECUTED_HOLD',coverageStatus='NOT_MEASURED',
        newAccepted=0,whole451Accepted=False,externalActions=0))
    print(json.dumps(dict(manifestSha256=data.sha((OUT/'manifest.json').read_bytes()),retainedRaw=len(actual_rows),negativeVectors=sum(negatives.values()))))

if __name__ == '__main__':main()

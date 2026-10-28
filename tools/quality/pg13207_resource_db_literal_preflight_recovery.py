"""Recover only saved original static reports after correcting BUG2037; no tool/Test replay."""
from collections import Counter
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import pg13203_resource_db_literal_config as cfg
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from f03_literal_batch_sources import original_value, prior_normal, inverse, negative, out
from f03_literal_batch_diagnostic_v2 import signature, selftest

OUT = data.BASE/'PG13207-resource-db-literal-preflight-recovery-v1'
FAILED_SLOT = data.ROOT.parent/'pgpt-runs/PG379'/out(cfg,cfg.PREFLIGHT_NUMBER).name.lower()

def main():
    invocation = capture(__file__);assert not OUT.exists();vectors = selftest()
    assert data.sha((data.ROOT/'tools/quality/pg13206_resource_db_literal_preflight.py').read_bytes()) == '85bc718d1ca4bd47827c1c9559fc68093c2b67f4d182764ddce46f40800a0470'
    original = original_value(cfg);normal = prior_normal(cfg);hashes = {};inverses = {};negatives = {};expected = {};removed = []
    for row in original['sources']:
        path = row['path'];text = (data.ROOT/path).read_text();hashes[path] = data.sha(text.encode());inverses[path] = inverse(row['text'],text,row['mapping']);negatives[path] = negative(row['text'],text,row['mapping'])
        selected = {r['id'] for r in row['mapping']};removed += sorted(selected)
        expected[path] = Counter(signature(r['attributes'],r['message']) for r in row['findings'] if r['id'] not in selected)
    assert len(removed) == 119 and {p for p,sha in normal['begin']['inputHashes'].items() if data.sha((data.ROOT/p).read_bytes()) != sha} == set(cfg.PATHS)
    listing = (FAILED_SLOT/'source-list.txt').read_text().splitlines();assert listing == [str(data.ROOT/p) for p in sorted(cfg.PATHS)]
    stages = {};report_hashes = {name:data.sha((FAILED_SLOT/(name+'.xml')).read_bytes()) for name in ['pmd','checkstyle']}
    for name,code in [('pmd',4),('checkstyle',0)]:
        stage = json.loads((FAILED_SLOT/(name+'-exit.safe.json')).read_bytes());assert stage['actualExit'] == code and not stage['timedOut']
        assert data.sha((FAILED_SLOT/(name+'.stdout')).read_bytes()) == stage['stdoutSha256'] and data.sha((FAILED_SLOT/(name+'.stderr')).read_bytes()) == stage['stderrSha256']
        assert stage['cwd'] == str(FAILED_SLOT);stages[name] = stage
    current = {p:Counter() for p in cfg.PATHS};rows = [];root = ET.parse(FAILED_SLOT/'pmd.xml').getroot()
    assert not [x for x in root.iter() if x.tag.rpartition('}')[2] in ['error','configerror']]
    for file in root:
        if file.tag.rpartition('}')[2] != 'file':continue
        path = str(Path(file.get('name')).relative_to(data.ROOT));assert path in current;lines = (data.ROOT/path).read_text().splitlines()
        for node in file:
            attrs = dict(node.attrib);assert node.tag.rpartition('}')[2] == 'violation'
            line = int(attrs['beginline']);assert 0 < line <= len(lines) and lines[line-1].strip()
            current[path][signature(attrs,node.text.strip())] += 1;rows.append(dict(path=path,attributes=attrs,message=node.text.strip(),sourceLine=lines[line-1].strip()))
    assert current == expected and len(rows) == 98
    assert not [x for x in ET.parse(FAILED_SLOT/'checkstyle.xml').getroot().iter() if x.tag == 'error']
    assert all(data.sha((data.ROOT/p).read_bytes()) == sha for p,sha in hashes.items())
    verify(invocation);OUT.mkdir()
    for name in report_hashes:
        with (OUT/(name+'.xml')).open('xb') as stream:stream.write((FAILED_SLOT/(name+'.xml')).read_bytes())
    data.write(OUT/'manifest.json',dict(actualExit=0,source=None,baseSource=cfg.BASE_SOURCE,invocation=invocation,candidateSourceHashes=hashes,
        originalTokenInverses=inverses,negativeVectors=negatives,diagnosticFormatVectors=vectors,removedFindingIds=removed,retainedRawFindings=rows,rawStatic=98,rawStaticGateExit=1,
        originalStaticStages=stages,reports=report_hashes,priorFailedEntryExit=1,priorFailedSlot=str(FAILED_SLOT),staticExecutionsReissued=0,
        sourceContinuity='Operator preserved same four dirty sources after original command; current full token inverses and report anchors rechecked; no retroactive original source hash claim',
        originalFailedStageSourceHashPersisted=False,productTestsExecuted=0,dynamicPtStatus='NOT_EXECUTED_HOLD',coverageStatus='NOT_MEASURED',newAccepted=0,whole451Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':main()

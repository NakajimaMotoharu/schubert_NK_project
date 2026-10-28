"""Current-source literal metadata only; never run a target Test, SQL or a protected operation."""
from collections import Counter
import json
import re
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from f03_literal_batch_sources import tokens,out,prior_normal
from f03_literal_batch_diagnostic_v3 import signature


def select(text,rows,expected):
    source = tokens(text)
    result = []
    for row in rows:
        if row['attributes']['rule'] != 'AvoidDuplicateLiterals':
            continue
        m = re.fullmatch(r'The String literal "(.*)" appears (\d+) times in this file; the first occurrence is on line \d+',row['message'])
        if not m or not re.fullmatch(r'[\x20-\x21\x23-\x5b\x5d-\x7e]{3,2000}',m[1]):
            continue
        literal = json.dumps(m[1])
        count = int(m[2])
        if count < 4 or source.count(literal) != count:
            continue
        stem = re.sub('[^A-Z0-9]+','_',m[1].upper()).strip('_')[:40] or 'VALUE'
        name = 'FIXTURE_'+stem+'_'+data.sha(literal.encode())[:8].upper()
        assert name not in source
        result.append(dict(id=row['id'],value=m[1],literal=literal,name=name,references=count))
    assert len(result) == expected and len({r['name'] for r in result}) == expected
    return result


def baseline(cfg,row):
    current = data.read_checked(data.BASE/cfg.CURRENT_BASELINE[0]/'manifest.json',cfg.CURRENT_BASELINE[1])
    path = row['path']
    if path in current['candidateSourceHashes']:
        assert current['actualExit'] == 0 and current['candidateSourceHashes'][path] == row['sha256']
        rows = [dict(r,sourceSha256=row['sha256']) for r in current['retainedRawFindings'] if r['path'] == path]
        ref = dict(manifest=cfg.CURRENT_BASELINE[0],sha256=cfg.CURRENT_BASELINE[1],basis='EXACT_CURRENT_CANDIDATE_HASH_AND_RETAINED_MEASURED_ROWS')
    else:
        global_manifest = data.read_checked(data.BASE/cfg.GLOBAL_BASELINE[0]/'manifest.json',cfg.GLOBAL_BASELINE[1])
        measured = data.read_checked(data.BASE/cfg.GLOBAL_BASELINE[0]/'findings.json',global_manifest['findingsSha256'])
        rows = [r for r in measured if r['path'] == path]
        assert rows and all(r['sourceSha256'] == row['sha256'] for r in rows)
        ref = dict(manifest=cfg.GLOBAL_BASELINE[0],sha256=cfg.GLOBAL_BASELINE[1],basis='UNCHANGED_EXACT_GLOBAL_MEASURED_SOURCE_HASH')
    assert rows
    return rows,dict(ref,currentSourceSha256=row['sha256'])


def originals(cfg):
    invocation = capture(__file__)
    target = out(cfg,cfg.ORIGINAL_NUMBER)
    assert not target.exists()
    normal = prior_normal(cfg)
    original_raw = (data.BASE/'PG10690-current-global-static-post-v1/findings.json').read_bytes()
    findings = json.loads(original_raw)
    ids,refs,_ = cfg.PREVIOUS_STATE()
    sources = []
    for path,(sha,expected,owner) in cfg.PATHS.items():
        assert path.startswith('src/') and '/src/test/java/' in path and path.endswith('Test.java')
        file = data.ROOT/path
        assert not file.is_symlink()
        text = file.read_text()
        assert data.sha(text.encode()) == sha == normal['begin']['inputHashes'][path]
        rows = [r for r in findings if r['path'] == path]
        mapping = select(text,[r for r in rows if r['id'] in ids-refs],expected)
        assert not any(x in text for x in ['getDeclaredField','Class.forName','setAccessible'])
        row = dict(path=path,sha256=sha,text=text,findings=rows,mapping=mapping,canonicalOwner=owner)
        measured,binding = baseline(cfg,row)
        active = Counter(signature(r['attributes'],r['message']) for r in rows if r['id'] in ids)
        assert active <= Counter(signature(r['attributes'],r['message']) for r in measured)
        row.update(currentDiagnosticBaseline=binding,originalDiagnosticInputHashes=sorted({r['inputSha256'] for r in rows}))
        sources.append(row)
    assert sum(len(r['mapping']) for r in sources) == cfg.EXPECTED_CORRECTIONS
    verify(invocation)
    target.mkdir()
    data.write(target/'originals.json',dict(source=cfg.BASE_SOURCE,originalFindingsSha256=data.sha(original_raw),sources=sources))
    data.write(target/'manifest.json',dict(actualExit=0,source=cfg.BASE_SOURCE,invocation=invocation,originalsSha256=data.sha((target/'originals.json').read_bytes()),
        sourcePaths=list(cfg.PATHS),selectedLiteralDiagnostics=cfg.EXPECTED_CORRECTIONS,currentDiagnosticBaselines={r['path']:r['currentDiagnosticBaseline'] for r in sources},
        productTestsExecuted=0,newAccepted=0,externalActions=0))
    print(data.sha((target/'manifest.json').read_bytes()))

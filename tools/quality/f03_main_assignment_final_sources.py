"""Strict full-token inverse of four explicit Main statement forms, never target execution."""
import json
import g07_host_class_provenance_inputs as data
from f03_literal_batch_sources import tokens, out, prior_normal
from f03_literal_batch_diagnostic_v3 import signature
from f03_main_assignment_sources import baseline
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from trace_owner_join import canonical

OLD = {
 'READ':'int read; while ((read = input.read(buffer)) != -1) {',
 'PHASE':'require(boundary.ordinal() == phase[0]++);',
 'SIZE':'require(n > 0 && (count += n) <= size);',
 'LINE':'String line; while ((line = reader.readLine()) != null) {',
}
NEW = {
 'READ':'while (true) { int read = input.read(buffer); if (read == -1) break;',
 'PHASE':'int observedPhase = boundary.ordinal(); int expectedPhase = phase[0]; phase[0]++; require(observedPhase == expectedPhase);',
 'SIZE':'boolean withinSize = n > 0; if (withinSize) { count += n; withinSize = count <= size; } require(withinSize);',
 'LINE':'while (true) { String line = reader.readLine(); if (line == null) break;',
}
WRONG = {
 'READ':['while(true){int read=input.read(buffer);if(read==0)break;',
         'while(true){int read=input.read(buffer);if(input.read(buffer)==-1)break;',
         'while(true){int read=input.read(buffer);if(read!=-1)break;',
         'while(true){int read=input.read(buffer);'],
 'PHASE':['int observedPhase=boundary.ordinal();int expectedPhase=phase[0]+1;phase[0]++;require(observedPhase==expectedPhase);',
          'int expectedPhase=phase[0];phase[0]++;int observedPhase=boundary.ordinal();require(observedPhase==expectedPhase);',
          'int observedPhase=boundary.ordinal();int expectedPhase=phase[0];phase[0]--;require(observedPhase==expectedPhase);',
          'int observedPhase=boundary.ordinal();int expectedPhase=phase[0];require(observedPhase==expectedPhase);'],
 'SIZE':['boolean withinSize=n>0;if(withinSize){count+=n;withinSize=count<size;}require(withinSize);',
         'boolean withinSize=n>0;if(withinSize){count-=n;withinSize=count<=size;}require(withinSize);',
         'count+=n;boolean withinSize=n>0;if(withinSize){withinSize=count<=size;}require(withinSize);',
         'boolean withinSize=n>=0;if(withinSize){count+=n;withinSize=count<=size;}require(withinSize);'],
 'LINE':['while(true){String line=reader.readLine();if(line.isEmpty())break;',
         'while(true){String line=reader.readLine();if(reader.readLine()==null)break;',
         'while(true){String line=reader.readLine();if(line!=null)break;',
         'while(true){String line=reader.readLine();'],
}

def location(values,pattern):
    matches = [i for i in range(len(values)) if values[i:i+len(pattern)] == pattern]
    assert len(matches) == 1
    return matches[0]

def inverse(old,new,mapping):
    assert len(mapping) == 1
    kind = mapping[0]['kind']
    before,after = tokens(old),tokens(new)
    a,b = tokens(OLD[kind]),tokens(NEW[kind])
    at = location(after,b)
    assert after[:at]+a+after[at+len(b):] == before
    return dict(originalTokens=len(before),rewrittenStatements=1,wholeSourceTokensRecovered=True,
                evaluationOrderPreserved=True,readCallsNotDuplicated=True,primitiveLocalsOnly=True)

def negative(old,new,mapping):
    kind = mapping[0]['kind']
    after,pattern = tokens(new),tokens(NEW[kind])
    at = location(after,pattern)
    variants = [after[:at]+tokens(part)+after[at+len(pattern):] for part in WRONG[kind]]+[after+[';']]
    assert len({tuple(value) for value in variants}) == len(variants) == 5
    for value in variants:
        assert value != after
        try:
            inverse(old,' '.join(value),mapping)
        except AssertionError:
            pass
        else:
            raise AssertionError('changed read/order/phase/short-circuit accepted')
    return len(variants)

def candidate(text,kind):
    matches = [match for match in LEX.finditer(text) if not match.group().startswith(('//','/*'))]
    at = location([match.group() for match in matches],tokens(OLD[kind]))
    end = at+len(tokens(OLD[kind]))
    return text[:matches[at].start()]+NEW[kind]+text[matches[end-1].end():]

def originals(cfg):
    invocation = capture(__file__)
    target = out(cfg,cfg.ORIGINAL_NUMBER)
    assert not target.exists()
    normal = prior_normal(cfg)
    catalog = json.loads((data.BASE/'PG10690-current-global-static-post-v1/findings.json').read_bytes())
    inv = json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())
    logical = {row['path']:row for row in inv['artifacts']}
    ids,refs,_ = cfg.previous_state()
    rows = []
    for path,(pin,chosen,owner,kind) in cfg.PATHS.items():
        text = (data.ROOT/path).read_text()
        assert data.sha(text.encode()) == pin == normal['begin']['inputHashes'][path]
        ownership = canonical(path,logical)
        assert ownership['canonicalOwner'] == ownership['canonicalCostOwner'] == owner
        findings = [row for row in catalog if row['path'] == path]
        selected = [row for row in findings if row['id'] in chosen]
        assert len(selected) == len(chosen) == 1 and set(chosen) <= ids-refs
        assert all(row['inputSha256'] == pin and row['rule'] == 'AssignmentInOperand' for row in selected)
        row = dict(path=path,sha256=pin,text=text,findings=findings,mapping=[dict(id=item['id'],kind=kind) for item in selected],**ownership)
        measured,_ = baseline(cfg,row)
        assert sum(signature(r['attributes'],r['message']) == signature(selected[0]['attributes'],selected[0]['message']) for r in measured) == 1
        new = candidate(text,kind)
        inverse(text,new,row['mapping'])
        row['preEditNegativeVectors'] = negative(text,new,row['mapping'])
        rows.append(row)
    verify(invocation)
    target.mkdir()
    data.write(target/'originals.json',dict(source=cfg.BASE_SOURCE,sources=rows))
    data.write(target/'manifest.json',dict(actualExit=0,source=cfg.BASE_SOURCE,invocation=invocation,
        originalsSha256=data.sha((target/'originals.json').read_bytes()),selectedMainSources=len(rows),selectedDiagnostics=4,
        metadataNegativeVectors=sum(row['preEditNegativeVectors'] for row in rows),productTestsExecuted=0,newAccepted=0,
        externalActions=0,plannedRecord=cfg.RECORD))
    print(data.sha((target/'manifest.json').read_bytes()))

"""Read exact current PMD source positions; no message-value decoding or target execution."""
from collections import Counter
import copy
import json
import re
import g07_host_class_provenance_inputs as data
from f03_literal_batch_sources import tokens,out,prior_normal
from f03_literal_batch_diagnostic_v3 import signature
from public_java_digest_provenance import LEX
from host_tool_invocation import capture,verify

NUMBER = r'(?:[1-9][0-9]*|[1-9][0-9]{0,2}(?:,[0-9]{3})+)'
TAIL = re.compile(r' appears ('+NUMBER+r') times in this file; the first occurrence is on line ('+NUMBER+r')$')


def baseline(cfg,row):
    matches = []
    for name,pin in cfg.BASELINE_REFERENCES:
        value = data.read_checked(data.BASE/name/'manifest.json',pin)
        assert value['actualExit'] == 0
        if value['candidateSourceHashes'].get(row['path']) == row['sha256']:
            matches.append((name,pin,value))
    assert len(matches) == 1
    name,pin,value = matches[0]
    rows = [dict(r,sourceSha256=row['sha256']) for r in value['retainedRawFindings'] if r['path'] == row['path']]
    assert rows
    return rows,dict(manifest=name,sha256=pin,currentSourceSha256=row['sha256'],basis='EXACT_CURRENT_FILE_HASH_AND_PINNED_MEASURED_POSITION_NOT_MESSAGE_VALUE')


def literal_at(text,attributes):
    starts = [0]+[match.end() for match in re.finditer('\n',text)]
    line,column,endline,endcolumn = [int(attributes[key]) for key in ['beginline','begincolumn','endline','endcolumn']]
    if not (1 <= line <= endline <= len(starts) and column >= 1 and endcolumn >= 1):
        return None
    start,end = starts[line-1]+column-1,starts[endline-1]+endcolumn-1
    if not (0 <= start < end <= len(text)):
        return None
    prefix = text[starts[line-1]:start]
    if '\t' in prefix or any(ord(char) > 0xffff for char in prefix):
        return None
    matches = [match for match in LEX.finditer(text) if match.start() == start and match.end() == end]
    if len(matches) != 1:
        return None
    literal = matches[0].group()
    if not literal.startswith('"') or not literal.endswith('"') or literal.startswith('"""'):
        return None
    value = literal[1:-1]
    if not re.fullmatch(r'[\x20-\x21\x23-\x5b\x5d-\x7e]{3,2000}',value) or json.dumps(value) != literal:
        return None
    first = next(match for match in LEX.finditer(text) if match.group() == literal)
    if first.start() != start:
        return None
    return literal,start,end


def select(text,expected_sha,original_rows,measured_rows,allowed_ids,expected):
    assert data.sha(text.encode()) == expected_sha
    source_tokens = tokens(text)
    result = []
    for row in original_rows:
        if row['attributes']['rule'] != 'AvoidDuplicateLiterals':
            continue
        assert row['id'] in allowed_ids
        matches = [r for r in measured_rows if signature(r['attributes'],r['message']) == signature(row['attributes'],row['message'])]
        assert len(matches) == 1
        measured = matches[0]
        located = literal_at(text,measured['attributes'])
        if located is None:
            continue
        tail = TAIL.search(measured['message'])
        assert tail
        count,line = [int(part.replace(',','')) for part in tail.groups()]
        assert line == int(measured['attributes']['beginline'])
        literal,start,end = located
        if count < 4 or source_tokens.count(literal) != count:
            continue
        value = literal[1:-1]
        stem = re.sub('[^A-Z0-9]+','_',value.upper()).strip('_')[:40] or 'VALUE'
        name = 'FIXTURE_'+stem+'_'+data.sha(literal.encode())[:8].upper()
        assert name not in source_tokens
        result.append(dict(id=row['id'],value=value,literal=literal,name=name,references=count,currentAttributes=measured['attributes'],
            currentDiagnosticMessage=measured['message'],sourceStartOffset=start,sourceEndOffsetExclusive=end,currentLiteralSha256=data.sha(literal.encode())))
    assert len({r['name'] for r in result}) == len(result)
    if expected is not None:
        assert len(result) == expected
    return result


def metadata_vectors(text,sha,original,measured,allowed,mapping):
    assert mapping and select(text,sha,original,measured,allowed,len(mapping)) == mapping
    chosen = next(row for row in original if row['id'] == mapping[0]['id'])
    index, = [i for i,row in enumerate(measured) if signature(row['attributes'],row['message']) == signature(chosen['attributes'],chosen['message'])]
    negatives = []
    for label,change in [
        ('begin-column',lambda rows:rows[index]['attributes'].update(begincolumn=str(int(rows[index]['attributes']['begincolumn'])+1))),
        ('end-column',lambda rows:rows[index]['attributes'].update(endcolumn=str(int(rows[index]['attributes']['endcolumn'])+1))),
        ('zero-line',lambda rows:rows[index]['attributes'].update(beginline='0')),
        ('outside-end',lambda rows:rows[index]['attributes'].update(endline='99999999')),
        ('wrong-count',lambda rows:rows[index].update(message=rows[index]['message'].replace(' appears ',' appears 0',1))),
        ('duplicate',lambda rows:rows.append(copy.deepcopy(rows[index]))),
    ]:
        bad = copy.deepcopy(measured)
        change(bad)
        assert bad != measured
        try:
            select(text,sha,original,bad,allowed,len(mapping))
        except AssertionError:
            negatives.append(label)
        else:
            raise AssertionError('false source-position metadata accepted')
    for label,body,pin,ids in [('changed-source',text+' ',sha,allowed),('wrong-source-sha',text,'0'*64,allowed),('foreign-id',text,sha,allowed-{chosen['id']})]:
        try:
            select(body,pin,original,measured,ids,len(mapping))
        except AssertionError:
            negatives.append(label)
        else:
            raise AssertionError('false source identity accepted')
    return dict(positive=1,negative=len(negatives),labels=negatives,productTestsExecuted=0)


def originals(cfg):
    invocation = capture(__file__)
    target = out(cfg,cfg.ORIGINAL_NUMBER)
    assert not target.exists()
    normal = prior_normal(cfg)
    original_raw = (data.BASE/'PG10690-current-global-static-post-v1/findings.json').read_bytes()
    findings = json.loads(original_raw)
    ids,refs,_ = cfg.PREVIOUS_STATE()
    allowed = ids-refs
    sources = []
    for path,(sha,expected,owner) in cfg.PATHS.items():
        file = data.ROOT/path
        assert path.startswith('src/') and '/src/test/java/' in path and path.endswith('Test.java') and not file.is_symlink()
        text = file.read_text()
        assert data.sha(text.encode()) == sha == normal['begin']['inputHashes'][path]
        assert not any(value in text for value in ['getDeclared','Class.forName','setAccessible','.getFields(','.getMethods('])
        rows = [row for row in findings if row['path'] == path]
        source = dict(path=path,sha256=sha,text=text,findings=rows,canonicalOwner=owner)
        measured,binding = baseline(cfg,source)
        active = Counter(signature(row['attributes'],row['message']) for row in rows if row['id'] in ids)
        assert active <= Counter(signature(row['attributes'],row['message']) for row in measured)
        eligible = [row for row in rows if row['id'] in allowed]
        mapping = select(text,sha,eligible,measured,allowed,expected)
        source.update(mapping=mapping,currentDiagnosticBaseline=binding,originalDiagnosticInputHashes=sorted({row['inputSha256'] for row in rows}),selectionMetadataVectors=metadata_vectors(text,sha,eligible,measured,allowed,mapping))
        sources.append(source)
    assert sum(len(row['mapping']) for row in sources) == cfg.EXPECTED_CORRECTIONS
    verify(invocation)
    target.mkdir()
    data.write(target/'originals.json',dict(source=cfg.BASE_SOURCE,originalFindingsSha256=data.sha(original_raw),sources=sources))
    data.write(target/'manifest.json',dict(actualExit=0,source=cfg.BASE_SOURCE,invocation=invocation,originalsSha256=data.sha((target/'originals.json').read_bytes()),
        sourcePaths=list(cfg.PATHS),selectedLiteralDiagnostics=cfg.EXPECTED_CORRECTIONS,currentDiagnosticBaselines={row['path']:row['currentDiagnosticBaseline'] for row in sources},
        selectionMetadataNegativeVectors=sum(row['selectionMetadataVectors']['negative'] for row in sources),productTestsExecuted=0,newAccepted=0,externalActions=0))
    print(data.sha((target/'manifest.json').read_bytes()))

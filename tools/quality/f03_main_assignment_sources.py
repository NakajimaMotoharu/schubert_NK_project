"""Strict token inverse for two explicit evaluation-order-preserving statement rewrites."""
from collections import Counter
import json
import re
import g07_host_class_provenance_inputs as data
from f03_literal_batch_sources import tokens, out, prior_normal
from f03_literal_batch_diagnostic_v3 import signature
from host_tool_invocation import capture, verify
from trace_owner_join import canonical

OLD = {'INDEX':'descriptors[count++] = descriptor;',
       'LIMIT':'if (++count > MAXIMUM_SOCKET_DIRECTORY_ENTRIES)'}
NEW = {'INDEX':'int ownedPosition = count; count++; descriptors[ownedPosition] = descriptor;',
       'LIMIT':'count++; if (count > MAXIMUM_SOCKET_DIRECTORY_ENTRIES)'}

def inverse(old,new,mapping):
    assert mapping and len({row['kind'] for row in mapping}) == 1
    kind = mapping[0]['kind']
    before,after = tokens(old),tokens(new)
    a,b = tokens(OLD[kind]),tokens(NEW[kind])
    recovered,count,i = [],0,0
    while i < len(after):
        if after[i:i+len(b)] == b:
            recovered.extend(a)
            count += 1
            i += len(b)
        else:
            recovered.append(after[i])
            i += 1
    assert count == len(mapping) and recovered == before
    if kind == 'INDEX':
        assert 'ownedPosition' not in before
    return dict(originalTokens=len(before),rewrittenStatements=count,wholeSourceTokensRecovered=True,
                countUpdateBeforeArrayWrite=True,limitComparedAfterIncrement=True,newLocalEscapes=False)

def negative(old,new,mapping):
    kind = mapping[0]['kind']
    compact = ' '.join(tokens(new))
    variants = [compact.replace('count ++','count --',1),compact+' ;',compact.replace('count ++ ;','',1)]
    if kind == 'INDEX':
        variants += [compact.replace('[ ownedPosition ]','[ count ]',1),
                     compact.replace('int ownedPosition = count ; count ++ ; descriptors [ ownedPosition ] = descriptor ;',
                                     'int ownedPosition = count ; descriptors [ ownedPosition ] = descriptor ; count ++ ;',1)]
    else:
        variants += [compact.replace('count > MAXIMUM_SOCKET_DIRECTORY_ENTRIES','count >= MAXIMUM_SOCKET_DIRECTORY_ENTRIES',1),
                     compact.replace('count ++ ; if ( count > MAXIMUM_SOCKET_DIRECTORY_ENTRIES )',
                                     'if ( count > MAXIMUM_SOCKET_DIRECTORY_ENTRIES ) count ++ ;',1)]
    assert len(set(variants)) == len(variants) == 5
    for value in variants:
        assert value != compact
        try:
            inverse(old,value,mapping)
        except AssertionError:
            pass
        else:
            raise AssertionError('non-equivalent count/index/order/guard accepted')
    return len(variants)

def baseline(cfg,row):
    value = data.read_checked(data.BASE/cfg.MEASUREMENT[0]/'manifest.json',cfg.MEASUREMENT[1])
    assert value['actualExit'] == 0 and value['analysisComplete'] and not value['processingErrors']
    rows = data.read_checked(data.BASE/cfg.MEASUREMENT[0]/'findings.json',value['findingsSha256'])
    selected = [item for item in rows if item['path'] == row['path']]
    assert selected and {item['sourceSha256'] for item in selected} == {row['sha256']}
    return selected,dict(manifest=cfg.MEASUREMENT[0],sha256=cfg.MEASUREMENT[1],currentSourceSha256=row['sha256'],
                         basis='EXACT_CURRENT_MAIN_SOURCE_HASH_AND_COMPLETE_MEASURED_DIAGNOSTICS')

def originals(cfg):
    invocation = capture(__file__)
    target = out(cfg,cfg.ORIGINAL_NUMBER)
    assert not target.exists()
    normal = prior_normal(cfg)
    catalog = json.loads((data.BASE/'PG10690-current-global-static-post-v1/findings.json').read_bytes())
    inventory = json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())
    logical = {row['path']:row for row in inventory['artifacts']}
    ids,refs,_ = cfg.previous_state()
    rows = []
    for path,(pin,chosen,owner,kind) in cfg.PATHS.items():
        text = (data.ROOT/path).read_text()
        assert data.sha(text.encode()) == pin == normal['begin']['inputHashes'][path]
        ownership = canonical(path,logical)
        assert ownership['canonicalOwner'] == ownership['canonicalCostOwner'] == owner
        findings = [row for row in catalog if row['path'] == path]
        selected = [row for row in findings if row['id'] in chosen]
        assert len(selected) == len(chosen) and set(chosen) <= ids-refs
        assert all(row['inputSha256'] == pin and row['rule'] == 'AssignmentInOperand' for row in selected)
        row = dict(path=path,sha256=pin,text=text,findings=findings,mapping=[dict(id=item['id'],kind=kind) for item in selected],**ownership)
        measured,_ = baseline(cfg,row)
        assert all(Counter(signature(r['attributes'],r['message']) for r in measured)[signature(item['attributes'],item['message'])] == 1 for item in selected)
        count = 0
        if kind == 'INDEX':
            assert 'ownedPosition' not in tokens(text)
            new,count = re.subn(re.escape(OLD[kind]),NEW[kind],text)
        else:
            new,count = re.subn(re.escape(OLD[kind]),NEW[kind],text)
        assert count == len(chosen)
        inverse(text,new,row['mapping'])
        row['preEditNegativeVectors'] = negative(text,new,row['mapping'])
        rows.append(row)
    verify(invocation)
    target.mkdir()
    data.write(target/'originals.json',dict(source=cfg.BASE_SOURCE,sources=rows))
    data.write(target/'manifest.json',dict(actualExit=0,source=cfg.BASE_SOURCE,invocation=invocation,
        originalsSha256=data.sha((target/'originals.json').read_bytes()),selectedMainSources=4,selectedDiagnostics=7,
        metadataNegativeVectors=sum(row['preEditNegativeVectors'] for row in rows),productTestsExecuted=0,newAccepted=0,
        externalActions=0,plannedRecord=cfg.RECORD))
    print(data.sha((target/'manifest.json').read_bytes()))

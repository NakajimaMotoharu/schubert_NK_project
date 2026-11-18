"""Rebind the six-module eligible source-only rule evidence with a minimal real delta."""
from datetime import datetime, timezone
from pathlib import Path
import gzip
import json
import runpy
import subprocess
from xml.etree import ElementTree as XML

HERE=Path(__file__).resolve()
P=runpy.run_path(str(HERE.with_name('5129_f03_current_source_lint_join.py')))
BASE=P['B']
ROOT=P['ROOT']
load, ref, sha, git, tree = (P[key] for key in ('load','ref','sha','git','tree'))
HELD=P['HOLD']


def key_for(path):
    label='/'+str(path).lstrip('/')
    offset=label.rfind('/src/schubert-nk-')
    if offset == -1:
        return str(path)
    return label[offset+1:]


def read_report(xml):
    top=XML.parse(xml).getroot()
    assert top.tag=='checkstyle' and not top.findall('.//error')
    paths=[key_for(x.get('name')) for x in top.findall('file')]
    assert len(paths)==len(set(paths))
    return set(paths)


def stage_covers(st, stage, base, stage_label, tools):
    cmd=stage['command']
    assert cmd and stage['actualExit']==0
    assert cmd[0]==str(tools[0])
    if stage_label=='checkstyle':
        assert cmd[cmd.index('-jar')+1]==str(tools[1]) and cmd[cmd.index('-c')+1]==str(tools[2])
    else:
        assert cmd[cmd.index('-jar')+1]==str(tools[3])
        assert all(x in cmd for x in ('--skip-reflowing-long-strings','--dry-run','--set-exit-if-changed'))
    if 'archive' in stage.get('stdout',{}):
        for stream in ('stdout','stderr'):
            v=stage[stream]
            path=Path(v['archive']['path'])
            assert ref(path)==v['archive']
            data=gzip.decompress(path.read_bytes())
            assert sha(data)==v['exactSha256'] and len(data)==v['size']
    else:
        assert stage['timedOut'] is False
        assert P['verify_stream'](base/st,stage)
    return cmd


def normal_receipt(path, m, candidate, tools):
    if m.get('actualExit')!=0 or m.get('checkstyleFindings')!=0:
        return {}
    inputs=m['inputHashes']
    assert sha(tools[2].read_bytes())==inputs[P['RULE']]
    matched={p for p in candidate if inputs.get(p)==candidate[p]}
    if not matched:
        return {}
    xml=path.with_name('checkstyle.xml')
    cs, fm = (m['stages'][x] for x in ('checkstyle','format'))
    for k, result in [('checkstyle',cs),('format',fm)]:
        stage_covers(k,result,path.parent,k,tools)
    formatted={key_for(arg) for arg in fm['command'] if arg.endswith('.java')}
    checked=read_report(xml)
    return {key:dict(receipt=ref(path),checkstyle=ref(xml),sha256=candidate[key],
                     formatChecked=key in formatted) for key in matched & checked if key in formatted or '/src/test/' in key}


def current_receipt(path, m, candidate, tools):
    if m.get('operatorExit')!=0 or not (m['actualExits']['checkstyle']==m['actualExits']['formatter']==0):
        return {}
    begin=load(path.with_name('begin.json'))
    cmd=begin['commands']
    xml=path.with_name('checkstyle.xml')
    terminal={}
    for k in ('checkstyle','formatter'):
        term=path.with_name(k+'-exit.json')
        terminal[k]=load(term)
        assert cmd[k]==terminal[k]['command']
        stage_covers(k,terminal[k],path.parent,k,tools)
    names={key_for(x) for x in cmd['formatter'] if x.endswith('.java')}
    known={key_for(key):(row['sha256'] if isinstance(row,dict) else row)
           for key,row in (begin.get('inputs') or begin['sourceHashes']).items()}
    # Old work-directory projection names match their source basenames. Name+SHA is unique in this delta.
    xml_names={Path(k).name for k in read_report(xml)}
    format_names={Path(n).name for n in names}
    local={Path(k).name:d for k,d in known.items()}
    return {key:dict(receipt=ref(path),checkstyle=ref(xml),sha256=expected,formatChecked=True)
            for key,expected in candidate.items() if local.get(Path(key).name)==expected and
            Path(key).name in xml_names and Path(key).name in format_names}


def run():
    a=next(Path('documents/400_PGPT/470_PMO/601_WBS66短期実行_20261117').glob('528_F03*'))
    v=load(a)['values']
    pins=[Path(p['path']) for p in v['oracleReferences']]
    assert [ref(p) for p in pins]==v['oracleReferences']
    assert git('rev-parse','HEAD').decode().strip()==v['source']
    original=load(pins[0]); orig=original['source']
    assert original['actualExit']==0
    assert original['mainCounts']['currentEligibleConfirmed']==1023 and original['testCounts']['confirmed']==1101
    tools=[Path(row['path']) for row in original['toolInputs']]
    assert [ref(p) for p in tools]==original['toolInputs']
    now={}
    for kind,old_size,new_size in (('main',1027,1027),('test',1133,1134)):
        before,after=(tree(rev,kind) for rev in (orig,v['source']))
        assert len(before)==old_size and len(after)==new_size and before.keys()<=after.keys()
        delta={key for key in after if before.get(key)!=after[key]}
        added=after.keys()-before.keys()
        assert not added or added=={'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/ProcessResourceScopeValueContractTest.java'}
        assert all(Path(key).stem not in HELD and not Path(key).name.startswith('Root') for key in delta)
        now.update({key:sha(git('show',f'{v["source"]}:{key}')) for key in delta})
    assert len(now)==32 and len({Path(path).name for path in now})==32
    recovered={}
    private_errors={}
    for path in reversed(pins[1:]):
        m=load(path)
        choices={key:d for key,d in now.items() if key not in recovered}
        try:
            if 'inputHashes' in m:
                additions=normal_receipt(path,m,choices,tools)
            elif path.parent.name.startswith(('PG39864','PG39865')):
                additions=current_receipt(path,m,choices,tools)
            else:
                additions={}
        except (AssertionError,KeyError,TypeError,ValueError,OSError) as error:
            line=error.__traceback__
            while line.tb_next: line=line.tb_next
            private_errors[path.parent.name]=dict(error=type(error).__name__,line=line.tb_lineno)
            continue
        assert not additions.keys() & recovered.keys()
        recovered.update(additions)
    needs={key:d for key,d in now.items() if key not in recovered}
    out=BASE/v['run']
    out.mkdir()
    def write(name,obj):
        file=out/name
        file.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
        return ref(file)
    before=write('prior-origins.json',dict(oldManifest=ref(pins[0]),reused=recovered,newNeeded=needs,
                                          localReceiptSchemaIneligible=private_errors,hasHeldSourceAction=False))
    additional=P['run_source_checks'](needs,tools,out)
    assert len(recovered)+len(needs)==32
    assert all(recovered[p]['formatChecked'] or '/src/test/' in p for p in recovered)
    result=dict(actualExit=0,source=v['productionCoreMain'],testSource=v['source'],oldSource=orig,
            staticSourceScope='Current six-module eligible source-only policy',currentTypedOrRunMerged=False,
            eligibleMain=1023,allMain=1027,eligibleTest=1102,allTest=1134,heldMain=4,heldTest=32,
            firstMetadataGuardExit=1,firstMetadataGuardReason='one new Batch PT source in 32 changed names',
            changedTrackedCurrent32=len(now),newAnalysedSource=len(needs),reusedExactSource=len(recovered),
            newProductTrials=0,overallF03Accepted=False,overall451Accepted=False,newAcceptance=0,
            priorJoin=before,asNeeded=additional,terminalAtUTC=datetime.now(timezone.utc).isoformat(),verifier=ref(HERE))
    manifest=write('manifest.json',result)
    print(dict(originalReused=len(recovered),newAnalyzed=len(needs),legacyUnusable=len(private_errors),manifest=manifest))


if __name__=='__main__':
    run()

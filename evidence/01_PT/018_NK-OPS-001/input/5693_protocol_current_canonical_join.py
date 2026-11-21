"""Compare present canonical UI/SS tables with independent Protocol fixtures."""

import ast
import json
from pathlib import Path
import re
import subprocess
from datetime import datetime, timezone
import hashlib

ROOT = Path.cwd()
PLAN = next(Path('documents/400_PGPT/470_PMO').glob('601_*'))
OPS = Path('evidence/01_PT/018_NK-OPS-001/evidence')
PROTOCOL = Path('src/schubert-nk-protocol/src/test/resources/protocol')
PARSER = Path('tools/quality/pg3284_protocol_canonical_fixtures.py')


def pin(path):
    return dict(path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def git(*items):
    return subprocess.check_output(['git', *items], timeout=20)


def proof(number, name='manifest.json'):
    return next(OPS.glob(f'PG{number}-*')) / name


def main():
    start = json.loads(next(PLAN.glob('1924_*')).read_bytes())['values']
    head, core, design = (start[k] for k in ('source','productionCoreMain','canonicalDesignSource'))
    assert git('rev-parse','HEAD').decode().strip() == head
    build = json.loads(proof('41304').read_bytes())
    current = json.loads(proof('41394').read_bytes())
    assert build['actualExit'] == current['actualExit'] == 0 and build['ordinaryTests'] == 171
    assert not git('diff','--name-only',build['source'],head,'--','pom.xml','src/schubert-nk-protocol','tools/quality/static')
    ast_source = ast.parse(PARSER.read_bytes(), filename=str(PARSER))
    functions = {'require','numeric','layouts','field_areas','named_types','tsv'}
    constants = {'MACROS','ID','FIELD'}
    declarations = [n for n in ast_source.body
                    if (isinstance(n, ast.FunctionDef) and n.name in functions)
                    or (isinstance(n, ast.Assign) and isinstance(n.targets[0],ast.Name) and n.targets[0].id in constants)]
    assert len(declarations) == len(functions | constants)
    parser = dict(re=re)
    exec(compile(ast.Module(body=declarations,type_ignores=[]),str(PARSER),'exec'),parser)
    canonical = []
    stored = []
    for number in (233,234,235,236,323):
        tree = Path('documents/200_UI/230_インターフェース' if number < 300 else
                    'documents/300_SS/320_メッセージング')
        p = next(tree.glob(f'{number}_*'))
        data = git('show',f'{design}:{p}')
        canonical.append(data.decode())
        stored.append(dict(path=str(p), sha256=hashlib.sha256(data).hexdigest()))
    layout = parser['layouts'](canonical[0])
    fields = {key: vals for key,vals in parser['field_areas'](canonical[1:4]).items() if vals}
    types = parser['named_types'](canonical[4])
    lpath, fpath, tpath = (PROTOCOL / name for name in
                          ('layouts-ui233.tsv','fields-ui234-236.tsv','named-types-ss323.tsv'))
    for p in (lpath,fpath,tpath):
        assert p.read_bytes() == git('show',f'{head}:{p}')
    expected_layouts={key:(kind,direction,*map(int,width))
                       for key,kind,direction,*width in parser['tsv'](lpath)}
    expected_fields={}
    for lid,area,name,begin,size,wire,mandatory,rule in parser['tsv'](fpath):
        expected_fields.setdefault((lid,area),[]).append((name,int(begin),int(size),wire,mandatory,rule))
    expected_types={key:(data,records) for key,data,records in parser['tsv'](tpath)}
    assert layout == expected_layouts and len(layout) == 64
    assert types == expected_types and len(types) == 64
    assert len({v for pair in types.values() for v in pair if v!='-'}) == 69
    assert set(fields) == set(expected_fields) and sum(map(len,fields.values())) == 389
    differences = []
    for key in sorted(fields):
        actual, previous = fields[key], expected_fields[key]
        assert len(actual)==len(previous)
        for a,b in zip(actual,previous,strict=True):
            assert a[:4] == b[:4], (key, a[0])
            if a != b:
                differences.append(dict(layout=key[0],area=key[1],field=a[0],
                                        presenceChanged=a[4]!=b[4],notesChanged=a[5]!=b[5]))
    assert all(d['layout']=='WLGEVT01' and d['field'] in {'Log type','Action'} for d in differences)
    rows = current['scopeRows']
    group_ids = {'WBS-P001-01','WBS-P001-02'}
    selected = [row for row in rows if row['wbsId'] in group_ids]
    actual = json.loads(proof('41304','cases.json').read_bytes())
    known = {(case['className'],case['method']) for case in actual if case['outcome']=='PASS'}
    for row in selected:
        assert all(miss==0 for miss in row['rawMissed'].values())
        assert all((x['className'],x['method']) in known for x in row['testSamples'])
    assert len(selected)==2 and len(known)==171
    out=OPS/'PG41524-current-protocol-canonical-ending-criteria-v1'
    out.mkdir()
    with (out/'manifest.json').open('x',encoding='utf-8') as f:
        json.dump(dict(source=head,core=core,canonicalDesign=design,run=start['run'],actualExit=0,
                       typeMappings=64,distinctTypes=69,layoutRows=64,fieldRows=389,
                       physicalCongruence=True,qa054NonStructuralDiff=differences,
                       canonicalPins=stored,fixtures=list(map(pin,(lpath,fpath,tpath))),parser=pin(PARSER),
                       originalCases=171,caseRoster=pin(proof('41304','cases.json')),
                       scopedEvidence=[dict(wbsId=x['wbsId'],ownedMainFiles=x['ownedMainFiles'],testSamples=x['testSamples'],
                                            measured=x['rawCovered'],missed=x['rawMissed']) for x in selected],
                       priorScope=pin(proof('41394')),whole451=False,formalAcceptanceId=None,
                       newRuns=0,P002Restored=0,terminalAtUTC=datetime.now(timezone.utc).isoformat()),f,ensure_ascii=False,indent=2)
        f.write('\n')
    print('layout 64, fields 389, types 69; approved notation differences',differences)


if __name__ == '__main__':
    main()

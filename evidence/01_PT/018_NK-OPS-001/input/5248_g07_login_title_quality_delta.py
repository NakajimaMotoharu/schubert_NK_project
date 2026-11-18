"""Verify scanner coordinates and the original offline comparator probe for the new interval."""
from pathlib import Path
import json
import re
import runpy
import sys
from xml.etree import ElementTree as ET

HERE=Path(__file__).resolve()
P=runpy.run_path(str(HERE.with_name('5216_g07_scope_build_delta.py')))
E=HERE.parent.parent/'evidence'
START=next(Path('documents/400_PGPT/470_PMO/601_WBS66短期実行_20261117').glob('532_G07*'))
V=json.loads(START.read_bytes())['values']
OUT=E/V['run']/'scan'
WORK=Path(V['volatileStaging'])
RETAIN=Path.cwd().parent/'pgpt-runs/PG379'/V['run'].lower()
HISTORY=('PG39880-g07-service-state-lock-public-delta-v1',
         'PG39840-g07-cleanup-static-and-characterization-delta-v1')
UNIT=E/'PG39904-p020-approved-login-title148-v1'
POST=E/'PG39910-p020-login-title-independent-v1/manifest.json'


def set_worker(worker):
    worker.OUT,worker.START,worker.TEMP,worker.RETAIN=OUT,START,WORK,RETAIN


def classify():
    p=P['load']('g07_login_qualification','5182_g07_jdbc_metrics_cached_classification.py')
    B=p.B
    set_worker(p.t.WRAPPER)
    p.OUT=p.t.OUT=B.OUT=OUT
    p.WORK=p.t.WORK=B.WORK=WORK
    p.t.PREPARE_RUNS=()
    p.t.ORDINARY_BUILD_RUNS=()
    before_ref=p.proven_content

    def old_rows():
        known=set()
        for run in HISTORY:
            manifest=E/run/'scan/manifest.json'
            prior=B.load(manifest)
            assert prior['qualifiedRangeOnly'] and prior['confirmedSecrets']==prior['unresolvedCandidates']==0
            for label in ('classified-findings.json','pinned-sdk-origin.json','additional-build-origins.json'):
                origin=prior['exactPrivateProofFiles'].get(label)
                if origin:
                    f=Path(origin['path'])
                    assert f.is_relative_to(RETAIN.parent) and B.ref(f)==origin
                    for r in B.load(f):
                        if r['ground']:
                            known.add((r['rule'],r['lineSha256'],r['startColumn'],r['endColumn']))
        return known,B.ref(E/HISTORY[0]/'scan/manifest.json')

    def all_binary(original, by_key, unused_scan):
        verified=[]
        for row in original:
            path=Path(row['path'])
            if row.get('actualExit')==0 or path.resolve()!=UNIT/'jacoco.exec':
                continue
            meta=by_key[row['path'],row['blob']]
            unit=B.load(UNIT/'manifest.json')
            start=B.load(UNIT/'begin.json')
            finished=B.load(POST)
            assert start['source']==unit['source']==finished['source']
            assert Path(finished['unit']['path']).resolve()==UNIT/'manifest.json'
            assert finished['unit']['sha256']==B.ref(UNIT/'manifest.json')['sha256']
            assert finished['tests']==unit['expected']==148
            terminal=unit['stages']['execinfo']
            assert terminal==B.load(UNIT/'execinfo-exit.json') and terminal['actualExit']==0
            decoded=Path(terminal['log']['path'])
            assert decoded==UNIT.relative_to(Path.cwd())/'execinfo.log' or decoded==UNIT/'execinfo.log'
            assert B.ref(decoded)==terminal['log']
            assert terminal['command'][-2:]==['execinfo',str((UNIT/'jacoco.exec').resolve())]
            assert meta['blobSha256']==B.ref(WORK/meta['relativeProjection'])['sha256']==B.ref(path)['sha256']
            root=ET.parse(UNIT/'xml/TEST-junit-jupiter.xml').getroot()
            assert len(list(root.iter('testcase')))==148
            assert not any(n.tag in ('failure','error','skipped') for n in root.iter())
            text=decoded.read_text()
            assert re.findall(r'^Session "([^"]+)":',text,re.M)==[unit['session']]
            rows=re.findall(r'^([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(\S+)$',text,re.M)
            assert any(n=='dev/codex/schubert/characterization/ArtifactComparator' and int(hit)>0 for _,hit,_,n in rows)
            assert not any(n.startswith(('dev/codex/schubert/nk/','org/postgresql/','com/microsoft/playwright/')) for _,_,_,n in rows)
            verified.append(dict(row,actualExit=0,originalUnitExit=0,ordinaryProbeDataOnly=True,
                                 decodedOrigin=terminal['log'],qualifiedOriginal=B.ref(POST),
                                 session=unit['session'],decodedRows=len(rows),toolExecutionRepeated=False))
        return verified

    p.exact_previous=old_rows
    p.t.extra_binary=all_binary
    p.proven_content=before_ref
    p.main()


def retain():
    p=P['load']('g07_login_retain','5184_g07_jdbc_metrics_retain_compact.py')
    set_worker(p.w)
    value=p.p.load(OUT/'qualified-cached-initial.json')
    assert value['unresolvedCandidates']==value['unqualifiedBinary']==0
    p.p.write(OUT/'qualified-final-private-detail.json',dict(value,verifier=p.p.ref(HERE),scannerExecutionCount=1,initialClassificationExit=1,initialIssue='Exact archived path was relative instead of absolute'))
    p.DETAILS=('scan-terminal.json','qualified-cached-initial.json','qualified-final-private-detail.json',
               'classified-findings.json','remaining-origins.json','binary-qualification.json')
    p.main()


if __name__=='__main__':
    {'classify':classify,'retain':retain}[sys.argv[1]]()

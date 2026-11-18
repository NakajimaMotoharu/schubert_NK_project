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
CONFIG = {
    '532': {
        'history': ('PG39880-g07-service-state-lock-public-delta-v1',
                    'PG39840-g07-cleanup-static-and-characterization-delta-v1'),
        'units': {'PG39904-p020-approved-login-title148-v1': ('unit', 148)},
        'post': 'PG39910-p020-login-title-independent-v1',
    },
    '536': {
        'history': ('PG39914-g07-approved-login-title-and-quality-delta-v1',
                    'PG39880-g07-service-state-lock-public-delta-v1',
                    'PG39840-g07-cleanup-static-and-characterization-delta-v1'),
        'units': {'PG39922-p020-approved-all-brand153-v1': ('firstUnit', 153),
                  'PG39923-p020-approved-all-brand153-v2': ('unit', 153)},
        'post': 'PG39928-p020-approved-all-brand-independent-v1',
    },
    '542': {
        'history': ('PG39932-g07-four-brand-public-delta-v1',
                    'PG39914-g07-approved-login-title-and-quality-delta-v1',
                    'PG39880-g07-service-state-lock-public-delta-v1'),
        'units': {'PG39944-p020-cache-and-session161-v1': ('unit', 161),
                  'PG39964-p020-invalid-range165-v1': ('firstUnit', 165),
                  'PG39965-p020-invalid-range165-v2': ('unit', 165)},
        'posts': {'PG39944-p020-cache-and-session161-v1': 'PG39954-p020-cache-and-session-independent-v1',
                  'PG39964-p020-invalid-range165-v1': 'PG39970-p020-invalid-range-independent-v1',
                  'PG39965-p020-invalid-range165-v2': 'PG39970-p020-invalid-range-independent-v1'},
    },
    '551': {
        'history': ('PG39974-g07-cache-session-range-public-delta-v1',
                    'PG39932-g07-four-brand-public-delta-v1',
                    'PG39914-g07-approved-login-title-and-quality-delta-v1',
                    'PG39880-g07-service-state-lock-public-delta-v1',
                    'PG39730-g07-weblog-session-and-comparator-public-delta-v1'),
        'units': {'PG39990-p020-search-empty170-v1': ('unit', 170)},
        'post': 'PG39994-p020-search-empty-independent-v1',
    },
}
GROUP=sys.argv[2] if len(sys.argv)==3 else '532'
settings=CONFIG[GROUP]
START=next(Path('documents/400_PGPT/470_PMO/601_WBS66短期実行_20261117').glob(GROUP+'_G07*'))
V=json.loads(START.read_bytes())['values']
OUT=E/V['run']/'scan'
WORK=Path(V['volatileStaging'])
RETAIN=Path.cwd().parent/'pgpt-runs/PG379'/V['run'].lower()
HISTORY=settings['history']



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
            name=path.parent.name
            if row.get('actualExit')==0 or name not in settings['units'] or path.name!='jacoco.exec':
                continue
            unit_folder=E/name
            assert path.resolve()==unit_folder/'jacoco.exec'
            ticket,expected=settings['units'][name]
            meta=by_key[row['path'],row['blob']]
            unit=B.load(unit_folder/'manifest.json')
            start=B.load(unit_folder/'begin.json')
            post=E/(settings.get('post') or settings['posts'][name])/'manifest.json'
            finished=B.load(post)
            assert start['source']==unit['source']
            assert Path(finished[ticket]['path']).resolve()==unit_folder/'manifest.json'
            assert finished[ticket]['sha256']==B.ref(unit_folder/'manifest.json')['sha256']
            assert finished['tests']==unit['expected']==expected
            if ticket=='unit':
                assert unit['source']==finished['source']
            else:
                assert unit['source']!=finished['source']
                typed_failure=finished.get('firstStaticNonzero')
                static_failure=typed_failure or finished['firstStaticFailure']
                prior_static=Path(static_failure['path'])
                assert B.ref(prior_static)==static_failure
                static_result=B.load(prior_static)
                if typed_failure:
                    assert static_result['stageExits']['spotbugs']==1
                else:
                    assert static_result['stageExits']['pmd']==4 and static_result['reports']['pmd']['findings']==8
            terminal=unit['stages']['execinfo']
            assert terminal==B.load(unit_folder/'execinfo-exit.json') and terminal['actualExit']==0
            decoded=Path(terminal['log']['path'])
            assert decoded==unit_folder.relative_to(Path.cwd())/'execinfo.log' or decoded==unit_folder/'execinfo.log'
            assert B.ref(decoded)==terminal['log']
            assert terminal['command'][-2:]==['execinfo',str((unit_folder/'jacoco.exec').resolve())]
            assert meta['blobSha256']==B.ref(WORK/meta['relativeProjection'])['sha256']==B.ref(path)['sha256']
            root=ET.parse(unit_folder/'xml/TEST-junit-jupiter.xml').getroot()
            assert len(list(root.iter('testcase')))==expected
            assert not any(n.tag in ('failure','error','skipped') for n in root.iter())
            text=decoded.read_text()
            assert re.findall(r'^Session "([^"]+)":',text,re.M)==[unit['session']]
            rows=re.findall(r'^([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(\S+)$',text,re.M)
            assert any(n=='dev/codex/schubert/characterization/ArtifactComparator' and int(hit)>0 for _,hit,_,n in rows)
            assert not any(n.startswith(('dev/codex/schubert/nk/','org/postgresql/','com/microsoft/playwright/')) for _,_,_,n in rows)
            verified.append(dict(row,actualExit=0,originalUnitExit=0,ordinaryProbeDataOnly=True,
                                 decodedOrigin=terminal['log'],qualifiedOriginal=B.ref(post),
                                 session=unit['session'],decodedRows=len(rows),toolExecutionRepeated=False,
                                 priorStaticFailureRemains=ticket!='unit'))
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
    original=p.p.load(RETAIN/'initial-classification'/'qualified-cached-initial.json') if GROUP=='551' else None
    if original:
        assert original['unresolvedCandidates']==1 and original['unqualifiedBinary']==0
    p.p.write(OUT/'qualified-final-private-detail.json',dict(
        value,verifier=p.p.ref(HERE),scannerExecutionCount=1,initialClassificationExit=int(GROUP=='532'),
        initialIssue='Exact archived path was relative instead of absolute' if GROUP=='532' else None,
        initialSetupExit=int(GROUP=='551'),
        initialSetupIssue='Public run directory parent was absent before scanner start' if GROUP=='551' else None,
        firstUnclassified=original['unresolvedCandidates'] if original else None,
        firstClassification=tuple(p.p.ref(f) for f in sorted((RETAIN/'initial-classification').iterdir())) if original else ()))
    p.DETAILS=('scan-terminal.json','qualified-cached-initial.json','qualified-final-private-detail.json',
               'classified-findings.json','remaining-origins.json','binary-qualification.json')
    p.main()


if __name__=='__main__':
    {'classify':classify,'retain':retain}[sys.argv[1]]()

"""Prove all nine compile-time JDBC strings, the unchanged oracle, and current raw quality."""
from datetime import datetime, timezone
from pathlib import Path
import gzip
import hashlib
import json
import re
import subprocess
from xml.etree import ElementTree as ET

B = Path('evidence/01_PT/018_NK-OPS-001')
E = B / 'evidence'
H = Path('documents/400_PGPT/470_PMO/601_WBS66短期実行_20261117')
START = H / '500_F03固定SQL切替の是正開始.json'
CFG = B / 'input/5219_cleanup_fixed_statement_profile.json'
OUT = E / 'PG39802-cleanup-fixed-statement-raw-v1'
FOUR = E / 'PG39804-cleanup-fixed-statement-four-main-v1/compile/manifest.json'
OLD = E / 'PG39764-process-resource-scope-four-main-v1/compile/manifest.json'
Q = 'dev/codex/schubert/nk/batch/repository/CleanupRepository'
S = Q.replace('CleanupRepository', 'CleanupStepRepository')
ROOT = Path.cwd()
JAVAP = ROOT.parent / 'toolchain/jdk-25.0.4/bin/javap'
PREFIX = 'select target_count,deleted_count,skipped_count,reason_code from '


def sha(data):
    return hashlib.sha256(data).hexdigest()


def ref(path):
    return dict(path=str(path), sha256=sha(path.read_bytes()))


def read(path):
    return json.loads(Path(path).read_bytes())


def git(*args):
    return subprocess.check_output(['git', *args], timeout=30)


def write(path, value):
    with path.open('x') as f:
        json.dump(value, f, indent=2, ensure_ascii=False)
        f.write('\n')


def javap(path, *opts):
    return subprocess.check_output([str(JAVAP), *opts, str(path)], timeout=10).decode()


def source_and_statement_identity(c, start, post, old_class, new_class):
    repo = next(Path(name) for name in c['mainSources'] if name.endswith('/CleanupRepository.java'))
    base = start['values']['productionCoreMain']
    fixed = post['source']
    old=git('show',f'{base}:{repo}').decode()
    new=git('show',f'{fixed}:{repo}').decode()
    assert new==repo.read_text()
    org = {kind:sql for kind,sql in
        re.findall(r'case ([A-Z_]+) ->\s+connection.prepareStatement\(\s*"([^"]+)"\);',old)}
    table = {kind:PREFIX+suffix for kind,suffix in re.findall(
        r'CleanupKind\.([A-Z_]+),\s*c ->\s+c.prepareStatement\(\s*CLEANUP_COUNTS \+ "([^"]+)"\)',new)}
    assert org==table and len(table)==9
    # The package's nine test-only suffix constants do not read production SQL.
    test = next(Path(row['path']) for row in c['testSources'] if row['path'].endswith('/CleanupQueryPortTest.java'))
    fixture = test.read_text()
    expect = {kind:PREFIX+f'schubert.maintenance_cleanup_{suffix}(?,?,?)'
               for kind,suffix in re.findall(r'CleanupKind\.([A-Z_]+),\s*"([a-z_]+)"',
                    fixture[fixture.index('SUFFIXES ='):fixture.index('PROGRESS_SQL =')])}
    assert expect==table
    assert 'fixture.sql' in fixture and 'fixture.assertClosed();' in fixture
    def remove_dispatch(text):
        begin=text.index('  private PreparedStatement prepare(CleanupKind kind)')
        end=text.index('  private static void closeRow',begin)
        return text[:begin]+text[end:]
    inverse=remove_dispatch(new).replace('import java.util.Map;\n','')
    begin=inverse.index('  private static final String CLEANUP_COUNTS')
    end=inverse.index('  private final Connection connection;',begin)
    assert inverse[:begin]+inverse[end:]==remove_dispatch(old)
    for row in c['testSources']:
        item=Path(row['path'])
        assert git('show',f'{base}:{item}')==git('show',f'{fixed}:{item}')==item.read_bytes()
    code=javap(new_class,'-p','-c')
    strings=re.findall(r'// String (select target_count,deleted_count,skipped_count,reason_code from [^\r\n]+)',code)
    assert len(strings)==9 and set(strings)==set(expect.values())
    assert 'makeConcatWithConstants' not in code and '$SwitchMap$' not in code
    assert code.count('InterfaceMethod java/sql/Connection.prepareStatement:')==10
    assert javap(old_class,'-public','-s')==javap(new_class,'-public','-s')
    return dict(main=ref(repo),unchangedMethodsOutsideDispatch=True,originalFixedSqlBytes=table,
                independentFixture=ref(test),compiledLiteralBindings=9,publicAbiEqual=True)


def raw_and_tests(post,p,post_path):
    raw_path=OUT/'raw.tsv'
    rows=[row.split('\t') for row in raw_path.read_text().splitlines()]
    def counters(row):
        return {key:dict(missed=int(miss),covered=int(hit))
                for key,miss,hit in (text.split(':') for text in row[6:])}
    raw={row[1]:counters(row) for row in rows if row[0]=='CLASS'}
    assert {name+'.class' for name in raw}==set(p['physicalClassHashes']) and len(raw)==21
    assert raw[Q]=={key:dict(missed=0,covered=n) for key,n in
        dict(INSTRUCTION=403,BRANCH=22,LINE=102,COMPLEXITY=31,METHOD=20,CLASS=1).items()}
    assert all(v['missed']==0 for v in raw[S].values())
    assert Q+'$1' not in raw and all(v['missed']==v['covered']==0 for v in raw[Q+'$StatementFactory'].values())
    assert not [row for row in rows if row[0]=='DEFICIT' and row[1] in (Q,S)]
    assert len({x[2] for x in rows if x[0]=='METHOD' and x[1]==Q and x[2].startswith('lambda$static$')})==9
    xml=post_path.with_name('original-TEST-junit-jupiter.xml')
    assert ref(xml)['sha256']==post['files'][xml.name]
    root=ET.parse(xml).getroot()
    cases=root.findall('testcase')
    assert len(cases)==len({(x.get('classname'),x.get('name')) for x in cases})==18
    assert not any(ch.tag in {'failure','error','skipped'} for case in cases for ch in case)
    assert any(x.get('name')=='allNineFixedQueriesBindOnlyLiteralUuidUtcCutoffAndIntegerLimit()' for x in cases)
    return dict(raw=ref(raw_path),target={k:raw[k] for k in (Q,S)},xml=ref(xml),
         noCodeFactory=True,support={k:v for k,v in raw.items() if k not in (Q,S) and any(r['missed'] for r in v.values())})


def main():
    start=read(START); c=read(CFG)
    proofs={k:Path(v)/'manifest.json' for k,v in c['slots'].items()}
    post,unit,prepare,static,preflight=(read(proofs[key]) for key in ('post','unit','prepare','static','preflight'))
    assert unit['actualExit']==post['actualExit']==0 and unit['tests']==post['tests']==18
    assert not any(unit[key] for key in ('failures','errors','skipped'))
    assert post['source']==unit['begin']['source'] and post['productionCoreMain']==c['productionCoreMain']
    assert post['oldExecCombined'] is False and post['manualCoverageExclusions']==[]
    assert post['actualBackendNativeFsRootOrHeldClassActions']==0
    assert len(static['rawFindings'])==len(preflight['classified'])==44
    assert all(preflight[x]==0 for x in ('staticApplicable','unclassified','checkstyle','spotbugs','processingErrors'))
    old,build=read(OLD),read(FOUR)
    assert build['actualExit']==0 and build['inputHashesReverified'] and build['sourceCore']==c['productionCoreMain']
    assert build['baselineSource']==old['sourceCore']
    assert sum(len(rows) for rows in build['physicalClassHashes'].values())==1101
    target=Q+'.class'; former=Q+'$1.class'; factory=Q+'$StatementFactory.class'
    assert build['deltas']['batch']==dict(added=[factory],removed=[former],changed=[target])
    assert all(not any(row.values()) for mod,row in build['deltas'].items() if mod!='batch')
    paths=[Path(m['cwd'])/'src/schubert-nk-batch/target/classes'/target for m in (old,build)]
    assert all(ref(path)['sha256']==m['physicalClassHashes']['batch'][target]
               for m,path in zip((old,build),paths,strict=True))
    for name in (target,factory):
        assert build['physicalClassHashes']['batch'][name]==prepare['physicalClassHashes'][name]
    proof=source_and_statement_identity(c,start,post,*paths)
    counters=raw_and_tests(post,prepare,proofs['post'])
    archives=[]
    for logfile,digest in build['logs'].items():
        data=FOUR.with_name(logfile).read_bytes()
        assert sha(data)==digest
        archive=OUT/(logfile+'.gz')
        with archive.open('xb') as f:
            f.write(gzip.compress(data,mtime=0))
        archives.append(dict(originalPath=str(FOUR.with_name(logfile)),originalSha256=digest,archived=ref(archive)))
    m=dict(actualExit=0,startEvent=start['eventId'],source=post['source'],
       productionCoreMain=c['productionCoreMain'],run=post['run'],tests=18,failures=0,errors=0,skipped=0,notRun=0,
       firstSuccessful=18,newTestDefinitions=0,sourceAndSql=proof,measurement=counters,
       build=ref(FOUR),originalFourInputs=490,startBuildProof=ref(OLD),buildArchives=archives,
       exactByteUniverse=1101,unchangedPhysical1099=True,compiledSqlPhysicalChanged=1,
       staticRawPreviouslyClassified=44,staticApplicable=0,oldWholeReplayedOnlyAfterNewSource=True,
       physicalGenerationRemoved=former,naturalNoCodeInterface=factory,
       manualExclusions=0,oldExecCombined=False,newAcceptance=0,whole451Accepted=False,
       absoluteScopeNativeOrDatabaseActions=0,proofs={k:ref(v) for k,v in proofs.items()},
       terminalAtUTC=datetime.now(timezone.utc).isoformat(),verifier=ref(Path(__file__)))
    write(OUT/'manifest.json',m)
    print(ref(OUT/'manifest.json'))


if __name__=='__main__':
    main()

"""Program-scoped manifest joining original source, specification, actual tests and open whole-quality conditions."""
import datetime as dt
from pathlib import Path
import platform
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from source_evidence_binding import bind

OUT = data.BASE/'PG10962-form-literal-completion-v1'
SOURCE = 'e7c2e2c89c41dcfced875a7fd480e6fc96da0ca6'
PINS = {
    'normal':('PG10950-form-literal-six-compile-v1','4cd53877ce16c93b44af747c29afdace410d2dc1ce7fec7eb5ebd48a67093baf'),
    'originalPt':('PG10954-form-literal-host-v1','8ca9f8c7b48966e1c1d8120b654cabb88efe5a21c2e257e63d1dc06b6c38d54a'),
    'post':('PG10956-form-literal-post-v1','6982240ef677049a33d34597bf14d134b56137afd0bb394132d1f56f6e6de906'),
    'trace':('PG10958-form-literal-trace-v1','77e58f6f185a0baebb4c22eb0a4a81bb9af802d7a30d370d46f79698e7da30db'),
    'tracePost':('PG10960-form-literal-trace-post-v1','423a0d6ec88eae246c4bc986a10630774cea8bed6f9fa5924596ea25320bca9f')}


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    bound = bind([(data.BASE/folder/'manifest.json',sha) for folder,sha in PINS.values()],SOURCE)
    manifests = {k:data.read_checked(data.BASE/folder/'manifest.json',sha) for k,(folder,sha) in PINS.items()}
    normal,host,post = (manifests[k] for k in ('normal','originalPt','post'))
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())
    static_path = data.BASE/'PG10952-form-literal-static-v1/manifest.json'
    static_sha = '1867bf0302e96d03904faa3d800761182628e4ea6be97782f9a436a14f4e37f1'
    static = data.read_checked(static_path,static_sha)
    assert static['actualExit'] == 1 and static['source'] == SOURCE
    specification = data.ROOT/'evidence/01_PT/016_NK-WEB-002/110_検索form二Test十三fixture同値化PGPT仕様.md'
    measurement_path = data.BASE/PINS['post'][0]/'measurement.json'
    measured = data.read_checked(measurement_path,post['measurementSha256'])
    form_units = {k:v for k,v in measured['units'].items() if '/form/' in k and
        (k.rpartition('/')[2].startswith('LogSearchForm') or k.rpartition('/')[2].startswith('ScenarioSearchForm'))}
    assert len(form_units) == 6 and all(c['missed'] == 0 for v in form_units.values() for c in v['counters'].values())
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,programId='NK-WEB-002',invocation=invocation,
        recordedUTC=dt.datetime.now(dt.timezone.utc).isoformat(),hostOs=platform.platform(),
        branch=subprocess.check_output(['git','branch','--show-current'],cwd=data.ROOT,text=True).strip(),
        operatorHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=data.ROOT,text=True).strip(),
        specificationPath=str(specification.relative_to(data.ROOT)),specificationSha256=data.sha(specification.read_bytes()),
        relatedBugs=['BUG-1884','BUG-1885'],relatedYkt=['YKT-1635','YKT-1636'],relatedSsc=['SSC-072','SSC-073'],
        boundOriginalRuns=bound,sourceChangeCommit=SOURCE,tests=host['begin']['cases'],
        originalCommandsAndToolEnvironmentReference=str((data.BASE/PINS['originalPt'][0]/'manifest.json').relative_to(data.ROOT)),
        expected='Original independent PT-WEB214..221 and PT-WEB278..285 literals/assertions retained by token inverse; F/E/S/aborted0',
        actual=dict(tests=16,suites=2,failures=0,errors=0,skipped=0,aborted=0),
        selectedFormMainUnits=form_units,selectedFormFourCounters100=True,
        completeWebCounters=post['bundleCounters'],completeWebFourCounters100=False,
        rawStaticManifest=str(static_path.relative_to(data.ROOT)),rawStaticManifestSha256=static_sha,
        rawStaticExit=1,rawPmd=4,localThreadContextReviewed=4,checkstyle=0,processingErrors=0,
        productTestsExecutedByCompletion=0,newAccepted=0,formal1964Scope53Unchanged=True,individualAccepted=17,
        individualTotal=190,effortPercent=None,qa051Final='HOLD',whole451Accepted=False,
        externalActions=0,oldRuntimeReassigned=False,secretScanScope='Separate explicit public delta; not wholeG07'))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()

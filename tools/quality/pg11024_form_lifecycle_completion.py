"""Final remaining-form program manifest joining original source, specification, actual tests and open whole-quality conditions."""
import datetime as dt
from pathlib import Path
import platform
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from source_evidence_binding import bind

OUT = data.BASE/'PG11024-form-lifecycle-completion-v1'
SOURCE = '9c37bc73a20bab2028413db2c08f6bbdf28c76a6'
PINS = {
    'normal':('PG11008-form-close-assert-six-compile-v1','5150b4e1aceb6ac51c8a38d253108f6729307cd7df77253b8a37f2c44426ea63'),
    'originalPt':('PG11010-form-close-assert-host-v1','f01bd332c206ff4d3a605f901905a4b7c261d21eb65e60e8cac271b6f092ead1'),
    'post':('PG11014-form-close-assert-post-v1','c5272833fa8e1597c93ee20fd5b2bc8fa382ddc9a82e1649108298e78d1caeaa'),
    'trace':('PG11020-form-lifecycle-trace-v1','5d58d536e3162b19421055f087b865af67efde8aa9644695cfa120c24f294bdb'),
    'contexts':('PG11016-form-remaining-context-v1','0d166f417ef583245eabbf1ae58702fbc777a9162f41aaf41ae5f22d54246f51'),
    'contextsPost':('PG11018-form-remaining-context-post-v1','cf7b7c88c64f9a04eafab135b022b05eeb2f2b08538e77ea52a943518ffb7947'),
    'tracePost':('PG11022-form-lifecycle-trace-post-v1','537f4db8e23cdf0b2ac566bccb0092e9b37c6ec12e8447a8c29f230855ce656f')}


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    bound = bind([(data.BASE/folder/'manifest.json',sha) for folder,sha in PINS.values()],SOURCE)
    manifests = {k:data.read_checked(data.BASE/folder/'manifest.json',sha) for k,(folder,sha) in PINS.items()}
    normal,host,post = (manifests[k] for k in ('normal','originalPt','post'))
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())
    static_path = data.BASE/'PG11012-form-close-assert-static-v1/manifest.json'
    static_sha = 'd642c529b96c8cac73372108e5ea6423cf829e5ea8923badae39fffe04be5df0'
    static = data.read_checked(static_path,static_sha)
    assert static['actualExit'] == 1 and static['source'] == SOURCE
    specification = data.ROOT/'evidence/01_PT/016_NK-WEB-002/112_残四form二十七fixture同値化PGPT仕様.md'
    measurement_path = data.BASE/PINS['post'][0]/'measurement.json'
    measured = data.read_checked(measurement_path,post['measurementSha256'])
    form_units = measured['selectedFormMain']
    assert len(form_units) == 10 and all(c['missed'] == 0 for v in form_units.values() for c in v['counters'].values())
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,programId='NK-WEB-002',invocation=invocation,
        recordedUTC=dt.datetime.now(dt.timezone.utc).isoformat(),hostOs=platform.platform(),
        branch=subprocess.check_output(['git','branch','--show-current'],cwd=data.ROOT,text=True).strip(),
        operatorHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=data.ROOT,text=True).strip(),
        specificationPath=str(specification.relative_to(data.ROOT)),specificationSha256=data.sha(specification.read_bytes()),
        relatedBugs=['BUG-1886','BUG-1887','BUG-1888'],relatedYkt=['YKT-1637','YKT-1638','YKT-1639'],relatedSsc=[],
        boundOriginalRuns=bound,sourceChangeCommit=SOURCE,tests=host['begin']['cases'],
        originalCommandsAndToolEnvironmentReference=str((data.BASE/PINS['originalPt'][0]/'manifest.json').relative_to(data.ROOT)),
        expected='Original independent CREATE8/CHANGE16/TARGET8/QSTFORM8 byte goldens retained; exact added lifecycle assertions; F/E/S/aborted0',
        actual=dict(tests=40,suites=4,failures=0,errors=0,skipped=0,aborted=0),
        selectedFormMainUnits=form_units,selectedFormFourCounters100=True,
        completeWebCounters=post['bundleCounters'],completeWebFourCounters100=False,
        rawStaticManifest=str(static_path.relative_to(data.ROOT)),rawStaticManifestSha256=static_sha,
        rawStaticExit=1,rawPmd=12,localThreadContextReviewed=8,localResourceOwnerContextsReviewed=4,checkstyle=0,processingErrors=0,
        productTestsExecutedByCompletion=0,newAccepted=0,formal1964Scope53Unchanged=True,individualAccepted=17,
        individualTotal=190,effortPercent=None,qa051Final='HOLD',whole451Accepted=False,
        externalActions=0,oldRuntimeReassigned=False,secretScanScope='Separate explicit public delta; not wholeG07'))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()

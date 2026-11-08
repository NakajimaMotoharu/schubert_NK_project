"""Canonical no-argument original whole Stub5; memory-only Main and new own public output."""
from pathlib import Path
import hashlib,json,sys
import scoped_prometheus_host as run
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
R=Path(__file__).resolve().parents[2];B=R/'evidence/01_PT/018_NK-OPS-001';RUNS=R.parent/'pgpt-runs/PG379';load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert len(sys.argv)==1
PREFLIGHT=B/'evidence/PG24888-stub-owner-canonical-entry-preflight-v1/manifest.json';pf=load(PREFLIGHT);assert pf['actualExit']==0 and pf['entrypointPath']==str(Path(__file__).relative_to(R)) and pf['entrypointSha256']==sha(Path(__file__))
pre=load(R/pf['prepare']['path']);assert sha(R/pf['prepare']['path'])==pf['prepare']['sha256'];app=load(R/pf['staticApplicability']['path']);assert sha(R/pf['staticApplicability']['path'])==pf['staticApplicability']['sha256'] and app['applicableViolations']==0
TEST=R/pre['testPath'];HELPER=R/pre['launcherPath'];REPORTER=R/'tools/quality/architecture/SharedSelectedJunitReporterV1.java';assert sha(TEST)==pre['testSha256'] and sha(HELPER)==pre['launcherSha256'] and sha(REPORTER)==pre['reporterSha256']
run.SOURCE='7aed8eace7c844c2f79f2e39db766faf914890d5';run.COMPILE=RUNS/'pg22084-api-stop-state-six-main-compile-v1';run.COMPILE_SHA='b2f07209804d71ee2ffbc4d9aca5311d4e6cf15721c74bcde411f86538cf4f27';run.SLOT=RUNS/'pg24872-stub-owner-original-whole5-v1';run.OUT=B/'evidence/PG24872-stub-owner-original-whole5-v1';run.HELPER=HELPER;run.NEW_TEST=TEST;run.TEST_ROOT=TEST.parent;run.TEST_SOURCE_OVERRIDES={};run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES={};run.COUNTS={'StubAnswerProviderTest':5};run.SESSION_ID='PG24872-STUB-ORIGINAL-WHOLE5'
def locale_step(name,command):
 if name=='selected-junit':command=[command[0],'-Duser.language=ja','-Duser.country=JP',*command[1:]]
 return environmental_step(name,command)
run.step=locale_step
try:run.main()
except SystemExit as terminal:
 if terminal.code!=0:raise
expected='provider=STUB\nanswerLength=0\nclockReadsPerCall=1\nconcurrentCalls=64\nuniqueClockValues=64\nexternalCalls=0\nrawBodySaved=false\n';p=run.SLOT/'target/question-stub-traces/PT-ASY-STB005.txt';assert p.read_bytes()==expected.encode('ascii') and not p.is_symlink();(run.OUT/'PT-ASY-STB005.txt').write_bytes(p.read_bytes());(run.OUT/'public-output.safe.json').write_text(json.dumps(dict(actualExit=0,path='target/question-stub-traces/PT-ASY-STB005.txt',sha256=sha(p),bytes=len(expected),independentLiteralMatches=True,productFileOperations=False,testOwnNewSlotPublicEvidenceWrites=True),indent=2)+'\n')

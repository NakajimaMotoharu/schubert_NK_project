"""Four explicit whole pure exception inputs; independent new JVMs, never runtime operations."""
import re
from types import SimpleNamespace
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
from pg14647_storage_catalog_whole_five_pt_v2 import source_operation_allowed,source_prevention
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
ROWS={
 'logging':('Logging','d8c183c953e82790dfa4faf59f0876c455030d21dbae2c3ab138058a619a942c','WebLogPayloadException','a040ed22b820dccdb7da66a7af28dcdc1ea0a43c295aae150202090daac127df','WBS-P006-04'),
 'revocation':('Revocation','81821dab9739a8c0694d2a4bceeae4484e898af51c2d4e549bb49a6cc9dddce5','RevocationPayloadException','b348ae32f6c4294a3e708b590fe46499386a0f1b516f7171d45574edc050ecf0','WBS-P015-05'),
 'media':('Media','7321e5c2dfcbb5bc338aeb0fdb1a54368663266a05bed49b21b7ccdb9f7ef4cb','MediaDeliveryException','1b67c19a97f0cd35f193bc38ad1e155a4691f54ce6ad0c58d9bb37728cc77585','WBS-P009-04'),
 'session':('Session','4abcd944b96516b892874227b1ab50d72695631c21df32cfc3c4750a87a11f4a','SessionPayloadException','93cef186b470be817f36dff0f390ee5b71a3f2b2a0299dac5c694e16b8bf374e','WBS-P015-01')}
REPORTER=run.host.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
OUT=data.BASE/'PG14726-web-four-exception-originals-v2'

def original(package):
    if not isinstance(package,str) or package not in ROWS:raise ValueError('explicit reviewed package only')
    root=data.ROOT/'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web'/package
    return SimpleNamespace(SOURCE=SOURCE,COMPILE=COMPILE,COMPILE_SHA=COMPILE_SHA,ROOT=root,TESTS={'ExceptionValueContractTest':root/'ExceptionValueContractTest.java'},COUNTS={'ExceptionValueContractTest':1},FIXTURES={},SESSION='PG14726-ORIGINAL-WEB-'+package.upper()+'-EXCEPTION1')

def folders(package):
    original(package)
    return 'PG14726-web-'+package+'-exception-one-pt-v2','PG14728-web-'+package+'-exception-one-post-v2'

def main():
    invocation=capture(__file__);assert not OUT.exists()
    negatives=[]
    for bad in ['security','../session','',None,'media/alias']:
        try:original(bad)
        except ValueError:negatives.append(bad)
        else:raise ValueError('unknown package admitted')
    assert len(negatives)==5 and source_prevention()==6
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    for package,(title,pin,_,_,_) in ROWS.items():
        info=original(package);p=info.TESTS['ExceptionValueContractTest'];relative=str(p.relative_to(data.ROOT))
        assert relative=='src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/'+package+'/ExceptionValueContractTest.java'
        assert run.host.sha(p)==normal['begin']['inputHashes'][relative]==run.host.sha(COMPILE/'snapshot'/relative)==pin
        text=p.read_text();assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text))==1 and source_operation_allowed(text)
        launcher=data.ROOT/'tools/quality/architecture'/('OriginalWeb'+title+'ExceptionJunitLauncher.java')
        assert '"dev.codex.schubert.nk.web.'+package+'.ExceptionValueContractTest", 1' in launcher.read_text()
        raw,_=folders(package);assert not (data.BASE/raw).exists() and not (run.host.W/raw.lower()).exists()
    records={}
    for package,(title,_,_,_,_) in ROWS.items():
        info=original(package);raw,_=folders(package)
        run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA;run.SLOT=run.host.W/raw.lower();run.OUT=data.BASE/raw
        run.HELPER=data.ROOT/'tools/quality/architecture'/('OriginalWeb'+title+'ExceptionJunitLauncher.java')
        run.NEW_TEST=info.TESTS['ExceptionValueContractTest'];run.TEST_ROOT=info.ROOT;run.TEST_SOURCE_OVERRIDES={};run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES={};run.COUNTS=info.COUNTS;run.SESSION_ID=info.SESSION;run.step=environmental_step
        try:run.main()
        except SystemExit as terminal:
            if type(terminal.code) is not int or terminal.code!=0:raise
        path=data.BASE/raw/'manifest.json';value=data.read_checked(path,data.sha(path.read_bytes()))
        assert value['actualExit']==0 and len(value['cases'])==1 and value['cases'][0]['classname']=='dev.codex.schubert.nk.web.'+package+'.ExceptionValueContractTest'
        records[package]=dict(folder=raw,sha256=data.sha(path.read_bytes()),tests=1,source=SOURCE)
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,originalRuns=records,originalMethods=4,originalSuites=4,originalProductJvms=4,packagePositiveChecks=4,packageNegativeChecks=len(negatives),bug='BUG-2110',ykt='YKT-1857',oldDraftToolsExecuted=False,oldSuccessReexecuted=False,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()

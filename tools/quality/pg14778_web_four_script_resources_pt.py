"""Whole original5 Java resource wrappers/30 Node DOM subcases; no Browser or network."""
import re
import zipfile
from pathlib import Path
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
COUNTS={'LogSearchScriptTest':1,'OperationPostScriptTest':2,'ScenarioSearchScriptTest':1,'QuestionInputScriptTest':1}
SESSION='PG14778-ORIGINAL-FOUR-SCRIPT-RESOURCES5'
ROOT=data.ROOT/'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/view'
TESTS={n:ROOT/(n+'.java') for n in COUNTS}
PINS={'LogSearchScriptTest':'b96954b82cff3ef2e6bb3da1ad277c8ee01081d91b4c5e2fbc3e8162a0bff76c','OperationPostScriptTest':'6ebb98ab4a23ecd7c0b9bcbc1faa90691a9ca474a96fa0cf144395f1c8b7c59f','ScenarioSearchScriptTest':'ff3ee89e25ce10c551161ad0953715e391742fcffe6b1fa7ca9a56c005a81fe3','QuestionInputScriptTest':'3253e842449d2f82e25365fdd3077b9f4d35d36dd88ccca08edc713930c655b7'}
NODE=data.ROOT.parent/'toolchain/node-v24.19.0/bin/node'
NODE_PIN='bc17c508ffeed0ec622934f9b7fa72f8e78da65350e63c3eceb56fa688aa5e12'
COPY_INPUTS={
 'src/main/resources/static/js/log-search-validation.js':'b5cfbc9a689c91d0f14461e3e46dadb88844b5d0c38358d762dd241a5458efad',
 'src/main/resources/static/js/operation-post-submit.js':'771029cb5f80dd32d17af01a5fb8e7fe471a615268de6645d543f57001050429',
 'src/main/resources/static/js/search-speaker-submit.js':'dcf25a57a0e304391a0d3c880c263db246e296d6a7af0322283ddb72fa3e48fa',
 'src/main/resources/static/js/question-input-validation.js':'742ebf22201034123b5e96fbb82b9fe25d0f8a5f0260651a42c011389a10cafa',
 'src/test/javascript/log-search-validation.test.cjs':'0a05c57bd6ef7ee97311d2130ccd6fa34e8e4ea7edb23be76f7f97bd76a68ed4',
 'src/test/javascript/operation-post-submit.test.cjs':'1bab02dd52161343c7d6403abaf62b74dd044d02eac1b496bf2535917ba65f45',
 'src/test/javascript/search-speaker-submit.test.cjs':'22f9f1fbdff29f1cacc59a2c87366a079231238fd0dc4723632ce56d2b3ffe48',
 'src/test/javascript/question-input-validation.test.cjs':'869254f2f9b7b1a31d938d8f8537836a5b28f8813be99aaa60cbf4e5e7426f95',
 'src/main/resources/templates/admin/user-new.html':'97fd0f78dbfbe4538ca36e5ddda507ed55d762c040d12b09d544fc568b0dbedd',
 'src/main/resources/templates/admin/user-detail.html':'c74fe2ced5c6492369f243bf9930e52e88fef40b18492195a1ac01a9b05f8fba',
 'src/main/resources/templates/notifications/detail.html':'10e4f709e65f4da0ee7f6afe05c13b3cc21cb3a0ad497a52ba1a2a2408824701',
 'src/main/resources/templates/questions/detail.html':'106063b219b894417619b35cd8a120cffc4f4aa21432f59bfcf6b54f7595e9f2',
 'src/main/resources/templates/questions/new.html':'199d2b490c33bc708d6c459cf4681d2a4307eaf25f18a8fcd3617e1d94125cb4',
 'src/main/resources/templates/fragments/layout.html':'a48bda151f893e28858afb26d1c636a564b8bd0cb3c3a16bc63bbb97f0e414bd',
 'src/main/resources/templates/admin/user-list.html':'75ff8f6521d9e48c852264d839e17f9d2224f17ad2d486b37750cdae612e7655'}
FIXTURES={}
REPORTER=data.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

def inputs():
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA);assert normal['source']==SOURCE
    assert run.host.sha(NODE)==NODE_PIN
    jar=normal['jars']['web'];assert run.host.sha(Path(jar['path']))==jar['sha256']
    with zipfile.ZipFile(jar['path']) as archive:
        for relative,pin in COPY_INPUTS.items():
            assert not Path(relative).is_absolute() and '..' not in Path(relative).parts and relative.startswith(('src/main/resources/','src/test/javascript/'))
            path='src/schubert-nk-web/'+relative
            assert normal['begin']['inputHashes'][path]==run.host.sha(data.ROOT/path)==run.host.sha(COMPILE/'snapshot'/path)==pin
            if relative.startswith('src/main/resources/'):assert data.sha(archive.read(relative[len('src/main/resources/'):]))==pin
    return normal

def resource_step(name,command):
    inputs()
    if name=='selected-junit':
        for relative,pin in COPY_INPUTS.items():
            target=run.SLOT/relative;assert not target.exists();target.parent.mkdir(parents=True,exist_ok=True)
            with target.open('xb') as stream:stream.write((COMPILE/'snapshot/src/schubert-nk-web'/relative).read_bytes())
            assert run.host.sha(target)==pin
        command=[command[0],'-Dnk.pt.node='+str(NODE),*command[1:]]
    result=environmental_step(name,command)
    if name=='selected-junit':
        result['ownedSourceCopies']=dict(COPY_INPUTS);result['nodeBinary']=dict(path=str(NODE),sha256=NODE_PIN)
        assert all(run.host.sha(run.SLOT/p)==h for p,h in COPY_INPUTS.items())
    inputs();return result

if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg14778-web-four-script-resources-pt-v1';run.OUT=data.BASE/'PG14778-web-four-script-resources-pt-v1'
    run.HELPER=data.ROOT/'tools/quality/architecture/OriginalFourScriptResourcesJunitLauncher.java'
    run.NEW_TEST=TESTS['LogSearchScriptTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={n:p for n,p in TESTS.items() if n!='LogSearchScriptTest'}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    normal=inputs()
    for n,p in TESTS.items():
        relative=str(p.relative_to(data.ROOT));assert relative=='src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/view/'+n+'.java'
        assert run.host.sha(p)==normal['begin']['inputHashes'][relative]==run.host.sha(COMPILE/'snapshot'/relative)==PINS[n]
        text=p.read_text();assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text))==COUNTS[n]
        assert '"dev.codex.schubert.nk.web.view.'+n+'", '+str(COUNTS[n]) in run.HELPER.read_text()
        assert not any(v in text for v in ['@BeforeAll','@BeforeEach','@TempDir','DriverManager','getConnection(','Linux','TemporaryInfrastructureException','preserveFatal(','Cipher.','Mac.'])
        assert text.count('new ProcessBuilder(')==1 and 'process.waitFor(30, TimeUnit.SECONDS)' in text and 'process.descendants()' in text and 'if (process.isAlive()) process.destroyForcibly();' in text
    run.step=resource_step;run.main()

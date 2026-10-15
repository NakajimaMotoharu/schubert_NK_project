"""One exact Test-only inode contract group, all Main/member bytes identical to actual3712."""
import ast
import inspect
import json
import subprocess
from pyflakes.api import check
import pg3348_related_boundary_group as base

ROOT,W=base.ROOT,base.W
SOURCE='4856b3fcaeb4cae983d77757a38dc0bf56a693e2'
TEST='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/RootServiceExecutableAdmissionTest.java'
CLASSES={
 'protocol':{'dev.codex.schubert.nk.protocol.file.LargeResultRecordCodecTest':7},
 'storage':{'dev.codex.schubert.nk.storage.LinuxProcessExecTest':8},
 'bootstrap':{'dev.codex.schubert.nk.bootstrap.FixedNativeCoverageProfileTest':5},
 'api':{'dev.codex.schubert.nk.api.security.LoginUsernameTest':3},
 'web':{'dev.codex.schubert.nk.web.media.HttpByteRangeParserTest':4},
 'batch':{'dev.codex.schubert.nk.batch.file.RootServiceExecutableAdmissionTest':6}}
METHODS=[('dev.codex.schubert.nk.batch.file.RootServiceExecutableAdmissionTest',n)for n in [
 'typedOwnerModeLinkSizeTimeAndAclContract',
 'typedValueBoundariesAreRejectedBeforeAclAndCorrectLimitsRemainAdmitted',
 'aclFailureIdentityAndRequiredBoundaryValuesCannotBeAccepted']]


def validate(snapshot):
    full=json.loads((W/'pg3414-outbox-full-qualified-v1/manifest.safe.json').read_bytes())
    native=json.loads((W/'pg3632-current-browser-native-qualified-v1/manifest.safe.json').read_bytes())
    base.require(full['actualExit']==native['actualExit']==0 and full['result']['productionSource']==native['result']['productionSource']==SOURCE,'current actual full/native source')
    result=full['result'];base.require(result['tests']==3712 and result['mainClasses']==1643 and native['result']['currentNativeStreams']==18,'actual full/native cardinality')
    changed=set(subprocess.check_output(['git','diff','--name-only',result['sourceSnapshot'],snapshot,'--',*base.engine.SCOPE],cwd=ROOT,text=True).splitlines())
    base.require(changed=={TEST},'one Test file only; every Main/resource/config/characterization unchanged')
    before=json.loads((W/'pg3678-numeric-conditional-before-v1/manifest.safe.json').read_bytes())
    base.require(before['actualExit']==0 and before['independentBeforeReproduced']and before['originalTestUnchanged'],'Java25 original before proof')
    for module,names in CLASSES.items():
        for name,count in names.items():
            path='src/schubert-nk-'+module+'/src/test/java/'+name.replace('.','/')+'.java'
            raw=subprocess.check_output(['git','show',snapshot+':'+path],cwd=ROOT,text=True)
            base.require(raw.count('@Test\n')==count,'selected exact method count')
    return result


def server_source():
    raw=base.SERVER.replace('PG3348','PG3680').replace('source-full-PG3330','source-full-PG3412')
    start=raw.index("\n if module=='batch':");end=raw.index('\nrequire(len(all_cases)',start)
    raw=raw[:start]+r'''
 if module=='batch':
  target=next(c for p in node.findall('package')for c in p.findall('class')if c.get('name')=='dev/codex/schubert/nk/batch/file/RootServiceExecutableAdmission')
  method=next(m for m in target.findall('method')if m.get('name')=='checkedAttributes')
  counters={x.get('type'):{'missed':int(x.get('missed')),'covered':int(x.get('covered'))}for x in method.findall('counter')}
  require(all(counters[k]['missed']==0 for k in ['LINE','METHOD','BRANCH']),'whole typed metadata method executed and every branch required')
  result[module]['checkedAttributesCounters']=counters
'''+raw[end:]
    tree=ast.parse(raw);counts=suites=methods=0
    for node in ast.walk(tree):
        if isinstance(node,ast.Constant)and type(node.value)is int and node.value==44:node.value=33;counts+=1
        if isinstance(node,ast.Constant)and type(node.value)is int and node.value==7:node.value=6;suites+=1
        if isinstance(node,ast.For)and isinstance(node.target,ast.Name)and node.target.id=='expected':node.iter=ast.parse(repr(METHODS),mode='eval').body;methods+=1
        if isinstance(node,ast.Dict):
            for k,v in zip(node.keys,node.values):
                if isinstance(k,ast.Constant)and k.value=='newMethods':v.value=2
    base.require(counts==3 and suites==2 and methods==1,'exact static cardinality/method replacements only')
    raw=ast.unparse(ast.fix_missing_locations(tree))
    complete='INPUT={}\n'+inspect.getsource(base.require)+'\n'+inspect.getsource(base.classify)+'\n'+raw
    base.require(check(complete,'<typed-related33>')==0,'complete namespace static0')
    return raw


def main():
    raw=inspect.getsource(base.main).replace('pg3348-related-boundary-group-v1','pg3680-typed-inode-related-v1').replace('PG3348','PG3680')
    namespace={**base.__dict__,'SOURCE':SOURCE,'CLASSES':CLASSES,'validate':validate,'SERVER':server_source()}
    exec(compile(raw,'<fixed typed inode related group>','exec'),namespace)
    return namespace['main']()


if __name__=='__main__':raise SystemExit(main())

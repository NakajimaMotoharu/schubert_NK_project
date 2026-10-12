"""Independent exact five selected XML/source/JAR/CRC/library/fixture qualification."""
import inspect
import json
import hashlib
import os
import pg1627_selected_contract_qualification as prior
from pg1700_new_source_live_binding import SOURCE

METHODS={'dev.codex.schubert.nk.api.bootstrap.ApiProcessMainTest:'+name for name in [
    'opsApiMain001AdmissionBeforeAssemblyAndUnwiredNativeRefusal',
    'opsApiMain002FailuresAndUnknownRemainNonSuccess','opsApiMain003FatalDiagnosticIsFixed',
    'opsApiMain004ActualExternalMainRejectsMissingConfigAndArgv',
    'opsApiMain005ConfigurationLoadFailuresNeverEnterAssembly']}


def qualified_tests(manifest,xml_bytes,expected):
    raw=inspect.getsource(prior.qualified_tests).replace('len(expected) not in (3, 6)','len(expected) != 5')
    ns={};exec(compile(raw,'<independent exact five XML oracle>','exec'),ns)
    return ns['qualified_tests'](manifest,xml_bytes,expected)


def server():
    raw=prior.SERVER.replace('PG1627','PG1715').replace('PG1532','PG1633')
    start=raw.index('for number,expected in ');end=raw.index(':\n root=',start)
    raw=raw[:start]+'for number,expected in [(1714,METHODS)]'+raw[end:]
    raw=raw.replace("fixtures=source/'src/schubert-nk-batch/target/test-classes'", "fixtures=source/'src/schubert-nk-api/target/test-classes'")
    raw=raw.replace("require(results['1625']['tests']==3 and results['1626']['tests']==6)","require(results['1714']['tests']==5)")
    raw=raw.replace("results['1626']['remaining']","results['1714']['remaining']")
    compile(raw,'<API5 independent source artifact qualifier>','exec')
    return raw


def main():
    os.umask(0o077);out=prior.W/'pg1715-api-configuration-selected-qualified-v1';out.mkdir(mode=0o700)
    host=json.loads((prior.W/'pg1714-api-configuration-negative-selected-v1/manifest.safe.json').read_bytes())
    if host.get('actualExit')!=0 or host.get('tests')!=5 or host.get('productionSource')!=SOURCE:
        raise ValueError('actual current five successful result required')
    code='INPUT='+repr({'1714':host['manifestSha256']})+'\nSOURCE='+repr(SOURCE)+'\nMETHODS='+repr(METHODS)+'\n'
    code+=inspect.getsource(prior.qualified_tests).replace('len(expected) not in (3, 6)','len(expected) != 5')+'\n'+server()
    from pyflakes.api import check
    if check(code,'<complete actual API5 qualifier>'):raise ValueError('static source closure refused')
    path=out/'pg1715-qualification.private.py';path.write_text(code)
    code_exit,output=prior.run('test ! -e /home/mini/schubert-nk-pgpt/transfer/pg1715-qualification.private.py && test ! -e /home/mini/schubert-nk-pgpt/runs/PG1715-selected-qualification-v1',timeout=30)
    if code_exit:raise ValueError('new-only qualification namespace required')
    code_exit,output=prior.copy(path,'/home/mini/schubert-nk-pgpt/transfer/',timeout=60)
    if code_exit:raise ValueError('qualification transfer refused')
    code_exit,output=prior.run('python3 -B /home/mini/schubert-nk-pgpt/transfer/pg1715-qualification.private.py',timeout=90)
    (out/'server.private.log').write_text(output)
    safe={'actualExit':code_exit,'scriptSha256':hashlib.sha256(code.encode()).hexdigest(),'formalAccepted':False}
    if code_exit==0:safe.update(json.loads(next(v for v in output.splitlines()if v.startswith('{'))))
    with(out/'manifest.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(safe));return code_exit


if __name__=='__main__':raise SystemExit(main())

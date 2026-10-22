"""One necessary grouped4189 regression after owned ABI/request Test additions; Main unchanged."""
import inspect
import json
import subprocess
import pg6188_native_ownership_whole as base
import pg6744_request_read_selected as selected

ROOT,W,BASE,sha=base.ROOT,base.W,base.BASE,base.sha
OLD='01e41088c6562c3b7d103ae0bacc9f693bc1aad4'
LABEL='PG6748'
SLOT='pg6748-owned-reader-six-v1'
QSHA='af3dcb55d39916cd4883ddfa37337c92033b60080e6e9c7c44de760a35b1714a'
TESTS={selected.TEST,'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/bootstrap/SystemdBinderAbiTest.java'}


def original_source():
    source=json.loads((W/selected.SLOT/'begin.safe.json').read_bytes())['source'];selected.guard(source)
    return source


def definitions():
    scope={**vars(base),'LABEL':LABEL,'SLOT':SLOT,'original_source':original_source,'prerequisites':prerequisites}
    for name in ('declared_inventory','server_source','driver_source','main'):
        raw=inspect.getsource(getattr(base,name))
        for before,after in (('4023','4189'),('605','645'),('pg6188','pg6748')):raw=raw.replace(before,after)
        exec(compile(raw,'<grouped4189 '+name+'>','exec'),scope)
    return scope


def declared_inventory():return definitions()['declared_inventory']()
def server_source(head,digest):return definitions()['server_source'](head,digest)


def driver_source(fresh):
    raw=definitions()['driver_source'](fresh);start=raw.index("'trigger': ");end=raw.index('}, sort_keys=True)',start)
    trigger=('Necessary grouped new5 independent Tests (owned21 ABI dispatcher2 and public request read3), '
      'not a confirmation replay of source01e4184. All851 Main/1667 physical unchanged, all old '
      'Test bytes fixed; fresh4189/645 includes each original XML identity, not PASS arithmetic. '
      'Original47/11 allsix qualification first. Allsix format-beforePT/compile/null/static; '
      'same finite self-owned tempDB/JMS/HTTP/child fixtures. No actual VM/current/Root/cohort/'
      'intent/permit/key/native qualification operation; held scopes remain held. '
      'Global100/F03/CHR/native/formal/trace require independent same-source evidence.')
    return raw[:start]+"'trigger': "+repr(trigger)+raw[end:]


def prerequisites(source):
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT):raise ValueError('clean committed operator first')
    if subprocess.check_output(['git','diff',source,'--','src','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=ROOT):
        raise ValueError('selected source/Test/gates fixed for whole and reader')
    qp=BASE/'PG6746-request-read-original-v1/manifest.json';private=W/'pg6746-request-read-original-v1/manifest.safe.json'
    if QSHA is None or sha(qp)!=QSHA:raise ValueError('freeze actual current47 original qualification first')
    q=json.loads(qp.read_bytes())
    if not(q['source']==source and q['actualExit']==0 and (q['tests'],q['suites'],q['physicalMain'])==(47,11,1667)
           and sha(private)==q['privateManifestSha256'] and q['changedPhysical']==[]):raise ValueError('genuine all47/all8511667 unchanged Main')
    p=json.loads(private.read_bytes())
    if {x.relative_to(ROOT).as_posix():sha(x) for x in ROOT.glob('src/*/src/main/java/**/*.java')}!=p['allSourceHashes']:
        raise ValueError('all actual851 Main byte fixed')
    changes=subprocess.check_output(['git','diff','--name-status',OLD,source,'--','src'],cwd=ROOT,text=True).splitlines()
    if set(changes)!={'A\t'+x for x in TESTS}:raise ValueError('exact two added Test files, every historical Test/Main fixed')
    declared_inventory()


def main():
    scope=definitions();scope['main'].__globals__['driver_source']=driver_source
    return scope['main']()


if __name__=='__main__':raise SystemExit(main())

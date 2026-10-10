"""New-only BUG1073 public refusal retry; actual prior failed slot retained."""
import inspect
import json
import pg1283_physical_pin_actual as previous
from pg1285_public_pin_compile import TARGET


def payload(manifest):
    code=inspect.getsource(previous.payload)
    old="'compile.private.log'}"
    if code.count(old)!=1:raise ValueError('closed fixture extension boundary required')
    code=code.replace(old,"'compile.private.log','Pg1285PublicRefusalTest.java','dev/codex/schubert/nk/bootstrap/Pg1285PublicRefusalTest.class'}")
    env=dict(previous.__dict__);env['TARGET']=TARGET;env['BODY']=previous.BODY.replace('pg1283','pg1286').replace('PG1283','PG1286')
    exec(compile(code,'<actual corrected closed public pin fixture>','exec'),env)
    return env['payload'](manifest)


def main():
    fixed=json.loads((previous.W/'pg1285-public-refusal.safe.json').read_bytes())
    if fixed['actualExit']!=0 or not fixed['sevenFixedVectors']:raise ValueError('independent seven public refusal vectors required')
    env=dict(previous.__dict__);env['TARGET']=TARGET;env['payload']=payload
    code=inspect.getsource(previous.main).replace('pg1283','pg1286').replace('PG1283','PG1286')
    exec(compile(code,'<new-only corrected actual pin execution>','exec'),env)
    return env['main']()


if __name__=='__main__':raise SystemExit(main())

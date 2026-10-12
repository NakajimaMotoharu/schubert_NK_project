"""New-only candidate with independent before oracle; reuse qualified immutable JARs.

Failed1535 tree remains incomplete and untouched. No re-receive/old-slot replay.
"""
import inspect
import json
import os
import pg1535_filesystem_signed_candidate as prior

def main():
    os.umask(0o077)
    gate=prior.validate_gate(json.loads((prior.W/'pg1542-filesystem-full-qualified-v3/manifest.safe.json').read_bytes()))
    cache=prior.W/'pg1535-frozen-six-v1'
    jars={m:cache/m/f'schubert-nk-{m}-0.1.0-SNAPSHOT.jar'for m in prior.MODULES}
    if any(p.is_symlink()or not p.is_file()or prior.sha(p)!=gate['jarHashes'][m]for m,p in jars.items()):
        raise ValueError('immutable independently qualified JAR cache refused')
    raw=inspect.getsource(prior.main).replace('PG1535','PG1544').replace('pg1535','pg1544')
    old='[NEXT,FROZEN,SIG,W/';new='[NEXT,SIG,W/'
    if raw.count(old)!=1:raise ValueError('new-only candidate reservation boundary refused')
    raw=raw.replace(old,new).replace('FROZEN.mkdir(mode=0o700);old_classes={};new_classes={};jars={}', 'old_classes={};new_classes={};jars={}').replace('p=receive(module);','p=cached_jars[module];')
    ns={**prior.__dict__,'NEXT':prior.W/'pg1544-release-v1','SIG':prior.P/'pg1544-manifest-v1.sig','FROZEN':cache,'cached_jars':jars}
    exec(compile(raw,'<new-only independently sourced candidate>','exec'),ns)
    return ns['main']()

if __name__=='__main__':raise SystemExit(main())

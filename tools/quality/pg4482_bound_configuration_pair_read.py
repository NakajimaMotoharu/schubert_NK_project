"""Restore original inline configuration contract without dropping any Unit/data field."""
import ast
import hashlib
import json
import os
import subprocess
from pyflakes.api import check
import pg4360_pool_bound_partial_sources as original
from pg4434_current_candidate_admission_read import authenticate_host
from pg1446_current_cold_stage import W, SSH


def inline_configuration():
    raw=original.files()['post.py'];tree=ast.parse(raw)
    nodes=[n for n in tree.body if isinstance(n,ast.Expr)and isinstance(n.value,ast.Call)
        and isinstance(n.value.func,ast.Name)and n.value.func.id=='exec'
        and any(isinstance(x,ast.Name)and x.id=='CONFIG_CONTRACT'for x in ast.walk(n))]
    if len(nodes)!=1:raise ValueError('one pinned inline full configuration contract')
    return ast.get_source_segment(raw,nodes[0])


def payload():
    raw=(W/'pg4480-complete-inspect-pair-read-v1/payload.private.py').read_bytes()
    if hashlib.sha256(raw).hexdigest()!='45775a9a6a26a4865a51eb8713f698e72a6de22b2a7efcbba9d57e94927a4828':raise ValueError('original rejected complete19 reader first')
    raw=raw.decode().replace('pg4480-complete-inspect-pair-read-v1','pg4482-bound-configuration-pair-read-v1')
    marker='CONFIG_CONTRACT={}'
    if raw.count(marker)!=1:raise ValueError('one missing configuration binding boundary')
    raw=raw.replace(marker,marker+'\n'+inline_configuration(),1)
    if check(raw,'<fully bound19/32/FD/data read>'):raise ValueError('all emitted static0')
    return raw


def main():
    raw=payload();authenticate_host();os.umask(0o077);out=W/'pg4482-bound-configuration-pair-read-v1';out.mkdir(mode=0o700)
    (out/'payload.private.py').write_text(raw)
    result=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw.encode(),capture_output=True,timeout=180)
    (out/'observer.private.log').write_bytes(result.stdout+result.stderr)
    value={'actualExit':result.returncode,'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'operationsIssued':0,'formalAccepted':False}
    if result.returncode==0:value['result']=json.loads(result.stdout)
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return result.returncode


if __name__=='__main__':
    raise SystemExit(main())

"""Complete19 Unit properties and all32 settings, preserving original full pair rejection."""
import ast
import hashlib
import inspect
import json
import os
import subprocess
from pyflakes.api import check
import pg4476_inspect_pair_full_read as previous
import pg4360_pool_bound_partial_sources as original
from pg4438_failed_current_canonical_view import PARENT_FIELDS
from pg4434_current_candidate_admission_read import authenticate_host
from pg1446_current_cold_stage import W, SSH


def strict_unit_values(raw, expected):
    if type(raw) is not str or type(expected) is not set or not expected or not raw.endswith('\n'):
        raise ValueError('full Unit property contract')
    result={}
    for line in raw.splitlines():
        key, sep, value=line.partition('=')
        if sep != '=' or key not in expected or key in result:raise ValueError('Unit missing/duplicate/foreign field')
        result[key]=value
    if set(result) != expected:raise ValueError('all Unit properties required')
    return result


def payload():
    raw=previous.payload()
    if hashlib.sha256(raw.encode()).hexdigest()!='b358c30d528251120f20cee63cfc865ab6dfd77e34c30c40147b947620e688ba':raise ValueError('original rejected read unchanged')
    raw=raw.replace('pg4476-inspect-pair-full-read-v1','pg4480-complete-inspect-pair-read-v1')
    top=ast.parse(raw)
    fields=next(n for n in top.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='fields'for t in n.targets))
    raw=raw.replace(ast.get_source_segment(raw,fields),'fields='+repr(','.join(PARENT_FIELDS)),1)
    target="dict(l.split('=',1)for l in command(['systemctl','show',name,'--property='+fields],65536).decode().splitlines())"
    if raw.count(target)!=1:raise ValueError('one actual complete Unit parse')
    raw=raw.replace(target,"strict_unit_values(command(['systemctl','show',name,'--property='+fields],65536).decode('ascii'),set(fields.split(',')))",1)
    # Keep the complete pinned declaration parser/capture, not an early subset.
    source=original.files()['post.py'];tree=ast.parse(source);pieces=[]
    for n in tree.body:
        if isinstance(n,ast.FunctionDef)and n.name in ['exec_record','configuration_value','complete_configuration','config']:
            pieces.append(ast.get_source_segment(source,n))
        elif isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id in ['CONFIG_SOURCE','CONFIG_CONTRACT','FIELDS']for t in n.targets):
            pieces.append(ast.get_source_segment(source,n))
        elif isinstance(n,ast.Expr)and 'exec(CONFIG_SOURCE' in ast.get_source_segment(source,n):
            pieces.append(ast.get_source_segment(source,n))
    insert=inspect.getsource(strict_unit_values)+'\n'+'\n'.join(pieces)+'\n'
    marker="os.umask(0o077);save=base/'pg4480-complete-inspect-pair-read-v1'"
    if raw.count(marker)!=1:raise ValueError('one new-only capture boundary')
    raw=raw.replace(marker,insert+'\n'+marker,1)
    raw=raw.replace('first_pair=read_pair();first_pair_sha=',"first_config=config();first_config_sha=private('first-config.private.json',first_config)\nfirst_pair=read_pair();first_pair_sha=",1)
    marker="for label,pid,ticks,digest in "
    raw=raw.replace(marker,"second_config=config();second_config_sha=private('second-config.private.json',second_config)\nrequire(first_config==second_config)\n"+marker,1)
    marker="'allCurrentOriginalDataPreserved':True"
    raw=raw.replace(marker,"'all19UnitFieldsAnd32SettingsPreserved':True,'firstConfigSha256':first_config_sha,'secondConfigSha256':second_config_sha,"+marker,1)
    if check(raw,'<whole19/32 current pair read>'):raise ValueError('all emitted static0')
    compile(raw,'<whole19/32 current pair read>','exec')
    return raw


def main():
    raw=payload();authenticate_host();os.umask(0o077);out=W/'pg4480-complete-inspect-pair-read-v1';out.mkdir(mode=0o700)
    (out/'payload.private.py').write_text(raw)
    result=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw.encode(),capture_output=True,timeout=180)
    (out/'observer.private.log').write_bytes(result.stdout+result.stderr)
    value={'actualExit':result.returncode,'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'operationsIssued':0,'formalAccepted':False}
    if result.returncode==0:value['result']=json.loads(result.stdout)
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return result.returncode


if __name__=='__main__':
    raise SystemExit(main())

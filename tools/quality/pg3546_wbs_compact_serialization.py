"""Restore existing one-record-per-line style; no WBS semantics/acceptance change."""
import hashlib
import json
import os
import types
import pg3282_wbs_current_source_apply as base
import pg3542_current_criteria_revalidation as review
import wbs_progress_audit as audit
from pg1446_current_cold_stage import W


def render(key,value):
    if key in {'tasks','artifacts'}:
        return '[\n'+',\n'.join('    '+json.dumps(row,ensure_ascii=False)for row in value)+'\n  ]'
    return base.render_value(key,value)


def main():
    os.umask(0o077);out=W/'pg3546-wbs-compact-serialization-v1';out.mkdir(mode=0o700)
    rewrite=types.FunctionType(base.rewrite_root.__code__,{**base.rewrite_root.__globals__,'render_value':render})
    targets={'481_PGPT詳細WBS.json':'tasks','485_WBS網羅性・受入対応.json':'artifacts'}
    before={n:(review.PMO/n).read_bytes()for n in [*targets,'486_WBS現行実績.json']}
    after={}
    for name,key in targets.items():
        text=before[name].decode();value=json.loads(text)
        after[name]=rewrite(text,{key:value[key]}).encode()
        review.require(json.loads(after[name])==value,'serialization must not alter any logical value')
    name='486_WBS現行実績.json';snapshot=json.loads(before[name])
    new_inventory_sha=hashlib.sha256(after['485_WBS網羅性・受入対応.json']).hexdigest()
    after[name]=base.rewrite_root(before[name].decode(),{'inventorySha256':new_inventory_sha}).encode()
    review.require(json.loads(after[name])=={**snapshot,'inventorySha256':new_inventory_sha},'only physical inventory hash binding may change in snapshot')
    for name in before:
        with(out/('before-'+name)).open('xb')as f:f.write(before[name])
        with(out/('after-'+name)).open('xb')as f:f.write(after[name])
    intent={'semanticSourceAcceptanceCostScopeChanges':False,'snapshotOnlyInventoryByteHashUpdated':True,
            'oldHashes':{n:review.sha(v)for n,v in before.items()},'newHashes':{n:review.sha(v)for n,v in after.items()}}
    with(out/'intent.safe.json').open('x')as f:json.dump(intent,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    for name in before:base.replace_public(review.PMO/name,after[name])
    result=audit.verify();review.require(result['acceptedTasks']==17,'same17 strict audit required')
    with(out/'result.safe.json').open('x')as f:json.dump({'actualExit':0,**intent,'audit':result},f,sort_keys=True)
    print(json.dumps({'actualExit':0,'restoredCompactStyle':True,'sourceAcceptanceCostScopeChanges':False,'acceptedTasks':17}));return 0


if __name__=='__main__':raise SystemExit(main())

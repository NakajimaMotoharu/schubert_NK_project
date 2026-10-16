"""New-only v2 namespace strips exactly the old materialization prelude, not historical literals."""
from bundle_hash_contract import unbind
import pg3756_hygiene_unused_sources as old

CURRENT,CURRENT_BOM,SOURCE,BOM,BEFORE,BOOT=old.CURRENT,old.CURRENT_BOM,old.SOURCE,old.BOM,old.BEFORE,old.BOOT
W=old.W;VIEW_LOCAL=old.VIEW_LOCAL;TOOLS='pg3766-hygiene-unused-tools-v2';SAVE='pg3770-hygiene-unused-placement-v2';ARCHIVE='pg3770-hygiene-release-v2.tar';REMOTE='/home/ubuntu/pg3770-hygiene-input-v2'
qualify=old.qualify;production=old.production;current_tuple=old.current_tuple


def bind(raw):
    for a,b in [(old.TOOLS,TOOLS),(old.SAVE,SAVE),(old.ARCHIVE,ARCHIVE),(old.REMOTE,REMOTE),('pg3756','pg3766'),('Pg3756','Pg3766'),('PG3756','PG3766'),('pg3758','pg3768'),('PG3758','PG3768'),('pg3760','pg3770'),('PG3760','PG3770'),('pg3762','pg3772'),('PG3762','PG3772')]:raw=raw.replace(a,b)
    return raw


def sources(bom=BOM,before=BEFORE):
    original=old.sources(bom,before);result={}
    for name,raw in original.items():
        if name in ['pg3756_native_refs.py','pg3756_input_preflight.py']:raw=unbind(raw)
        result[bind(name)]=bind(raw)
    if len(result)!=18:raise ValueError('all eighteen exact source roles required')
    return result

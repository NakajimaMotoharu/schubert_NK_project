"""Independent seven finite296 phases/new signed current; old88 preservation never new native."""
import inspect
import json
import types
import pg5014_ssc304_publication_post as previous
import pg5454_ownership_publication_sources as role
from pg4996_resume_connection import authenticate_host
from immutable_payload_binding import bind_preserving_payloads

SLOT='pg5460-ownership-publication-independent-post-v1'
FULL_BEFORE='/var/lib/pgpt-s1-preservation/'+role.ro.unused.view.SLOT+'/before.private.json'
FULL_SHA=role.BEFORE


def readonly_source():
    raw=previous.readonly_source()
    changes={previous.role.SOURCE:role.SOURCE,previous.role.BOM:role.BOM,'PG4980':'PG5430',
        'pg4980-manifest.sig':'pg5430-manifest.sig',previous.FULL_BEFORE:FULL_BEFORE,previous.FULL_SHA:FULL_SHA,
        '==80)':'==88)','native80Preserved':'native88Preserved'}
    for old in changes:
        if old not in raw:raise ValueError('one new296 reader boundary '+old)
    # Independent one-pass replacements avoid currentA2/candidate296 role collisions.
    import re
    pattern='|'.join(re.escape(key)for key in sorted(changes,key=len,reverse=True))
    return bind_preserving_payloads(raw,lambda text:re.sub(pattern,lambda match:changes[match.group()],text))


def publication():
    template=previous.previous.previous.old
    ns={**vars(template),'role':role}
    raw=inspect.getsource(template.publication).replace('pg3788_ordinary_publication_contract','pg5454_ordinary_publication_contract')
    exec(compile(raw,'<all seven actual finite phases independent oracle>','exec'),ns)
    value=ns['publication']()
    if value.count('old_after=after')!=1:raise ValueError('one full current baseline')
    return value.replace('old_after=after',"old_after={**after,'native':expected['native']}",1)


def payload():
    template=previous.previous.previous
    ns={**vars(template),'role':role,'SLOT':SLOT,'readonly_source':readonly_source,'publication':publication}
    raw=inspect.getsource(template.payload)
    for old,new in(('pg4724-frozen-v1.safe.json','pg5456-frozen-v1.safe.json'),
        ('pg4706_configuration_capture.py','pg5438_configuration_capture.py'),
        ('originalBackupNative64Preserved','originalBackupNative88Preserved')):
        raw=raw.replace(old,new)
    exec(compile(raw,'<full88/new signed296 independent finite post>','exec'),ns)
    return ns['payload']()


def main():
    actual=json.loads((role.W/'pg5458-activate-v1.safe.json').read_bytes())
    wanted={'actualExit':0,'sourceQualified':True,'candidateSource':role.SOURCE,'currentApprovalEpochChanged':True}
    if any(type(actual.get(k))is not type(v)or actual[k]!=v for k,v in wanted.items()):raise ValueError('actual296 finite publication first')
    authenticate_host();transport=previous.previous.previous.transport
    return types.FunctionType(transport.execute.__code__,{**vars(transport),'SOURCE':role.SOURCE})(SLOT,payload(),180)


if __name__=='__main__':raise SystemExit(main())

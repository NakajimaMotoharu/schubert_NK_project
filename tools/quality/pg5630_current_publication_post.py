"""Independent seven finite phases/newCurrent0ea; all94 native remain preservation only."""
import inspect
import json
import re
import types
import pg5460_ownership_publication_post as previous
import pg5624_current_publication_sources as role
from pg4996_resume_connection import authenticate_host
from immutable_payload_binding import bind_preserving_payloads

SLOT='pg5630-current-publication-independent-post-v1'
FULL_BEFORE='/var/lib/pgpt-s1-preservation/'+role.ro.unused.capture.SLOT+'/before.private.json'
FULL_SHA=role.BEFORE


def readonly_source():
    raw=previous.readonly_source()
    changes={previous.role.SOURCE:role.SOURCE,previous.role.BOM:role.BOM,'PG5430':'PG5598','pg5430-manifest.sig':'pg5598-manifest.sig',
      previous.FULL_BEFORE:FULL_BEFORE,previous.FULL_SHA:FULL_SHA,'==88)':'==94)','native88Preserved':'native94Preserved'}
    for old in changes:
        if old not in raw:raise ValueError('exact new0ea reader binding: '+old)
    pattern='|'.join(re.escape(k)for k in sorted(changes,key=len,reverse=True))
    return bind_preserving_payloads(raw,lambda text:re.sub(pattern,lambda match:changes[match.group()],text))


def publication():
    template=previous.previous.previous.previous.old
    scope={**vars(template),'role':role}
    raw=inspect.getsource(template.publication).replace('pg3788_ordinary_publication_contract','pg5624_ordinary_publication_contract')
    exec(compile(raw,'<seven actual finite phases independent oracle>','exec'),scope)
    value=scope['publication']()
    if value.count('old_after=after')!=1:raise ValueError('one full preservation baseline boundary')
    return value.replace('old_after=after',"old_after={**after,'native':expected['native']}",1)


def payload():
    template=previous.previous.previous.previous
    scope={**vars(template),'role':role,'SLOT':SLOT,'readonly_source':readonly_source,'publication':publication}
    raw=inspect.getsource(template.payload)
    for old,new in(('pg4724-frozen-v1.safe.json','pg5626-frozen-v1.safe.json'),
      ('pg4706_configuration_capture.py','pg5608_configuration_capture.py'),('originalBackupNative64Preserved','originalBackupNative94Preserved')):raw=raw.replace(old,new)
    exec(compile(raw,'<full94/new signed0ea independent finite post>','exec'),scope)
    return scope['payload']()


def main():
    actual=json.loads((role.W/'pg5628-activate-v1.safe.json').read_bytes())
    wanted={'actualExit':0,'sourceQualified':True,'candidateSource':role.SOURCE,'currentApprovalEpochChanged':True}
    if any(type(actual.get(k))is not type(v)or actual[k]!=v for k,v in wanted.items()):raise ValueError('actual original finite activation first')
    authenticate_host();transport=previous.previous.previous.previous.transport
    return types.FunctionType(transport.execute.__code__,{**vars(transport),'SOURCE':role.SOURCE})(SLOT,payload(),240)


if __name__=='__main__':raise SystemExit(main())

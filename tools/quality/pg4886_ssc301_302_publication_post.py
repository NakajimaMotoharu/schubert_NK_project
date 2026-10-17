"""Independent seven finite phases/new signed current, all old72 preserved as data."""
import inspect
import json
import types
import pg4728_ssc299_publication_post as previous
import pg4880_ssc301_302_publication_sources as role

SLOT='pg4886-ssc301-302-publication-independent-post-v1'
FULL_BEFORE='/var/lib/pgpt-s1-preservation/pg4862-current-preservation-readonly-v1/before.private.json'
FULL_SHA=role.BEFORE


def readonly_source():
    raw=previous.readonly_source()
    changes={previous.role.SOURCE:role.SOURCE,previous.role.BOM:role.BOM,
             'PG4702':'PG4860','pg4702-manifest.sig':'pg4860-manifest.sig',
             previous.FULL_BEFORE:FULL_BEFORE,previous.FULL_SHA:FULL_SHA,
             '==64)':'==72)','native64Preserved':'native72Preserved'}
    for a,b in changes.items():
        if a not in raw:raise ValueError('one new signed current reader boundary '+a)
        raw=raw.replace(a,b)
    return raw


def publication():
    ns={**vars(previous.old),'role':role}
    raw=inspect.getsource(previous.old.publication).replace('pg3788_ordinary_publication_contract','pg4880_ordinary_publication_contract')
    exec(compile(raw,'<independent all seven finite phase values>','exec'),ns)
    result=ns['publication']()
    if result.count('old_after=after')!=1:raise ValueError('one complete current baseline')
    return result.replace('old_after=after',"old_after={**after,'native':expected['native']}",1)


def payload():
    ns={**vars(previous),'role':role,'SLOT':SLOT,'readonly_source':readonly_source,'publication':publication}
    raw=inspect.getsource(previous.payload).replace('pg4724-frozen-v1.safe.json','pg4882-frozen-v1.safe.json').replace('pg4706_configuration_capture.py','pg4864_configuration_capture.py').replace('originalBackupNative64Preserved','originalBackupNative72Preserved')
    exec(compile(raw,'<full72/current04bb finite independent post>','exec'),ns);return ns['payload']()


def main():
    actual=json.loads((role.W/'pg4884-activate-v1.safe.json').read_bytes())
    if not(type(actual.get('actualExit'))is int and actual['actualExit']==0 and actual.get('sourceQualified')is True
           and actual.get('candidateSource')==role.SOURCE and actual.get('currentApprovalEpochChanged')is True):
        raise ValueError('actual finite publication first')
    previous.authenticate_host()
    execute=types.FunctionType(previous.transport.execute.__code__,{**vars(previous.transport),'SOURCE':role.SOURCE})
    return execute(SLOT,payload(),180)


if __name__=='__main__':raise SystemExit(main())

"""New-only dispatcher with actual current-observation receipt schema contract."""
import sys
import pg1314_ordinary_publication_dispatch as previous
from pg1293_completed_unused_stage_sources import BASELINE_SHA

GUEST=previous.GUEST
STAGE=previous.STAGE.replace('pg1314','pg1316').replace('PG1314','PG1316')


def preflight_digest(value):
    if type(value)is not dict:raise ValueError('complete current preflight required')
    flags=['all24UnchangedTwice','allTenUnitsKernelEmpty','allActorGone','allClientAdvisoryFlock0',
      'whole187SignedArtifactBytesVerified','normalNewMetadataScopes','nativeMetadataStableTwice','startsStopsReloadsSqlWrites0']
    if any(value.get(k)is not True for k in flags)or type(value.get('actualExit'))is not int or value['actualExit']!=0:
        raise ValueError('actual full current preflight required')
    if value.get('productionSource')!='d5b00104280028d9ea81b44c1d1c805f3c2861ed' or value.get('formalAccepted')is not False or value.get('rawExported')is not False:
        raise ValueError('same current source and private receipt required')
    proofs=value.get('proofHashes');item=proofs.get('after.private.json')if type(proofs)is dict else None
    if type(item)is not dict or item.get('sha256')!=BASELINE_SHA or type(item.get('bytes'))is not int or not 0<item['bytes']<=67108864:
        raise ValueError('complete sealed baseline evidence required')
    return item['sha256']


def source():
    code=previous.source().replace('pg1314','pg1316').replace('PG1314','PG1316')
    old="pre['privateBeforeSha256']"
    if code.count(old)!=1:raise ValueError('one current precondition boundary required')
    code=code.replace(old,'preflight_digest(pre)')
    compile(code,'<actual corrected current receipt dispatcher>','exec');return code


def main():
    if sys.argv[1:]not in (['stage'],['activate']):raise ValueError('closed stage or activate required')
    env=dict(previous.previous.__dict__,GUEST=GUEST,STAGE=STAGE,sources=previous.sources,BEFORE=BASELINE_SHA,preflight_digest=preflight_digest)
    exec(compile(source(),'<actual corrected finite dispatcher>','exec'),env)
    return env['main']()


if __name__=='__main__':raise SystemExit(main())

"""Only the six unexecuted batch cases after v1 compile failure; no successful27 replay."""
import ast
import inspect
import json
from pyflakes.api import check
import pg3680_typed_inode_related as p

CLASSES={'batch':p.CLASSES['batch']}


def validate(snapshot):
    failed=json.loads((p.W/'pg3680-typed-inode-related-v1/manifest.safe.json').read_bytes())
    p.base.require(failed['actualExit']==1,'original group failure retained; not successful33')
    return p.validate(snapshot)


def server_source():
    tree=ast.parse(p.server_source());counts=suites=members=0
    for node in ast.walk(tree):
        if isinstance(node,ast.Constant)and type(node.value)is int:
            if node.value==33:node.value=6;counts+=1
            elif node.value==6:node.value=1;suites+=1
            elif node.value==1643:node.value=568;members+=1
        if isinstance(node,ast.Constant)and isinstance(node.value,str):
            node.value=node.value.replace('PG3680','PG3682').replace('staticSixModules','staticSelectedModules').replace('all44 actual cases/all1643 physical Main required','actual six cases/all568 selected Main required')
    p.base.require((counts,suites,members)==(3,2,1),'exact case/suite/physical counters')
    # Cached upstream dependencies are permitted only if EVERY Main/resource/debug byte matches
    # the actual qualified whole. These reads neither install nor mutate shared Maven artifacts.
    raw=ast.unparse(ast.fix_missing_locations(tree))
    anchor="start = datetime.datetime.now(datetime.timezone.utc).isoformat()"
    p.base.require(raw.count(anchor)==1,'one before-execution dependency boundary')
    dep=r'''
for dependency in ['protocol','storage','bootstrap']:
 cached=B/('m2/repository/dev/codex/schubert/schubert-nk-'+dependency+'/0.1.0-SNAPSHOT/schubert-nk-'+dependency+'-0.1.0-SNAPSHOT.jar')
 qualified=B/('source-full-PG3412/src/schubert-nk-'+dependency+'/target/schubert-nk-'+dependency+'-0.1.0-SNAPSHOT.jar')
 require(sha(qualified)==INPUT['priorJarHashes'][dependency],'qualified original upstream Jar')
 with zipfile.ZipFile(cached)as z:
  require(len(z.namelist())==len(set(z.namelist())),'unique cached upstream members')
  cached_members={n:z.read(n)for n in z.namelist()}
 with zipfile.ZipFile(qualified)as z:require(cached_members=={n:z.read(n)for n in z.namelist()},'all upstream class/resource/debug bytes identical')
'''
    raw=raw.replace(anchor,dep+'\n'+anchor)
    complete='INPUT={}\n'+inspect.getsource(p.base.require)+'\n'+inspect.getsource(p.base.classify)+'\n'+raw
    p.base.require(check(complete,'<corrected batch-six>')==0,'complete namespace static0')
    return raw


def main():
    raw=inspect.getsource(p.base.main).replace('pg3348-related-boundary-group-v1','pg3682-typed-inode-corrected-v1').replace('PG3348','PG3682')
    ns={**p.base.__dict__,'SOURCE':p.SOURCE,'CLASSES':CLASSES,'validate':validate,'SERVER':server_source()}
    exec(compile(raw,'<only unexecuted batch-six>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())

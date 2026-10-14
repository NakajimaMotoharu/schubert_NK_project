"""Separate full seven-phase finite pointer/original/DB/resource proof after once publication."""
import inspect
from pyflakes.api import check
import pg2850_network_cold_ro_post as prior
import pg1453_current_cold_post as runner
import pg2852_network_cold_publication_sources as s
from pg1446_current_cold_stage import W,P
from pg1674_critical_management_gate import management_gate

SLOT='pg2860-network-cold-publication-independent-post-v1'


def payload():
    raw=prior.payload().replace(prior.SLOT,SLOT).replace('PG2850-network-cold-ro-independent-post-v1','PG2860-network-cold-publication-independent-post-v1')
    raw=raw.replace(s.ro.SAVE,s.SAVE).replace('candidateImmutableVerified=true','finiteColdActivation=true')
    raw=s.unused.one(raw,"require(pathlib.Path('/opt/schubert-nk/current').readlink()==release)",
        "require(str(pathlib.Path('/opt/schubert-nk/current').readlink())=='/opt/schubert-nk/releases/0.1.0-PG2802')")
    raw=s.unused.one(raw,"require(set(before)=={'current','runtime','parent'})","require(set(before)=={'immutable','trees','runtime','parent','beginNs'})")
    raw=raw.replace("first==before['current']","first==before['immutable']")
    old="require(runtime[n][2:6]==[0,0,stat.S_IFDIR|0o700,2] and not os.listdir(ROOT/n) and not os.listxattr(ROOT/n))"
    new="""require(runtime[n][2:6]==[0,0,stat.S_IFDIR|0o700,2] and not os.listxattr(ROOT/n))
  require(set(os.listdir(ROOT/n))==({'epoch.current'}if n=='startup'else set()))"""
    raw=s.unused.one(raw,old,new)
    addition=""" import types,time
 pub=types.ModuleType('independent_newboot_finite');exec(PUB_SOURCE,pub.__dict__)
 io=types.ModuleType('independent_finite_capture');exec(IO_SOURCE,io.__dict__)
 original=json.loads((prepared/'before.private.json').read_bytes())
 epoch=(prepared/'new-epoch.private').read_bytes()
 require((prepared/'old-approval.private').read_bytes()==pub.OLD_APPROVAL)
 require((prepared/'old-current.private').read_bytes()==pub.OLD_LINK.encode('ascii'))
 phases=[('before.private.json','before'),('epoch.private.json','epoch'),('approval.private.json','approval'),
  ('link-staged.private.json','link-staged'),('after.private.json','after'),('database-closed.private.json','after'),('release.private.json','release')]
 for name,phase in phases:
  value=json.loads((prepared/name).read_bytes())
  require(value['parent']==original['parent']and value['beginNs']==original['beginNs']and value['immutable']==original['immutable'])
  pub.verify(original['trees'],value['trees'],phase,epoch,original['beginNs'],time.time_ns())
 trees={root:io.direct_tree(root)for root in (pub.STARTUP,pub.APPROVAL,pub.CURRENT)}
 pub.verify(original['trees'],trees,'after',epoch,original['beginNs'],time.time_ns())
 require(trees==before['trees'])
 archived=io.path_record(prepared/'current-link.private')
 pub.verify_retained(pub.CURRENT+'/current',original['trees'][pub.CURRENT][pub.CURRENT+'/current'],archived,'after',trees,original['beginNs'],time.time_ns())
 require(archived['metadata'][5]==1 and archived['target']==pub.OLD_LINK)
 require(not os.path.lexists(pathlib.Path(pub.CURRENT)/'pg2852-current.part'))
 require((ROOT/'startup/epoch.current').read_bytes()==epoch)
 require((pathlib.Path(pub.APPROVAL)/'current').read_bytes()==pub.NEW_APPROVAL)
 require(complete==b'allScopesReturnedNormally=true\\nfiniteColdActivation=true\\nepochDbBusinessWrites=0\\n')
 require(first==snapshot()and runtime==runtime_check())
"""
    raw=s.unused.one(raw,'finally:\n errors=[]',addition+'finally:\n errors=[]')
    raw=s.unused.one(raw,"'candidateNotActivated':True,","'candidateNotActivated':False,'coldPublicationSevenPhasesVerified':True,'linkedOldCurrentPreserved':True,'newCanonicalInvalidNoPermission':True,'newCurrentSource':"+repr(s.unused.CANDIDATE)+',')
    # This standalone oracle binds the same approved literals independently; it
    # does not call any Production publication or expected-byte generator.
    head='PUB_SOURCE='+repr(s.bind(inspect.getsource(s.finite)))+'\nIO_SOURCE='+repr(inspect.getsource(s.capture))+'\n'
    raw=head+raw
    if check(raw,'<whole seven phase independent publication post>'):raise ValueError('complete standalone publication post namespace required')
    compile(raw,'<actual full cold publication independent post>','exec');return raw


def main():
    raw=inspect.getsource(runner.main).replace('pg1452-current-cold-owned-prepare-v1','pg2858-network-cold-publication-owned-activate-v1').replace('pg1453-current-cold-independent-post-v1',SLOT)
    ns={**runner.__dict__,'payload':payload,'W':W}
    exec(compile(raw,'<independent full publication post dispatcher>','exec'),ns)
    with management_gate(P/'current-management-critical.lock'):return ns['main']()


if __name__=='__main__':raise SystemExit(main())

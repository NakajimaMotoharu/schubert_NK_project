"""Independent SSC254/255 finite native metadata projection, PT-DEP-1148002."""
COVERAGE='/run/schubert-nk/pt-coverage'
ROLES={'root-api193':'root','root-web193':'root','ordinary-api193':'schubert-api','ordinary-web193':'schubert-web','ordinary-inspector196':'schubert-inbox-inspector'}
LEGACY={'parent','backup','cleanup','expiry','inspector','root-api'}
UNIT_ROLES={'schubert-nk-morning-controller.service':{'parent'},'schubert-nk-api.service':{'root-api193','ordinary-api193'},'schubert-nk-web.service':{'root-web193','ordinary-web193'},'schubert-nk-backup.service':{'backup'},'schubert-nk-cleanup.service':{'cleanup'},'schubert-nk-expiry-cleanup.service':{'expiry'},'schubert-nk-inbox-inspector.service':{'ordinary-inspector196'}}


def namespace_config():
 prefix=COVERAGE+'/'
 actual={u:{p.removeprefix(prefix)for p in show(u,{'ReadWritePaths','LoadState'})['ReadWritePaths'].split()if p.startswith(prefix)}for u in UNIT_ROLES}
 require(actual==UNIT_ROLES and all(show(u,{'LoadState'})['LoadState']=='loaded'for u in UNIT_ROLES))


def coverage_delta(actual,previous,identities):
 import stat
 if type(actual)is not dict or type(previous)is not dict or COVERAGE not in actual or COVERAGE not in previous:return False
 if any(p not in actual or actual[p]!=v for p,v in previous.items()if p!=COVERAGE):return False
 extra=set(actual)-set(previous)
 if not extra<={COVERAGE+'/'+n for n in ROLES}:return False
 a,b=actual[COVERAGE],previous[COVERAGE];am,bm=a['metadata'],b['metadata']
 if len(am)!=9 or len(bm)!=9 or am[:4]!=bm[:4]or am[2:4]!=[0,0]or a['sha256']is not None or b['sha256']is not None:return False
 if bm[4]!=stat.S_IFDIR|0o711 or am[4]not in [stat.S_IFDIR|0o711,stat.S_IFDIR|0o755]or am[5]!=bm[5]+len(extra):return False
 if extra and am[4]!=stat.S_IFDIR|0o755:return False
 if not extra and am[6:8]!=bm[6:8]:return False
 if am[6]<bm[6]or am[7]<bm[7]or am[8]<bm[8]:return False
 if type(identities)is not dict or set(identities)!=set(ROLES):return False
 for p in extra:
  n=p.removeprefix(COVERAGE+'/');v=actual[p]['metadata']
  if len(v)!=9 or any(type(x)is not int or x<0 for x in v)or v[1]<1 or v[2:5]!=[*identities[n],stat.S_IFDIR|0o700]or v[5]!=2 or actual[p]['sha256']is not None:return False
 return True


def coverage_preserved(actual,previous):
 ids={n:[int(command(['/usr/bin/id','-u',a])),int(command(['/usr/bin/id','-g',a]))]for n,a in ROLES.items()}
 require(coverage_delta(actual,previous,ids))
 for n in ROLES:
  p=pathlib.Path(COVERAGE,n)
  if not p.exists():continue
  require(not list(p.iterdir())and not os.listxattr(p)and command(['/usr/bin/findmnt','--target',str(p),'--output','FSTYPE','--noheadings']).strip()==b'tmpfs')
 require({p.name for p in pathlib.Path(COVERAGE).iterdir()}<=set(ROLES)|LEGACY)
 return True

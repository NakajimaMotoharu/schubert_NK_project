"""Independent current existing20 post: fresh refs, exact whole20 extra witnesses."""
from pathlib import Path
from pg662_sources import replace

R=Path(__file__).resolve().parent


def source():
    raw=(R/'pg572_bootstrap_final.py').read_text()
    raw=replace(raw,(
        ('pg570','pg664'),('PG570','PG664'),('pg572','pg665'),('PG572','PG665'),
        ('1d42516cf498d3ae58b5ba8a6253844676ed9162c588492f0cf78478a31ea2c6','8767e53ccfc2ea3f434689674dad7395feaef31cec48d53a92bc6fd7eed81c08'),
        ('8cd3195cc3a326ba4a2a84ba2cd5abe6e931bcd2131c2609c29983e9c85bd164','fa1cd96cc5110f8bb582d7befecb9fd13f66cea63f707b1a03db9e3d5287ef98'),
        ('c0592572f0f94070964eb3ee4ff4903c','65bfe1da3b9e454997f1d899fea9510e'),
        ("'907340'","'2142585'"),
        ('a224ea9cf421b06e7029b1f8845f2a7eb3d620b5ec2bdf90bfe64c731b99515b','57a5355d7d0c6a3af7ff2ec619eacee20ee9236916de25e02b95953ffa6aa2fe'),
        ('969d8ded10c0bf5841d9e3a5c531e922caf4a24a','36fe7a0b938489d61d17d49c1c30a6fbbef699d5'),
        ('PG548','PG631'),('pg548-manifest.sig','pg631-manifest.sig'),
        ('pg557-native-stop-v1','pg655-native-stop-v1'),
        ('import ast,datetime,hashlib,json,os,pathlib,re,stat,subprocess,sys,time','import ast,datetime,dbus,hashlib,json,os,pathlib,re,stat,subprocess,sys,time'),
    ))
    addon=r'''
initial=strict(base/'pg661-completed-baseline-v1/before.private.json',0o600,67108864)
require(hashlib.sha256(initial).hexdigest()=='8963796af5d95b30f01169d79bed2d6055782988af497dd09903b8f73a8af4d8');initial=json.loads(initial);require(len(initial)==20)
require(all(b[key]==initial[key]for key in b)and len(a['rows']['schubert.batch_runs'])==514)
require(actor['ticks']=='11164505'and not pathlib.Path('/proc',actor['pid']).exists())
require(jobs[0]['JOB_ID']=='119175'and jobs[0]['__MONOTONIC_TIMESTAMP'].isdigit())
require(a['units'][UNIT]['ExecMainStartTimestampMonotonic']=='111645058422'and a['units'][UNIT]['ExecMainExitTimestampMonotonic']=='111646651773')
require(111645058422<=int(jobs[0]['__MONOTONIC_TIMESTAMP'])<=111675058422)
for name in('bootstrap-admin-username','bootstrap-admin-password'):
 p=proof/(name+'.retired.private');s=metadata(p);require(s[2:6]==[0,0,stat.S_IFREG|0o400,1]and 1<=s[6]<=256 and not os.listxattr(p))
require(re.fullmatch(rb'pgpt_[0-9a-f]{32}',strict(proof/'bootstrap-admin-username.retired.private',0o400,256))is not None)
require(re.fullmatch(rb'[A-Za-z0-9_-]{43}',strict(proof/'bootstrap-admin-password.retired.private',0o400,256))is not None)
def extra():
 from pg529_dependency_graph import dependency_graph
 require(dependency_graph({u:show(u,{'Requires','Before','After','PartOf','BindsTo'})for u in UNITS},UNITS)==initial['dependencies'])
 for key,path in (('bootstrapOldProofs','pg570-bootstrap-existing-v1'),('bootstrapTools','pg570-bootstrap-tools-v1')):require(tree(base/path)==initial[key])
 require(show('caddy.service',{'ExecStartPre'})['ExecStartPre']==initial['caddyPre'])
 require(not list(pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d').iterdir())and initial['runtime']is None)
 for key in ('unitFiles','pid1Stop'):
  for name,witness in initial[key].items():
   p=pathlib.Path(name if key=='unitFiles'else str(base/'pg655-native-stop-v1'/(name+'.stopped.private')))
   require(metadata(p)==witness['metadata']and hashlib.sha256(p.read_bytes()).hexdigest()==witness['sha256'])
 p=pathlib.Path('/etc/schubert-nk/release-approval/current');require(metadata(p)==initial['approval']['metadata']and hashlib.sha256(p.read_bytes()).hexdigest()==initial['approval']['sha256'])
 raw=command(['journalctl','--boot=cc9ed8747f4f450ea1888de1e42c8441','_PID=1','UNIT=schubert-nk-morning-controller.service','INVOCATION_ID=095f6d1d7f8442b7b2b44ae59a4314f5','-o','json','--no-pager'])
 require([json.loads(line)for line in raw.splitlines()]==initial['parentPid1'])
bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager');refs=[]
try:
 for u in UNITS:manager.RefUnit(u);refs.append(u)
 extra();snapshot();extra();snapshot()
finally:
 for u in reversed(refs):manager.UnrefUnit(u)
 bus.close()
'''
    return replace(raw,(
        ('snapshot();snapshot()',addon),
        ("'whole187SignedArtifactBytesVerified':True", "'whole187SignedArtifactBytesVerified':True,'full20Fields':True,'newMetadataScopesNormal':True,'batchRows':514,'bootstrapElapsedSeconds':1.593351"),
    ))


if __name__=='__main__':
    exec(compile(source(),str(R/'pg665_final.py'),'exec'),{'__name__':'__main__','__file__':str(R/'pg665_final.py')})

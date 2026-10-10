"""Preserve exact current canonical runtime and UNKNOWN owner without replay."""
import ast
import inspect
import json
from pg1164_runtime_failed_owner_proof import payload as previous
from pg1041_cold_policy_diagnostic import W
import pg1120_current_failed_capture as transport


def payload():
    s=previous().replace('runtime-failed-owner-proof-v1','canonical-runtime-owner-proof-v1')
    start=s.index('NATIVE_FILES=');end=s.index('\n',start)
    frozen=json.loads((W/'pg1175-runtime-frozen-v2.safe.json').read_bytes())
    if frozen['actualExit']!=0:raise ValueError('qualified actual canonical runtime tools refused')
    s=s[:start]+'NATIVE_FILES='+repr(frozen['fileHashes'])+s[end:]
    for old,new in [('native-five-post-v1/after.private.json','wrong-runtime-post-v1/after.private.json'),
                    ('03d3aab26b1da00c6c68cad0a54fc1dbd5074c82fa961036a732fdb24f78b612','a936fd3e8f851255acc66156a99db967b52195033dea4b75cf2515e3bce7b36c'),
                    ('415524','420139'),('4807423','5003981'),('415553','420168'),('4807540','5004100'),
                    ('dff614fe6734a813f68a6c816bce48da90749373d222093c8a952d30b8764e5a','fa4551d834910cac50c0292d04405b0ec512dc984079969a50ccc3f9c2fb1f8b'),
                    ('76b5416846c91bdd5ec9f0261fec0544680b9326de3cd9a25867b448263aed2d','0ab4c85f987a6c25670389e575132f7a9bc967b052390b3541651f2e03878a99'),
                    ('pg1160-runtime-tools-v1','pg1172-runtime-tools-v2'),('pg1160-runtime-resume-v1','pg1172-runtime-resume-v1'),
                    ('7b9f79c57231cd87e4ee4aa8fb9c95b520bd26d8ebefb7cc5ffd9cd115547d7d','ab2d586bc6830e3ebb03e7ecc3a6f2223d6fd4818a4535972f09739de24061d8')]:
        if old not in s:raise ValueError('fixed canonical owner insertion refused')
        s=s.replace(old,new)
    s=s.replace("reload_policy.configuration(CURRENT['configuration'],configuration,True)","canonical_configuration(CURRENT['configuration'],configuration)")
    start=s.index('def current():');end=s.index('def owner():',start)
    s=s[:start]+CURRENT+s[end:]
    i=s.index('JAVA=420139');s=s[:i]+CONFIG+s[i:]
    ast.parse(s);return s


CONFIG=r'''
def canonical_configuration(old,current):
 require(set(old)==set(current))
 for unit,before in old.items():
  after=current[unit];require(set(before)==set(after))
  if unit=='schubert-nk-morning-controller.service':
   require(all(before[k]==after[k]for k in before.keys()-{'ExecStart','DropInPaths'}))
   a,b=exec_record(before['ExecStart']),exec_record(after['ExecStart']);require(a is not None and b is not None and b[:3]==(a[0],a[1]+' --resume 343a5a1b-d064-47d5-88c2-31c36d7ba7a4',a[2])and b[3:]==a[3:])
   require(after['DropInPaths']==before['DropInPaths']+' /run/systemd/system/schubert-nk-morning-controller.service.d/zz-pg1160-once-resume.conf')
  else:require(before==after)
'''
CURRENT=r'''
def current():
 v=capture();require({k:x for k,x in v.items()if k not in {'configuration','runtime'}}=={k:x for k,x in CURRENT.items()if k not in {'configuration','runtime'}})
 parent=pathlib.Path('/run/systemd/system');directory=parent/'schubert-nk-morning-controller.service.d';target=directory/'zz-pg1160-once-resume.conf'
 actual=tree(parent);before=CURRENT['runtime'];require(set(actual)==set(before)|{str(target)})
 require(actual[str(parent)]==before[str(parent)])
 a,b=actual[str(directory)],before[str(directory)];require(a['metadata'][:6]==b['metadata'][:6]and a['metadata'][7]>=b['metadata'][7]and a['metadata'][8]>=b['metadata'][8])
 require(md(target)[2:7]==[0,0,stat.S_IFREG|0o644,1,647]and hashlib.sha256(target.read_bytes()).hexdigest()=='d344cecf96e7a5219adf22b312420ff6e0a1b314834d230e476c507ade7903b0')
 require(target.read_bytes()==pathlib.Path('/var/lib/pgpt-s1-preservation/pg1172-runtime-resume-v1/new-runtime.private').read_bytes())
 v['runtime']=actual;return v
'''


def main():
    s=inspect.getsource(transport.main).replace('pg1120-current-failed-capture-v1','pg1177-canonical-runtime-owner-proof-v1').replace('PG1120-current-failed-capture-v1','PG1177-canonical-runtime-owner-proof-v1')
    env=dict(transport.__dict__);env['PAYLOAD']=payload();exec(compile(s,'<fixed canonical runtime owner proof>','exec'),env);return env['main']()


if __name__=='__main__':raise SystemExit(main())

"""SSC260 fixed failed runtime owner plus immutable wrong-file full proof."""
import ast
import inspect
import json
from pg1155_native_failed_owner_proof_v3 import payload as previous
from pg1041_cold_policy_diagnostic import W
from pg870_ordinary_before import parser_source
import pg1163_reload_policy as policy
import pg1120_current_failed_capture as transport


def payload():
    s=previous().replace('native-failed-owner-proof-v3','runtime-failed-owner-proof-v1')
    end=s.index('\n',s.index('NATIVE_FILES='))
    frozen=json.loads((W/'pg1161-runtime-frozen-v1.safe.json').read_bytes())
    if frozen['actualExit']!=0:raise ValueError('fixed runtime helper closure refused')
    s='NATIVE_FILES='+repr(frozen['fileHashes'])+s[end:]
    changes=[('terminal-management-post-v1/after.private.json','native-five-post-v1/after.private.json'),
             ('cfd139237f179e7531b94d28c1570c07af9612b476857f3eb479d9a732a7c0b9','03d3aab26b1da00c6c68cad0a54fc1dbd5074c82fa961036a732fdb24f78b612'),
             ('410279','415524'),('4653404','4807423'),('410308','415553'),('4653520','4807540'),
             ('98f1a3a4ae2d298e8eae985059cf6a30f3f203fbb5ede0ec95350b3ab9f15791','dff614fe6734a813f68a6c816bce48da90749373d222093c8a952d30b8764e5a'),
             ('48eb3b90dae4122879878b95aa6a7db29aff1a052c6b7cfddc4f981c8d262b3c','76b5416846c91bdd5ec9f0261fec0544680b9326de3cd9a25867b448263aed2d'),
             ('pg1148-native-five-tools-v3','pg1160-runtime-tools-v1'),('pg1148-native-five-recovery-v1','pg1160-runtime-resume-v1'),
             ('f9790b619e2420ce980281c7ef5317e93b9efd93b787c063cdd7e3961cde2094','7b9f79c57231cd87e4ee4aa8fb9c95b520bd26d8ebefb7cc5ffd9cd115547d7d')]
    for old,new in changes:
        if old not in s:raise ValueError('fixed current runtime ownership binding refused')
        s=s.replace(old,new)
    start=s.index(' for u in units:\n  if u==\'artemis.service\':broker_policy.configuration')
    end=s.index(' resource_zero()\n return',start)
    s=s[:start]+" reload_policy.configuration(CURRENT['configuration'],configuration,True)\n"+s[end:]
    marker=' v=capture();require(v==CURRENT);return v'
    replacement=''' v=capture();require({k:x for k,x in v.items()if k!='configuration'}=={k:x for k,x in CURRENT.items()if k!='configuration'})
 runtime=pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d');target=runtime/'pg1160-once-resume.conf'
 require({p.name for p in runtime.iterdir()}=={target.name}and md(runtime)[2:6]==[0,0,stat.S_IFDIR|0o755,2])
 require(md(target)[2:7]==[0,0,stat.S_IFREG|0o644,1,647]and hashlib.sha256(target.read_bytes()).hexdigest()=='d344cecf96e7a5219adf22b312420ff6e0a1b314834d230e476c507ade7903b0')
 prepared=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1160-runtime-resume-v1/new-runtime.private');require(prepared.read_bytes()==target.read_bytes())
 v['runtime']=tree(pathlib.Path('/run/systemd/system'));return v'''
    if s.count(marker)!=1:raise ValueError('fixed full runtime proof insertion refused')
    s=s.replace(marker,replacement)
    nodes=[n for n in ast.parse(inspect.getsource(policy)).body if isinstance(n,ast.FunctionDef)or isinstance(n,ast.Assign)and all(isinstance(t,ast.Name)and t.id in {'MORNING','WRONG','RESET'}for t in n.targets)]
    snippet=ast.unparse(ast.Module(body=nodes,type_ignores=[]))
    s=parser_source()+"import types,re\nreload_policy=types.ModuleType('fixed-all-field-reload');reload_policy.exec_record=exec_record\nexec("+repr(snippet)+",reload_policy.__dict__)\n"+s
    ast.parse(s);return s


def main():
    s=inspect.getsource(transport.main).replace('pg1120-current-failed-capture-v1','pg1164-runtime-failed-owner-proof-v1').replace('PG1120-current-failed-capture-v1','PG1164-runtime-failed-owner-proof-v1')
    env=dict(transport.__dict__);env['PAYLOAD']=payload();exec(compile(s,'<fixed failed runtime allfield owner proof>','exec'),env);return env['main']()


if __name__=='__main__':raise SystemExit(main())

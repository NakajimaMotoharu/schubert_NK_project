"""Current1068 cold ordinary admission declaration and private before, starts0."""
import ast
import inspect
from pg1103_linked_preservation_post import payload as previous
from pg870_ordinary_before import parser_source
from pg870_ordinary_policy import ordinary_argv
from pg1051_cold_tree_preflight_v2 import dispatch


def payload():
    raw=previous().replace('PG1103-linked-preservation-post-v1','PG1106-ordinary-cold-before-v1').replace('pg1103-newcurrent-post-v1','pg1106-ordinary-cold-before-v1')
    marker='\ndef post():\n'
    # previous AST-unparsed prefix preserves the appended body literal spacing.
    if raw.count(marker)!=1:raise ValueError('fixed ordinary preflight insertion refused')
    raw=raw.replace(marker,'\nimport re\n'+inspect.getsource(ordinary_argv)+'\n'+parser_source()+EXTRA+marker)
    raw=raw.replace('after=post();assert after==post()','after=ordinary_post();assert after==ordinary_post()')
    raw=raw.replace("'observerNormalClose':True,'afterPrivateSha256'", "'observerNormalClose':True,'ordinaryNoargs':True,'starts0':True,'afterPrivateSha256'")
    ast.parse(raw);return raw


EXTRA=r'''
def ordinary_post():
 value=post();root=pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG1068')
 command=ordinary_argv((root/'systemd/schubert-nk-morning-controller.service').read_bytes(),
   pathlib.Path('/etc/systemd/system/schubert-nk-morning-controller.service.d/pg477-native-coverage.conf').read_bytes())
 effective=env['exec_record'](value['snapshot']['configuration']['schubert-nk-morning-controller.service']['ExecStart'])
 assert effective is not None and effective[:3]==('/usr/bin/java',command,'no')
 assert '--resume'not in command and command.endswith(' dev.codex.schubert.nk.batch.file.MorningProcessMain')
 budget=env['command'](['systemctl','show','schubert-nk-morning-controller.service','--value','--property=TimeoutStartUSec'],4096)
 assert budget==b'30min\n'
 assert not pathlib.Path('/var/lib/schubert-nk/maintenance/active').exists()
 files={}
 for config in value['snapshot']['configuration'].values():
  for name in (config['FragmentPath'],*config['DropInPaths'].split()):
   assert name.startswith(('/etc/systemd/system/','/usr/lib/systemd/system/','/lib/systemd/system/'))
   p=pathlib.Path(name);m=io.metadata(p.lstat());assert stat.S_ISREG(m[4])and m[2]==0 and not m[4]&0o022 and m[5]==1 and not os.listxattr(p)
   files[name]={'metadata':m,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()};assert m==io.metadata(p.lstat())
 assert set(value['runtime'])==set(expected_runtime)
 cov=pathlib.Path('/run/schubert-nk/pt-coverage')
 assert all(not list(p.iterdir())for p in cov.iterdir())
 value.update(unitFiles=files,ordinaryNoargs=True,oldOriginalCompleted=True,rootBudgetSeconds=1800,
              startupAgentCommandSha256=hashlib.sha256(command.encode()).hexdigest(),nativeBeforeEmpty=True)
 return value
'''


if __name__=='__main__':dispatch('PG1106-ordinary-cold-before-v1','pg1106-ordinary-cold-before-v1',payload())

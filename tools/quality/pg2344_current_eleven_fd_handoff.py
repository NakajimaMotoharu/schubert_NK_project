"""Published SSC284: whole same-peer fresh child eleven-FD proof, owned TERM once."""
import inspect
import subprocess
import types
from pyflakes.api import check
import pg2311_current_resume_pair_handoff as prior
from pg2338_current_reloaded_pair_proof import body,bound,SOURCE
from pg2322_current_partial_runtime_pair_proof import bound as first_bound

SLOT='pg2344-current-eleven-fd-handoff-v1'
PROOF_SLOT='pg2342-current-reloaded-pair-proof-v2'
PROOF_SHA='a8eb610cff840dc9be93eb83f59d369097ec145d743c92e62d1e5344a41147ff'


def fresh_child(old,actual,parent,upper_ns):
    keys={'pid','ticks','argvSha256','authority','cgroup','fds','busNames'}
    if type(old)is not dict or type(actual)is not dict or set(old)!=keys or set(actual)!=keys or type(parent)is not dict or type(upper_ns)is not int or upper_ns<0:raise ValueError('complete current child required')
    if any(old[k]!=actual[k]for k in keys-{'fds'}):raise ValueError('same child authority required')
    if type(old['fds'])is not dict or type(actual['fds'])is not dict or set(old['fds'])!=set(actual['fds'])or set(old['fds'])!={str(i)for i in range(11)}:raise ValueError('exact eleven child FDs required')
    for name,a in old['fds'].items():
        b=actual['fds'][name]
        if type(a)is not dict or type(b)is not dict or set(a)!={'metadata','target'}or set(b)!=set(a)or a['target']!=b['target']:raise ValueError('same complete child target required')
        for value in [a['metadata'],b['metadata']]:
            if type(value)is not list or len(value)!=9 or any(type(v)is not int or v<0 for v in value):raise ValueError('typed nine child attributes required')
        if name=='5':
            if a['target']!='/run'or a['metadata'][:7]!=b['metadata'][:7]or any(not a['metadata'][i]<=b['metadata'][i]<=upper_ns for i in [7,8]):raise ValueError('finite shared child run chrono required')
        elif a!=b:raise ValueError('all other ten child FD attributes unchanged required')
    if type(parent.get('fds'))is not dict or actual['fds']['5']!=parent['fds'].get('31')or actual['fds']['5']!=parent['fds'].get('90'):raise ValueError('three linked run witnesses required')
    return True


def payload():
    def corrected_body():
        raw=body()
        for old,new in [("fds[n]['metadata'][2:4]==[0,0]","tuple(fds[n]['metadata'][2:4])==(0,0)"),("fds['9']['metadata']==[28,4224,0,0,stat.S_IFREG|0o644,1,644,1791913648316105696,1791913648316105696]","tuple(fds['9']['metadata'])==(28,4224,0,0,stat.S_IFREG|0o644,1,644,1791913648316105696,1791913648316105696)")]:raw=raw.replace(old,new)
        return raw
    ns={**prior.__dict__,'body':corrected_body,'PROOF_SLOT':PROOF_SLOT,'PROOF_SHA':PROOF_SHA,'SLOT':SLOT}
    exec(compile(inspect.getsource(prior.payload),'<current eleven-FD generator>','exec'),ns)
    raw=bound(first_bound(ns['payload']()))
    raw=raw.replace("expected['candidateNotPlaced']is True","expected['partialRuntimeFileVerified']is True and expected['reloadKnownReturnedBeforePostGuard']is True")
    old=" require(fresh['child']==expected['pair']['child']and fresh['peer']==expected['pair']['peer'])"
    if raw.count(old)!=1:raise ValueError('one exact child fresh comparison required')
    raw=raw.replace(old," fresh_child(expected['pair']['child'],fresh['child'],fresh['parent'],time.time_ns())\n require(fresh['peer']==expected['pair']['peer'])")
    raw=inspect.getsource(fresh_child)+'\n'+raw
    if check(raw,'<whole SSC284 same-peer handoff>'):raise ValueError('all current handoff globals required')
    compile(raw,'<current same-peer eleven-FD handoff>','exec');return raw


def main():
    for path in ['documents/300_SS/340_batch・基盤/343_設定file・directory・初期data・migration・切戻し設計.md','documents/300_SS/350_運用・品質/353_障害検知・復旧runbook.md','documents/300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md']:
        local=subprocess.check_output(['git','show','HEAD:'+path],text=True)
        remote=subprocess.check_output(['git','show','origin/main:'+path],text=True)
        marker='## SSC-284（'
        def scope(value):return value[value.index(marker):].split('\n## ',1)[0]
        if scope(local)!=scope(remote):raise ValueError('published SSC284 scope required')
    fn=types.FunctionType(prior.main.__code__,{**prior.__dict__,'SLOT':SLOT,'PROOF_SLOT':PROOF_SLOT,'PROOF_SHA':PROOF_SHA,'SOURCE':SOURCE,'payload':payload},'current_eleven_fd_handoff')
    return fn()


if __name__=='__main__':raise SystemExit(main())

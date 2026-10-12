"""Fresh read-only all-normal-stop/current original proof before typed runtime mutation."""
import pg1583_current_stop_independent_post as prior
from pg1591_current_runtime_retirement_sources import SHA

def payload(seals):
    return prior.payload(seals).replace('PG1583-current-terminal-post-v1','PG1593-current-retirement-preflight-v1').replace('pg1583-current-terminal-post-v1','pg1593-current-retirement-preflight-v1')

def main():
    # The preflight reads original stop seals from1581/1580, not an invented
    # retirement completion. Only its output slot is new.
    host=prior.source().replace("base=W/'pg1583-current-terminal-post-v1'","base=W/'pg1593-current-retirement-preflight-v1'")
    marker="    if r.returncode==0:value.update(json.loads(r.stdout))"
    replacement=marker+"\n    if r.returncode==0:\n        if value['proofHashes']['after.private.json']['sha256']!="+repr(SHA)+":raise ValueError('current normal completed baseline changed')\n        value['privateBeforeSha256']="+repr(SHA)
    if host.count(marker)!=1:raise ValueError('current preflight result boundary absent')
    host=host.replace(marker,replacement)
    ns={**prior.prior.previous.transport.__dict__,'SOURCE':prior.SOURCE,'payload':payload}
    exec(compile(host,'<fresh full completed retirement preflight>','exec'),ns);return ns['main']()

if __name__=='__main__':raise SystemExit(main())

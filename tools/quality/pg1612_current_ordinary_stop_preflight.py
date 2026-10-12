"""Separate new-slot current complete seal equality, before any owned stop."""
import inspect
import pg1608_current_observation_full_seal_v3 as prior

def payload():return prior.payload().replace('pg1608-current-observation-full-seal-v3','pg1612-current-ordinary-stop-preflight-v1')

def main():
    raw=inspect.getsource(prior.prior.prior.prior.main).replace('pg1578-current-completed-seal-v1','pg1612-current-ordinary-stop-preflight-v1').replace('pg1577-current-root-done-receipt-v1','pg1601-current-newrun-done-receipt-v1')
    marker='    print(json.dumps(safe));return result.returncode'
    if raw.count(marker)!=1:raise ValueError('separate ordinary fullseal equality boundary refused')
    raw=raw.replace(marker,"    fixed=json.loads((W/'pg1608-current-observation-full-seal-v3/manifest.safe.json').read_bytes())\n    if result.returncode==0 and safe['privateBeforeSha256']!=fixed['privateBeforeSha256']:raise ValueError('ordinary fullseal changed before normal stop')\n    with(W/'pg1612-current-ordinary-stop-preflight-v1.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True);f.flush();os.fsync(f.fileno())\n"+marker)
    env={**prior.prior.prior.prior.__dict__,'payload':payload};exec(compile(raw,'<separate ordinary stop fullseal>','exec'),env)
    return env['main']()

if __name__=='__main__':raise SystemExit(main())

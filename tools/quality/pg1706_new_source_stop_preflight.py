"""Separate unchanged all-field complete-seal prerequisite; no stop permission."""
import inspect
import pg1702_new_source_completed_seal as seal
from pg1700_new_source_live_binding import SOURCE


def payload():
    return seal.payload().replace('pg1702-new-source-completed-seal-v1','pg1706-new-source-stop-preflight-v1')


def main():
    base=seal.prior.prior.prior.prior
    raw=inspect.getsource(base.main).replace('pg1578-current-completed-seal-v1','pg1706-new-source-stop-preflight-v1')
    raw=raw.replace('pg1577-current-root-done-receipt-v1','pg1701-new-source-done-receipt-v1')
    raw=raw.replace('4d6bcbddb417b76d27e52d5d9640752c300edccf',SOURCE)
    marker='    print(json.dumps(safe));return result.returncode'
    if raw.count(marker)!=1:raise ValueError('one unchanged whole-seal join required')
    raw=raw.replace(marker,"    fixed=json.loads((W/'pg1702-new-source-completed-seal-v1/manifest.safe.json').read_bytes())\n    if result.returncode==0 and safe['privateBeforeSha256']!=fixed['privateBeforeSha256']:raise ValueError('whole current seal changed before owned stop')\n    with(W/'pg1706-new-source-stop-preflight-v1.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True);f.flush();os.fsync(f.fileno())\n"+marker)
    ns={**base.__dict__,'payload':payload}
    exec(compile(raw,'<new Source separate all-field preflight>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())

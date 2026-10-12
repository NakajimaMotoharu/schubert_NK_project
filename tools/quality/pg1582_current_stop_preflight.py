"""Separate new-slot full current seal; fixed equality required before stop."""
import inspect
import pg1578_current_completed_seal as prior

def payload():
    return prior.payload().replace('pg1578-current-completed-seal-v1','pg1582-current-stop-preflight-v1')

def main():
    raw=inspect.getsource(prior.main).replace('pg1578-current-completed-seal-v1','pg1582-current-stop-preflight-v1')
    # Fixed dispatcher ABI expects a single safe file, while full capture keeps
    # its raw payload and stderr privately in a new directory.
    raw=raw.replace("    print(json.dumps(safe));return result.returncode", "    fixed=json.loads((W/'pg1578-current-completed-seal-v1/manifest.safe.json').read_bytes())\n    if result.returncode==0 and safe['privateBeforeSha256']!=fixed['privateBeforeSha256']:raise ValueError('current fullseal changed before owned stop')\n    with(W/'pg1582-current-stop-preflight-v1.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True);f.flush();os.fsync(f.fileno())\n    print(json.dumps(safe));return result.returncode")
    env={**prior.__dict__,'payload':payload};exec(compile(raw,'<separate current preflight>','exec'),env)
    return env['main']()

if __name__=='__main__':raise SystemExit(main())

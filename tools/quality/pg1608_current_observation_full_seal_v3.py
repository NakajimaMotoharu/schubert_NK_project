"""Fresh separate-bound full seal; no Root/services mutation or formal acceptance."""
import inspect
import pg1606_current_ordinary_full_seal_v2 as prior
from pg1607_current_observation_rows_oracle_v3 import source as oracle

def payload():
    raw=prior.payload()
    raw=prior.prior.once(raw,'ORACLE='+repr(prior.oracle()),'ORACLE='+repr(oracle()))
    raw=raw.replace('pg1606-current-ordinary-full-seal-v2','pg1608-current-observation-full-seal-v3')
    raw=prior.prior.once(raw,"proof.done.decode('ascii').splitlines()[4])","proof.done.decode('ascii').splitlines()[4],OBSERVED_UPPER)")
    # Freeze once outside the three complete captures. It is independently
    # observed data, not a changed Production deadline or an expected result.
    raw='import datetime\nOBSERVED_UPPER=datetime.datetime.now(datetime.timezone.utc).isoformat()\n'+raw
    raw=raw.replace("'actualExit':0,'privateBeforeSha256'","'actualExit':0,'observedUpperUtc':OBSERVED_UPPER,'privateBeforeSha256'")
    compile(raw,'<current separate-bound observation seal>','exec');return raw

def main():
    raw=inspect.getsource(prior.prior.prior.main).replace('pg1578-current-completed-seal-v1','pg1608-current-observation-full-seal-v3').replace('pg1577-current-root-done-receipt-v1','pg1601-current-newrun-done-receipt-v1')
    ns={**prior.prior.prior.__dict__,'payload':payload};exec(compile(raw,'<new observation-bound seal transport>','exec'),ns)
    return ns['main']()

if __name__=='__main__':raise SystemExit(main())

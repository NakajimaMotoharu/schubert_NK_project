"""New-only raw metadata tuple boundary correction; all fixed identity values unchanged."""
import types
import pg2338_current_reloaded_pair_proof as prior

SLOT='pg2342-current-reloaded-pair-proof-v2'


def payload():
    raw=prior.payload().replace(prior.SLOT,SLOT)
    for old,new in [("fds[n]['metadata'][2:4]==[0,0]","tuple(fds[n]['metadata'][2:4])==(0,0)"),("fds['9']['metadata']==[28,4224,0,0,stat.S_IFREG|0o644,1,644,1791913648316105696,1791913648316105696]","tuple(fds['9']['metadata'])==(28,4224,0,0,stat.S_IFREG|0o644,1,644,1791913648316105696,1791913648316105696)")]:
        if raw.count(old)!=1:raise ValueError('one raw metadata boundary required')
        raw=raw.replace(old,new)
    compile(raw,'<current reloaded pair metadata tuple>','exec');return raw


def main():
    base=prior.prior.prior
    fn=types.FunctionType(base.main.__code__,{**base.__dict__,'SLOT':SLOT,'payload':payload},'current_reloaded_pair_v2')
    return fn()


if __name__=='__main__':raise SystemExit(main())

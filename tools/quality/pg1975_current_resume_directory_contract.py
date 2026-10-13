"""Distinct actual parent/child link counts; all current metadata and literal bytes retained."""
import inspect
import pg1974_current_resume_input_inventory as prior

SLOT='pg1975-current-resume-directory-contract-v1'


def payload():
    raw=prior.payload();old="metadata(p)[2:6]==[0,0,stat.S_IFDIR|0o755,2]"
    if raw.count(old)!=1:raise ValueError('one actual metadata loop required')
    raw=raw.replace(old,"metadata(p)[2:6]==[0,0,stat.S_IFDIR|0o755,3 if p==runtime else 2]")
    from pyflakes.api import check
    if check(raw,'<actual parent child current directory>'):raise ValueError('all payload globals required')
    return raw


def main():
    ns={**prior.prior.__dict__,'SLOT':SLOT,'PAYLOAD':payload()}
    exec(compile(inspect.getsource(prior.prior.main),'<actual parent child current inventory>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())

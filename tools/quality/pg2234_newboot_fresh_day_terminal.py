"""Current-boot legitimate fresh-day DONE receipt; read-only, never old-run replay."""
import inspect
import pg2182_newsource_terminal_receipt as prior

SLOT='pg2234-newboot-fresh-day-terminal-v1'


def payload(binding):
    raw=prior.payload(binding).replace(prior.SLOT,SLOT)
    raw=raw.replace("'a31dd6da-cf4c-4d0f-ab7c-5c8bb59c0b75'","'a31dd6da-cf4c-4d0f-ab7c-5c8bb59c0b75','02bddddf-9cd3-4668-9d67-7561232fc4e4'")
    raw=raw.replace("'9026b2ab-bb42-49cd-a2bd-4c661049dce3'","'9026b2ab-bb42-49cd-a2bd-4c661049dce3','20b86040-ffd5-4d17-9fca-5d83048ba905'")
    compile(raw,'<newboot actual fresh-day terminal>','exec')
    return raw


def entry():
    raw=inspect.getsource(prior.prior.previous.main).replace('pg2019-fresh-resume-live-binding-complete-v1','pg2230-newboot-current-live-binding-v1').replace('pg2010-parent-watch-v1','pg2224-parent-watch-v1')
    raw=raw.replace("payload(actual['binding'])","payload({**actual['binding'],'rootPid':actual['rootPid']})")
    ns={**prior.prior.previous.__dict__,'SOURCE':prior.SOURCE,'SLOT':SLOT,'payload':payload}
    exec(compile(raw,'<fresh-day current read-only terminal transport>','exec'),ns)
    return ns['main']


if __name__=='__main__':raise SystemExit(entry()())

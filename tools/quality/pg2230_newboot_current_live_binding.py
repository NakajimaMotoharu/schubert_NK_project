"""Actual newboot fresh-day Root/run capture; no old activation or PID reuse."""
import inspect
from pyflakes.api import check
import pg1457_current_day_binding as prior
from pg2208_current_newboot_cold_sources import bindings,BOOT
from pg2176_newsource_normal_observer import SOURCE,BOM


def compose(expected):
    raw=bindings(prior.compose(expected)).replace('3d69f5af6bac46b1a5407591c4a79a0d',BOOT.replace('-',''))
    if check(raw,'<actual current live Root binding>'):raise ValueError('whole actual binding exports required')
    compile(raw,'<actual current fresh-day Root binding>','exec');return raw


def main():
    raw=inspect.getsource(prior.main).replace('pg1456-current-day-once-v1','pg2227-newboot-fresh-day-once-v1').replace('pg1457-current-day-live-binding-v1','pg2230-newboot-current-live-binding-v1')
    ns={**prior.__dict__,'SOURCE':SOURCE,'BOM':BOM,'compose':compose}
    exec(compile(raw,'<actual current Root binding transport>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())

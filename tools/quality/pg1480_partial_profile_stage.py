"""New-only immutable current ABI readonly profiler stage; no worker start."""
import inspect
import pg1446_current_cold_stage as previous

OUTNAME='pg1480-partial-profile-stage-v1'


def main():
    body=inspect.getsource(previous.main)
    for old,new in [('pg1444-current-cold-frozen-v2.safe.json','pg1478-partial-profile-frozen-v1.safe.json'),
                    ('pg1446','pg1480'),('PG1446','PG1480'),
                    ('pg1441-current-cold-tools-v1','pg1478-partial-original-tools-v1')]:
        if old not in body:raise ValueError('fixed stage source binding absent')
        body=body.replace(old,new)
    ns={**previous.__dict__,'OUT':previous.W/OUTNAME,
        'TOOLS':previous.W/'pg1478-partial-original-tools-v1'}
    exec(compile(body,'<new-only immutable readonly profile stage>','exec'),ns)
    ns['main']();return 0


if __name__=='__main__':raise SystemExit(main())

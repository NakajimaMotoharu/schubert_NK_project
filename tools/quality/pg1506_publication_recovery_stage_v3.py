"""New-only immutable corrected 115 member stage; no recovery start."""
import inspect
import pg1446_current_cold_stage as previous

OUTNAME='pg1506-publication-recovery-stage-v3'
def main():
    raw=inspect.getsource(previous.main)
    for old,new in [('pg1444-current-cold-frozen-v2.safe.json','pg1505-publication-recovery-frozen-v3.safe.json'),('pg1446','pg1506'),('PG1446','PG1506'),('pg1441-current-cold-tools-v1','pg1505-publication-only-tools-v3')]:
        if old not in raw:raise ValueError('immutable corrected current stage binding refused')
        raw=raw.replace(old,new)
    ns={**previous.__dict__,'OUT':previous.W/OUTNAME,'TOOLS':previous.W/'pg1505-publication-only-tools-v3'}
    exec(compile(raw,'<new immutable broker mapping owner stage>','exec'),ns);ns['main']();return 0
if __name__=='__main__':raise SystemExit(main())

"""Immutable qualified 115-member tools stage; does not start recovery or a service."""
import inspect
import pg1446_current_cold_stage as previous

OUTNAME='pg1494-publication-recovery-stage-v2'

def main():
    raw=inspect.getsource(previous.main)
    for old,new in [('pg1444-current-cold-frozen-v2.safe.json','pg1493-publication-recovery-frozen-v2.safe.json'),('pg1446','pg1494'),('PG1446','PG1494'),('pg1441-current-cold-tools-v1','pg1493-publication-only-tools-v2')]:
        if old not in raw:raise ValueError('fixed qualified recovery stage binding refused')
        raw=raw.replace(old,new)
    ns={**previous.__dict__,'OUT':previous.W/OUTNAME,'TOOLS':previous.W/'pg1493-publication-only-tools-v2'}
    exec(compile(raw,'<new-only immutable current recovery stage>','exec'),ns);ns['main']();return 0

if __name__=='__main__':raise SystemExit(main())

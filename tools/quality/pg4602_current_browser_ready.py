"""Identity-only new964e Browser oracle freeze; execution waits for genuine Root terminal."""
import types
import pg3578_current_browser_ready as shared
import pg4576_current_fresh_noargs_once as entry

SLOT='pg4602-current-browser-ready-v1'
SOURCE=entry.SOURCE
PINNED=[n.replace('pg3578_current_browser_ready.py','pg4602_current_browser_ready.py')for n in shared.PINNED]
JAVA=shared.JAVA
classpath=shared.classpath


def namespace():return {**vars(shared),'SOURCE':SOURCE,'SLOT':SLOT,'PINNED':PINNED}


def require_ready():return types.FunctionType(shared.require_ready.__code__,namespace())()


def main():
    from pg4586_current_independent_acceptance import TERM
    proof=shared.json.loads((shared.W/TERM/'manifest.safe.json').read_bytes())
    if proof['actualExit']!=0 or proof['source']!=SOURCE or proof['result']['genuineRootDone']is not True:raise ValueError('no live Root DB interference: genuine same-source terminal0 first')
    return types.FunctionType(shared.main.__code__,namespace())()


if __name__=='__main__':raise SystemExit(main())

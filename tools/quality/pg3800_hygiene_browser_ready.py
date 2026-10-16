"""Before new Root: freeze unchanged twelve independent Browser oracles for new identity."""
import inspect
import pg3578_current_browser_ready as previous
from pg3788_hygiene_publication_sources import SOURCE

SLOT='pg3800-hygiene-browser-ready-v1'
PINNED=[n.replace('pg3578_current_browser_ready.py','pg3800_hygiene_browser_ready.py')for n in previous.PINNED]


def require_ready():
    namespace={**previous.__dict__,'SOURCE':SOURCE,'SLOT':SLOT,'PINNED':PINNED}
    exec(compile(inspect.getsource(previous.require_ready),'<same-source Browser readiness>','exec'),namespace)
    return namespace['require_ready']()


def main():
    namespace={**previous.__dict__,'SOURCE':SOURCE,'SLOT':SLOT,'PINNED':PINNED}
    exec(compile(inspect.getsource(previous.main),'<one new-source Browser preflight>','exec'),namespace)
    return namespace['main']()


if __name__=='__main__':raise SystemExit(main())

"""Identity-only twelve-case Browser oracle freeze; no business activity before Root DONE."""
import types
import pg3578_current_browser_ready as shared
import pg4752_new_current_admission_image as admission
import pg4754_new_current_terminal as terminal

SLOT='pg4762-new-current-browser-ready-v1'
SOURCE=admission.SOURCE
PINNED=[n.replace('pg3578_current_browser_ready.py','pg4762_new_current_browser_ready.py')for n in shared.PINNED]
JAVA=shared.JAVA
classpath=shared.classpath


def namespace():return {**vars(shared),'SOURCE':SOURCE,'SLOT':SLOT,'PINNED':PINNED}


def require_ready():return types.FunctionType(shared.require_ready.__code__,namespace())()


def main():
    admission.authenticate_host()
    proof=shared.json.loads((shared.W/terminal.TERM/'manifest.safe.json').read_bytes())
    if not(type(proof['actualExit'])is int and proof['actualExit']==0 and proof['source']==SOURCE and proof['result']['genuineRootDone']is True):raise ValueError('genuine same-source Root DONE before Browser preflight')
    return types.FunctionType(shared.main.__code__,namespace())()


if __name__=='__main__':raise SystemExit(main())

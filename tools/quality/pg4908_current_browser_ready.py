"""Identity-only twelve real Browser oracle qualification after genuine Root DONE."""
import types
import pg4762_new_current_browser_ready as previous
import pg4900_current_admission_image as admission
import pg4902_current_genuine_terminal as terminal

shared=previous.shared
SLOT='pg4908-current-browser-ready-v1'
SOURCE=admission.SOURCE
PINNED=[n.replace('pg4762_new_current_browser_ready.py','pg4908_current_browser_ready.py')for n in previous.PINNED]
JAVA=shared.JAVA;classpath=shared.classpath


def namespace():return {**vars(shared),'SOURCE':SOURCE,'SLOT':SLOT,'PINNED':PINNED}


def require_ready():return types.FunctionType(shared.require_ready.__code__,namespace())()


def main():
    admission.authenticate_host()
    proof=shared.json.loads((shared.W/terminal.TERM/'manifest.safe.json').read_bytes())
    if not(type(proof['actualExit'])is int and proof['actualExit']==0 and proof['source']==SOURCE and proof['result']['genuineRootDone']is True):
        raise ValueError('genuine current Root DONE before Browser qualification')
    return types.FunctionType(shared.main.__code__,namespace())()


if __name__=='__main__':raise SystemExit(main())

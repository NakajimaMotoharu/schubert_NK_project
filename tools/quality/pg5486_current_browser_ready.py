"""Same independent12 Browser cases; genuine new296 Root DONE is required first."""
import types
import pg5046_current_browser_ready as previous
import pg5476_current_admission_image as admission
import pg5478_current_genuine_terminal as terminal

shared=previous.shared
SLOT='pg5486-current-browser-ready-v1'
SOURCE=admission.SOURCE
PINNED=[name.replace('pg5046_current_browser_ready.py','pg5486_current_browser_ready.py')for name in previous.PINNED]
JAVA,classpath=shared.JAVA,shared.classpath


def namespace():return{**vars(shared),'SOURCE':SOURCE,'SLOT':SLOT,'PINNED':PINNED}


def require_ready():return types.FunctionType(shared.require_ready.__code__,namespace())()


def main():
    admission.authenticate_host();value=shared.json.loads((shared.W/terminal.TERM/'manifest.safe.json').read_bytes())
    if not(type(value['actualExit'])is int and value['actualExit']==0 and value['source']==SOURCE and value['result']['genuineRootDone']is True):
        raise ValueError('genuine current296 Root DONE before Browser readiness')
    return types.FunctionType(shared.main.__code__,namespace())()


if __name__=='__main__':raise SystemExit(main())

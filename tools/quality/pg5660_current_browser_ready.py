"""Current0ea identity-only12 Browser qualification; genuine currentRoot DONE required."""
import types
import pg5522_guest_clock_browser_ready as previous
import pg5644_current_admission_image as admission
import pg5646_current_genuine_terminal as terminal

shared=previous.shared
SLOT='pg5660-current-browser-ready-v1'
SOURCE=admission.SOURCE
PINNED=[n for n in previous.PINNED if not any(s in n for s in('pg5522_','pg5524_','pg5526_','pg5528_','pg5529_'))]
PINNED+=['tools/quality/'+n for n in('pg5660_current_browser_ready.py','pg5662_current_same_owner_browser.py',
  'pg5664_current_browser_composite.py','pg5666_current_parent_projection.py','pg5668_current_browser_chain_test.py')]
JAVA,classpath=shared.JAVA,shared.classpath


def namespace():return{**vars(shared),'SOURCE':SOURCE,'SLOT':SLOT,'PINNED':PINNED,'ORACLES':previous.namespace()['ORACLES']}


def require_ready():return types.FunctionType(shared.require_ready.__code__,namespace())()


def main():
    admission.authenticate_host();v=shared.json.loads((shared.W/terminal.TERM/'manifest.safe.json').read_bytes())
    if not(type(v['actualExit'])is int and v['actualExit']==0 and v['source']==SOURCE and v['result']['genuineRootDone']is True):raise ValueError('sameRoot0ea genuine DONE before Browser')
    return types.FunctionType(shared.main.__code__,namespace())()


if __name__=='__main__':raise SystemExit(main())

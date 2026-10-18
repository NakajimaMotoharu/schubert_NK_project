"""New-only same296 Browser bundle after clock-capture repair; old5486/5488 retained."""
import types
import pg5486_current_browser_ready as previous

shared=previous.shared
SLOT='pg5522-guest-clock-browser-ready-v1'
SOURCE=previous.SOURCE
PINNED=[name.replace('pg5486_current_browser_ready.py','pg5522_guest_clock_browser_ready.py')for name in previous.PINNED]
PINNED+=['tools/quality/pg5520_guest_clock_contract.py','tools/quality/pg5520_guest_clock_contract_test.py']
PINNED+=['tools/quality/'+name for name in('pg5524_guest_clock_same_owner_browser.py','pg5526_guest_clock_browser_composite.py','pg5528_guest_clock_parent_projection.py','pg5529_guest_clock_chain_test.py')]
JAVA,classpath=shared.JAVA,shared.classpath


def namespace():
    return{**vars(shared),'SOURCE':SOURCE,'SLOT':SLOT,'PINNED':PINNED,
        'ORACLES':shared.ORACLES+['tools/quality/pg5520_guest_clock_contract_test.py']}


def require_ready():return types.FunctionType(shared.require_ready.__code__,namespace())()


def main():
    previous.admission.authenticate_host();v=shared.json.loads((shared.W/previous.terminal.TERM/'manifest.safe.json').read_bytes())
    if not(type(v['actualExit'])is int and v['actualExit']==0 and v['source']==SOURCE and v['result']['genuineRootDone']is True):raise ValueError('sameRoot296 genuine DONE first')
    return types.FunctionType(shared.main.__code__,namespace())()


if __name__=='__main__':raise SystemExit(main())

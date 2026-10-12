"""New read-only closing after finalized SSC268, exact warm receipt/current GC separation."""
import inspect
from pathlib import Path
import pg1508_publication_recovery_independent_closing as previous

def payload():
    raw=previous.payload().replace('pg1508-publication-recovery-closing-v3','pg1511-publication-gc-closing-v1')
    marker="first=snapshot();second=snapshot();require(first==second==after['current']);validate_current(first)"
    assert raw.count(marker)==1
    source=Path(__file__).with_name('pg1510_publication_gc_bridge.py').read_text()
    replacement='GC_SOURCE='+repr(source)+"\n gc_contract=types.ModuleType('strict_gc_bridge');exec(GC_SOURCE,gc_contract.__dict__)\n first=snapshot();second=snapshot();require(first==second);normalized,gc_kinds=gc_contract.normalize(after['current'],first,exec_record);validate_current(normalized)"
    raw=raw.replace(marker,replacement)
    raw=raw.replace("'actions0':True,'formalAccepted':False,'resumeIssued':False","'gcKinds':gc_kinds,'warmStopProofRetained':True,'gcAloneNotStopProof':True,'actions0':True,'formalAccepted':False,'resumeIssued':False")
    compile(raw,'<strict current GC independent closing>','exec');return raw

def main():
    entry=inspect.getsource(previous.main).replace('pg1508-publication-recovery-closing-v3','pg1511-publication-gc-closing-v1')
    ns={**previous.__dict__,'payload':payload};exec(compile(entry,'<new-only strict GC closing transport>','exec'),ns);return ns['main']()
if __name__=='__main__':raise SystemExit(main())

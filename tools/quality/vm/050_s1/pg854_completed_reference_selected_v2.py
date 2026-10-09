"""BUG971 new-only batch selected: exact nine suites, no parent plugin invocation."""
from pathlib import Path
import inspect
import pg743_closing_selected as selected
import pg854_completed_reference_selected as definition
selected.D=selected.W/'pg854-completed-reference-selected-v2'
if __name__=='__main__':
    raw=inspect.getsource(selected.main)
    marker="'src/schubert-nk-bootstrap,src/schubert-nk-api', '-am',"
    assert raw.count(marker)==1
    raw=raw.replace(marker,"'src/schubert-nk-batch',")
    raw=raw.replace('PG743-closing-selected-v1','PG854-completed-reference-selected-v2')
    raw=raw.replace('1ec19782a1afe22d1de75b05f4cd12b8a8a8a172','2a0d5aa392c85a1dc12a1cdb423978e8500895b8')
    namespace=dict(selected.__dict__)
    exec(compile(raw,'<854v2 actual batch-only selection>','exec'),namespace)
    namespace['main']()

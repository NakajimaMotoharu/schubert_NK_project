"""New-only retained Inspector provenance with explicit startup/DONE/current epochs."""
import ast
from pathlib import Path
from pg906_retained_inspector import payload as previous
R=Path(__file__).resolve().parent
def payload(proof,seals):
 raw=previous(proof,seals)
 marker="require(first['rows']==old['rows'])";assert raw.count(marker)==1
 replacement=(R/'pg906_progress_epoch.py').read_text()+"\nrequire(first_progress(old['rows']['schubert.inbox_inspection_progress'],first['rows']['schubert.inbox_inspection_progress'],value['rows']['schubert.inbox_inspection_progress'],'19022204-8a9e-418d-ba2a-9967ff923dc2'))"
 raw=raw.replace(marker,replacement)
 raw=raw.replace('pg906-retained-inspector-v1','pg906-retained-inspector-v2').replace('PG906-retained-inspector-v1','PG906-retained-inspector-v2')
 ast.parse(raw);return raw
if __name__=='__main__':
 source=(R/'pg901_bootstrap_post.py').read_text();env={'__file__':str(R/'pg906_retained_inspector_v2.py'),'__name__':'retained_inspector_v2'}
 exec(compile(source,'<901 readonly dispatcher>','exec'),env);env['payload']=payload
 main_source=source[source.index('def main():'):source.index("if __name__=='__main__':")].replace('pg901-bootstrap-post-v1','pg906-retained-inspector-v2')
 exec(compile(main_source,'<906 phase-specific inspector v2>','exec'),env);env['main']()

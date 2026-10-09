"""Use qualified batch-only CLI; pin all dependency main classes against frozen current857."""
import inspect,json,hashlib,zipfile
from pathlib import Path
import pg743_closing_selected as selected
import pg911_snapshot_selected as definition
selected.D=selected.W/'pg911-snapshot-selected-v2'
def code():
 raw=inspect.getsource(selected.main)
 marker="'src/schubert-nk-bootstrap,src/schubert-nk-api', '-am',";assert raw.count(marker)==1
 raw=raw.replace(marker,"'src/schubert-nk-batch',")
 return raw.replace('PG743-closing-selected-v1','PG911-snapshot-selected-v2').replace('1ec19782a1afe22d1de75b05f4cd12b8a8a8a172','e01612fcd7f2752df5ae0836b78538fd5e87f120')
def dependency_bytes():
 repo=Path('/home/mini/codex/project1/work/toolchain/m2/repository/dev/codex/schubert')
 host=selected.W/'pg857-completed-reference-six-host-v1';h=json.loads((host/'manifest.safe.json').read_bytes());assert h['actualExit']==0 and h['candidateSource']=='e01612fcd7f2752df5ae0836b78538fd5e87f120';counts={}
 for m in ('protocol','storage','bootstrap'):
  name='schubert-nk-'+m+'-0.1.0-SNAPSHOT.jar';left=host/m/name;right=repo/('schubert-nk-'+m)/'0.1.0-SNAPSHOT'/name
  assert hashlib.sha256(left.read_bytes()).hexdigest()==h['moduleResults'][m]['jarSha256']
  def classes(p):
   with zipfile.ZipFile(p)as z:return {n:hashlib.sha256(z.read(n)).hexdigest()for n in z.namelist()if n.endswith('.class')}
  a=classes(left);b=classes(right);assert a==b,(m,len(a),len(b));counts[m]=len(a)
 return counts
if __name__=='__main__':
 assert '-am'not in code();assert 'src/schubert-nk-batch'in code()
 print(json.dumps({'dependencyMainClassCounts':dependency_bytes(),'classByteMismatch':0,'oldV1NotRunNotCounted':True}),flush=True)
 env=dict(selected.__dict__);exec(compile(code(),'<911 v2 qualified batch only>','exec'),env);env['main']()

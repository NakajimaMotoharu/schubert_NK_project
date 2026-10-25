"""Independent full-module literal Bootstrap17 metadata; no credential/DB/native effects."""
from pathlib import Path
import explicit_primary_source_post as post

def other_module(path):
    for current,other in (('schubert-nk-bootstrap','schubert-nk-web'),('schubert-nk-batch','schubert-nk-api')):
        prefix='src/'+current+'/src/test/java/'
        if path.startswith(prefix):return 'src/'+other+'/src/test/java/'+path[len(prefix):]
    raise ValueError('explicit bootstrap or shared batch source required')

if __name__=='__main__':
    assert other_module('src/schubert-nk-bootstrap/src/test/java/p/Foo.java')=='src/schubert-nk-web/src/test/java/p/Foo.java'
    assert other_module('src/schubert-nk-batch/src/test/java/p/Foo.java')=='src/schubert-nk-api/src/test/java/p/Foo.java'
    post.run(Path(__file__),post.BASE/'PG9508-bootstrap17-source-post-v1','PG9506-bootstrap17-source-metadata-v1',
      '149b4cd28bab67a5d02b1e1aa7eb7dee3b7313320b87cc1e68c631ba9f5c3a64','fd7978038891755775640710dbe926a34faa75dd7bab70fb79b23e7eda3fc8a8',
      'evidence/01_PT/018_NK-OPS-001/1928_G13Bootstrap17_主関連責任仕様.md','6dfbea72a188c1a85765a33eb74ba7458f78d827afae79664c26e5b81b46cf7a',
      'src/',('schubert-nk-bootstrap/','schubert-nk-batch/'),17,
      {'InspectorCredentialLoader':'WBS-P018-01','AesCredentialFile':'WBS-P018-01','ServiceCredentialReader':'WBS-P018-01',
       'ServiceCredentialSet':'WBS-P018-01','ServiceProcessResources':'WBS-P018-04','ServiceDatabaseAdmission':'WBS-P019-01',
       'ChildStartupContext':'WBS-P018-03','NativeCoveragePrivateFile':'WBS-P018-08','FixedNativeCoverageProfile':'WBS-P018-08',
       'FixedNativeCoverageCheckpoint':'WBS-P018-08'},source_path_mutator=other_module,source_mutator_vectors=2)

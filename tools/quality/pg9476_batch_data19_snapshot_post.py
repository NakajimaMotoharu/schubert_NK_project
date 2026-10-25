"""Limited batch trace pointer binding; whole current WBS remains its actual scope HOLD."""
from pathlib import Path
import trace_snapshot_binding as post

if __name__=='__main__':
    post.run(Path(__file__),post.BASE/'PG9476-batch-data19-snapshot-post-v1','91d1ab3f4d4e664a274d92020cfa51c869631bc3',
      '64446a9f8901084a4ad7eba1f66ae975eb2bbdea','PG9474-batch-data19-source-join-v1/manifest.json',
      '916f308c85f4b0465f2ef54bfe64b2bbb1529ecf57235a521fe3a67c9422e32c',1651,826)

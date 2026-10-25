"""Bind exact Bootstrap17 trace metadata; whole source acceptance remains independently held."""
from pathlib import Path
import trace_snapshot_binding as post

if __name__=='__main__':
    post.run(Path(__file__),post.BASE/'PG9512-bootstrap17-snapshot-post-v1','c9bda14c007c6d89d364e021e23d08f1e0c7eca4',
      '64446a9f8901084a4ad7eba1f66ae975eb2bbdea','PG9510-bootstrap17-source-join-v1/manifest.json',
      '7f314d491c7ff05eabf7464cd3f42efb313cfbb5e8c499b5c49b316f77f3c650',1727,902)

"""Resource-backed source metadata only; no whole-current qualification or target runtime."""
from pathlib import Path
import trace_snapshot_binding as post

if __name__=='__main__':
    post.run(Path(__file__),post.BASE/'PG9428-resource33-snapshot-post-v1','580154e6908cd193f8fffec316bf8900e50ecf4b',
      '64446a9f8901084a4ad7eba1f66ae975eb2bbdea','PG9426-resource33-source-join-v1/manifest.json',
      '91f349d3158c28d4b6da2bfddf9c2ca1b9469de764ebb2d87cb4c7d137f21690',1566,741)

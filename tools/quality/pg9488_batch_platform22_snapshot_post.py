"""Bind limited Batch platform22 trace metadata, keeping whole current-source audit HOLD."""
from pathlib import Path
import trace_snapshot_binding as post

if __name__=='__main__':
    post.run(Path(__file__),post.BASE/'PG9488-batch-platform22-snapshot-post-v1','f63190509e4433d508656fb56e9bc53c7a91e88d',
      '64446a9f8901084a4ad7eba1f66ae975eb2bbdea','PG9486-batch-platform22-source-join-v1/manifest.json',
      '960c0986edd66ef7626d8d752497bf3a49700ed3e68019db1d3ac31b708ff405',1673,848)

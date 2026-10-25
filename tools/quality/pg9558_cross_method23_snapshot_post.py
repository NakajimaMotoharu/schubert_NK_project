"""Bind additional method trace metadata only; file inventory/source acceptance remain unchanged."""
from pathlib import Path
import trace_snapshot_binding as post

if __name__=='__main__':
    post.run(Path(__file__),post.BASE/'PG9558-cross-method23-snapshot-post-v1','a51bf765c198e2ecb3fc328356a92c13a888e1fa',
      '64446a9f8901084a4ad7eba1f66ae975eb2bbdea','PG9546-shared-fixture7-source-join-v1/manifest.json',
      '4d82743eb894ccd448a2ef88b40f566bc0fb08a8ee4b5128a925e49c08b7dd61',1781,956)

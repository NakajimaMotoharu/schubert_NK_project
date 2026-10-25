"""Protocol primary/related registration metadata only; retain true whole-source audit HOLD."""
from pathlib import Path
import trace_snapshot_binding as post

if __name__=='__main__':
    post.run(Path(__file__),post.BASE/'PG9404-protocol-composite-snapshot-post-v1','5d9df30ac0805475e42bab45c27eace41d57c2a2',
      '64446a9f8901084a4ad7eba1f66ae975eb2bbdea','PG9402-protocol-composite-join-v1/manifest.json',
      '6bc494ba796f9752639739ea1d6cdb811f160637dd82cd1fc0866b2943e9e985',1508,683)

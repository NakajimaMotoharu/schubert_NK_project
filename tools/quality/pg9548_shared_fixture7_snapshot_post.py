"""Bind current shared fixture7 trace pointers without altering any whole-source qualification."""
from pathlib import Path
import trace_snapshot_binding as post

if __name__=='__main__':
    post.run(Path(__file__),post.BASE/'PG9548-shared-fixture7-snapshot-post-v1','e94801bf34204312cd587841a57265996905c748',
      '64446a9f8901084a4ad7eba1f66ae975eb2bbdea','PG9546-shared-fixture7-source-join-v1/manifest.json',
      '4d82743eb894ccd448a2ef88b40f566bc0fb08a8ee4b5128a925e49c08b7dd61',1781,956)

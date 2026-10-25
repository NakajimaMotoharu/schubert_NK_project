"""Current composite47 supplemental pointers only; full-current audit stays HOLD."""
from pathlib import Path
import trace_snapshot_binding as post

if __name__=='__main__':
    post.run(Path(__file__),post.BASE/'PG9392-composite-snapshot-post-v1','ff23db14e',
      '64446a9f8901084a4ad7eba1f66ae975eb2bbdea','PG9390-composite-owner-join-v1/manifest.json',
      '90b5394c4afd5f9ee468620f9ef593f49ae350969e144d5d0db9b425ee03d602',1498,673)

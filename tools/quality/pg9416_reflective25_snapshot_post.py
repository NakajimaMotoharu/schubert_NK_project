"""Exact-path static25 metadata only, preserving real runtime and whole-current audit HOLD."""
from pathlib import Path
import trace_snapshot_binding as post

if __name__=='__main__':
    post.run(Path(__file__),post.BASE/'PG9416-reflective25-snapshot-post-v1','25a23561e',
      '64446a9f8901084a4ad7eba1f66ae975eb2bbdea','PG9414-reflective25-source-join-v1/manifest.json',
      'c9d1ddfbf5a0766430221a57e837278155289d39fe5c2d64b076972345125b46',1533,708)

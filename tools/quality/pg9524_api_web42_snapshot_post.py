"""Exact current API/Web42 trace pointer proof, not a whole-current-source WBS qualification."""
from pathlib import Path
import trace_snapshot_binding as post

if __name__=='__main__':
    post.run(Path(__file__),post.BASE/'PG9524-api-web42-snapshot-post-v1','fa5ce0726555c716efdcc840e75eec80f4a2c722',
      '64446a9f8901084a4ad7eba1f66ae975eb2bbdea','PG9522-api-web42-source-join-v1/manifest.json',
      '4f85bf805c3e32dbe668e6374bf6a70cb6fa6c0d93edd1ef4ea99bc30925f927',1769,944)

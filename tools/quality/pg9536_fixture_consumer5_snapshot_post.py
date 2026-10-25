"""Bind fixture-consumer responsibility pointers without changing historical/formal acceptance."""
from pathlib import Path
import trace_snapshot_binding as post

if __name__=='__main__':
    post.run(Path(__file__),post.BASE/'PG9536-fixture-consumer5-snapshot-post-v1','07045e0ba619b876f08d8d73202b60978c86dcf9',
      '64446a9f8901084a4ad7eba1f66ae975eb2bbdea','PG9534-fixture-consumer5-source-join-v1/manifest.json',
      '69d5360bb5d7fb9f8e9eef09ca7427ecb24f01acfa3c682a5eb9bc41033a62e8',1774,949)

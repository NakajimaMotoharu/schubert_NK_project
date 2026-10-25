"""Web screen22 trace pointers only; original source/acceptance/budgets and actual holds preserved."""
from pathlib import Path
import trace_snapshot_binding as post

if __name__=='__main__':
    post.run(Path(__file__),post.BASE/'PG9464-web-screen22-snapshot-post-v1','e7ba0e8f9add1c30d91deb37f105664dd9c0d090',
      '64446a9f8901084a4ad7eba1f66ae975eb2bbdea','PG9462-web-screen22-source-join-v1/manifest.json',
      '7ea77aaaa24b59d395ea34e6e1e0af822ec5d43354c6ec1e4748f0c0b9084bdc',1632,807)

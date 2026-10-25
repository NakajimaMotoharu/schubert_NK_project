"""API transaction/JMS20 supplemental trace pointers; all current whole-source holds retained."""
from pathlib import Path
import trace_snapshot_binding as post

if __name__=='__main__':
    post.run(Path(__file__),post.BASE/'PG9440-api-jms20-snapshot-post-v1','73f4c5dc5a811c78a2183c7ff55daee7d5355ea2',
      '64446a9f8901084a4ad7eba1f66ae975eb2bbdea','PG9438-api-jms20-source-join-v1/manifest.json',
      '0eb6d96826969b6f605e4001e738c0f4ab802ce3f6cfbe734f2811ecdf41fd88',1586,761)

"""Register37 Batch file source labels; never transform ownership into runtime acceptance."""
from pathlib import Path
import explicit_primary_source_registration as register
import trace_owner_join_batch_file37 as resolver

if __name__=='__main__':
    register.run(Path(__file__),resolver,register.BASE/'PG9498-batch-file37-source-join-v1',
      'PG9486-batch-platform22-source-join-v1/manifest.json','960c0986edd66ef7626d8d752497bf3a49700ed3e68019db1d3ac31b708ff405',
      'PG9496-batch-file37-source-post-v1/manifest.json','a605e5d152e320db77396d02ee6044c0745786d57ad2928c0be2991be9253e70',37,1710)

"""Register19 exact batch source labels after independent post, never count as PT."""
from pathlib import Path
import explicit_primary_source_registration as register
import trace_owner_join_batch_data19 as resolver

if __name__=='__main__':
    register.run(Path(__file__),resolver,register.BASE/'PG9474-batch-data19-source-join-v1',
      'PG9462-web-screen22-source-join-v1/manifest.json','7ea77aaaa24b59d395ea34e6e1e0af822ec5d43354c6ec1e4748f0c0b9084bdc',
      'PG9472-batch-data19-source-post-v1/manifest.json','5957f49f6ebc509b4358e1d1ed9521d1c4980aa649fd0ca39da1fe7a22f6b5fe',19,1651)

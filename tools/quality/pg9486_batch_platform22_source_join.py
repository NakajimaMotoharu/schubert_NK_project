"""Register22 Batch platform source labels; neither product PT nor live process proof."""
from pathlib import Path
import explicit_primary_source_registration as register
import trace_owner_join_batch_platform22 as resolver

if __name__=='__main__':
    register.run(Path(__file__),resolver,register.BASE/'PG9486-batch-platform22-source-join-v1',
      'PG9474-batch-data19-source-join-v1/manifest.json','916f308c85f4b0465f2ef54bfe64b2bbb1529ecf57235a521fe3a67c9422e32c',
      'PG9484-batch-platform22-source-post-v1/manifest.json','8d463a2ce2a9dd4a4e677604372d689b527641df5bd950fe07fd6b69050418be',22,1673)

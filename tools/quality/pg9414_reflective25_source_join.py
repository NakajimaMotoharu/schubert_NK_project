"""Exact25 static source responsibilities only, runtime uncertainty retained."""
from pathlib import Path
import exact_path_owner_registration as register
import trace_owner_join_reflective25 as resolver

if __name__=='__main__':
    register.run(Path(__file__),resolver,register.BASE/'PG9414-reflective25-source-join-v1',
      'PG9402-protocol-composite-join-v1/manifest.json','6bc494ba796f9752639739ea1d6cdb811f160637dd82cd1fc0866b2943e9e985',
      'PG9412-reflective25-source-post-v1/manifest.json','3744825998125a964bcd0029d5af61fffb0f30f1afd95e05706ce7e8e1581071',25,1533)

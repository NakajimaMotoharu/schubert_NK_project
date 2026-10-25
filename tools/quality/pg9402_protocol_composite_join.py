"""Literal protocol10 source responsibilities only, not dynamic PT or whole source trace."""
from pathlib import Path
import reviewed_owner_registration as registration
import trace_owner_join_protocol_composite as resolver

if __name__=='__main__':
    registration.run(Path(__file__),resolver,registration.BASE/'PG9402-protocol-composite-join-v1',
      'PG9390-composite-owner-join-v1/manifest.json','90b5394c4afd5f9ee468620f9ef593f49ae350969e144d5d0db9b425ee03d602',
      'PG9400-protocol-composite-post-v1/manifest.json','e4597b904e78d01633f2c0d5e8a6408b17554a32b792e9bc38e19039c9210061',10,1508)

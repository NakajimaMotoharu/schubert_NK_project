"""New-only generated current750 payload after namespace correction, old compile1 retained."""
from pathlib import Path

R=Path(__file__).resolve().parent


if __name__=='__main__':
    import pg797_sources as sources
    original=sources.java
    sources.java=lambda:original().replace('pg797-liveness-tools-v1','pg797-liveness-tools-v2')
    raw=(R/'pg797_compile.py').read_text().replace('pg797-liveness-tools-v1','pg797-liveness-tools-v2')
    # Inner inherited recipe names are generated at runtime; change the evaluated raw before compile.
    raw=raw.replace("    exec(compile(raw,'<new797 current750 two-session liveness>'", "    raw=raw.replace('pg797-liveness-tools-v1','pg797-liveness-tools-v2').replace(\"phase+'-v1.private.log'\",\"phase+'-v2.private.log'\").replace(\"phase+'-v1.exit'\",\"phase+'-v2.exit'\").replace('pg797-frozen-v1.safe.json','pg797-frozen-v2.safe.json').replace('pg797-oracle-v1.private.log','pg797-oracle-v2.private.log')\n    exec(compile(raw,'<new797 current750 two-session liveness>'")
    exec(compile(raw,'<new immutable797v2>', 'exec'),{'__file__':str(R/'pg797_compile_v2.py'),'__name__':'__main__'})

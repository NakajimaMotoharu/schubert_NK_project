"""Distinct307-condition probe after session/effective-role correction; no old slot reuse."""
from pathlib import Path

R=Path(__file__).resolve().parent


if __name__=='__main__':
    import pg797_sources as sources
    original=sources.java
    sources.java=lambda:original().replace('pg797-liveness-tools-v1','pg797-liveness-tools-v3')
    raw=(R/'pg797_compile.py').read_text()
    old="    exec(compile(raw,'<new797 current750 two-session liveness>'"
    assert raw.count(old)==1
    adjustment="    raw=raw.replace('pg797-liveness-tools-v1','pg797-liveness-tools-v3').replace(\"phase+'-v1.private.log'\",\"phase+'-v3.private.log'\").replace(\"phase+'-v1.exit'\",\"phase+'-v3.exit'\").replace('pg797-frozen-v1.safe.json','pg797-frozen-v3.safe.json').replace('pg797-oracle-v1.private.log','pg797-oracle-v3.private.log').replace(\"'javaOwnedDatabaseAssertions':299\",\"'javaOwnedDatabaseAssertions':307\")\n"
    raw=raw.replace(old,adjustment+old)
    exec(compile(raw,'<immutable797v3 actual roles>', 'exec'),{'__file__':str(R/'pg797_compile_v3.py'),'__name__':'__main__'})

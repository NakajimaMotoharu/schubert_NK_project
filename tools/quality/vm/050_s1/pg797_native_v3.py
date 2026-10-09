"""Distinct797v3 stage/one75s verify after real effective-role diagnosis; oldv2 failed."""
from pathlib import Path

R=Path(__file__).resolve().parent


if __name__=='__main__':
    raw=(R/'pg797_native_v2.py').read_text().replace('pg797-liveness-tools-v2','pg797-liveness-tools-v3').replace('pg797-frozen-v2.safe.json','pg797-frozen-v3.safe.json').replace('pg797-stage-v2.exit','pg797-stage-v3.exit').replace("action+'-v2'", "action+'-v3'")
    # Each inherited stage also has its own unpublished archive/home slot.
    raw=raw.replace("    exec(compile(raw,", "    raw=raw.replace('pg797-fixed-stage-v1','pg797-fixed-stage-v3')\n    exec(compile(raw,")
    exec(compile(raw,'<new797v3 stage/verify>', 'exec'),{'__file__':str(R/'pg797_native_v3.py'),'__name__':'__main__'})

"""Distinct797v2 stage/once verify; never stage failed v1."""
from pathlib import Path

R=Path(__file__).resolve().parent


if __name__=='__main__':
    raw=(R/'pg797_native.py').read_text()
    raw=raw.replace("    exec(compile(raw,", "    raw=raw.replace('pg797-liveness-tools-v1','pg797-liveness-tools-v2').replace('pg797-frozen-v1.safe.json','pg797-frozen-v2.safe.json').replace(\"action+'-v1'\",\"action+'-v2'\").replace('pg797-stage-v1.exit','pg797-stage-v2.exit')\n    exec(compile(raw,")
    exec(compile(raw,'<new797v2 stage/verify>', 'exec'),{'__file__':str(R/'pg797_native_v2.py'),'__name__':'__main__'})

"""Fresh corrected current ADMIN compile after normal exact-tool recovery."""
from pathlib import Path
from pg664_sources import current

R=Path(__file__).resolve().parent
if __name__=='__main__':
    raw=current((R/'pg662_compile.py').read_text())
    raw=raw.replace("assert (W/'pg661-completed-baseline-v1.exit').read_bytes()==b'0\\n'", "assert (W/'pg661-completed-baseline-v1.exit').read_bytes()==b'0\\n'\n    assert (W/'pg663-handoff-execute-v1.exit').read_bytes()==b'0\\n'")
    exec(compile(raw,str(R/'pg664_compile.py'),'exec'),{'__name__':'__main__','__file__':str(R/'pg664_compile.py')})

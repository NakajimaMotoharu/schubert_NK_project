"""Immutable fresh existing-only profile, currentPG750 ABI, Werror and puregate oracle."""
from pathlib import Path
from pg783_sources import bind

R=Path(__file__).resolve().parent


if __name__=='__main__':
    raw=bind((R/'pg778_compile.py').read_text().replace('Pg778FailedRecovery','Pg779FailedRecovery').replace('pg778','pg779').replace('PG778','PG779'))
    raw=raw.replace('pg783-failed758-tools-v1','pg783-existing-pair-tools-v1')
    raw=raw.replace("(W/'pg777-failure-full758-v1.exit')", "(W/'pg786-stopped-current-v1.exit')")
    raw=raw.replace("'pg783_contract_test.py'", "'pg783_pure_gate_test.py'")
    raw=raw.replace("(R/'pg783_refs.py').read_text()", "refs_source()")
    raw=raw.replace("'pythonIndependentAssertions':151", "'pythonIndependentAssertions':10")
    raw=raw.replace("'pythonAssertions':151", "'pythonCallbackInvocations':10,'productionPTAdded':0")
    raw=raw.replace("'snapshotSha256':'80594db5e3a5588a26b05be729e80a40f750a44230f34c3e025f923f365ddba4'", "'snapshotSha256':'b6165c75ccc067991654d0b43db272096fc05019029d7e15e31af157cf35ad23'")
    raw=raw.replace("subprocess.run(['python3','-B',str(R/'pg783_pure_gate_test.py')],check=True)", "subprocess.run(['python3','-B',str(R/'pg783_pure_gate_test.py')],check=True)\n    subprocess.run(['python3','-B',str(R/'pg785_exec_history_test.py')],check=True)")
    def refs_source():return bind((R/'pg778_refs.py').read_text().replace('pg778','pg779').replace('PG778','PG779')).replace('pg783-failed758-tools-v1','pg783-existing-pair-tools-v1')
    exec(compile(raw,'<new783 current existingPair compilation>','exec'),{'__file__':str(R/'pg783_compile.py'),'__name__':'__main__','refs_source':refs_source})

"""Same fixed source selected batch completion boundaries; no VM or formal acceptance."""
from pathlib import Path

R=Path(__file__).resolve().parent
TESTS={'batch':['MorningCompletionRetirementTest','MorningStartupLaunchOwnerTest','MorningCompletionChecksTest','MorningCompletionEvidenceTest','MorningNewRunAdmissionTest','MorningPendingAdmissionTest','MorningServiceReadinessTest','MorningCaddyReadinessTest','BackupUnitStartClientTest','RootStartupContextTest']}


if __name__=='__main__':
    raw=(R/'pg743_closing_selected.py').read_text().replace('pg743-closing-selected-v1','pg790-completion-selected-v1').replace("'src/schubert-nk-bootstrap,src/schubert-nk-api', '-am',", "'src/schubert-nk-batch',")
    start=raw.index('TESTS = {');end=raw.index('\n\n\ndef main():',start);raw=raw[:start]+'TESTS = '+repr(TESTS)+raw[end:]
    raw=raw.replace("'1ec19782a1afe22d1de75b05f4cd12b8a8a8a172'", "'8d4b68b4f1449932ebe506aaf08e584bbfea8dd2'")
    exec(compile(raw,'<PG790 fixed selected batch>','exec'),{'__file__':str(R/'pg790_completion_selected.py'),'__name__':'__main__'})

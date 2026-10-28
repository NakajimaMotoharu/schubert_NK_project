"""Recover completed help metadata, preserving actual help1 and both original failed tool versions."""
import json
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

OLD = data.ROOT.parent/'pgpt-runs/PG379/pg13213-spotbugs-fresh-aux-plan-v2'
OUT = data.BASE/'PG13218-spotbugs-fresh-aux-plan-recovery-v1'

def main():
    invocation = capture(__file__);assert not OUT.exists()
    plan = json.loads((OLD/'begin.safe.json').read_bytes());assert plan['source'] == '6d7f55c22a3ffec8a9013e706282ac845c595492'
    assert plan['configuration'] == dict(version='4.10.4',effort='max',threshold='low',excludes=[],onlyAnalyze=None,productTestsExecuted=0)
    assert plan['expectedMainClasses'] == 1843 and sum(len(v) for v in plan['oldMissingClasses'].values()) == 18
    verify(plan['invocation'])
    for p,sha in {**plan['toolRuntimeHashes'],**plan['auxiliaryClasspathHashes'],**plan['currentJarHashes']}.items():assert data.sha(Path(p).read_bytes()) == sha
    stage = json.loads((OLD/'cli-help-exit.safe.json').read_bytes());assert stage['actualExit'] == 1 and not stage['timedOut']
    for suffix in ['stdout','stderr']:assert data.sha((OLD/('cli-help.'+suffix)).read_bytes()) == stage[suffix+'Sha256']
    help_text = (OLD/'cli-help.stdout').read_text()+(OLD/'cli-help.stderr').read_text()
    assert 'Usage:' in help_text and all(flag in help_text for flag in ['-auxclasspath','-auxclasspathFromFile','-effort','-low','-xml','-exitcode'])
    assert not any(text in help_text for text in ['Exception in thread','NoClassDefFoundError','Could not find or load main class','Unrecognized option'])
    verify(invocation);OUT.mkdir();plan['planInvocation'] = plan.pop('invocation')
    data.write(OUT/'manifest.json',dict(plan,actualExit=0,invocation=invocation,originalHelpStage=stage,originalHelpActualExit=1,
        helpSha256=data.sha(help_text.encode()),originalPlanBeginSha256=data.sha((OLD/'begin.safe.json').read_bytes()),helpReexecuted=False,
        analysisExecuted=False,productTestsExecuted=0,externalActions=0,newAccepted=0,whole451Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':main()

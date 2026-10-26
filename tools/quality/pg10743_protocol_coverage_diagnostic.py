"""New metadata-only diagnostic for original locale exec; keeps the original failing guard."""
import json
import os
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import pg9346_direct_companion_jdk_post as steps

SLOT = data.ROOT.parent/'pgpt-runs/PG379/pg10743-protocol-coverage-diagnostic-v1'
OUT = data.BASE/'PG10743-protocol-coverage-diagnostic-v1'


def main():
    invocation = capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    prepared = data.read_checked(data.BASE/'PG10738-protocol-locale-preflight-v1/manifest.json',
        '93e24bd060ad721cc5536b24cbc11d5d00cf6caf3d010d9b3a14cf4e8eb6f899')
    host = data.read_checked(data.BASE/'PG10740-protocol-locale-host-v1/manifest.json',
        'f04f5dc19003d241b411a1ede0d9b24f614758e3b0f67ccf19fa79b61c58a0b6')
    prior = data.ROOT.parent/'pgpt-runs/PG379/pg10742-protocol-locale-post-v1'
    classes = prior/'complete-main'
    assert all(data.sha((classes/name).read_bytes()) == h for name,h in prepared['completeProtocolMainClasses'].items())
    raw_exit = json.loads((prior/'measure-jp-exit.safe.json').read_bytes())
    assert raw_exit['actualExit'] == 1 and not raw_exit['timedOut']
    run = data.ROOT.parent/'pgpt-runs/PG379/pg10740-protocol-locale-host-v1/jp/jacoco.exec'
    assert data.sha(run.read_bytes()) == host['localeRuns'][0]['execSha256']
    helper = data.ROOT/'tools/quality/architecture/ProtocolLocaleCoverageDiagnostic.java'
    helper_sha = data.sha(helper.read_bytes())
    tc = data.ROOT.parent/'toolchain'
    libs = [tc/'m2/repository/org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar',
        *[tc/f'm2/repository/org/ow2/asm/{n}/9.10.1/{n}-9.10.1.jar' for n in ('asm','asm-tree','asm-commons')]]
    deps = {str(p):data.sha(p.read_bytes()) for p in libs}
    SLOT.mkdir()
    reader = SLOT/'reader'
    reader.mkdir()
    cp = os.pathsep.join(map(str,libs))
    steps.SLOT = SLOT
    stages = [steps.step('compile-diagnostic',[str(tc/'jdk-25.0.4/bin/javac'),'--release','25','-proc:none','-Xlint:all','-Werror',
        '-cp',cp,'-d',str(reader),str(helper)])]
    assert stages[0]['actualExit'] == 0
    stages.append(steps.step('diagnose-original-jp',[str(tc/'jdk-25.0.4/bin/java'),'-cp',str(reader)+os.pathsep+cp,
        helper.stem,str(run),str(classes),str(prior/'complete-main-catalog.txt'),'PG10740-PROTOCOL-JP']))
    text = (SLOT/'diagnose-original-jp.stdout').read_text()
    assert 'PHYSICAL_COUNT' in text and 'ANALYZED_COUNT' in text and 'NO_MATCH_COUNT' in text
    assert all(data.sha(Path(p).read_bytes()) == h for p,h in deps.items()) and data.sha(helper.read_bytes()) == helper_sha
    assert data.sha(run.read_bytes()) == host['localeRuns'][0]['execSha256']
    verify(invocation)
    OUT.mkdir()
    with (OUT/'diagnostic.safe.txt').open('x') as stream:
        stream.write(text)
    data.write(OUT/'manifest.json',dict(actualExit=stages[-1]['actualExit'],source=prepared['source'],invocation=invocation,
        stages=stages,diagnosticSha256=data.sha((OUT/'diagnostic.safe.txt').read_bytes()),helperSha256=helper_sha,
        dependencyHashes=deps,originalGuardNotRelaxed=True,originalExecSha256=data.sha(run.read_bytes()),
        productTestsExecuted=0,productCodeExecuted=False,coverageAcceptance=False,wholeF03Accepted=False,
        externalActions=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(json.dumps(dict(actualExit=stages[-1]['actualExit'],diagnostic=text,
        manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))
    raise SystemExit(stages[-1]['actualExit'])


if __name__ == '__main__':
    main()

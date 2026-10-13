"""Explicit published SSC284 section boundary; new-only same owned recovery."""
import types
import subprocess
import pg2344_current_eleven_fd_handoff as prior

SLOT='pg2346-current-eleven-fd-handoff-v2'


def scope(value):
    start='## SSC-284（'
    end='設計公開はこれらやcoverage/PGPT完了の認定ではない。'
    if type(value)is not str or value.count(start)!=1:raise ValueError('one published SSC284 section required')
    body=value[value.index(start):]
    if body.count(end)!=1:raise ValueError('one explicit SSC284 end required')
    return body[:body.index(end)+len(end)]


def payload():return prior.payload().replace(prior.SLOT,SLOT)


def main():
    for path in ['documents/300_SS/340_batch・基盤/343_設定file・directory・初期data・migration・切戻し設計.md','documents/300_SS/350_運用・品質/353_障害検知・復旧runbook.md','documents/300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md']:
        if scope(subprocess.check_output(['git','show','HEAD:'+path],text=True))!=scope(subprocess.check_output(['git','show','origin/main:'+path],text=True)):
            raise ValueError('actual published SSC284 exact section required')
    base=prior.prior
    fn=types.FunctionType(base.main.__code__,{**base.__dict__,'SLOT':SLOT,'PROOF_SLOT':prior.PROOF_SLOT,'PROOF_SHA':prior.PROOF_SHA,'SOURCE':prior.SOURCE,'payload':payload},'current_eleven_fd_handoff_v2')
    return fn()


if __name__=='__main__':raise SystemExit(main())

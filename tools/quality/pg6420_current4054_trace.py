"""Refresh existing943 only from independently qualified original4054, no acceptance increment."""
import argparse
import inspect
import json
import pg6258_current4034_trace as prior

ROOT, PMO, NAMES, W, BASE = prior.ROOT, prior.PMO, prior.NAMES, prior.W, prior.BASE
SOURCE = '669ad5fd83f67ad031b2c1734d7fc5716599d35d'
OUT = W/'pg6420-current4054-trace-v1'
PUBLIC = BASE/'PG6420-current4054-host-measurement-v1'
require, sha, trace, audit = prior.require, prior.sha, prior.trace, prior.audit
base = prior.base


def read_qualified():
    qp = BASE/'PG6408-current4054-cases/qualification.json'; cp = qp.with_name('cases.json')
    receipt = json.loads((W/'pg6410-original4054-artifacts-v1/manifest.safe.json').read_bytes())
    originalpath = W/'pg6408-web-frame-six-v1/manifest.safe.json'; original = json.loads(originalpath.read_bytes())
    require(receipt['actualExit'] == original['actualExit'] == 0 and receipt['source'] == original['source'] == SOURCE
        and receipt['wholeReplayed'] is False and receipt['originalManifestSha256'] == sha(originalpath.read_bytes())
        and receipt['publicQualificationSha256'] == sha(qp.read_bytes()) and receipt['publicCasesSha256'] == sha(cp.read_bytes()),
        'genuine original4054 receipt/artifacts, never begin/prior source')
    q = json.loads(qp.read_bytes())
    require(q['actualExit'] == q['FESFlakyNotRun'] == q['staticSixModules'] == 0 and q['productionSource'] == SOURCE
        and (q['tests'], q['suites'], q['mainClasses']) == (4054, 610, 1667)
        and q['currentOriginalXmlQualified'] is True and q['returnedOriginalTerminalExact'] is True,
        'exact same-source original4054 qualification')
    return qp, q


def definitions(qsha, csha):
    scope = {**vars(prior), 'SOURCE': SOURCE, 'OUT': OUT, 'PUBLIC': PUBLIC, 'read_qualified': read_qualified, 'candidates': candidates}
    raw = inspect.getsource(prior.definitions).replace('PG6244-six-v1', 'PG6408-six-v1').replace('4034', '4054').replace('suites=606', 'suites=610').replace('PG6258-current943-trace-v1', 'PG6420-current943-trace-v1')
    exec(compile(raw, '<original4054 trace definitions>', 'exec'), scope)
    return scope['definitions'](qsha, csha)


def authenticated():
    qp, _ = read_qualified()
    return definitions(sha(qp.read_bytes()), sha(qp.with_name('cases.json').read_bytes()))


def measurement(): return authenticated()['measurement']()


def candidates(texts, before_head):
    scope = {**vars(prior), 'SOURCE': SOURCE, 'OUT': OUT, 'PUBLIC': PUBLIC, 'measurement': measurement}
    raw = inspect.getsource(prior.candidates).replace('870010d6681d74519237be7a7ca6381a190f471a', 'c34159083bfec296fd929ec9b2fbdbb80831c05c').replace('4034', '4054')
    exec(compile(raw, '<saved943 refresh from actual4054>', 'exec'), scope)
    return scope['candidates'](texts, before_head)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('action', choices=['publish', 'stage', 'apply', 'report'])
    args = parser.parse_args(); authenticated()[args.action]()

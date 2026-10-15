"""One necessary whole3706 integration for maintenance PT and lifecycle94 fixes."""
import argparse
import ast
import hashlib
import inspect
import json
import subprocess

from pyflakes.api import check

import pg3350_oracle_boundary_group_integration as base
import pg3366_maintenance_boundary_group as related
from pg3274_header_group_full_six import rebase

ROOT, SOURCE, W = base.ROOT, base.SOURCE, base.W
RENAMES = [('PG3350', 'PG3372'), ('pg3350', 'pg3372'),
           ('PG3352', 'PG3374'), ('pg3352', 'pg3374'),
           ('PG3354', 'PG3376'), ('pg3354', 'pg3376')]


def renamed_function(function, overrides):
    # Transform only function/template code, before actual metadata is embedded.
    raw = inspect.getsource(function)
    for old, new in RENAMES:
        raw = raw.replace(old, new)
    raw = raw.replace('3704', '3706')
    raw = raw.replace('3702 retained plus Media independent UTF8 max and Morning new interrupt; existing Exec/max oracles corrected; Main a9 unchanged;542suite1643',
                      '3704 retained plus two maintenance readback/entry methods and94 lifecycle guards; Main a9 unchanged;542suite1643')
    raw = raw.replace('BUG1291/1292 actual wrong implementation rejections and related44 require one whole3706; no Main/VM/sign/deploy/Root replay',
                      'BUG1294 env corrected/related54 and BUG1295 actual BeforeAll IO no secondaryNPE with94 guarded files require one whole3706; Main a9 unchanged')
    namespace = {**base.__dict__, **overrides}
    exec(compile(raw, '<new3706 code before metadata binding>', 'exec'), namespace)
    return namespace[function.__name__]


def validate(snapshot):
    related.validate(snapshot)
    path = W / 'pg3366-maintenance-boundary-group-v2/manifest.safe.json'
    proof = json.loads(path.read_bytes()); r = proof['result']
    related.prior.require(proof['actualExit'] == r['actualExit'] == r['mavenExit'] == r['staticSixModules'] == r['FESFlakyNotRun'] == 0
                          and r['tests'] == 54 and r['suites'] == 7 and r['mainClasses'] == 1643
                          and r['allMainResourcesDebugSameBytes'] is True, 'actual related54/allMain qualification')
    related.prior.require(not subprocess.check_output(['git', 'diff', r['sourceSnapshot'], snapshot, '--', *related.prior.engine.SCOPE], cwd=ROOT),
                          'all inputs exactly equal actually related-tested source')
    p = W / 'pg3370-db-beforeall-canary-v2/manifest.safe.json'; proof = json.loads(p.read_bytes()); n = proof['result']
    related.prior.require(proof['actualExit'] == n['actualExit'] == n['started'] == n['newPtCredit'] == 0
                          and n['found'] == n['containerFailed'] == 1 and n['beforeAllIoPreserved'] is True
                          and n['secondaryNpe'] is False and n['productionSource'] == SOURCE
                          and n['sourceSnapshot'] == r['sourceSnapshot'], 'actual same-source BeforeAll error without secondary NPE')
    related.prior.require(hashlib.sha256((p.parent / 'canary.private.py').read_bytes()).hexdigest() == proof['payloadSha256'],
                          'fixed actual negative diagnostic payload')


def server_source(head, digest):
    return rebase(base.server_source(head, digest), 'PG3350', 'PG3372', 3704, 3706)


def independent_server():
    tree = ast.parse(rebase(base.independent_server(), 'PG3350', 'PG3372', 3704, 3706)); hits = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            for key, value in zip(node.keys, node.values):
                if isinstance(key, ast.Constant) and key.value == 'batch' and isinstance(value, ast.Tuple) and ast.literal_eval(value) == (1300, 173, 568):
                    value.elts = [ast.Constant(x) for x in (1302, 173, 568)]; hits += 1
    related.prior.require(hits == 1, 'exact independent batch1302/173/568 tuple')
    raw = ast.unparse(ast.fix_missing_locations(tree))
    related.prior.require(check(raw, '<independent3706>') == 0, 'complete namespace')
    return raw


def native_build(*args):
    return renamed_function(base.native_build, {})(*args)


def native_summary(value):
    return renamed_function(base.native_summary, {})(value)


def whole():
    return renamed_function(base.whole, {'validate': validate, 'server_source': server_source})()


def qualify():
    return renamed_function(base.qualify, {'validate': validate, 'independent_server': independent_server})()


def native():
    return renamed_function(base.native, {'validate': validate, 'native_build': native_build, 'native_summary': native_summary})()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['whole', 'qualify', 'native'])
    raise SystemExit({'whole': whole, 'qualify': qualify, 'native': native}[parser.parse_args().action]())

"""Exact journalled mechanical71 apply of proven isolated187 constants, no VM deployment."""
import argparse
import inspect
import json
import pg3694_hygiene_candidate_apply as previous
from pg3928_current_boundary_full_six import ROOT, W, SOURCE, require

OUT = W / 'pg3960-literal-candidate-material-v1'
REMOTE = '/home/mini/schubert-nk-pgpt/runs/PG3952-literal-candidate-v1'


def qualify(proof, fixed):
    r, s = proof['result'], fixed['result']
    require(proof['actualExit'] == fixed['actualExit'] == r['actualExit'] == s['actualExit'] == 0, 'genuine candidate/static success')
    require(r['baseProductionSource'] == s['baseProductionSource'] == SOURCE and r['sourceFiles'] == 849 and r['changedFiles'] == 71 and r['proposedConstants'] == r['requestedFindings'] == 187 and not r['held'], 'actual187/71/all849 same base')
    require(r['allValuesTypedBindingsFullAstAndPublicAbiIdentical'] is True and r['privateCompileTimeStringFieldsOnly'] is True and r['generated70Unchanged'] is True and r['MainApplied'] is False and len(r['modules']) == 6 and all(m['actualExit'] == 0 for m in r['modules'].values()), 'all six final normalized semantic/value/ABI proofs')
    require(s['candidateManifestSha256'] == r['serverManifestSha256'] and s['literalDelta']['candidateManifestSha256'] == r['serverManifestSha256'] and s['literalDelta']['allSourceSha256'] == r['allCandidateSourceSha256'], 'exact complete candidate/static byte closure')
    require(s['pmd']['processingErrors'] == 0 and s['pmd']['rawFindings'] == 1653 and s['literalDelta']['actualRawReduction'] == 187 and s['literalDelta']['ruleCountDeltaFromBase'] == {'AvoidDuplicateLiterals': -187}, 'only exact187 rule reduction, all others unchanged')
    require(s['checkstyle']['actualExit'] == s['checkstyle']['findings'] == 0 and s['mainApplied'] is False and s['F03Accepted'] is False and s['candidateGitSource'] is None, 'fixed Checkstyle0, still unapplied/nonformal')
    return {**r, 'candidateChanges': {p: {'original': v['before'], 'candidate': v['candidate']} for p, v in r['changes'].items()}, 'productionSource': SOURCE, 'checkstyle': s['checkstyle'], 'mainApplied': False}


def qualified():
    return qualify(json.loads((W / 'pg3952-literal-candidate-v1/manifest.safe.json').read_bytes()), json.loads((W / 'pg3958-literal-candidate-static-v1/manifest.safe.json').read_bytes()))


def stage_source():
    raw = inspect.getsource(previous.stage); boundary = raw.index('    os.umask(0o077);')
    raw = 'def stage():\n    require(not subprocess.check_output(["git","status","--porcelain"],cwd=ROOT),"clean committed apply operator")\n    r=qualified()\n' + raw[boundary:]
    raw = raw.replace("not v['mainApplied']", "not v['MainApplied']")
    raw = raw.replace('all214', 'all71').replace('exact214', 'exact71')
    compile(raw, '<closed exact71 source material stage>', 'exec'); return raw


def namespace():
    values = {**previous.__dict__, 'OUT': OUT, 'REMOTE': REMOTE, 'PRIVATE': True, 'OCTAL': False, 'qualified': qualified}
    exec(compile(stage_source(), '<journalled exact71 stage>', 'exec'), values)
    raw = inspect.getsource(previous.apply)
    old = 'count==(30 if OCTAL else 90 if PRIVATE else 214)'
    require(raw.count(old) == 1, 'exact old cardinality boundary')
    raw = raw.replace(old, 'count==71').replace('all214', 'all71').replace('exact214', 'exact71')
    exec(compile(raw, '<journalled exact71 apply>', 'exec'), values)
    return values


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('action', choices=['stage', 'apply']); raise SystemExit(namespace()[parser.parse_args().action]())

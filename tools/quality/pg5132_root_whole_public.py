"""Allowlisted projection of original fresh3814 XML, no new tests/signing/deployment."""
import ast
import inspect
import hashlib
import json
import os
import sys
import pg5058_whole_case_projection as previous
from pg5128_root_full import SOURCE

SLOT = 'PG5128-current3814-cases'


def counts(raw):
    class Rebase(ast.NodeTransformer):
        def visit_Constant(self, node):
            if type(node.value) is int and node.value in (3791, 553, 1650):
                return ast.copy_location(ast.Constant({3791:3814, 553:556, 1650:1654}[node.value]), node)
            return node
    return ast.unparse(ast.fix_missing_locations(Rebase().visit(ast.parse(raw))))


def export_source():
    return counts(inspect.getsource(previous.export).replace('PG4968', 'PG5128'))


def main_source():
    raw = inspect.getsource(previous.main)
    if raw.count('inspect.getsource(export)') != 1: raise ValueError('one complete read-only export source')
    raw = raw.replace('inspect.getsource(export)', 'export_source()')
    raw = raw.replace('pg4970-ssc304-whole-qualified-v1', 'pg5130-root-whole-qualified-v1')
    raw = raw.replace('pg5058-original-case-projection-v2', 'pg5132-root-case-projection-v1')
    raw = raw.replace('PG4968', 'PG5128').replace('PG4970', 'PG5130').replace('PG5058_READ_ONLY', 'PG5132_READ_ONLY')
    return counts(raw)


def main():
    ns = {**vars(previous), 'SOURCE':SOURCE, 'SLOT':SLOT, 'export_source':export_source}
    exec(compile(main_source(), '<original3814 case projection only>', 'exec'), ns)
    return ns['main']()


def publish_qualification():
    path = previous.W / 'pg5130-root-whole-qualified-v1/manifest.safe.json'
    raw = path.read_bytes(); proof = json.loads(raw); value = proof['result']
    out = previous.ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional' / SLOT
    projected = json.loads((out / 'manifest.json').read_bytes())
    if not (type(proof['actualExit']) is int and proof['actualExit'] == 0 and proof['source'] == SOURCE
            and value['tests'] == 3814 and value['suites'] == 556 and value['mainClasses'] == 1654
            and value['staticSixModules'] == value['FESFlakyNotRun'] == 0
            and value['allOriginalCaseIdentitiesRetained'] is True and value['allSixFormatBeforeAnyPt'] is True
            and projected['qualificationManifestSha256'] == hashlib.sha256(raw).hexdigest()):
        raise ValueError('same original full and case projection qualification')
    keys = ('productionSource','sourceSnapshot','sourceArchiveSha256','tests','suites','mainClasses',
            'FESFlakyNotRun','staticSixModules','allSixMainBuildsPassed','allSixFormatBeforeAnyPt',
            'formatBeforePtProofSha256','allOriginalCaseIdentitiesRetained','modules','coverage','jarHashes',
            'allPhysicalMainSha256','changedClasses','unchangedPhysicalClasses','oldNativeImported',
            'candidateNativePending','F03Accepted','formalAccepted','global100','serverManifestSha256')
    output = {key:value[key] for key in keys}
    output.update(deploymentHold=['BUG1414','YKT1178'], newSourceNativeQualified=False,
                  unacceptedSourceIsNotPromoted=True, wholeReplayed=False, acceptedLeafDelta=0, effortPercent=None)
    with (out / 'qualification.json').open('x') as target:
        json.dump(output,target,ensure_ascii=False,indent=2);target.write('\n');target.flush();os.fsync(target.fileno())
    print(json.dumps({'actualExit':0,'sha256':hashlib.sha256((out/'qualification.json').read_bytes()).hexdigest(),
                      'tests':3814,'mainClasses':1654,'deploymentHeld':True}))


if __name__ == '__main__':
    if sys.argv[1:] == ['--qualification-summary']: publish_qualification()
    elif not sys.argv[1:]: main()
    else: raise SystemExit('known read-only publication mode required')

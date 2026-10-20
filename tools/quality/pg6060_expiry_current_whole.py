"""One necessary3979 ordinary finite fixture whole after SSC310; no current/VM/cohort operations."""
import ast
import json
import os
import subprocess
from pyflakes.api import check
import pg6040_remaining33_whole as previous
from pg5940_private_lock_compile import ROOT, W, BASE, sha
from pg6054_expiry_read_qualification import SOURCE
from pg5966_api_sql_selected import source_test_names, ordinary_names

LABEL = 'PG6060'
SLOT = 'pg6060-expiry-six-v1'


def declared_inventory():
    declared = []
    repeated_path = 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/BackupStartIntentFilesTest.java'
    for p in ROOT.glob('src/*/src/test/java/**/*Test.java'):
        if p.relative_to(ROOT).as_posix() == repeated_path:
            old = subprocess.check_output(['git', 'show', previous.SOURCE+':'+repeated_path], cwd=ROOT)
            if p.read_bytes() != old or p.read_text().count('@RepeatedTest(10)') != 1:
                raise ValueError('one exact unchanged historical repeated10 fixture,not generalized expansion')
            names = ordinary_names(p.read_text().replace('@RepeatedTest(10)', '@Test', 1))
            if len(names) != 7 or 'concurrentDistinctOwnersCannotPublishTwoIntents' not in names:
                raise ValueError('six ordinary plus one ten-repetition method')
            declared.append(len(names)+9)
        else:
            declared.append(len(source_test_names(p)))
    if (sum(declared), len(declared)) != (3979, 594):
        raise ValueError('all current named JUnit declarations and fixed repeated10;not inferred PASS')
    return sum(declared), len(declared)


def server_source(head, digest):
    raw = previous.server_source(head, digest).replace('PG6040', LABEL).replace('pg6040', 'pg6060').replace(previous.SOURCE, SOURCE)
    parsed = ast.parse(raw)
    counts = {n: sum(isinstance(x, ast.Constant) and type(x.value) is int and x.value == n for x in ast.walk(parsed)) for n in (3976, 593, 1667)}
    if counts != {3976: 2, 593: 1, 1667: 1}:
        raise ValueError('all exact ordinary whole verdict/result constants accounted for')
    class CurrentCounts(ast.NodeTransformer):
        def visit_Constant(self, node):
            if type(node.value) is int and node.value in (3976, 593):
                return ast.copy_location(ast.Constant({3976: 3979, 593: 594}[node.value]), node)
            return node
    raw = ast.unparse(ast.fix_missing_locations(CurrentCounts().visit(parsed)))
    if check(raw, '<current3979 host fixtures>') or any(s in raw for s in ('systemctl', 'qemu-system', 'virsh', 'sudo ', '/opt/schubert-nk/current', '--recover', '--resume')):
        raise ValueError('same approved finite PT profile;held actual runtime actions excluded')
    compile(raw, '<current3979 ordinary fixture whole>', 'exec')
    return raw


def driver_source(fresh):
    raw = previous.driver_source(fresh).replace(previous.SLOT, SLOT).replace('PG6040', LABEL).replace('pg6040', 'pg6060')
    old = "'tests': 3976, 'suites': 593, 'mainClasses': 1667"
    if raw.count(old) != 1:
        raise ValueError('one explicit new3979/594 expected inventory')
    raw = raw.replace(old, "'tests': 3979, 'suites': 594, 'mainClasses': 1667", 1)
    start = raw.index("'trigger': "); end = raw.index('}, sort_keys=True)', start)
    trigger = 'SSC310/PG-D456/BUG1530: one changed Expiry read,one new private mandatory projection helper,three new pure proxy JUnit cases and BAT287 approved readRuntime oracle correction. Genuine148/16 and all8511667/4physical/other18method unchanged/publicABI/static1305/Checkstyle0 first. Necessary same-source3979/594 after behavioral fix,not confirmation replay of old3976 or selected148. Allsix format first,ordinary owned tempDB/JMS/HTTP/finite children only;no actual VM/current/Root/cohort/permit or historical native import. Formal/global/native/CHR/451 remain separate.'
    raw = raw[:start]+"'trigger': "+repr(trigger)+raw[end:]
    compile(raw, '<new-only3979 driver>', 'exec')
    return raw


def prerequisites():
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT):
        raise ValueError('clean committed operator first')
    if subprocess.check_output(['git', 'diff', SOURCE, '--', 'src', 'pom.xml', '.mvn', 'mvnw', 'tools/quality/static', 'program/characterization'], cwd=ROOT):
        raise ValueError('canonical Main/Test/gates fixed')
    for name, digest in (('PG6054-expiry-read-qualification-v1', '9f1269de6b66c0be2467aab5de164e82553f03d33dc79f5212e410ff4f1daee9'), ('PG6056-expiry-read-methods-v1', 'cf6ff34569efcb8a261935c03bd4d4ba64092163c4b717f0aaa2f3e687e6afeb')):
        p = BASE/name/'manifest.json'
        if sha(p) != digest or json.loads(p.read_bytes())['source'] != SOURCE:
            raise ValueError('actual same-source selected/static/method qualification first')
    data = json.loads((W/'pg6054-expiry-read-qualification-v1/manifest.safe.json').read_bytes())
    if sha(W/'pg6054-expiry-read-qualification-v1/manifest.safe.json') != '14128e3496c796aca15bb9bd8bc46d87a2662a34e8f412125d1b667ff029c885' or data['actualExit'] != 0:
        raise ValueError('actual original all8511667 manifest')
    if {p.relative_to(ROOT).as_posix(): sha(p) for p in ROOT.glob('src/*/src/main/java/**/*.java')} != data['allSourceHashes']:
        raise ValueError('all original Main fixed')
    declared_inventory()


def main():
    prerequisites(); server_source(SOURCE, '0'*64)
    fresh = previous.RUNTIME.preflight(); os.umask(0o077)
    with (W/'pg6060-preflight-v1.safe.json').open('x') as f:
        json.dump(fresh, f, sort_keys=True); f.flush(); os.fsync(f.fileno())
    scope = {**vars(previous.RUNTIME.previous.driver), 'SOURCE': SOURCE, 'LABEL': LABEL, 'server_source': server_source}
    exec(compile(driver_source(fresh), '<one necessary current3979>', 'exec'), scope)
    return scope['main']()


if __name__ == '__main__':
    raise SystemExit(main())

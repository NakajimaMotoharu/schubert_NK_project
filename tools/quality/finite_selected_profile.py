"""Shared finite component profile; fixed six gates and original snapshot/terminal contracts."""
import re
import subprocess
import pg5732_enum48_selected as engine
from pg5966_api_sql_selected import source_test_names
from pg5984_web_form_selected_v2 import node_environment
from pg6052_expiry_combined_selected import runner_source
from pg6470_web_owned_component_selected import compile_first


def inventory(extra, expected):
    cases = {m: set(names) for m, names in engine.CASES.items()}
    for module, names in extra.items():
        cases[module].update(names)
    counts = {engine.PACKAGE+n: len(source_test_names(
        engine.ROOT/('src/schubert-nk-'+m+'/src/test/java')/
        ((engine.PACKAGE+n).replace('.', '/')+'.java')))
        for m, names in cases.items() for n in names}
    if (sum(counts.values()), len(counts)) != tuple(expected):
        raise ValueError('exact ordinary declarations and all six guards required')
    return cases, counts


def runner(total, suites, targets):
    if type(total) is not int or type(suites) is not int or total < 12 or suites < 7:
        raise ValueError('explicit complete baseline inventory')
    if not targets or any(m not in engine.MODULES or not names for m, names in targets.items()):
        raise ValueError('explicit nonempty module targets')
    raw = runner_source(total, suites, target_count=sum(len(names) for names in targets.values()))
    before = "os.pathsep+os.environ['PATH'],MAVEN_OPTS"
    if raw.count(before) != 1:
        raise ValueError('one pinned Node environment')
    return compile_first(raw.replace(before, 'os.pathsep+NODE_PATH,MAVEN_OPTS', 1))


def execute(slot, guard, cases, counts, expected, targets):
    if not re.fullmatch(r'pg[0-9]+-[a-z0-9-]+', slot):
        raise ValueError('new-only finite profile name')
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=engine.ROOT):
        raise ValueError('clean committed Main/Test/operator first')
    guard('HEAD')
    if set(cases) != set(engine.MODULES) or (sum(counts.values()), len(counts)) != tuple(expected):
        raise ValueError('all six exact inventory guards retained')
    scope = {**vars(engine), 'SLOT': slot, 'NODE_PATH': node_environment(),
             'CASES': cases, 'COUNTS': counts, 'TARGETS': targets, 'test_names': source_test_names}
    exec(compile(runner(*expected, targets), '<finite shared component profile>', 'exec'), scope)
    return scope['main']()

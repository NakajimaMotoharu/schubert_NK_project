"""Current758 signed existing-only ADMIN; same source, closed newpair/marker contract."""
import datetime
import json
from pathlib import Path
import re
import pg737_sources as previous
from pg761_current_binding import bind
from pg662_sources import replace

R=Path(__file__).resolve().parent
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
SOURCE='8d4b68b4f1449932ebe506aaf08e584bbfea8dd2'


def actual():
    return (json.loads((W/'pg761-completed-readonly-v1.safe.json').read_bytes()),
            json.loads((W/'pg767-completed-baseline-v1.safe.json').read_bytes()))


def current(raw,proof=None,baseline=None):
    if proof is None and baseline is None:proof,baseline=actual()
    assert type(proof)is dict and type(proof.get('actualExit'))is int and proof['actualExit']==0
    assert proof['productionSource']==SOURCE and proof['batchRun']=='9de2d03c-28c7-4647-97d9-c66ace06048c'
    assert proof['cutoff']=='2026-10-09T05:42:22.532331Z' and proof['activation']=='021111b4-6de5-4733-917d-5ac176240ffc'
    assert proof['genuineCompletion']['genuineRootDone']is True and proof['genuineCompletion']['genuinePid1StartDone']is True
    end=proof['genuineCompletion']['endMonotonicUs'];assert type(end)is int and 137240785885<=end<=139040785885
    wall=proof['parentEndedUTC'];assert type(wall)is str and re.fullmatch(r'2026-10-09T[0-9:]{8}\.[0-9]{6}Z',wall)
    assert datetime.datetime.fromisoformat(wall.replace('Z','+00:00'))>=datetime.datetime.fromisoformat(proof['cutoff'].replace('Z','+00:00'))
    assert type(baseline)is dict and type(baseline.get('actualExit'))is int and baseline['actualExit']==0
    assert baseline['source']==SOURCE and type(baseline['batchRows'])is int and baseline['batchRows']==544
    assert baseline['full21Fields']is True and baseline['all24UnchangedTwice']is True and baseline['all10KernelAndResources0']is True
    sha=baseline['beforeSha256'];assert type(sha)is str and re.fullmatch('[0-9a-f]{64}',sha)
    raw=bind(raw)
    pairs=(('pg737','pg768'),('Pg737','Pg768'),('PG737','PG768'),
        ('pg736-completed-baseline-v1','pg767-completed-baseline-v1'),
        ('c69d13e43a14525d2e2ec894378e5fd1f6735574f1c63dadadb2306324936f0b',sha),
        ('==534)','==544)'),('==129343844863','=='+str(end)),
        ('2026-10-09T03:30:40.608594Z',wall),
        ('pg715-release-v1','pg750-release-v1'),('pg713-expiry-six-host-v1','pg748-closing-six-host-v1'))
    return replace(raw,tuple((a,b)for a,b in pairs if a in raw))


def assemble(proof,baseline):
    def c(raw):return current(raw,proof,baseline)
    refs=c(previous.refs())
    old="require(messages.count('Initial ADMIN bootstrap finished')==messages.count('Bootstrap fixed PT native capture complete')==1 and 'Initial ADMIN bootstrap failed'not in messages)"
    refs=replace(refs,((old,'completion_messages(messages)'),
        ('retire_no_replace,UNIT,SOURCES','retire_no_replace,UNIT,SOURCES,completion_messages'),
        ("'pg702-bootstrap-existing-v1'}", "'pg702-bootstrap-existing-v1','pg737-bootstrap-tools-v1','pg737-bootstrap-verify-v1','pg737-bootstrap-existing-v1'}")))
    contract=(R/'pg768_bootstrap_contract.py').read_text()
    python={'pg768_bootstrap_existing.py':refs,'pg768_parent_receipt.py':c(previous.receipt()),'pg768_parent_join.py':c(previous.join()),'pg535_bootstrap_contract.py':contract}
    for name in ('pg536_bootstrap_execution_contract.py','pg529_dependency_graph.py','pg556_parent_receipt.py',
                 'pg559_terminal_refs.py','pg457_stable_actor.py','pg570_directory_identity.py'):python[name]=(R/name).read_text()
    native=c(previous.native())
    old="files[name] = CLASSDIR / name if name in ('pg768_bootstrap_existing.py','pg768_parent_receipt.py','pg768_parent_join.py') else R / name"
    new="files[name] = CLASSDIR / name if name in ('pg768_bootstrap_existing.py','pg768_parent_receipt.py','pg768_parent_join.py','pg535_bootstrap_contract.py') else R / name"
    native=replace(native,((old,new),))
    return {'java':c(previous.java()),'refs':refs,'receipt':python['pg768_parent_receipt.py'],'join':python['pg768_parent_join.py'],
        'argument_test':c(previous.argument_test()),'compile_script':c(previous.compile_script()),'native':native,'python_files':python}


def value(name):return assemble(*actual())[name]
def java():return value('java')
def refs():return value('refs')
def receipt():return value('receipt')
def join():return value('join')
def argument_test():return value('argument_test')
def compile_script():return value('compile_script')
def native():return value('native')
def python_files():return value('python_files')

"""Immutable a2ecc same-cohort full11 admission; prior80 exec are data only."""
import ast
import json
import types
import pg4900_current_admission_image as previous
import pg5022_new_normal_root_once as entry
import pg5024_new_normal_live_binding as binding
from pg4996_resume_connection import authenticate_host

W = entry.W
SLOT = 'pg5036-current-full11-admission-v1'
SOURCE, BOM, ONCE, LIVE = entry.SOURCE, entry.BOM, entry.SLOT, binding.SLOT
PUBLICATION = '03d3cd12a41861fa7c495949aebe5ac12cf3a638f66b13f3ef9e0ef96a059d8f'
PUBLICATION_PATH = 'pg5014-ssc304-publication-independent-post-v1/after.private.json'


def bind(raw):
    raw = previous.bind(raw)
    for a, b in [(previous.SOURCE, SOURCE), (previous.BOM, BOM), (previous.ONCE, ONCE),
                 (previous.LIVE, LIVE), (previous.PUBLICATION, PUBLICATION),
                 (previous.PUBLICATION_PATH, PUBLICATION_PATH)]:
        raw = raw.replace(a, b)
    return raw


def project_source():
    return previous.project_source().replace('!=72', '!=80').replace('all72', 'all80')


def project(value, publication):
    ns = {}
    exec(compile(project_source(), '<lossless actual full11/all80 view>', 'exec'), ns)
    return ns['project'](value, publication)


def payload(observed):
    raw = bind(previous.previous.payload(observed)).replace("'nativeExecEntries':64", "'nativeExecEntries':80")
    node = next(n for n in ast.parse(raw).body if isinstance(n, ast.FunctionDef) and n.name == 'project')
    return raw.replace(ast.get_source_segment(raw, node), project_source(), 1)


def live():
    value = json.loads((W / LIVE / 'manifest.safe.json').read_bytes())
    if not (type(value['actualExit']) is int and value['actualExit'] == 0
            and value['source'] == SOURCE and value['result']['productionSource'] == SOURCE):
        raise ValueError('actual current same-generation independent live binding')
    return {**value['result']['binding'], 'rootPid': value['result']['rootPid']}


def before():
    value = json.loads((W / SLOT / 'manifest.safe.json').read_bytes())
    if not (type(value['actualExit']) is int and value['actualExit'] == 0
            and value['source'] == SOURCE and value['result']['binding'] == live()):
        raise ValueError('actual same-cohort immutable before proof')
    return value['result']['privateBeforeSha256']


def execute(slot, raw, timeout=90):
    authenticate_host()
    transport = previous.transport
    return types.FunctionType(transport.execute.__code__, {**vars(transport), 'SOURCE': SOURCE})(slot, raw, timeout)


if __name__ == '__main__':
    raise SystemExit(execute(SLOT, payload(live())))

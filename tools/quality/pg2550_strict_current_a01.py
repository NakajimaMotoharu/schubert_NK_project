"""Fresh Source real A01 while actual Root owns ordinary peers; unchanged Current oracle."""
import ast
import json
import pg2470_question_current_a01 as previous
from pg2516_current_strict_candidate_sources import SOURCE, W
from pg2532_strict_normal_publication_sources import candidate_bom


def code():
    live = json.loads((W / 'pg2542-strict-current-live-binding-v1/manifest.safe.json').read_bytes())
    if type(live.get('actualExit')) is not int or live['actualExit'] != 0 or live.get('productionSource') != SOURCE:
        raise ValueError('actual same-source new Root identity required')
    raw = previous.code()
    for before, after in [('PG2470', 'PG2550'), ('pg2470', 'pg2550'), ('pg2446', 'pg2538'),
        ('pg2448-question-current-noargs-once-v1', 'pg2540-strict-current-noargs-once-v1'),
        ('pg2444-question-normal-publication-post-v1', 'pg2536-strict-normal-publication-post-v1'),
        (previous.SOURCE, SOURCE), (previous.BOM, candidate_bom()), ('PG2428', 'PG2512'),
        ("issued['MainPID']=='194154'", "issued['MainPID']=='" + str(live['rootPid']) + "'"),
        ("m['InvocationID']=='9024d0364d07478d9237b6941d725208'", "m['InvocationID']=='" + live['binding']['invocation'] + "'")]:
        if before not in raw:
            raise ValueError('one exact actual A01 producer/consumer boundary required')
        raw = raw.replace(before, after)
    ast.parse(raw)
    return raw


if __name__ == '__main__':
    ns = {'__file__':__file__, '__name__':'strict_current_a01'}
    exec(compile(code(), '<new Source actual A01 driver>', 'exec'), ns)
    ns['main']()

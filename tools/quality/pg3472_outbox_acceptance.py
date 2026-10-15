"""New-source terminal/all24/seal independent readers, no business mutation authority."""
import inspect
import ast
import json
import sys
import types
from pyflakes.api import check

import pg2700_operation_current_terminal as old_terminal
import pg2702_operation_current_rows as old_rows
import pg2704_operation_current_full_seal as old_seal
from pg3462_outbox_current_observer import SOURCE, BOM
from pg3464_outbox_current_noargs_once import SLOT as ONCE
from pg3466_outbox_current_live_binding import SLOT as LIVE
from pg3470_outbox_admission_before import before
from pg3434_current_outbox_candidate_sources import BOOT
from pg1446_current_cold_stage import W
import pg1769_next_day_rows_oracle as newday
import pg2886_network_newcurrent_full_seal as prior_newday_seal

TERM = 'pg3472-outbox-current-terminal-v1'
ROWS = 'pg3474-outbox-current-rows-v1'
SEAL = 'pg3476-outbox-current-full-seal-v1'


def bind(raw):
    for a, b in [('PG2654', 'PG3420'), ('pg2654-manifest.sig', 'pg3420-manifest.sig'),
                 ('b2d6f605-61cf-425f-8fbd-12d606f6ee66', BOOT),
                 ('b2d6f60561cf425f8fbd12d606f6ee66', BOOT.replace('-', '')),
                 ('pg2686-operation-current-live-binding-v1', LIVE),
                 ('pg2684-operation-current-noargs-once-v2', ONCE),
                 ('pg2682-parent-watch-v1', 'pg3462-parent-watch-v1'),
                 (old_terminal.SOURCE, SOURCE), (old_terminal.SLOT, TERM),
                 (old_rows.SLOT, ROWS), (old_seal.SLOT, SEAL)]:
        raw = raw.replace(a, b)
    compile(raw, '<actual current4856 independent reader>', 'exec')
    return raw


def terminal_payload(binding):
    return bind(old_terminal.payload(binding, BOM))


def rows_payload():
    # The immutable before-image proves day16 has no prior step history. The
    # old same-day/ALREADY_SUCCESSFUL oracle is deliberately not used here.
    live = json.loads((W / LIVE / 'manifest.safe.json').read_bytes())
    proof = json.loads((W / 'pg3470-outbox-admission-before-v1/manifest.safe.json').read_bytes())
    if (live['actualExit'] != 0 or proof['actualExit'] != 0
            or proof['productionSource'] != SOURCE or proof['guest']['businessDate'] != '2026-10-16'
            or proof['guest']['sameDayHistoryCount'] != 0):
        raise ValueError('actual day16 new-run before/oracle binding required')
    g = proof['guest']; binding = live['binding']
    oracle = newday.oracle_source().replace("r['business_date']=='2026-10-13'", "r['business_date']=='2026-10-16'")
    body = newday.payload()
    body = body[body.index('import hashlib,os,pathlib,subprocess\n'):]
    for a, b in [('pg1759-next-day-ordinary-once-v1', ONCE),
                 ('a919274268cfd66a4478f83cfeff52c1bfc3fb12323209133218bdc72d01c23e', before()),
                 ('pg1768-next-day-inbox-oracle-v1', 'pg3470-outbox-admission-before-v1'),
                 ('a1f2ff92e014509b67dfb727f41fe5165b75d18f271ee90a68b8f7518aefe030', g['oracleSha256']),
                 ('pg1769-next-day-rows-oracle-v1', ROWS)]:
        body = body.replace(a, b)
    return 'SOURCE=' + repr(SOURCE) + '\n' + oracle + '\nRUN=' + repr(binding['run']) + '\nCUT=' + repr(binding['cutoff']) + '\n' + body


def seal_payload(binding):
    fn = types.FunctionType(old_seal.payload.__code__,
                            {**old_seal.__dict__, 'SOURCE': SOURCE, 'SLOT': SEAL, 'TERM': TERM,
                             'before': before, 'terminal': lambda b, bom: terminal_payload(b)})
    raw = bind(fn(binding, BOM))
    # Whole-seal independently re-evaluates the same SS before selectors. Never
    # leave the historical same-day/ALREADY_SUCCESSFUL oracle embedded here.
    oracle = prior_newday_seal.oracle(binding)
    for name in ['r', 'row']:
        old = name + "['business_date']=='2026-10-15'"
        if oracle.count(old) != 1:
            raise ValueError('one exact newday predicate required: ' + name)
        oracle = oracle.replace(old, name + "['business_date']=='2026-10-16'")
    nodes = [n for n in ast.parse(raw).body if isinstance(n, ast.Assign)
             and any(isinstance(t, ast.Name) and t.id == 'ORACLE' for t in n.targets)]
    if len(nodes) != 1:
        raise ValueError('one complete independent whole-seal oracle required')
    segment = ast.get_source_segment(raw, nodes[0])
    raw = raw.replace(segment, 'ORACLE=' + repr(oracle), 1)
    if check(raw, '<whole current4856 seal>'):
        raise ValueError('all actual source/run seal exports required')
    return raw


def entry(phase):
    modules = {'terminal': (old_terminal, TERM, terminal_payload),
               'rows': (old_rows, ROWS, rows_payload), 'seal': (old_seal, SEAL, seal_payload)}
    if phase not in modules:
        raise ValueError('explicit independent terminal/rows/seal only')
    module, slot, payload = modules[phase]
    raw = inspect.getsource(module.entry)
    for a, b in [('pg2686-operation-current-live-binding-v1', LIVE),
                 ('pg2682-parent-watch-v1', 'pg3462-parent-watch-v1'),
                 ('pg2702-operation-current-rows-v1', ROWS),
                 ('pg2700-operation-current-terminal-v1', TERM)]:
        raw = raw.replace(a, b)
    ns = {**module.__dict__, 'SOURCE': SOURCE, 'SLOT': slot, 'TERM': TERM, 'payload': payload}
    exec(compile(raw, '<new independent phase factory>', 'exec'), ns)
    return ns['entry']()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('explicit terminal/rows/seal required')
    raise SystemExit(entry(sys.argv[1])())

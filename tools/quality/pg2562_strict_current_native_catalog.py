"""Fresh actual native ten-point catalogue; historical22 copies preserved, never imported."""
import inspect
import json
from pyflakes.api import check
import pg2466_question_current_native_catalog as previous
from pg2554_strict_current_owned_sources import SOURCE, TOOLS
from pg2546_strict_current_rows import BEFORE
from pg1446_current_cold_stage import W

SLOT = 'pg2562-strict-current-native-catalog-v1'


def catalog_source(receipt, binding, end):
    raw = previous.catalog_source(receipt, binding, end)
    for before, after in [(previous.TOOLS, TOOLS), ('pg2458', 'pg2554'), ('Pg2458', 'Pg2554'),
        ('PG2458', 'PG2554'), ('pg2448-question-current-noargs-once-v1', 'pg2540-strict-current-noargs-once-v1'),
        (previous.BEFORE, BEFORE), (previous.SOURCE, SOURCE), ('require(len(old)==16)', 'require(len(old)==22)'),
        ('priorOldSourceSixteenCopiesPreserved', 'priorOldSourceTwentyTwoCopiesPreserved')]:
        raw = raw.replace(before, after)
    if check('SEALS={}\n' + raw, '<new actual ten point native catalogue>'):
        raise ValueError('whole actual native catalogue namespace required')
    compile(raw, '<fresh current native all points>', 'exec')
    return raw


def main():
    live = json.loads((W / 'pg2542-strict-current-live-binding-v1/manifest.safe.json').read_bytes())
    terminal = json.loads((W / 'pg2544-strict-current-terminal-v1/manifest.safe.json').read_bytes())
    if any(type(v.get('actualExit')) is not int or v['actualExit'] != 0 or v.get('productionSource') != SOURCE for v in [live, terminal]):
        raise ValueError('actual fresh Source Root terminal required')
    raw = inspect.getsource(previous.prior.transport.main).replace(
        'pg2040-fresh-normal-warning-terminal-post-v1', 'pg2560-strict-current-owned-post-v1').replace(
        'pg2030_parent_receipt.py', 'pg2554_parent_receipt.py')
    ns = {**previous.prior.transport.__dict__, 'SOURCE':SOURCE, 'TOOLS':TOOLS, 'SLOT':SLOT,
          'catalog_source':lambda receipt:catalog_source(receipt, live['binding'], terminal['endMonotonicUs'])}
    exec(compile(raw, '<fresh Source actual point catalogue observer>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())

"""Receipt-only proof for actual PG1184 generation; never old timeout acceptance."""
import ast
import inspect
import pg1117_current_done_probe as previous
from pg1185_current_resume_receipt import source as receipt_source, CURRENT

BINDING = dict(CURRENT, run='343a5a1b-d064-47d5-88c2-31c36d7ba7a4',
               cutoff='2026-10-10T12:40:27.396847Z', activation='ada3f7ff-8287-48d7-9ba9-5cce71f61bd3')


def payload():
    receipt = receipt_source().replace("oracle = Path(__file__).with_name('pg609_parent_receipt.py').read_bytes()", 'oracle = ORACLE_SOURCE')
    s = 'ORACLE_SOURCE='+repr((previous.R/'pg609_parent_receipt.py').read_bytes())+'\nBINDING='+repr(BINDING)+'\n'+receipt+'\n'+previous.PROBE
    ast.parse(s);return s


def main():
    s = inspect.getsource(previous.main).replace('pg1112-parent-watch-v1.private.jsonl', 'pg1183-parent-watch-v1.private.jsonl').replace('pg1117-current-done-receipt-v1', 'pg1186-current-resume-done-receipt-v1').replace('PG1117-current-done-receipt-v1', 'PG1186-current-resume-done-receipt-v1')
    env = dict(previous.__dict__);env['payload'] = payload
    exec(compile(s, '<fresh actual current done probe>', 'exec'), env);return env['main']()


if __name__ == '__main__':raise SystemExit(main())

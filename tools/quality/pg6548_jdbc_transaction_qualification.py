"""Join actual green23/9 to all851/1667 original artifacts; no prior-source coverage union."""
import json
from pg6544_jdbc_transaction_selected import W, BASE, MAINS, inventory, guard_source
from pg6054_expiry_read_qualification import qualify

RUN = W/'pg6546-jdbc-transaction-green-v1'


def main():
    source = json.loads((RUN/'begin.safe.json').read_bytes())['source']
    guard_source(source, 'green'); cases, _ = inventory('green')
    return qualify(source, RUN, cases, (23, 9), MAINS,
        BASE/'PG6540-jdbc-graph-qualification-v1/manifest.json',
        '34fa4259f6c8a0ab250c1aba63b2e03346dd5d75364f9d5f4ce41bb4f4255222',
        W/'pg6540-jdbc-graph-qualification-v1/manifest.safe.json',
        W/'pg6540-jdbc-graph-qualification-v1/findings.safe.json',
        'pg6548-jdbc-transaction-qualification-v1', 'PG6548-jdbc-transaction-qualification-v1',
        expected_phase_exits=(0, 0, 0))


if __name__ == '__main__':
    main()

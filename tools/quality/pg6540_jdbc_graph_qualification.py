"""Original green23/12 only; exact three Main deltas and unchanged red oracle bytes."""
import json
from pg6534_jdbc_fatal_graph_selected import W, BASE, PROFILES, MAINS, inventory, guard_source
from pg6054_expiry_read_qualification import qualify

RUN = W/PROFILES['green'][0]


def original_source():
    source = json.loads((RUN/'begin.safe.json').read_bytes())['source']
    guard_source(source, 'green')
    return source


def main():
    source = original_source(); cases, _ = inventory('green')
    return qualify(source, RUN, cases, (23, 12), MAINS,
        BASE/'PG6522-maintenance-owner-qualification-v1/manifest.json',
        'f8944dbe60d775ee479169070d2e883a0a4d5aa8f05818f6f3dd51a254a97ae9',
        W/'pg6522-maintenance-owner-qualification-v1/manifest.safe.json',
        W/'pg6522-maintenance-owner-qualification-v1/findings.safe.json',
        'pg6540-jdbc-graph-qualification-v1', 'PG6540-jdbc-graph-qualification-v1',
        expected_phase_exits=(0, 0, 0))


if __name__ == '__main__':
    main()

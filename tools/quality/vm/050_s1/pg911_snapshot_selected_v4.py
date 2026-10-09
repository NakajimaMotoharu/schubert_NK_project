"""PG-D407 new candidate: selected independent state-partition tests, not old native acceptance."""
import json
import pg743_closing_selected as selected
from pg911_snapshot_selected_v2 import code, dependency_bytes

selected.D = selected.W / 'pg911-snapshot-selected-v4'
if __name__ == '__main__':
    print(json.dumps({'dependencyMainClassCounts': dependency_bytes(), 'classByteMismatch': 0}), flush=True)
    raw = code().replace('PG911-snapshot-selected-v2', 'PG911-snapshot-selected-v4')
    env = dict(selected.__dict__)
    exec(compile(raw, '<911 v4 PG-D407 new candidate>', 'exec'), env)
    env['main']()

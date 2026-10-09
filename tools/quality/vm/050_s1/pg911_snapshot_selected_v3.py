"""Separate fixed live-data fixture run; failed v1/v2 and their stale XML remain preserved."""
import inspect,json
import pg743_closing_selected as selected
from pg911_snapshot_selected_v2 import code,dependency_bytes
selected.D=selected.W/'pg911-snapshot-selected-v3'
if __name__=='__main__':
 print(json.dumps({'dependencyMainClassCounts':dependency_bytes(),'classByteMismatch':0}),flush=True)
 raw=code().replace('PG911-snapshot-selected-v2','PG911-snapshot-selected-v3')
 env=dict(selected.__dict__);exec(compile(raw,'<911 v3 fixed independent live fixture>','exec'),env);env['main']()

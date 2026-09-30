"""Scope-limited evidence structure and secret-pattern check, not whole project acceptance."""
import json, pathlib, re, xml.etree.ElementTree as ET
root = pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation/evidence/01_PT/018_NK-OPS-001/evidence/provisional')
files = []
for name in ['PG400-broker-double-readiness-baseline', 'PG400-native-three-actual-gates']:
    files.extend(p for p in (root/name).rglob('*') if p.is_file())
for path in files:
    assert path.suffix in ['.xml', '.json']
    text = path.read_text()
    assert '-----BEGIN' not in text
    assert not re.search(r'(?i)(authorization|cookie|password|session_id|access_token)\s*[:=]\s*["\']?[^\s<>]', text)
    if path.suffix == '.xml':
        suite = ET.fromstring(text)
        assert suite.tag == 'testsuite' and set(suite.attrib) == {'name','tests','failures','errors','skipped','time'}
        assert all(c.tag == 'testcase' and set(c.attrib) == {'name','classname','time'} and not list(c) for c in suite)
    else:
        data = json.loads(text)
        assert data['formal'] is False and data['sourceCommit'] == 'bb003f2b8bca09456cd8bb856dbdd22f4a09f872'
print(json.dumps({'scope':'PG400 new sanitized evidence only','files':len(files),'structureErrors':0,'secretPatternFindings':0,'wholeProjectGate':False}))

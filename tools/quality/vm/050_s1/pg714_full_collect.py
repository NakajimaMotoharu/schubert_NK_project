"""Fresh 3502PT517suite whole qualification; changed batch matches independent PG712."""
from pathlib import Path
from pg662_sources import replace

R = Path(__file__).resolve().parent
SOURCE = '1ec19782a1afe22d1de75b05f4cd12b8a8a8a172'


def source():
    raw = (R / 'pg618_collect_candidate_full.py').read_text()
    raw = replace(raw, (
        ("'PG630': ('pg630-retention-factory-six-host-v1', 'pg628-retention-factory-component-v1',\n                  'e5ab539ed7e48de9889f6acbe28a8e2f71b3d20a633714ea6b548fc0ca3340b8',\n                  3468, 277, None)",
         "'PG630': ('pg713-expiry-six-host-v1', 'pg712-expiry-core-qualification-v1',\n                  '6ec88744cd5bffc3eee238753cba6bf22e21b8f4dd96287852de0c9121d804ef',\n                  3502, 283, None)"),
        ("old = W/('pg620-typed-oracle-six-host-v1'if selector=='PG630'", "old = W/('pg680-owner-six-host-v1'if selector=='PG630'"),
        ('e83d2c34652b8c2bea5c1b9c02f00e9b757b88b5de6b1fb45e79b615ec003b57', 'b710c69b798fcd14b35644541aed835689d81e6f0cbf40c3d67786e014f599e6'),
        ("'api': (5, 4)", "'api': (7, 6)"),
        ('reference = selected/name if module == selected_module else old/module/name',
         "reference = W/'pg711-expiry-core-v1/batch'/name if module == selected_module else old/module/name\n        if module == selected_module:assert sha(reference)==json.loads((selected/'manifest.safe.json').read_bytes())['jarSha256']"),
        ('suites == 512 and total_classes == 1605', 'suites == 517 and total_classes == 1614'),
        ("'72fb7440697ee1048a5c0145055dc1cc3c577914'if selector=='PG630'", "'9bd50536f692610036a0ed8b83e0a8b35fe2a66f'if selector=='PG630'"),
        ('assert len(cases) == int(root.get(\'tests\')) > 0', "assert len(cases) == int(root.get('tests')) > 0\n            assert len({(c.get('classname'),c.get('name'))for c in cases})==len(cases)"),
        ("assert not ET.parse(base/'spotbugsXml.xml').getroot().findall('.//BugInstance')", "bugs=ET.parse(base/'spotbugsXml.xml').getroot();assert not bugs.findall('.//BugInstance')and not bugs.findall('.//Error')"),
    ))
    return raw


if __name__ == '__main__':
    env = {'__file__': str(R / 'pg714_full_collect.py'), '__name__': 'qualified_expiry_source'}
    exec(compile(source(), '<fresh six new Expiry source>', 'exec'), env)
    # The actual frozen run source is recorded by its clean source guard.
    recorded = (Path('/home/mini/codex/project1/work/pgpt-runs/PG379/pg713-expiry-six-host-v1') / 'source').read_text().strip()
    assert recorded == SOURCE
    env['main'](recorded, 'PG630')

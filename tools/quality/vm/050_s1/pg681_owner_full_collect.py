"""Independent fixed whole-six qualification with two selected module byte oracles."""
from pathlib import Path
import sys
from pg674_collect_full import source as previous

R = Path(__file__).resolve().parent


def source():
    raw = previous()
    replacements = (
        ('pg672-entry-six-host-v2', 'pg680-owner-six-host-v1'),
        ('pg670-entry-component-v1', 'pg678-parent-guard-component-v1'),
        ('fec725f2f89945be5c88d5ef98a8446e155e7d701748a118191cdd2c8211f95b', '4c923f5f1f065885b3abb3f242b7fa68b69fe64c275681e72d59df47360d6daf'),
        ('3477, 277, None', '3489, 283, None'),
        ("old = W/('pg630-retention-factory-six-host-v1'if selector=='PG630'", "old = W/('pg672-entry-six-host-v2'if selector=='PG630'"),
        ('067b8a155fe5a137aebb9c732bf800122752cb173ca8a09f3c41087d9efc178b', 'b66da36efa077a7f41bcfb9777fad702c986dccc07b872962db00495f378a26c'),
        ('suites == 514 and total_classes == 1608', 'suites == 516 and total_classes == 1612'),
        ("selected_module = 'api'if selector=='PG630'", "selected_module = 'bootstrap'if selector=='PG630'"),
        ('reference = selected/name if module == selected_module else old/module/name',
         "references = {'bootstrap': selected, 'api': W/'pg676-inspector-owner-component-v3'}\n        if module == 'api':\n            assert sha(references['api']/'manifest.safe.json') == 'b914ab23de6be3100eea616188d415b8e10baa4b23da8fd7aad20413b97d339b'\n        reference = references[module]/name if module in references else old/module/name"),
        ('if module != selected_module:', 'if module not in references:'),
    )
    for old, new in replacements:
        assert old in raw, old
        raw = raw.replace(old, new)
    assert "references = {'bootstrap': selected" in raw
    return raw


if __name__ == '__main__':
    assert len(sys.argv) == 2
    env = {'__file__': str(R/'pg681_owner_full_collect.py'), '__name__': 'frozen_owner_full'}
    exec(compile(source(), '<two-module source qualification>', 'exec'), env)
    env['main'](sys.argv[1], 'PG630')

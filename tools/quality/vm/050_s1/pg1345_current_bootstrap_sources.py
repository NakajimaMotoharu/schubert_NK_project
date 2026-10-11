"""Current769 existing-only ADMIN normal20/closing; original1320 remains immutable."""
import ast
from pathlib import Path
from pg983_current_bootstrap_sources import files as prior
from pg1334_published_owned_stop_sources_v2 import SOURCE, W

BEFORE = 'pg1344-current-bootstrap-before-v1'
CHANGES = (
    ('Pg983', 'Pg1345'), ('PG983', 'PG1345'), ('pg983', 'pg1345'),
    ('PG932', 'PG1292'), ('pg932', 'pg1292'),
    ('40ef6e894573d2ffab1d1732124960f9c98d5f97', SOURCE),
    ('b75e8bd539edf40d1324896a16e51842d00a3983ba1eae661c86ab68d4692524',
     'ecae1310716f356d763b346528988ccdbfad0eccf0b2b27b1f3e77ed546afc99'),
    ('eeae04ea-713c-4f2d-888d-358fb4bed274', 'd2e3a86f-27a4-4c2a-be21-b512eebf1216'),
    ('2026-10-09T23:31:22.087768Z', '2026-10-10T23:30:23.481632Z'),
    ('091663ce-1cf4-47e7-8311-218ebb0c8653', '841b507c-2713-4ffe-8882-68f5fb3f87f5'),
    ('2026-10-09T23:56:48.112404Z', '2026-10-10T23:54:39.918039Z'),
    ('0bb4d6f3b9e74cdc91c553748a4cd018', '400b2e34105149ff8f3a11c21da0be6a'),
    ('202927375873', '75132489604'),
    ('cc9ed874-7f4f-450e-a188-8de1e42c8441', 'cbca8738-3b24-4090-b77c-bf029677cdd6'),
    ('pg978-bootstrap-before-v2', BEFORE),
    ('pg963-native-stop-v1', 'pg1334-native-stop-v1'),
    ('pg963_parent_receipt', 'pg1334_parent_receipt'),
    ('==594', '==634'),
)

def files(baseline_sha):
    result = {}
    for name, raw in prior(baseline_sha).items():
        for old, new in CHANGES:
            name = name.replace(old, new)
            raw = raw.replace(old, new)
        if name == 'pg1334_parent_receipt.py':
            raw = (W / 'pg1334-native-tools-v1' / name).read_text()
        if name.endswith('.py'):
            ast.parse(raw)
        result[name] = raw
    if 'pg1334_parent_receipt.py' not in result:
        raise ValueError('genuine current Root receipt required')
    return result

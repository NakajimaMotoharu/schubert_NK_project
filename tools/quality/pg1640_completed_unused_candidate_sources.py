"""Current genuine ordinary-DONE unused sibling placement source factory.

Uses the completed ownership ABI, not pending/failed/cold authority. Only new
PG1638 sibling and detached public signature may be placed; current/epoch,
approval, Unit/runtime, DB and original Backup bytes are held unchanged.
"""
import ast
import re
from pg1293_completed_unused_stage_sources import sources as previous
from pg1328_published_owned_stop_sources import CHANGES as first
from pg1579_current_owned_stop_sources import CHANGES as second
from pg1609_current_ordinary_owned_stop_sources import CHANGES as third
from pg1630_api_terminal_selected import PRODUCTION

BEFORE = '9f18ef24f4b236dddcf6c4de228e1c45ffb09c52d9229516a82829bfb6ce3b37'
CURRENT = '4d6bcbddb417b76d27e52d5d9640752c300edccf'
TOOLS = 'pg1640-completed-unused-tools-v1'


def sources(bom):
    if type(bom) is not str or re.fullmatch('[0-9a-f]{64}', bom) is None:
        raise ValueError('qualified exact candidate BOM required')
    result = {}
    for name, raw in previous().items():
        # Protect NEW identity before applying the qualified OLD-generation map.
        raw = raw.replace('769ddb15cd735c25fef581b5f9850ef9d0053c0f', PRODUCTION)
        raw = raw.replace('ecae1310716f356d763b346528988ccdbfad0eccf0b2b27b1f3e77ed546afc99', bom)
        raw = raw.replace('PG1292', 'PG1638').replace('pg1292', 'pg1638').replace('pg1295', 'pg1643')
        raw = raw.replace('/var/lib/pgpt-s1-preservation/pg1253-native-stop-v1/after.private.json', '/var/lib/pgpt-s1-preservation/pg1641-completed-current-before-v2/before.private.json')
        raw = raw.replace('7b48c21af7d30d0bdad3d0341ad3a29412fff405540ef95c0ca97328608f8f77', BEFORE)
        for a, b in first + second + third:
            if a in ['Pg1253', 'PG1253', 'pg1253', 'Pg1334', 'PG1334', 'pg1334', '1579'] or a.startswith('pg1334-native-tools'):
                continue
            raw = raw.replace(a, b)
        raw = raw.replace('702983', '204695')
        raw = raw.replace('1293', '1640').replace('pg1640-native-tools-v1', TOOLS).replace('pg1640-unused-stage-v1', 'pg1644-completed-unused-placement-v1')
        name = name.replace('1293', '1640')
        if name.endswith('.py'):
            ast.parse(raw)
        result[name] = raw
    return result

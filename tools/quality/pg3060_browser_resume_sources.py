"""New namespace and exact latest positive identity; historical rejection tuples unchanged."""
import json
from pyflakes.api import check
import pg2970_current_resume_sources as previous
from pg1446_current_cold_stage import W

SOURCE = previous.SOURCE
BOM = previous.BOM
BOOT = previous.BOOT
RUN = previous.RUN
BEFORE = '92c953ea49001ec6cca15073665e6c4ae939485c08f66a91bf3f597ddc0d7ece'
TOOLS = 'pg3060-browser-resume-tools-v1'
SAVE = 'pg3064-browser-resume-preparation-v1'
CLASS = 'Pg3060FreshResumePreparation'


def bind(raw):
    for old, new in [
        (previous.TOOLS, TOOLS), (previous.SAVE, SAVE), ('pg2970', 'pg3060'), ('Pg2970', 'Pg3060'), ('PG2970', 'PG3060'),
        (previous.BEFORE, BEFORE), ('pg2890-native-stop-v1/after.private.json', 'pg3034-native-stop-v1/after.private.json'),
        ('74729e17-91c0-43e7-b01f-74f9e6461d6a', '0ac69fb7-3cb7-4d33-b2d9-4733fba5a4cf'),
        ('d4197711cfc54770a4ac7c8d90a3a576', '65ad6798d497474685fa32d6750cea1f'),
        ('4396782047', '18100986959'), ('6027336854', '19749542200'),
        ("'job': '11471'", "'job': '35795'"), ('/proc/27414', '/proc/122976'),
        ('2026-10-14T19:39:10.330316Z', '2026-10-14T23:27:40.948070Z'),
    ]:
        raw = raw.replace(old, new)
    return raw


def sources():
    proof = json.loads((W / 'pg3040-current-runtime-retirement-post-v1/manifest.safe.json').read_bytes())
    if not (proof['actualExit'] == 0 and proof['productionSource'] == SOURCE and proof['exactRuntimeEntryRetired'] and proof['allClientAdvisoryFlock0'] and proof['proofHashes']['after.private.json']['sha256'] == BEFORE and proof['genuineCompletion']['endMonotonicUs'] == 19749542200):
        raise ValueError('actual latest retired current original/full resources proof required')
    values = {bind(n): bind(raw) for n, raw in previous.sources().items()}
    if len(values) != 20:
        raise ValueError('complete twenty-source graph required')
    for name, raw in values.items():
        if name.endswith('.py'):
            if check(raw, '<complete new Browser resume ' + name + '>'):
                raise ValueError('complete assembled globals required')
            compile(raw, '<whole latest completed resume>', 'exec')
    return values

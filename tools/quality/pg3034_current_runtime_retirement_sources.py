"""Current exact completed-runtime entry; proven held-FD scope, no business replay."""
import inspect
import pg2392_current_completed_runtime_retirement_sources as previous
from pg3006_current_resume_owned_sources import sources as stop_sources, SOURCE

TOOLS = 'pg3034-current-runtime-retirement-tools-v1'
BASE = '/var/lib/pgpt-s1-preservation/pg3006-native-stop-v1/after.private.json'
SHA = 'a234e7edb4bb2c11600efce0b59f64b0097a7255663818b0f8c6d1337c01e37b'
RUNTIME_SHA = 'abe8732db9bad858e6d1b27e541ded5f0d82bf68998c710a757464f4eee9fbbd'


def contract_source():
    raw = previous.contract_source().replace('zz-pg2316-once-resume.conf', 'zz-pg2970-once-resume.conf').replace('91f5484b-9702-4c7c-97f3-dd5110a853f9', '0dc63b79-3f9a-450c-b2a6-56f86272d272').replace('888ee8561e9c25da302470c2561cdbf65cbf10cdebf668f7196f27b485bc5035', RUNTIME_SHA)
    compile(raw, '<actual exact644byte current owned runtime entry>', 'exec')
    return raw


def sources():
    raw = inspect.getsource(previous.sources)
    for a, b in [('2392', '3034'), ('2374', '3006'), ('2380', '3012'), ('2368', '3000'), ('79c934ae247523f5914c4e8964b2b649ed44b884619210531115619d3cab04fc', 'c2ba19c1448efaadfec235ef65070c7ee1d6ff09daa7e8c80818535cb4693a74')]:
        raw = raw.replace(a, b)
    ns = {**previous.__dict__, 'SOURCE': SOURCE, 'TOOLS': TOOLS, 'BASE': BASE, 'SHA': SHA, 'stop_sources': stop_sources, 'contract_source': contract_source}
    exec(compile(raw, '<current held-FD retirement source graph>', 'exec'), ns)
    return ns['sources']()

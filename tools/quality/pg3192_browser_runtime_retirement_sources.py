"""Current completed Browser Root's exact zz3100 retirement, not prepare/start.

SS343/353/451, PT-OPS-3192-001..004. Original stopped ten-key raw is retained;
native22 remains separately pinned by the qualified stop post and native capsule.
"""
import inspect
import pg3034_current_runtime_retirement_sources as previous
import pg2050_fresh_completed_runtime_retirement_sources as generator
from pg3150_browser_business_owned_sources import sources as stop_sources, SOURCE

TOOLS = 'pg3192-browser-runtime-retirement-tools-v1'
BASE = '/var/lib/pgpt-s1-preservation/pg3150-native-stop-v1/after.private.json'
SHA = '09998d2eb6f6c88e2bb8cb9121a3298a669254277a616d0cc09c9fbe3740d8e4'


def contract_source():
    return previous.contract_source().replace('zz-pg2970-once-resume.conf', 'zz-pg3100-once-resume.conf')


def bind(raw):
    for a, b in [('3034', '3192'), ('3006', '3150'), ('3012', '3156'), ('3000', '3146'),
                 ('c2ba19c1448efaadfec235ef65070c7ee1d6ff09daa7e8c80818535cb4693a74', '23ec7de88581dc4f56875e07ec16be79647e6077be2dad1e4432b02e538a598c')]:
        raw = raw.replace(a, b)
    return raw.replace('pg3156-current-resume-owned-post-v1', 'pg3156-browser-business-owned-post-v1').replace('pg3146-current-resume-full-seal-v1', 'pg3146-browser-business-full-seal-v1')


def sources():
    # Rebind the complete generator once. Rebinding an inspect-of-inspect wrapper
    # changes a number but can leave a historical output-slot suffix behind.
    raw = inspect.getsource(generator.sources)
    for a, b in [('pg2040-fresh-normal-warning-terminal-post-v1', 'pg3156-browser-business-owned-post-v1'),
                 ('2050', '3192'), ('2030', '3150'),
                 ('pg2025-fresh-resume-full-live-seal-v1', 'pg3146-browser-business-full-seal-v1'),
                 ('8a7d42b110a047d60a3b10d948cf51731dab4b37b59d85052332acaa42942788', '23ec7de88581dc4f56875e07ec16be79647e6077be2dad1e4432b02e538a598c')]:
        raw = raw.replace(a, b)
    ns = {**generator.__dict__, 'SOURCE': SOURCE, 'TOOLS': TOOLS, 'BASE': BASE, 'SHA': SHA,
          'stop_sources': stop_sources, 'contract_source': contract_source}
    exec(compile(raw, '<same stopped current Browser retirement graph>', 'exec'), ns)
    return {n: body.replace('pg3192-browser-business-owned-stop-tools-v1', TOOLS) for n, body in ns['sources']().items()}

"""Six actual ABI phases for full11-key fresh Ref snapshot against unchanged signed a9."""
import inspect
import pg3082_retained_parent_compile as previous
from pg3100_full_native_resume_sources import sources, TOOLS, CLASS, SOURCE, BOM, BEFORE
from pg1446_current_cold_stage import W

TARGET = W / TOOLS


def main():
    raw = inspect.getsource(previous.main).replace('pg3082', 'pg3102').replace('Pg3080', 'Pg3100').replace('pg3078-recovered-browser-full-post-v1', 'pg3096-recovered-native-schema-full-post-v1')
    ns = {**previous.__dict__, 'sources': sources, 'TOOLS': TOOLS, 'CLASS': CLASS, 'SOURCE': SOURCE, 'BOM': BOM, 'BEFORE': BEFORE, 'TARGET': TARGET}
    exec(compile(raw, '<full11 snapshot exact ABI>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())

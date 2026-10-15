"""Current latest retired image and same signed a9 jars; six ABI phases before action."""
import inspect
import pg2972_current_resume_compile as previous
from pg3060_browser_resume_sources import sources, TOOLS, CLASS, SOURCE, BOM, BEFORE
from pg1446_current_cold_stage import W

TARGET = W / TOOLS


def main():
    raw = inspect.getsource(previous.main).replace('pg2972', 'pg3062').replace('Pg2970', 'Pg3060').replace('pg2968-recovered-pair-full-post-v1', 'pg3040-current-runtime-retirement-post-v1')
    ns = {**previous.__dict__, 'sources': sources, 'TOOLS': TOOLS, 'CLASS': CLASS, 'SOURCE': SOURCE, 'BOM': BOM, 'BEFORE': BEFORE, 'TARGET': TARGET}
    exec(compile(raw, '<latest actual jar six ABI>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())

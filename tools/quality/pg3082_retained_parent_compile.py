"""Fixed corrected twenty-source graph and current recovered original; six ABI phases."""
import inspect
import pg3062_browser_resume_compile as previous
from pg3080_retained_parent_resume_sources import sources, TOOLS, CLASS, SOURCE, BOM, BEFORE
from pg1446_current_cold_stage import W

TARGET = W / TOOLS


def main():
    raw = inspect.getsource(previous.main).replace('pg3062', 'pg3082').replace('Pg3060', 'Pg3080').replace('pg3040-current-runtime-retirement-post-v1', 'pg3078-recovered-browser-full-post-v1')
    ns = {**previous.__dict__, 'sources': sources, 'TOOLS': TOOLS, 'CLASS': CLASS, 'SOURCE': SOURCE, 'BOM': BOM, 'BEFORE': BEFORE, 'TARGET': TARGET}
    exec(compile(raw, '<existing-parent corrected six ABI>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())

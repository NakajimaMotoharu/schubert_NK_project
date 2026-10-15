"""Current17-source held-FD retirement ABI; no guest mutation or new build."""
import inspect
import pg3036_current_runtime_retirement_compile as previous
from pg3192_browser_runtime_retirement_sources import sources, SOURCE, SHA, TOOLS


def main():
    raw = inspect.getsource(previous.main).replace('Pg3034', 'Pg3192').replace('pg3036', 'pg3194')
    ns = {**previous.__dict__, 'sources': sources, 'SOURCE': SOURCE, 'SHA': SHA, 'TOOLS': TOOLS}
    exec(compile(raw, '<current Browser runtime normal ABI>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())

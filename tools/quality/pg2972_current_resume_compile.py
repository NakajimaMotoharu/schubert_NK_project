"""New-only 20-source ABI with corrected namespace-only current negative guards."""
import inspect
import pg2944_current_resume_compile as prior
from pg2970_current_resume_sources import sources, TOOLS, CLASS, SOURCE, BOM, BEFORE

TARGET = prior.prior.W / TOOLS


def main():
    raw = prior.source().replace('pg2944', 'pg2972').replace('Pg2942', 'Pg2970').replace('pg2940-current-resume-before-v1', 'pg2968-recovered-pair-full-post-v1')
    ns = {**prior.prior.__dict__, 'sources': sources, 'TOOLS': TOOLS, 'CLASS': CLASS, 'SOURCE': SOURCE, 'BOM': BOM, 'BEFORE': BEFORE, 'TARGET': TARGET}
    exec(compile(inspect.getsource(prior.prior.write), '<namespace-only source writer>', 'exec'), ns)
    exec(compile(raw, '<corrected current six ABI phases>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())

"""New immutable stage/one exact runtime retire only, all ten refs and M/A/DB."""
import inspect
import pg3038_current_runtime_retirement_dispatch as engine
import pg3154_browser_business_owned_dispatch as owned
from pg3192_browser_runtime_retirement_sources import sources, SOURCE, SHA, TOOLS
from pg3156_browser_business_owned_post import payload as stopped_payload

GUEST = '/var/lib/pgpt-s1-preservation/' + TOOLS
REMOTE = '/home/ubuntu/pg3196-browser-retirement-stage-v1'
ARCHIVE = 'pg3196-' + TOOLS + '.tar'
POST_SLOT = 'pg3156-browser-business-owned-post-v1'


def bind(raw):
    for a, b in [('pg3034', 'pg3192'), ('Pg3034', 'Pg3192'), ('pg3006', 'pg3150'),
                 ('pg3012', 'pg3156'), ('pg3008', 'pg3152'), ('pg3036', 'pg3194'), ('pg3038', 'pg3196'),
                 ('pg3039', 'pg3197'), ('pg3041', 'pg3199')]:
        raw = raw.replace(a, b)
    return raw


STAGE = bind(engine.STAGE.replace(engine.ARCHIVE, ARCHIVE).replace(engine.REMOTE, REMOTE).replace(engine.TOOLS, TOOLS))
PARENT_PREQUAL = bind(engine.PARENT_PREQUAL)


def namespace():
    ns = {**engine.__dict__, 'previous': owned, 'sources': sources, 'SOURCE': SOURCE, 'SHA': SHA, 'TOOLS': TOOLS,
          'GUEST': GUEST, 'REMOTE': REMOTE, 'ARCHIVE': ARCHIVE, 'POST_SLOT': POST_SLOT, 'STAGE': STAGE,
          'PARENT_PREQUAL': PARENT_PREQUAL, 'stopped_payload': stopped_payload}
    for fn in [engine.context, engine.post_payload, engine.run_source, engine.run_action, engine.main]:
        raw = bind(inspect.getsource(fn))
        # engine.run_source starts from the original owned dispatcher. Our owned
        # dispatcher is already3154; close its output/profile coordinates too.
        if fn is engine.run_source:
            raw = raw.replace("raw = previous.run_source()", "raw = previous.run_source().replace('pg3152','pg3194').replace('pg3154','pg3196').replace('pg3155','pg3197').replace('pg3157','pg3199').replace('Pg3150','Pg3192')")
        exec(compile(raw, '<closed current exact retirement dispatcher>', 'exec'), ns)
    return ns


def run_source():
    return namespace()['run_source']()


def post_payload():
    return namespace()['post_payload']()


def context():
    return namespace()['context']()


def main():
    return namespace()['main']()


if __name__ == '__main__':
    raise SystemExit(main())

"""BUG1145: bind actual TARGET namespace; first1646 issued no remote operation.

New host action slots; immutable input remote names stay fixed to compiled refs.
They must not exist at stage. No overwrite or duplicate placement is permitted.
"""
import sys
import pg1646_completed_unused_dispatch as prior
from pg1630_api_terminal_selected import PRODUCTION


def namespace(candidate):
    if type(candidate) is not dict or candidate.get('actualExit') != 0 or candidate.get('candidateSource') != PRODUCTION:
        raise ValueError('actual signed candidate required')
    return {**prior.previous.__dict__, 'SOURCE': PRODUCTION, 'DIGEST': candidate['manifestSha256'], 'BASELINE_SHA': prior.BEFORE, 'GUEST': prior.GUEST, 'REMOTE': prior.REMOTE, 'STAGE': prior.STAGE, 'sources': prior.compiler.sources, 'TARGET': prior.compiler.TARGET}


def source():
    raw = prior.source()
    if raw.count("base=W/('pg1646-'+action+'-v1')") != 1:
        raise ValueError('one new host action reservation boundary required')
    return raw.replace("base=W/('pg1646-'+action+'-v1')", "base=W/('pg1648-'+action+'-v2')").replace("W/'pg1646-stage-v1.exit'", "W/'pg1648-stage-v2.exit'")


def main():
    if sys.argv[1:] not in (['stage'], ['place']):
        raise ValueError('closed stage/place required')
    candidate = prior.json.loads((prior.previous.W / 'pg1638-candidate-build-v1.safe.json').read_bytes())
    ns = namespace(candidate)
    exec(compile(source(), '<newslot actual current placement namespace>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())

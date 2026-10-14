"""New immutable readonly observer for separately authorized fresh resume Root."""
import pg2862_network_newcurrent_observer as previous
from pg2224_newboot_current_observer import R
from pg1446_current_cold_stage import P
from pg1674_critical_management_gate import management_gate

SOURCE = previous.SOURCE
BOM = previous.BOM


def source():
    raw = previous.source().replace('pg2862', 'pg2982').replace('PG2862', 'PG2982')
    raw = raw.replace('pg2860-network-cold-publication-independent-post-v1/manifest.safe.json', 'pg2980-scoped-resume-independent-post-v1/manifest.safe.json')
    old = " assert json.loads((W/'pg2980-scoped-resume-independent-post-v1/manifest.safe.json').read_bytes())['actualExit']==0"
    new = old + "\n post=json.loads((W/'pg2980-scoped-resume-independent-post-v1/manifest.safe.json').read_bytes());assert post['normalResumePrepared']is True and post['allClientAdvisoryFlock0']is True and post['productionSource']==SOURCE"
    if raw.count(old) != 1:
        raise ValueError('one actual normal fresh-preparation admission')
    return raw.replace(old, new)


def namespace():
    ns = {'__file__': str(R / 'pg2982_current_resume_observer.py'), '__name__': 'current_fresh_resume_observer'}
    exec(compile(source(), '<new immutable current resume observer>', 'exec'), ns)
    return ns


def main():
    import sys
    ns = namespace()
    if sys.argv[1:] == ['stage']:
        with management_gate(P / 'current-management-critical.lock'):
            ns['main']()
    else:
        ns['main']()


if __name__ == '__main__':
    main()

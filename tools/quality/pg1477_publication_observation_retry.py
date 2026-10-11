"""Separate fresh readonly profile after Type-qualified broker oracle fix."""
import inspect
import pg1475_failed_publication_owner_observation as previous


def payload():
    raw=previous.payload().replace('pg1475-failed-publication-owner-v1','pg1477-failed-publication-owner-v1').replace('PG1475-failed-publication-owner-v1','PG1477-failed-publication-owner-v1')
    compile(raw,'<type-qualified current publication readonly>','exec');return raw


def main():
    entry=inspect.getsource(previous.previous.main).replace('pg1464-failed-current-capture-v1','pg1477-failed-publication-owner-v1')
    ns={**previous.previous.__dict__,'payload':payload}
    exec(compile(entry,'<new-only type-qualified transport>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())

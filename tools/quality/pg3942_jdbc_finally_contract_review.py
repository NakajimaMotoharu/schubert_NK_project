"""Annotated Throwable identities resolved semantically; first unqualified zero-fact run preserved."""
import inspect
import pg3940_jdbc_finally_contract_review as previous


def main():
    namespace = dict(previous.__dict__)
    for function in [previous.server, previous.main]:
        raw = inspect.getsource(function).replace('PG3940', 'PG3942').replace('pg3940', 'pg3942')
        exec(compile(raw, '<new-only annotated typed finally review>', 'exec'), namespace)
    return namespace['main']()


if __name__ == '__main__':
    raise SystemExit(main())

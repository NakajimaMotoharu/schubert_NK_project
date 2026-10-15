"""Host-only complete finite publication ABI and independent boundaries."""
import inspect
import pg2675_operation_publication_compile as old
import pg3450_current_outbox_publication_sources as role

TARGET = role.W / role.TOOLS


def compiler(bom):
    raw = role.bind(old.compiler(bom), bom).replace('pg2675-', 'pg3452-')
    compile(raw, '<same signed candidate whole finite publication ABI>', 'exec')
    return raw


def main():
    bom = role.candidate_bom()
    engine = old.previous.previous.prior.prior
    namespace = {**engine.__dict__, 'TARGET': TARGET, 'TOOLS': role.TOOLS,
                 'sources': role.sources, 'CANDIDATE': role.production(), 'OLD': role.CURRENT,
                 'BOM': bom, 'BEFORE': role.BEFORE}
    exec(compile(inspect.getsource(engine.write), '<new finite writer>', 'exec'), namespace)
    exec(compile(compiler(bom), '<actual whole host publication ABI>', 'exec'), namespace)
    return namespace['main']()


if __name__ == '__main__':
    raise SystemExit(main())

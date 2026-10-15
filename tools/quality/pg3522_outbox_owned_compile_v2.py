"""Host-only full ABI/Werror for actual emitted v2 graph; no guest authority."""
import inspect
import pg3492_outbox_owned_compile as previous
import pg3520_outbox_owned_sources_v2 as role


def main():
    raw = role.bind(inspect.getsource(previous.old.previous.main))
    ns = {**previous.old.previous.__dict__, 'sources': role.sources, 'context': role.context,
          'SOURCE': role.SOURCE, 'TOOLS': role.TOOLS}
    exec(compile(raw, '<complete v2 owned ABI>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':raise SystemExit(main())

"""All emitted same-source owned-stop ABI before any stop action."""
import inspect
import pg3492_outbox_owned_compile as template
import pg4042_literal_invariant_owned_sources as role


def main():
    raw = role.bind(inspect.getsource(template.old.previous.main))
    values = {**template.old.previous.__dict__, 'sources': role.sources, 'context': role.context, 'SOURCE': role.SOURCE, 'TOOLS': role.TOOLS}
    exec(compile(raw, '<new whole owned ABI>', 'exec'), values)
    return values['main']()


if __name__ == '__main__': raise SystemExit(main())

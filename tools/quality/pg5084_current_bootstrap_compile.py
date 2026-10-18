"""All five current existing20 ABI phases against actual signedPG4980; no VM."""
import pg4934_current_bootstrap_compile as previous
import pg5082_current_bootstrap_sources as role


def source():
    raw = previous.source()
    for old, new in [('pg4934-', 'pg5084-'), ('Pg4932', 'Pg5082'),
                     ('pg4916-current-owned-tools-v1', role.owned.TOOLS),
                     ('pg4918-frozen-v1.safe.json', 'pg5062-frozen-v1.safe.json'),
                     ('pg4860-release-v1', 'pg4980-release-v1')]:
        raw = raw.replace(old, new)
    return raw


def main():
    ns = {**vars(previous.previous.previous), 'role': role}
    exec(compile(source(), '<actual signed current nested Bootstrap ABI>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())

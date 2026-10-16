"""New-only v2 artifacts after original host import-closure rejection; no guest action."""
import pg4446_failed_current_unused_compile as previous


def main():
    # All namespace/bundle/ABI guards are identical; new output/log names preserve
    # every original failed artifact. The factory's sole extra stdlib is uuid.
    raw = previous.compiler().replace('pg4446-', 'pg4452-').replace('PG4446', 'PG4452')
    namespace = {**vars(previous), 'compiler': lambda: raw}
    import inspect
    exec(compile(inspect.getsource(previous.main), '<new-only v2 closed UUID host compile>', 'exec'), namespace)
    return namespace['main']()


if __name__ == '__main__':
    raise SystemExit(main())

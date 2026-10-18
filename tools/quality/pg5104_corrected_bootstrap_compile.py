"""New namespace/helper source bytes require actual current five-phase ABI, no full replay."""
import pg5084_current_bootstrap_compile as previous
import pg5102_corrected_bootstrap_sources as role


def source():
    return previous.source().replace('pg5084-', 'pg5104-').replace('Pg5082', 'Pg5102')


def main():
    ns = {**vars(previous.previous.previous.previous), 'role': role}
    exec(compile(source(), '<corrected new-only current ABI>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())

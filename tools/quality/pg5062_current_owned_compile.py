"""Actual signed currenta2ecc ABI of the complete normal owned-stop graph."""
import inspect
import pg4918_current_owned_compile as previous
import pg5060_current_owned_sources as role


def main():
    template = previous.previous.previous
    ns = {**vars(template), 'role': role}
    exec(compile(inspect.getsource(template.main), '<currenta2ecc all owned ABI>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())

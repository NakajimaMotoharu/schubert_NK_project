"""Actual signed current04bb ABI of the entire normal owned-stop graph."""
import inspect
import pg4774_new_current_owned_compile as previous
import pg4916_current_owned_sources as role


def main():
    ns={**vars(previous.previous),'role':role}
    exec(compile(inspect.getsource(previous.previous.main),'<current04bb all owned ABI>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())

"""Compile whole normal owned graph against this signed current's actual JAR ABI."""
import inspect
import pg4044_literal_invariant_owned_compile as previous
import pg4772_new_current_owned_sources as role


def main():
    ns={**vars(previous),'role':role}
    exec(compile(inspect.getsource(previous.main),'<new normal owned current ABI>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())

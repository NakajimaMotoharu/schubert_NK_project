"""New-only current ABI and independent complete finite publication oracle compile."""
import inspect
import pg2844_network_cold_ro_compile as prior
import pg1442_current_cold_compile as compiler
import pg2852_network_cold_publication_sources as s

FROZEN='pg2854-network-cold-publication-frozen-v1.safe.json'


def main():
    s.qualify();raw=inspect.getsource(prior.main)
    # Expand the compiler transformation without dispatching prior RO compiler.
    # Its local `s` is this fixed new publication family and same current source.
    ns={**prior.__dict__,'s':s,'FROZEN':FROZEN,'prior':compiler}
    # Compiler role paths are explicit, not guessed historical replacements.
    raw=raw.replace('pg2842_network_cold_ro_sources_test.py','pg2852_network_cold_publication_test.py')
    raw=raw.replace('PG2844-network-cold-ro-compile-v1','PG2854-network-cold-publication-compile-v1')
    exec(compile(raw,'<fixed publication ABI compiler>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())

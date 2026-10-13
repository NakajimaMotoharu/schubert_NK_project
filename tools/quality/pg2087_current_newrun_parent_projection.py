"""Public current parent18 from the actual2085 qualified immutable fullseal."""
import inspect
import pg2083_current_newrun_sealed_parent_fields as previous

SLOT='pg2087-current-newrun-parent-projection-v1'


def payload(sha):return previous.payload(sha).replace('pg2081-current-newrun-full-live-seal-v1','pg2085-native-augmented-newrun-full-seal-v1')


def entry():
    raw=inspect.getsource(previous.main).replace('pg2081-current-newrun-full-live-seal-v1','pg2085-native-augmented-newrun-full-seal-v1')
    ns={**previous.__dict__,'payload':payload,'SLOT':SLOT}
    exec(compile(raw,'<actual qualified newrun projection>','exec'),ns);return ns['main']


if __name__=='__main__':raise SystemExit(entry()())

"""Readonly diagnostic joins the actual complete 32-field capture, no empty inference."""
import inspect
import pg1945_reload_configuration_delta as prior

SLOT='pg1947-reload-configuration-delta-v1'


def payload():
    raw=prior.PAYLOAD
    old=" rows=dict(x.split('=',1)for x in p.stdout.decode().splitlines());assert set(rows)==set(keys);return rows"
    new=""" if 'ExecStop'in keys:
  rows=capture.complete_configuration(p.stdout.decode(),unit)
 else:rows=dict(x.split('=',1)for x in p.stdout.decode().splitlines())
 assert set(rows)==set(keys);return rows"""
    if raw.count(old)!=1:raise ValueError('actual one read boundary required')
    prefix="import sys\nsys.path.insert(0,'/var/lib/pgpt-s1-preservation/pg1925-partial-reload-tools-v1')\nimport pg1925_configuration_capture as capture\n"
    return prefix+raw.replace(old,new)


def main():
    ns={**prior.__dict__,'SLOT':SLOT,'PAYLOAD':payload()}
    exec(compile(inspect.getsource(prior.main),'<actual complete readonly diagnostic>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())

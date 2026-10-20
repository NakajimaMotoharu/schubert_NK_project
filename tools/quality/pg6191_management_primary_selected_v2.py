"""New-only60 after fixture comment correction; original format-rejected6190 preserved."""
import inspect
import subprocess
import pg6190_management_primary_selected as profile

OLD='4734a9bbaceb1b12b2547a3752b87c7ea8508932'


def main():
    changed=set(subprocess.check_output(['git','diff','--name-only',OLD,'HEAD','--','src'],cwd=profile.ROOT,text=True).splitlines())
    if changed!={profile.TEST}:raise ValueError('only fixture comment changed since rejected format source')
    raw=inspect.getsource(profile.main)
    before="'pg6190-management-primary-selected-v1'"
    if raw.count(before)!=1:raise ValueError('one new-only namespace')
    scope=dict(vars(profile))
    exec(compile(raw.replace(before,"'pg6191-management-primary-selected-v2'",1),'<new-only60 v2>','exec'),scope)
    return scope['main']()


if __name__=='__main__':raise SystemExit(main())

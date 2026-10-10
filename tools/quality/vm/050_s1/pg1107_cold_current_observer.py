"""Fresh observer for bootcbca/current1068, read-only no budget renewal."""
import ast
from pathlib import Path
from pg956_current_observer import source as previous


def source():
    raw=previous()
    for old,new in [('pg956','pg1107'),('PG956','PG1107'),('PG932','PG1068'),
        ('pg954-ordinary-before-v1','pg1106-ordinary-cold-before-v1'),
        ('40ef6e894573d2ffab1d1732124960f9c98d5f97','d5b00104280028d9ea81b44c1d1c805f3c2861ed'),
        ('b75e8bd539edf40d1324896a16e51842d00a3983ba1eae661c86ab68d4692524','0b617d455553f89cb15043ea9555c4d81ddf3e1dc27176af62e5f50ba8931b0d'),
        ('cc9ed874-7f4f-450e-a188-8de1e42c8441','cbca8738-3b24-4090-b77c-bf029677cdd6')]:
        if old not in raw:raise ValueError('fixed cold current observer profile refused')
        raw=raw.replace(old,new)
    marker="def watch():return(R/'pg522_watch_parent.py').read_text().replace('PG495','PG1068')"
    if raw.count(marker)!=1:raise ValueError('fixed watch boot binding refused')
    raw=raw.replace(marker,marker+".replace('cc9ed874-7f4f-450e-a188-8de1e42c8441','cbca8738-3b24-4090-b77c-bf029677cdd6')")
    raw=raw.replace("pg1106-ordinary-cold-before-v1.safe.json", "pg1106-ordinary-cold-before-v1/manifest.safe.json")
    ast.parse(raw);return raw


if __name__=='__main__':exec(compile(source(),'<PG1107 cold current observer>','exec'),{'__file__':__file__,'__name__':'__main__'})

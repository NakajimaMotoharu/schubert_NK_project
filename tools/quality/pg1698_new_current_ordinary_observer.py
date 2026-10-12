"""New Source/current immutable ordinary observer, no start or stop authority."""
from pg1597_current_ordinary_observer import source as previous,R


def source():
    raw=previous()
    for a,b in [('pg1597','pg1698'),('PG1597','PG1698'),('pg1596-current-ordinary-before-v1/manifest.safe.json','pg1697-new-current-ordinary-before-v1/manifest.safe.json'),('4d6bcbddb417b76d27e52d5d9640752c300edccf','2741c4546afad6c1e8b6efbd53dfb58144edf7bb'),('e36d39f470bedf445e182f03e926c4c22252ef37952fde5b9a12614e60b0f07c','195e0668bc5a1fea2cbf2a93747e0cdcbf1bcb66c3f3f23a362fca7c89ae82e1'),('PG1544','PG1638')]:
        if a not in raw:raise ValueError('one new current observer binding required')
        raw=raw.replace(a,b)
    compile(raw,'<new current ordinary readonly observer>','exec')
    return raw


def namespace():
    ns={'__file__':str(R/'pg1698_new_current_ordinary_observer.py'),'__name__':'new_current_ordinary_observer'}
    exec(compile(source(),'<new current observer scope>','exec'),ns)
    return ns


if __name__=='__main__':namespace()['main']()

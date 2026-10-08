"""SSC231 fresh whole20 completed/terminal baseline, readonly no operation authority."""
from pathlib import Path

R=Path(__file__).resolve().parent


def source():
    raw=(R/'pg646_completed_baseline.py').read_text()
    for old,new in (
        ('pg646','pg661'),('pg642-native-stop-v1','pg655-native-stop-v1'),
        ('011d96090bac12c58f0a9531455e72bb79a23a413d5b16fa886c9df8dac4bf3c','c13792efb16007ad6fbdcec310dc9c8a598d9a5bad1b4680bef93384ab092285'),
        ('293d218b06454bd1a8ff350bb93de2d5','095f6d1d7f8442b7b2b44ae59a4314f5'),
        ('pg611-native-stop-v1','pg655-native-stop-v1'),
        ('==504','==514'),("'batchRows':504","'batchRows':514"),
        ("require({p.name for p in runtime.iterdir()}=={'pg635-once-resume.conf'})", "require(not list(runtime.iterdir()))"),
        ("v['runtime']=file(runtime/'pg635-once-resume.conf')", "v['runtime']=None"),
        ('len(set(paths))==19','len(set(paths))==18'),
        ("require(v['unitFiles'][str(runtime/'pg635-once-resume.conf')]==v['runtime']);", "require(v['runtime']is None);"),
        ("require(len(v)==19);return v", "paths={**{n:pathlib.Path('/run/schubert-nk')/n for n in ('backup-request','cleanup-request','expiry-request')},'runtime-parent':runtime}\n  v['namespace']={n:{'metadata':metadata(p),'entries':sorted(c.name for c in p.iterdir()),'xattrs':os.listxattr(p)}for n,p in paths.items()}\n  for n,a in v['namespace'].items():require(a['metadata'][2:6]==[0,0,stat.S_IFDIR|(0o755 if n=='runtime-parent'else 0o700),2]and not a['entries']and not a['xattrs'])\n  require(len(v)==20);return v"),
        ("'full19Fields':True", "'full20Fields':True"),("'runtimeFiles':1", "'runtimeFiles':0"),
        ("(W/'pg643-terminal-final-v2.exit')", "(W/'pg656-terminal-final-v1.exit')"),
    ):
        assert old in raw,old;raw=raw.replace(old,new)
    return raw


if __name__=='__main__':
    exec(compile(source(),str(R/'pg661_current_baseline.py'),'exec'),{'__file__':str(R/'pg661_current_baseline.py'),'__name__':'__main__'})

"""BUG1387: new-only nested graph compiler; preserve failed4822 partial v1."""
import inspect
import pg4822_new_current_bootstrap_compile as previous


def source():
    raw=inspect.getsource(previous.main).replace('pg4822-','pg4824-')
    marker="        if name.endswith('.class'):\n"
    if raw.count(marker)!=1:raise ValueError('one class-copy boundary')
    raw=raw.replace(marker,marker+"            if name.startswith('/')or any(p in ('','.','..')for p in name.split('/'))or '\\\\'in name:raise ValueError('canonical class path required')\n            (target/name).parent.mkdir(parents=True,exist_ok=True,mode=0o700)\n")
    raw=raw.replace("hashes={f.name:hashlib.sha256(f.read_bytes()).hexdigest()for f in target.iterdir()}","hashes={f.relative_to(target).as_posix():hashlib.sha256(f.read_bytes()).hexdigest()for f in target.rglob('*')if f.is_file()}")
    raw=raw.replace('for p in target.iterdir():p.chmod(0o400)',"for p in target.rglob('*'):\n        p.chmod(0o700 if p.is_dir()else 0o400)")
    compile(raw,'<nested current Bootstrap compiler>','exec');return raw


def main():
    values=dict(vars(previous));exec(compile(source(),'<new-only Bootstrap compiler>','exec'),values)
    return values['main']()


if __name__=='__main__':raise SystemExit(main())

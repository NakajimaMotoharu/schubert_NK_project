"""New-only current ABI compile; independent parent/five-role real FD oracle."""
import ast
from pg1145_terminal_cleanup_compile import source as previous


def source():
    text=previous()
    text=text.replace('from pg1144_terminal_cleanup_recovery_sources import files','from pg1148_native_five_sources import files')
    text=text.replace('pg1144-terminal-tools-v1','pg1148-native-five-tools-v1').replace('pg1145-terminal-frozen-v1','pg1149-native-five-frozen-v1').replace('PG1145-terminal-compile-v1','PG1149-native-five-compile-v1')
    text=text.replace("'pg1144*test.py'","'pg1148*test.py'")
    text=text.replace('def write(path, data):\n', 'def write(path, data):\n    path.parent.mkdir(mode=0o700,parents=True,exist_ok=True)\n')
    # Reuse pinned helpers by byte, while compiling current fixtures and every new class.
    marker="    for name, text in files().items():"
    text=text.replace(marker,"    prior=json.loads((W/'pg1145-terminal-frozen-v1.safe.json').read_bytes())\n    if prior['actualExit']!=0:raise ValueError('qualified helper closure refused')\n    for name,digest in prior['fileHashes'].items():\n        if name.endswith('.class'):\n            p=W/'pg1144-terminal-tools-v1'/name\n            if sha(p)!=digest:raise ValueError('immutable helper refused')\n            if not (OUT/name).exists():write(OUT/name,p.read_bytes())\n"+marker)
    start=text.index("                ('single-intent-oracle'");end=text.index('    phases = []',start)
    text=text[:start]+"                ('native-five-directory-oracle',[str(J/'java'),'--enable-native-access=ALL-UNNAMED','-cp',cp,'dev.codex.schubert.nk.batch.file.Pg1148NativeRoleDirectoryTest'])]\n"+text[end:]
    ast.parse(text);return text


if __name__=='__main__':exec(compile(source(),'<new-only current native five compiler>','exec'),{'__file__':__file__,'__name__':'__main__'})

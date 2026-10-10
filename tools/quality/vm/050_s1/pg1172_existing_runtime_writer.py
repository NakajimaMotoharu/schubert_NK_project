"""SSC260 canonical zz file in existing admitted empty Unit.d, held ancestors."""
import ast
import inspect
import pg1160_runtime_writer as previous


def source():
    s=inspect.getsource(previous).replace("NAME='pg1160-once-resume.conf'","NAME='zz-pg1160-once-resume.conf'")
    s=s.replace("['run','systemd','system']","['run','systemd','system',UNIT]")
    # Reuse actual byte writer/force/readback/normal-close block; no mkdir/mode repair.
    start=s.index('        os.mkdir(UNIT,0o700,dir_fd=root)')
    end=s.index('        os.fsync(root)',start)
    block=s[start:end]
    a=block.index('            fd=os.open(NAME,');b=block.index('            child_after=metadata(child);',a)
    body=block[a:b].replace('dir_fd=child','dir_fd=root').replace('os.fsync(child)','os.fsync(root)').replace('os.listdir(child)','os.listdir(root)')
    body='\n'.join(line[4:]if line.startswith('    ')else line for line in body.splitlines())+'\n'
    s=s[:start]+body+s[end:]
    s=s.replace('now[5]==expected[5]+1','now[5]==expected[5]').replace('os.listdir(root)==[UNIT]','os.listdir(root)==[NAME]')
    ast.parse(s);return s


def module():
    import types
    m=types.ModuleType('pg1172_existing_runtime_writer_generated');exec(compile(source(),'<existing canonical runtime writer>','exec'),m.__dict__);return m

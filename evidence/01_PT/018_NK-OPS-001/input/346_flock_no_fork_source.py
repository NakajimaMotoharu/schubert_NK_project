"""Explicit Test-only util-linux no-fork source detail; never execute a process fixture."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';m=json.loads((B/'evidence/PG23132-flock-five-original-v1/manifest.json').read_bytes());rows={v['path']:(R/v['path']).read_text() for v in m['inputs']};assert all(hashlib.sha256(rows[v['path']].encode()).hexdigest()==v['sha256'] for v in m['inputs']);new={};total=0
for n,s in rows.items():
 assert '--no-fork' not in s and '--close' not in s;expected=1 if n.endswith('/LinuxStartupFileLockTest.java') else 2;assert s.count('"/usr/bin/flock",')==expected
 new[n]=s.replace('"/usr/bin/flock",','"/usr/bin/flock",\n"--no-fork", // BUG2468: keep the command in this PID.\n')
 total+=expected
assert total==5
for n,s in new.items():(R/n).write_text(s)
print('five explicitly documented Test argv flag additions; original Test/process/native actions0')

"""Independent allowed partial phase: newcurrent/newUnit, old loaded config, no reload."""
from pg1896_complete_publication_post import payload as completed
from pg1877_warning_publication_sources import once


def payload():
    raw=completed()
    begin=raw.index("require(publication_private('complete.private')")
    end=raw.index('\nold_after=after',begin)
    raw=raw[:begin]+"require(not(publication/'complete.private').exists()and not(publication/'after.private.json').exists()and not(publication/'daemon-reload-reserved.private').exists())"+raw[end:]
    raw=once(raw,"published_raw=publication_private('after.private.json');after=json.loads(published_raw)","after=dict(old_after);after['startup']=tree(pathlib.Path('/run/schubert-nk/startup'));after['unitFilesActual']=dict(old_after['unitFilesActual']);unit_file=pathlib.Path('/etc/systemd/system/schubert-nk-morning-controller.service');after['unitFilesActual'][str(unit_file)]=metadata(unit_file)+[hashlib.sha256(unit_file.read_bytes()).hexdigest()]")
    raw=once(raw,"set(oracle['PHASES'])","set(oracle['PHASES'][:-1])")
    raw=once(raw,"phases[-1][1]=='release'","phases[-1][1]=='old-linked-private'")
    raw=once(raw,"upper=phases[-1][0]","upper=__import__('time').time_ns()")
    raw=once(raw,"require(publication_private('daemon-reload-reserved.private')==b'one normal daemon-reload; no retry\\n')","require(not(publication/'daemon-reload-reserved.private').exists())")
    raw=once(raw,"[b'SuccessExitStatus=10',b'Type=oneshot']","[b'SuccessExitStatus=',b'Type=oneshot']")
    raw=once(raw,"require(publication_private('refs-prepare.private.log')==b'')","require(publication_private('refs-prepare.private.log')==b'PG1891_READBACK_UNKNOWN type=ValueError\\nPG1891_FRAME method=<module> line=227\\nPG1891_FRAME method=main line=209\\n')")
    begin=raw.index("gap=publication_private('observations.private')")
    end=raw.index('\nbus = dbus.SystemBus(private=True)',begin)
    raw=raw[:begin]+"require(not(publication/'observations.private').exists())\n"+raw[end:]
    # Return a complete observed current snapshot from the independent phase
    # oracle; never normalize partial publication to completed or old current.
    return raw

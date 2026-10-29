"""Fresh six Main artifact SpotBugs; complete physical classes, no Product run."""
import snapshot_program_qualified_v2 as cfg
import f03_spotbugs_fresh as analysis

if __name__ == '__main__':
    analysis.out = cfg.out
    _,normal_pin = cfg.normal()
    preflight = cfg.data.BASE/'PG13834-snapshot-program-test-static-v1/manifest.json'
    analysis.stage(cfg,cfg.SOURCE,normal_pin,(preflight.parent.name,cfg.data.sha(preflight.read_bytes())))

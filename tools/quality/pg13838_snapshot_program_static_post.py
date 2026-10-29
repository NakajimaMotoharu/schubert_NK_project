"""Independent original six static reports; no reanalysis or target invocation."""
import snapshot_program_qualified_v2 as cfg
import f03_spotbugs_fresh as analysis

if __name__ == '__main__':
    analysis.out = cfg.out
    _,normal_pin = cfg.normal()
    result = cfg.out(cfg,cfg.STATIC_NUMBER)/'manifest.json'
    analysis.independent(cfg,cfg.SOURCE,normal_pin,cfg.data.sha(result.read_bytes()),13838)

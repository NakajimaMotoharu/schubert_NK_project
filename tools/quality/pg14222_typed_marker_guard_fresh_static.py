"""New candidate six Main artifacts, static only; no replay of prior Source analysis."""
import typed_marker_guard_qualified_v1 as cfg
import f03_spotbugs_fresh as analysis

if __name__=='__main__':
    analysis.out=cfg.out
    _,pin=cfg.normal()
    analysis.stage(cfg,cfg.SOURCE,pin,('PG14218-typed-marker-guard-source-post-v1','ce3dbfd768a78ef45481db15ecf7c599b00bcb90a5b0b84eac568a54d1dc1909'))

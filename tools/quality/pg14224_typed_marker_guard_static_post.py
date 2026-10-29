"""Independently read current-source six static reports; do not rerun analysis."""
import typed_marker_guard_qualified_v1 as cfg
import f03_spotbugs_fresh as analysis

if __name__=='__main__':
    analysis.out=cfg.out
    analysis.independent(cfg,cfg.SOURCE,cfg.NORMAL_PIN,'c333f1004d5616488748491a3ec5ba946d44112a53915fd403d9d2da3d915551',14224)

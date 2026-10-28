"""Independent same-source six reports and complete physical-class census."""
import pg13571_lgs_boundary_config_v5 as cfg
from f03_spotbugs_fresh import independent

if __name__ == '__main__':
    independent(cfg, 'e8e06bedba3311c8335dbb5ba9c4fdffafd86acf',
                '849422e3b3794d6c1d580ffc016c36e1bc83b8864eefd33ab1eae10b3793db7a',
                '0c759607d9eae657600709834edf6a0b391def3a1fff413ca1d3eeeabb132066', 13575)

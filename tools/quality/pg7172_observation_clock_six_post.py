"""Current91/current23 physical Batch and historical Web10, never a combined current114 run."""
import pg7158_filesystem_health_six_post as post
import pg7170_observation_clock_six_compile as compilation


if __name__=='__main__':
    post.compilation=compilation
    post.SLOT=post.host.W/'pg7172-observation-clock-six-post-v1'
    post.OUT=post.host.BASE/'PG7172-observation-clock-six-post-v1'
    post.PINS['currentBatch']=('PG7168-observation-clock-post-v1/manifest.json',
                              '580abe8ff4eea75f6f2fda9fbd45c787f16b468a2536f16590705734f23bdcc5')
    post.CURRENT_TESTS=91;post.CURRENT_SUITES=13;post.CURRENT_PHYSICAL=23
    post.PHYSICAL_COUNT=1702;post.SOURCE_DELTA_COUNT=39
    post.main()

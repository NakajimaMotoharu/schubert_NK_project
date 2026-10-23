"""Corrected count-independent current domain label and actual executable inventory check."""
import pg7124_micrometer_current_trace as trace


if __name__=='__main__':
    trace.SOURCE='19c777bf3dbe3ddd0286d4c356a00ca8a47c99c5'
    trace.OUT=trace.host.BASE/'PG7150-current-terminal-trace-v2'
    trace.SOURCE_COUNT=34
    trace.ADDED_PHYSICAL_COUNT=30
    trace.CURRENT_TESTS=23
    trace.CURRENT_EXECUTABLE=9
    trace.WEB_RESULTS=(1579,1580)
    trace.PINS['physical']=('PG7142-http-terminal-six-post-v1/manifest.json',
                           'e29b54744f769b519aec562f6e1bccbcf3535ab448439dd365efcaf07a900ff7')
    trace.PINS['currentWeb']=('PG7140-http-terminal-post-v2/manifest.json',
                            '1e66707fc37eef6842dda56ff945635b64f0d8ce0cab6a197b0b4ac0ed4a8653')
    trace.main()

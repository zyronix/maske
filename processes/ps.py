from utils import Command
import logging
from __builtin__ import True

log = logging.getLogger('thelogger')

#__name__

def run():
    def _detect():
        # Detects if the module is available
        output = Command('ps')
        if (output.returncode == 127):
            log.debug("backend:ps: ps not found")
            return False
        log.debug("backend:ps: ps detected")
        return True
    
    def _getProccesses():
        command_obj = Command('ps -ef | awk -F \' \' \'{print $8}\' | grep -e \'bin\' | uniq')
        proccesses = command_obj.output.split('\n')[:-1]
        log.info('backend:ps: detected: %r' % proccesses)
        return proccesses
    
    if _detect():
        log.info("proccesses:ps: Starting ps detection")
        return _getProccesses()
    else:
        return False

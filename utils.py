import logging.handlers
import logging as log2

log = log2.getLogger('thelogger')



class Command():
    """Run a command and capture it's output string, error string and exit status"""
    def __init__(self, command):
        self.command = command
        self.returncode = None
        self.run()
        
    def run(self, shell=True):
        import subprocess as sp
        log.debug("utils:Command: running command %s" % (self.command))
        process = sp.Popen(self.command, shell = shell, stdout = sp.PIPE, stderr = sp.PIPE)
        self.pid = process.pid
        self.output, self.error = process.communicate()
        self.returncode = process.returncode
        log.debug("utils:Command: error code %s output is %r" % (self.returncode ,self.output))
        return self


def initLogging():
    
    logfile = 'main.log'
    loglevel = logging.DEBUG
    loglevel_console = logging.INFO
    logsize = 1000000
    lognum = 1
    
    
    # initialize logging
    # A log directory has to be created below the start directory
    log = logging.getLogger("thelogger")
    log.setLevel(loglevel)

    log_script = logging.handlers.RotatingFileHandler(logfile, 'a', logsize, lognum)
    log_script_formatter=logging.Formatter('%(asctime)s %(levelname)s  %(message)s')
    log_script.setFormatter(log_script_formatter)
    log_script.setLevel(loglevel)
    log.addHandler(log_script)
    
    #CONSOLE log handler

    console = logging.StreamHandler()
    console.setLevel(loglevel_console)
    # set a format which is simpler for console use
    formatter = logging.Formatter('%(asctime)s %(levelname)s  %(message)s')
    console.setFormatter(formatter)
    log.addHandler(console)
 
    return log
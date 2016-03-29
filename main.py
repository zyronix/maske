import backend
import processes
import convert
from output import puppet

from utils import initLogging

from os.path import basename

log = initLogging()

log.info("main: Starting run")
processes_dic = {}

log.info("main: Starting process detect")
for plugin in processes.plugins:
    log.debug("main: running %s process plugin" %plugin.__name__)
    processes_dic[plugin.__name__] = plugin.run()
log.info("main: Done with process detect")

backend_dic = {}

log.info("main: Starting package backend run")
for plugin in backend.plugins:
    log.debug("main: running %s package backend plugin" % plugin.__name__)
    for key in processes_dic.keys():
        backend_dic[plugin.__name__] = plugin.run(processes_dic[key])

log.info("main: Done with package backend run")

converted = []

log.info("main: Starting convert run")
for backends in backend_dic.keys():
    if type(backend_dic[backends]) == dict:
        for process in backend_dic[backends].keys():
            if basename(process) in convert.plugins_dic.keys():
                converted.append(convert.plugins_dic[basename(process)].run(backend_dic[backends][process]['config']))
log.info("main: Done with convert run")

log.info("main: Writing output to file")
f = open('test.pp', 'w')    
for config in converted:
    for i in puppet.run(config):
        f.write(i)
        f.write('\n')

f.close()
log.info("main: Done")
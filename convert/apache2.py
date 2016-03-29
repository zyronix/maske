from utils import Command
import logging
import augeas

log = logging.getLogger('thelogger')

def run(configs):
    puppet_conf = {}
    vhost = {}
    log.info("convert:apache2: Starting apache convert")
    print "%r" %configs
    
    # Get the module path
    from os import listdir
    
    
    # Modules
    # Vhosts
    # Ports
    for config in configs:
        if 'apache2.conf' in config:
        # Let get the module dir:
            aug_obj = augeas.augeas()
            for match in aug_obj.match('/files/%s/directive[*]' % configs[0]):
                value = aug_obj.get(match)
                if 'IncludeOptional' == value.split('/')[-1]:
                    value2 = aug_obj.get(match + '/arg')
                    if 'mods' in value2:
                        print value2
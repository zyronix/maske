from utils import Command
import logging
import augeas

log = logging.getLogger('thelogger')

def run(configs):
    puppet_conf = {}
    keepalived_virtualservers = {}
    keepalived_realservers = {}
    keepalived_global_defs = {}
    keepalived_vrrp_instance = {}
    
    log.info("convert:keepalived: Starting keepalived convert")
    for config in configs:
        if ('init' or 'rc') in config:
            log.debug("convert:keepalived: Getting the config file from the init script")
            command_obj = Command('grep -E \'^CONFIG=\' %s' % config)
            config_keep = command_obj.output.split('=')[-1].split('\n')[0]
    
    aug_obj = augeas.augeas()
    
    if config_keep:
        # Start with global configs
        for match in aug_obj.match('/files%s/global_defs/*' % config_keep):
            log.debug("convert:keepalived: match in global defs %s" %match)
            keepalived_global_defs[str(match.split('/')[-1])] = str(aug_obj.get(match))
        
        # Virtual servers:
        for match in aug_obj.match('/files%s/virtual_server[*]' % config_keep):
            log.debug("convert:keepalived: match in virtual server %s" %match)
            # Get all the virtual server
            ip_virt = str(aug_obj.get(match + '/ip'))
            port_virt = str(aug_obj.get(match + '/port'))
            idd_virt = "%s_%s" % (ip_virt, port_virt)
            keepalived_virtualservers[idd_virt] = {}
            keepalived_virtualservers[idd_virt]['ip_address'] = ip_virt
            keepalived_virtualservers[idd_virt]['port'] = port_virt
            for match2 in aug_obj.match('%s/*' % match):
                log.debug("convert:keepalived: looping through elements of virtual server")
                if 'real_server' in str(match2.split('/')[-1]):
                    ip = str(aug_obj.get(match2 + '/ip'))
                    port = str(aug_obj.get(match2 + '/port'))
                    idd = "%s_%s" % (ip, port)
                    keepalived_realservers[idd] = {}
                    keepalived_realservers[idd]['ip_address'] = ip
                    keepalived_realservers[idd]['port'] = port
                    keepalived_realservers[idd]['virtual_server'] = idd_virt
                    #keepalived_realservers['%s %s' % (ip, port)]['port'] = port
                    keepalived_realservers[idd]['options'] = {}
                    for match3 in aug_obj.match('%s/*' % match2):
                        if (match3.split('/')[-1] != u'ip') and (match3.split('/')[-1] != u'port'):
                            keepalived_realservers[idd]['options'][str(match3.split('/')[-1])] = {}
                            for match4 in aug_obj.match('%s/*' % match3):
                                keepalived_realservers[idd]['options'][str(match3.split('/')[-1])][str(match4.split('/')[-1])] = str(aug_obj.get(match4))
                elif (match2.split('/')[-1] != u'ip') and (match2.split('/')[-1] != u'port'):
                    keepalived_virtualservers[idd_virt][str(match2.split('/')[-1])] = str(aug_obj.get(match2))
        # VRRP Instances
        
        for match in aug_obj.match('/files%s/vrrp_instance[*]' % config_keep):
            log.debug("convert:keepalived: found vrrp_instance %s" %match)
            instance = str(aug_obj.get(match))
            keepalived_vrrp_instance[instance] = {}
            keepalived_vrrp_instance[instance]['interface'] = str(aug_obj.get(match + '/interface'))
            keepalived_vrrp_instance[instance]['priority'] = str(aug_obj.get(match + '/priority'))
            keepalived_vrrp_instance[instance]['state'] =  str(aug_obj.get(match + '/state'))
            keepalived_vrrp_instance[instance]['virtual_router_id'] =  str(aug_obj.get(match + '/virtual_router_id'))
            
            keepalived_vrrp_instance[instance]['virtual_ipaddress'] = []
            # Virtual addresses
            for match2 in aug_obj.match(match + '/virtual_ipaddress/*'):
                log.debug("convert:keepalived: found virtual ip %s" % match2)
                keepalived_vrrp_instance[instance]['virtual_ipaddress'].append(str(aug_obj.get(match2)))
            
            # Now the optional parameters:
            lvs_sync_daemon_interface = str(aug_obj.get(match + '/lvs_sync_daemon_interface'))
            if lvs_sync_daemon_interface:
                keepalived_vrrp_instance[instance]['lvs_interface'] = lvs_sync_daemon_interface
            
            if aug_obj.match(match + '/authentication/*'):
                auth_type = str(aug_obj.get(match + '/authentication/auth_type'))
                auth_pass = str(aug_obj.get(match + '/authentication/auth_pass'))
                if auth_type:
                    keepalived_vrrp_instance[instance]['auth_type'] = auth_type
                if auth_pass:
                    keepalived_vrrp_instance[instance]['auth_pass'] = auth_pass
    
    puppet_conf['class'] = {}
    puppet_conf['keepalived::vrrp::instance'] = keepalived_vrrp_instance
    puppet_conf['class']['keepalived::global_defs'] = keepalived_global_defs
    puppet_conf['class']['keepalived'] = {}
    puppet_conf['keepalived::lvs::virtual_server'] = keepalived_virtualservers
    puppet_conf['keepalived::lvs::real_server'] = keepalived_realservers
    
    log.debug("convert:keepalived: puppet_config %r" %puppet_conf)
    
    log.info("convert:keepalived: Done keepalived convert")
    
    return puppet_conf

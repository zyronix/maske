import logging

log = logging.getLogger('thelogger')

def _nested(in_dict, tab, level = 0):
    line = []
    for variable in in_dict.keys():
        if type(in_dict[variable]) == str:
            if level == 0:
                line.append('%s%s => \'%s\',' % (tab, variable, in_dict[variable]))
            else:
                line.append('%s\'%s\' => \'%s\',' % (tab, variable, in_dict[variable]))
        elif type(in_dict[variable]) == dict:
            if level == 0:
                line.append('%s%s => {' % (tab, variable))
            else:
                line.append('%s\'%s\' => {' % (tab, variable))
            line.extend(_nested(in_dict[variable], tab + tab, level + 1))
            line.append('%s}' % tab)
        elif type(in_dict[variable]) == list:
            line.append('%s%s => %r,' % (tab, variable, in_dict[variable]))
    return line

def run(in_dict):
    # First create the objects
    log.info('output:puppet: Starting conversion')
    tab = '    '
    line = []
    for resource in in_dict.keys():
        for element in in_dict[resource].keys():
            line.append('%s { \'%s\': ' %(resource, element))
            #for variable in in_dict[resource][element].keys():
            line.extend(_nested(in_dict[resource][element], tab))
            line.append('}')
    log.info('output:puppet: Done conversion')
    return line

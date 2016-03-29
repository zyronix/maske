# maske
## Maske - Linux State Generator
Maske is a tool which helps system engineers implementing configuration management. A similar tool is Blueprint, but Blueprint does not use any reusable Puppet module. Maske tries to do this.

This is not a full tool yet, it was create for the course Large Infrastructure Administration for the Master System and Network Engineering at the University of Amsterdam.

Written by: Marat Nigmatullin & Romke van Dijk

## Introduction
Maske consists of 4 steps:
1. Detect phase, where it tries to detect which services are being offered by a server
2. Takes those services and determine which resource are related to those services
3. Analyses those services and prepares them
4. Output

We created a PoC for this model by implementing all 4 phases for the keepalived application.

## Installation
This is tested for ubuntu 14.04
    apt-get install python-augeas

## Usages
    python2 main.py

## Example
    2016-03-29 23:09:05,455 INFO  main: Starting run
    2016-03-29 23:09:05,456 INFO  main: Starting process detect
    2016-03-29 23:09:05,473 INFO  proccesses:ps: Starting ps detection
    2016-03-29 23:09:05,495 INFO  backend:ps: detected: ['/sbin/init', '/usr/sbin/sshd', '/sbin/getty', '/usr/sbin/keepalived', '/bin/sh']
    2016-03-29 23:09:05,496 INFO  main: Done with process detect
    2016-03-29 23:09:05,496 INFO  main: Starting package backend run
    2016-03-29 23:09:05,506 INFO  backend:dpkg: Starting dpkg detection
    2016-03-29 23:09:05,543 INFO  backend:dpkg: Found package 'upstart' for binary /sbin/init
    2016-03-29 23:09:05,563 INFO  backend:dpkg: Getting all configuration files for /sbin/init
    2016-03-29 23:09:05,658 INFO  backend:dpkg: Found package 'openssh-server' for binary /usr/sbin/sshd
    2016-03-29 23:09:05,696 INFO  backend:dpkg: Getting all configuration files for /usr/sbin/sshd
    2016-03-29 23:09:05,790 INFO  backend:dpkg: Found package 'util-linux' for binary /sbin/getty
    2016-03-29 23:09:05,810 INFO  backend:dpkg: Getting all configuration files for /sbin/getty
    2016-03-29 23:09:05,904 INFO  backend:dpkg: Found package 'keepalived' for binary /usr/sbin/keepalived
    2016-03-29 23:09:05,924 INFO  backend:dpkg: Getting all configuration files for /usr/sbin/keepalived
    2016-03-29 23:09:06,025 INFO  main: Done with package backend run
    2016-03-29 23:09:06,026 INFO  main: Starting convert run
    2016-03-29 23:09:06,026 INFO  convert:keepalived: Starting keepalived convert
    2016-03-29 23:09:07,258 INFO  convert:keepalived: Done keepalived convert
    2016-03-29 23:09:07,287 INFO  main: Done with convert run
    2016-03-29 23:09:07,288 INFO  main: Writing output to file
    2016-03-29 23:09:07,288 INFO  output:puppet: Starting conversion
    2016-03-29 23:09:07,289 INFO  output:puppet: Done conversion
    2016-03-29 23:09:07,289 INFO  main: Done

The file which was analysed:

```
global_defs {
	router_id berlin_lb10
}

vrrp_instance VI_WEB {
	state BACKUP
	interface eth0
	lvs_sync_daemon_interface eth0

	virtual_router_id 10
	priority 10
	authentication {
		auth_type PASS
		auth_pass example
        } 
	virtual_ipaddress {
		10.0.0.200
	}
}


virtual_server 10.0.0.200 80 {
	lb_algo rr
	lb_kind DR 
	protocol TCP
	
	real_server 10.0.0.120 80 {
		TCP_CHECK {
			connect_timeout 3
			connect_port 22
		}
	}
	real_server 10.0.0.20 80 {
		TCP_CHECK {
			connect_timeout 3
			connect_port 22
		}
	}

}


vrrp_instance VI_DB {
        state BACKUP
        interface eth0
        lvs_sync_daemon_interface eth0

        virtual_router_id 11
        priority 5
        authentication {
                auth_type PASS
                auth_pass example
        }
        virtual_ipaddress {
                10.0.0.201
        }
}





virtual_server 10.0.0.201 3306 {
        lb_algo rr
        lb_kind DR
        protocol TCP

        real_server 10.0.0.130 3306 {
                TCP_CHECK {
                        connect_timeout 3
                        connect_port 3306
                }
        }
        real_server 10.0.0.30 3306 {
                TCP_CHECK {
                        connect_timeout 3
                        connect_port 3306
                }
        }
}
```

And the output file in the Puppet DSL

    keepalived::lvs::virtual_server { '10.0.0.201_3306': 
        lb_kind => 'DR',
        protocol => 'TCP',
        ip_address => '10.0.0.201',
        port => '3306',
        lb_algo => 'rr',
    }
    keepalived::lvs::virtual_server { '10.0.0.200_80': 
        lb_kind => 'DR',
        protocol => 'TCP',
        ip_address => '10.0.0.200',
        port => '80',
        lb_algo => 'rr',
    }
    keepalived::vrrp::instance { 'VI_WEB': 
        auth_type => 'PASS',
        auth_pass => 'example',
        lvs_interface => 'eth0',
        priority => '10',
        virtual_ipaddress => ['10.0.0.200'],
        state => 'BACKUP',
        virtual_router_id => '10',
        interface => 'eth0',
    }
    keepalived::vrrp::instance { 'VI_DB': 
        auth_type => 'PASS',
        auth_pass => 'example',
        lvs_interface => 'eth0',
        priority => '5',
        virtual_ipaddress => ['10.0.0.201'],
        state => 'BACKUP',
        virtual_router_id => '11',
        interface => 'eth0',
    }
    keepalived::lvs::real_server { '10.0.0.20_80': 
        virtual_server => '10.0.0.200_80',
        ip_address => '10.0.0.20',
        port => '80',
        options => {
            'TCP_CHECK' => {
                    'connect_port' => '22',
                    'connect_timeout' => '3',
            }
        }
    }
    keepalived::lvs::real_server { '10.0.0.130_3306': 
        virtual_server => '10.0.0.201_3306',
        ip_address => '10.0.0.130',
        port => '3306',
        options => {
            'TCP_CHECK' => {
                    'connect_port' => '3306',
                    'connect_timeout' => '3',
            }
        }
    }
    keepalived::lvs::real_server { '10.0.0.120_80': 
        virtual_server => '10.0.0.200_80',
        ip_address => '10.0.0.120',
        port => '80',
        options => {
            'TCP_CHECK' => {
                    'connect_port' => '22',
                    'connect_timeout' => '3',
            }
        }
    }
    keepalived::lvs::real_server { '10.0.0.30_3306': 
        virtual_server => '10.0.0.201_3306',
        ip_address => '10.0.0.30',
        port => '3306',
        options => {
            'TCP_CHECK' => {
                    'connect_port' => '3306',
                    'connect_timeout' => '3',
            }
        }
    }
    class { 'keepalived': 
    }
    class { 'keepalived::global_defs': 
        router_id => 'berlin_lb10',
    }

And the file after applying the manifest:

```
# Managed by Puppet
global_defs {
  router_id berlin_lb10
}

vrrp_instance VI_DB {
  interface                 eth0
  state                     BACKUP
  virtual_router_id         11
  priority                  5
  advert_int                1
  garp_master_delay         5
  lvs_sync_daemon_interface eth0



  # notify scripts and alerts are optional
  #
  # filenames of scripts to run on transitions
  # can be unquoted (if just filename)
  # or quoted (if has parameters)




  authentication {
    auth_type PASS
    auth_pass example
  }


  virtual_ipaddress {
    10.0.0.201 dev eth0
  }





}
vrrp_instance VI_WEB {
  interface                 eth0
  state                     BACKUP
  virtual_router_id         10
  priority                  10
  advert_int                1
  garp_master_delay         5
  lvs_sync_daemon_interface eth0



  # notify scripts and alerts are optional
  #
  # filenames of scripts to run on transitions
  # can be unquoted (if just filename)
  # or quoted (if has parameters)




  authentication {
    auth_type PASS
    auth_pass example
  }


  virtual_ipaddress {
    10.0.0.200 dev eth0
  }





}
}
group 10.0.0.200_80 {

  virtual_server 10.0.0.200 80

  lb_algo rr
  lb_kind DR
  protocol TCP


  real_server 10.0.0.120 80 {
    TCP_CHECK {
      connect_port 22
      connect_timeout 3
    }
  }
  real_server 10.0.0.20 80 {
    TCP_CHECK {
      connect_port 22
      connect_timeout 3
    }
  }
}
group 10.0.0.201_3306 {

  virtual_server 10.0.0.201 3306

  lb_algo rr
  lb_kind DR
  protocol TCP


  real_server 10.0.0.130 3306 {
    TCP_CHECK {
      connect_port 3306
      connect_timeout 3
    }
  }
  real_server 10.0.0.30 3306 {
    TCP_CHECK {
      connect_port 3306
      connect_timeout 3
    }
  }
```

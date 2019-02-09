# lustre_diamond_collectors

### Overview
This collector will run on mds and oss host in order to gather iops statistics
and block read write data. It then ships it to graphite host which is queried by
grafana to graph it properly.

### How to install

#### Puppet implementation

* install garethr/garethr-diamond module
  
  ```
  # mod for managing diamond
    mod 'garethr-diamond',
      :git    => 'https://github.com/fasrc/garethr-diamond.git',
  ```
  
#### configuration in yaml format:

  * diamond puppet class
  
  ```
  # Class: profiles::diamond
  # installs diamond and configures collectors
  #
  class profiles::diamond {
    $collectors = hiera_hash('profiles::diamond::collectors', {})
    $collector_installs = hiera_hash('profiles::diamond::collector_installs', {})
  
    if ! empty($collectors) or ! empty($collector_installs) {
      include ::diamond
      create_resources(diamond::collector, $collectors)
      create_resources(diamond::collector::install, $collector_installs)
    }
  }
  ```
  * yaml defaults
  
  ```  
  ---
  diamond::graphite_host: 'www.graphite_host.com'
  diamond::graphite_port: 2003
  diamond::interval: 10
  diamond::install_from_pip: true
  diamond::manage_pip: false
  diamond::manage_build_deps: false
  ```
  * heira yaml on mds'

  ```
  ---
  profiles::diamond::collectors:
    'LustreMdsStatsCollector':
      options:
        interval: 60
        path_prefix: "diamond.%{::datacenter}"
  profiles::diamond::collector_installs:
    'lustre_diamond_collectors':
      repo_url: 'https://github.com/luisilva/lustre_diamond_collectors.git'
      repo_revision: 'master'
  ```
  * heira yaml on oss'

  ```
  ---
  profiles::diamond::collectors:
    'LustreOssStatsCollector':
      options:
        interval: 60
        path_prefix: "diamond.%{::datacenter}"
  profiles::diamond::collector_installs:
    'lustre_diamond_collectors':
      repo_url: 'https://github.com/luisilva/lustre_diamond_collectors.git'
      repo_revision: 'master'
  ```
#### Manual install

* installing diamond
  * Read the [documentation](http://diamond.readthedocs.org)
  * Install via `pip install diamond`.
    The releases on GitHub are not recommended for use.
    Use `pypi-install diamond` on Debian/Ubuntu systems with python-stdeb installed to build packages.
  * Copy the `diamond.conf.example` file to `diamond.conf`.
  * Optional: Run `diamond-setup` to help set collectors in `diamond.conf`.
  * Modify `diamond.conf` for your needs.
  * Run diamond with one of: `diamond` or `initctl start diamond` or `/etc/init.d/diamond restart`.

* Add the following lines to the daimond collectors config area:

  CentOS => /etc/diamond/collectors/LustreOssStatsCollector.conf
  ```
  enabled=True
  interval = 60
  path_prefix = diamond.summer
  ```
  OR
  CentOS => /etc/diamond/collectors/LustreMdsStatsCollector.conf
  ```
  enabled=True
  interval = 60
  path_prefix = diamond.summer
  ```
* Add the script to diamond collectors repository section:

  `CentOS => /usr/share/diamond/collectors/lustre_diamond_collectors/lustreossstatscollector.py`
  
  OR
  
  `CentOS => /usr/share/diamond/collectors/lustre_diamond_collectors/lustremdsstatscollector.py`
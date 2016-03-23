#
# Copyright (c) 2015 Autodesk Inc.
# All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import json
import os
import logging
import time

from jinja2 import Environment, FileSystemLoader
from ochopod.bindings.generic.marathon import Pod
from ochopod.models.piped import Actor as Piped
from ochopod.core.utils import shell

logger = logging.getLogger('ochopod')


if __name__ == '__main__':
    
    cfg = json.loads(os.environ['pod'])

    class Strategy(Piped):

        cwd = '/usr/share/grafana'
        
        check_every = 60.0
        
        pipe_subprocess = True

        pid_grafana = None
        pid_apache2 = None
        pid_statsd = None
        pid_carbon = None
        pid_postgres = None

        since_grafana = 0.0
        since_apache2 = 0.0
        since_statsd = 0.0
        since_carbon = 0.0
        since_postgres = 0.0   
        
        def get_pid(self, hints, hints_ignore = None):
            if hints_ignore:
                hints_ignore.append("grep")
            else:
                hints_ignore = ["grep"]
            assert hints, "need at least one hint"
            try:
                _, lines = shell("ps -ef | grep -v %s | grep %s | awk '{print $2}'" % (" | grep -v ".join(hints_ignore),  " | grep ".join(hints)))
                if lines:
                    return [int(x) for x in lines]
                else:
                    return None
            except Exception:
                return None
            
        

        def sanity_check(self, pid):
            

            #
            # - simply use the provided process ID to start counting time
            # - this is a cheap way to measure the sub-process up-time
            #
            now = time.time()
            if pid != self.pid_grafana:
                self.pid_grafana = pid
                self.since_grafana = now
             
            pid_apache2 = self.get_pid(hints = ["apache2ctl"])
            assert pid_apache2, "Apache2 process not running"
            assert len(pid_apache2) == 1, "More than 1 Apache2 process"
            if pid_apache2[0] != self.pid_apache2:
                self.pid_apache2 = pid_apache2[0]
                self.since_apache2 = now
            
            
            pid_statsd = self.get_pid(hints = ["statsd"])
            assert pid_statsd, "StatsD process not running"
            assert len(pid_statsd) == 1, "More than 1 StatsD process"
            if pid_statsd[0] != self.pid_statsd:
                self.pid_statsd = pid_statsd[0]
                self.since_statsd = now
            
            pid_carbon = self.get_pid(hints = ["carbon"])
            assert pid_carbon, "Carbon process not running"
            assert len(pid_carbon) == 1, "More than 1 Carbon process"
            if pid_carbon[0] != self.pid_carbon:
                self.pid_carbon = pid_carbon[0]
                self.since_carbon = now
            
            pid_postgres = self.get_pid(hints = ["postgresql", "sudo"])
            assert pid_postgres, "PostgreSQL process not running"
            assert len(pid_postgres) == 1, "More than 1 PostgreSQL process"
            if pid_postgres[0] != self.pid_postgres:
                self.pid_postgres = pid_postgres[0]
                self.since_postgres = now
        
            
            lapse_grafana = (now - self.since_grafana) / 3600.0
            lapse_apache2 = (now - self.since_apache2) / 3600.0
            lapse_statsd = (now - self.since_statsd) / 3600.0
            lapse_carbon = (now - self.since_carbon) / 3600.0
            lapse_postgres = (now - self.since_postgres) / 3600.0
            
            # The global uptime is the min of all uptimes.
            lapse = min(lapse_grafana, lapse_apache2, lapse_statsd, lapse_carbon, lapse_postgres)

            return {'uptime': '%.2f hours' % lapse, 
                    'uptime Grafana': '%.2f hours (pid %s)' % (lapse_grafana, self.pid_grafana), 
                    'uptime Apache2': '%.2f hours (pid %s)' % (lapse_apache2, self.pid_apache2), 
                    'uptime StatsD': '%.2f hours (pid %s)' % (lapse_statsd, self.pid_statsd), 
                    'uptime Carbon': '%.2f hours (pid %s)' % (lapse_carbon, self.pid_carbon), 
                    'uptime PostgreSQL': '%.2f hours (pid %s)' % (lapse_postgres, self.pid_postgres)}
        
        # Lets make sure that Apache2, StatsD, Carbon and PostgreSQL are running
        # before starting Grafana.
        def can_configure(self, js):
            pid_apache2 = self.get_pid(hints = ["apache2ctl"])
            assert pid_apache2, "Apache2 process not running"
            assert len(pid_apache2) == 1, "More than 1 Apache2 process"            
            
            pid_statsd = self.get_pid(hints = ["statsd"])
            assert pid_statsd, "StatsD process not running"
            assert len(pid_statsd) == 1, "More than 1 StatsD process"
            
            pid_carbon = self.get_pid(hints = ["carbon"])
            assert pid_carbon, "Carbon process not running"
            assert len(pid_carbon) == 1, "More than 1 Carbon process"
            
            pid_postgres = self.get_pid(hints = ["postgresql", "sudo"])
            assert pid_postgres, "PostgreSQL process not running"
            assert len(pid_postgres) == 1, "More than 1 PostgreSQL process"
            
            logger.debug("Apache2, StatsD, Carbon and PostgreSQL are running - ready to start Grafana")

        def configure(self, _):            
            # Defaults to empty dict if key not present.
            mappings = {'server': cfg['grafana_server'] if 'grafana_server' in cfg.keys() else {}}
            
            env = Environment(loader=FileSystemLoader("/opt/ochostats/templates"))       
            template = env.get_template('grafana.ini')
            with open('/etc/grafana/grafana.ini', 'w') as f:
                f.write(template.render(mappings))       

            return '/usr/sbin/grafana-server --pidfile=/var/run/grafana-server.pid --config=/etc/grafana/grafana.ini cfg:default.paths.data=/var/lib/grafana cfg:default.paths.logs=/var/log/grafana', {}

    Pod().boot(Strategy)
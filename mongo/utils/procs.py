# Copyright (C) 2012 Costia Adrian
# Created on Mar 6, 2012
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import psutil
import os
from signal import *

class Process:
    def __init__(self):
        procs = psutil.get_process_list()
        self.system_procs = sorted(procs, key=lambda proc: proc.name)
    
    def kill(self,pid):
        if psutil.pid_exists(pid):
            os.kill(pid, SIGTERM)
    
    def kill_name(self, name):
        proc = self.search_process(name)
        if proc is not None:
            if proc.is_running():
                proc.terminate()
    
    def suspend(self, pr):
        if isinstance(pr, int):
            if psutil.pid_exists(pr):
                p = psutil.Process(pr)
                p.suspend()
        elif isinstance(pr,str):
            p = self.search_process(pr)
            p.suspend()
    
    def resume(self, pr):
        if isinstance(pr, int):
            if psutil.pid_exists(pr):
                p = psutil.Process(pr)
                p.resume()
        elif isinstance(pr,str):
            p = self.search_process(pr)
            p.resume()
    
    def search_process(self, name):
        for proc in self.system_procs:
            if name in proc.name:
                return proc        
        
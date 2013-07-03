# Copyright (c) 2005-2011 Dynamic Solutions Inc. (support@dynamic-solutions.com)
#
# This file is part of DataZoomer.
#
# DataZoomer is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# DataZoomer is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import os, datetime
from system import system
from request import route
from user import user

class Logger:
    def __init__(self):
        """Initialize logger."""
        self.logging = True
        
    def reset(self):
        db = system.database
        if 'log' in [i[0] for i in db('show tables')]:
            db('drop table log')
        self.setup()
        
    def setup(self):
        """Create a log file if it doesn't already exist"""
        db = system.database

        if not 'log' in [i[0] for i in db('show tables')]:
            db("""
                CREATE TABLE `log` (
                  `id` int(11) NOT NULL AUTO_INCREMENT,
                  `app` varchar(30) DEFAULT NULL,
                  `route` varchar(50) DEFAULT NULL,
                  `status` char(1) DEFAULT NULL,
                  `user` varchar(30) DEFAULT NULL,
                  `address` varchar(15) DEFAULT NULL,
                  `login` varchar(30) DEFAULT NULL,
                  `server` varchar(60) DEFAULT NULL,
                  `timestamp` datetime DEFAULT NULL,
                  `elapsed` int(10) DEFAULT NULL,
                  `message` text,
                  PRIMARY KEY (`id`),
                  KEY `log_status` (`status`),
                  KEY `log_app` (`app`)
                ) ENGINE=MyISAM DEFAULT CHARSET=latin1;
            """)

    def info(self,message):
        """Log general information about an applicaiton or process."""
        return self.log('I',message)
    
    def notify(self,**values):
        """Notify processes that an event has occured."""
        import pickle
        message = pickle.dumps(values)
        return self.log('N',message)
    
    def complete(self,message=''):
        """Log completion of application or process execution."""
        return self.log('C',message)
    
    def warning(self,message):
        """Log system warning."""
        return self.log('W',message)
    
    def security(self, message, user_override=None):
        """Log system security warning."""
        return self.log('S', message, username=user_override)

    def error(self,message):
        """Log system error."""
        return self.log('E',message)
    
    def activity(self,feed,message):
        """Log system error."""
        return self.log('A',message,feed)

    def log(self, status, message, username=None, feed=None):
        """Insert an entry into the system log."""

        if not system.logging:
            return False

        db = system.database
        elapsed = system.elapsed_time * 1000 

        cmd = 'insert into log (app,route,status,user,address,login,server,timestamp,elapsed,message) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        values = [
            system.app.name,
            feed or '/'.join(route),
            status,
            username or user.login_id,
            os.environ.get('REMOTE_ADDR',''),
            os.environ.get('LOGNAME',''),
            system.request.server,
            datetime.datetime.now(),
            elapsed,
            message
            ]
        result = db(cmd,*values)
        
        return result
                        
logger = Logger()

if __name__ == '__main__':
    
    logger.info('this is some info')
    logger.notify(comment='This is a notification')
    logger.warning('This is a warning')

    
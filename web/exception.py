#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab
'''
Copyright (C) 2011 Youn sok Choi

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

from gettext import gettext as _
import sys
import traceback
import logging

E_DEFAULT = 9000

E_RPC_GET_PARAMS_FAILED = 1000
E_RPC_INVALID_PARAMS = 1001
# RPC services
E_RPC_SERVICE_FILE_NOT_FOUND = 2000
E_RPC_SERVICE_CLASS_NOT_FOUND = 2001
E_RPC_SERVICE_METHOD_NOT_FOUND = 2002
E_RPC_SERVICE_INVALID_PARAM = 2003
E_RPC_SERVICE_INVALID_PERMISSION = 2004
E_RPC_SERVICE_SCHEMA_NOT_DEFINED = 2005
# Configuration
E_CONFIG_OBJ_NOT_FOUND = 3000
E_CONFIG_SAVE_FAILED = 3001
E_CONFIG_SET_OBJ_FAILED = 3002
E_CONFIG_GET_OBJ_FAILED = 3003
E_CONFIG_INVALID_XPATH = 3004
E_CONFIG_OBJ_UNIQUENESS = 3005
E_CONFIG_OBJ_DUPLICATE = 3005
E_CONFIG_OBJ_INVALID = 3006
E_CONFIG_OBJ_INUSE = 3007
E_CONFIG_LOAD_FAILED = 3008
# Exec
E_EXEC_FAILED = 4000
E_EXEC_CMD_NOT_FOUND = 4001
E_EXEC_MISC = 4100
# Session
E_SESSION_NOT_AUTHENTICATED = 5000
E_SESSION_TIMEOUT = 5001
E_SESSION_INVALID_IPADDRESS = 5002
E_SESSION_INVALID_USERAGENT = 5003
E_SESSION_INVALID_USER = 5004
E_SESSION_ALREADY_AUTHENTICATED = 5005
# Misc
E_MISC_FAILURE = 6000
E_MISC_OPERATION_DENIED = 6001
E_MISC_INVALID_PARAM = 6002

# Object
E_OBJ_NOT_FOUND = 7000
E_OBJ_DUPLICATE = 7001
E_OBJ_CREATION_FAILED = 7002
E_OBJ_DELETION_FAILED = 7003
E_OBJ_MODIFICATION_FAILED = 7004
E_OBJ_OCCUPIED = 7005

# System
E_SYSTEM_GENERAL = 8000

# Device
E_DEVICE_ACCESS_FAILED = 8000

_errors = {
    E_DEFAULT: _("Failed to operate"),
    E_RPC_GET_PARAMS_FAILED: _("Failed to get RPC parameters"),
    E_RPC_INVALID_PARAMS: _("Invalid RPC parameters: %s"),
    E_RPC_SERVICE_FILE_NOT_FOUND: _("File '%s' not found"),
    E_RPC_SERVICE_CLASS_NOT_FOUND: _("Class '%s' not found"),
    E_RPC_SERVICE_METHOD_NOT_FOUND: _("The method '%s' does not exist for class '%s'"),
    E_RPC_SERVICE_INVALID_PARAM: _("Invalid method parameter: %s"),
    E_RPC_SERVICE_INVALID_PERMISSION: _("Invalid permission"),
    E_RPC_SERVICE_SCHEMA_NOT_DEFINED: _("No schema defined for method %s"),
    E_CONFIG_OBJ_NOT_FOUND: _("Configuration object not found (xpath=%s)"),
    E_CONFIG_LOAD_FAILED: _("Failed to load configuration (%s)"),
    E_CONFIG_SAVE_FAILED: _("Failed to save configuration (%s)"),
    E_CONFIG_SET_OBJ_FAILED: _("Failed to set configuration (xpath=%s, data=%s)"),
    E_CONFIG_GET_OBJ_FAILED: _("Failed to get configuration (xpath=%s)"),
    E_CONFIG_INVALID_XPATH: _("Invalid XPath (%s)"),
    E_CONFIG_OBJ_UNIQUENESS: _("The configuration object is not unique"),
    E_CONFIG_OBJ_INVALID: _("The fields '%s' are missing in the configuration object"),
    E_CONFIG_OBJ_DUPLICATE: _("The configuration object '%s' is already exists"),
    E_CONFIG_OBJ_INUSE: _("The configuration object is in use"),
    E_EXEC_FAILED: _("Failed to execute command '%(command)s'"),
    E_EXEC_CMD_NOT_FOUND: _("Failed to execute command '%s': command not found"),
    E_EXEC_MISC: _("%s"),
    E_SESSION_NOT_AUTHENTICATED: _("Session not authenticated"),
    E_SESSION_TIMEOUT: _("Session timeout"),
    E_SESSION_INVALID_IPADDRESS: _("Invalid IP address"),
    E_SESSION_INVALID_USERAGENT: _("Invalid User-Agent"),
    E_SESSION_INVALID_USER: _("Invalid user"),
    E_SESSION_ALREADY_AUTHENTICATED: _("Another user is already authenticated"),
    E_MISC_FAILURE: _("%s"),
    E_MISC_OPERATION_DENIED: _("The operation is denied"),
    E_MISC_INVALID_PARAM: _("Invalid parameter (%s). Expected (%s)"),
    E_OBJ_NOT_FOUND: _("The object '%s' not found"),
    E_OBJ_DUPLICATE: _("The object '%s' is already exists"),
    E_OBJ_CREATION_FAILED: _("The object '%s' creation failed"),
    E_OBJ_DELETION_FAILED: _("The object '%s' deletion failed"),
    E_OBJ_MODIFICATION_FAILED: _("The object '%s' modification failed"),
    E_SYSTEM_GENERAL: _("System has error. Message: '%s' see log for detail"),
    E_OBJ_OCCUPIED: _("%s is occupied by '%s'. Cannot perform the operation."),
    E_DEVICE_ACCESS_FAILED: _("Cannot get exclusive access to %s device '%s'"),
}

_failures = {
}

W_DEFAULT = 0000

# SYSTEM
W_INVALID_PASSWORD = 9001
W_PASSWORD_TOO_SHORT = 9002
# RAID
W_RAID_INIT_INPROGRESS = 1000
W_PHYSICAL_DISK_UNHEALTHY = 1001

# FILESYSTEM
W_NOT_ENOUGH_FREE_SPACE = 2000
W_VOLUME_NOT_FOUND = 2001
W_OPERATION_DENIED = 2002
W_VOLUME_ALREADY_EXISTS = 2003

_warnings = {
    W_DEFAULT: 
    { 
        "title": _("Generic Warning"),
        "message": _("Please retry"),
    },
    W_INVALID_PASSWORD: 
    { 
        "title": _("Invalid Password"),
        "message": _("Password is invalid. Please retry"),
    },
    W_PASSWORD_TOO_SHORT: 
    { 
        "title": _("Password too short"),
        "message": _("Password too short. Password length must be longer than 6 characters. Please retry"),
    },

    W_RAID_INIT_INPROGRESS: 
    { 
        "title": _("Filesystem initialization in progress..."),
        "message": _("%s is currently initializing. Please wait"),
    },

    W_PHYSICAL_DISK_UNHEALTHY: 
    {

        "title": _("Physical Disk(s) unhealthy"),
        "message": _("Physical Disk(s) are unhealthy. Please Check Disks. Faulty device(s) '%s'"),
    },

    W_NOT_ENOUGH_FREE_SPACE: 
    {

        "title": _("Not enough free space"),
        "message": _("Not enough free space '%s'"),
    },

    W_VOLUME_NOT_FOUND: 
    {

        "title": _("Volume not found."),
        "message": _("Volume not found. Please Creat RAID before create filesystem."),
    },

    W_OPERATION_DENIED: 
    {

        "title": _("Operation denied."),
        "message": _("Operation denied. %s"),
    },

    W_VOLUME_ALREADY_EXISTS: 
    {

        "title": _("Operation denied."),
        "message": _("Volume %s already exists"),
    }
}



class NASException(Exception):
    def __init__ (self, code, params):
        self._type = "error"
        self._params = params
        if code in _errors.keys():
            self._code = code
            self._errors = _errors[code]
        else:
            self._code = E_DEFAULT
            self._errors = _errors[E_DEFAULT]

    def __str__(self):
        # This is needed because, without a __str__(), printing an exception
        # instance would result in this:
        # AttributeError: ValidationError instance has no attribute 'args'
        # See http://www.python.org/doc/current/tut/node10.html#handling
        return '%s(%s)' % (self.__class__.__name__, self._errors % tuple(self._params))

    def __repr__(self):
        return '%d %s(%s)' % (self._code, self.__class__.__name__, self._errors % tuple(self._params))

    def traceback(self):
        exc_type, exc_value, exc_tb = sys.exc_info()
        return ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))

    def to_json(self):
        logging.debug(self._errors)
        logging.debug(tuple(self._params))
        logging.debug(self._errors % tuple(self._params))
        return {
            'code': self._code,
            'type': self._type,
            'title': "", 
            'message': self._errors % tuple(self._params),
            'trace': self.traceback()
        }


class NASWarning(NASException):
    def __init__ (self, code, params):
        self._type = "warning"
        self._params = params
        if code in _warnings.keys():
            self._code = code
            self._title = _warnings[code]['title']
            self._message = _warnings[code]['message']
        else:
            self._code = W_DEFAULT
            self._title = _warnings[W_DEFAULT]['title']
            self._message = _warnings[W_DEFAULT]['message']

    def __str__(self):
        # This is needed because, without a __str__(), printing an exception
        # instance would result in this:
        # AttributeError: ValidationError instance has no attribute 'args'
        # See http://www.python.org/doc/current/tut/node10.html#handling
        return '%s(%s)' % (self.__class__.__name__, self._message % tuple(self._params))

    def __repr__(self):
        return '%d %s(%s)' % (self._code, self.__class__.__name__, self._message % tuple(self._params))

    def traceback(self):
        exc_type, exc_value, exc_tb = sys.exc_info()
        return ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))

    def to_json(self):
        return {
            'code': self._code,
            'type': self._type,
            'title': self._title,
            'message': self._message % tuple(self._params),
            'trace': ''
        }

class DeviceAccessFailed(NASException):
    def __init__ (self, dev_type, dev_path):
        super(DeviceAccessFailed, self).__init__(E_DEVICE_ACCESS_FAILED, [dev_type, dev_path])

class PhysicalDiskUnhealthy(NASWarning):
    def __init__ (self, dev_paths):
        self._dev_path = dev_paths
        super(PhysicalDiskUnhealthy, self).__init__(W_PHYSICAL_DISK_UNHEALTHY, [",".join(dev_paths)])

class RaidInitInProgress(NASWarning):
    def __init__ (self, dev_path):
        super(RaidInitInProgress, self).__init__(W_RAID_INIT_INPROGRESS, [dev_path])

class NotEnoughFreeSpace(NASWarning):
    def __init__ (self, dev_path):
        super(NotEnoughFreeSpace, self).__init__(W_NOT_ENOUGH_FREE_SPACE, [dev_path])

class VolumeNotFound(NASWarning):
    def __init__ (self):
        super(VolumeNotFound, self).__init__(W_VOLUME_NOT_FOUND, [])

class VolumeAlreadyExists(NASWarning):
    def __init__ (self, dev_path):
        super(VolumeAlreadyExists, self).__init__(W_VOLUME_ALREADY_EXISTS, [dev_path])

class OperationDenied(NASWarning):
    def __init__ (self, detail):
        super(OperationDenied, self).__init__(W_OPERATION_DENIED, [detail])

class PasswordTooShort(NASWarning):
    def __init__ (self):
        super(PasswordTooShort, self).__init__(W_PASSWORD_TOO_SHORT, [])

class InvalidPassword(NASWarning):
    def __init__ (self):
        super(InvalidPassword, self).__init__(W_INVALID_PASSWORD, [])

class BlockDeviceNotFoundException(NASException):
    def __init__ (self, object):
        super(BlockDeviceNotFoundException, self).__init__(E_MISC_FAILURE, [object])

class ObjectOccupiedException(NASException):
    def __init__ (self, object):
        super(ObjectOccupiedException, self).__init__(E_MISC_FAILURE, [object])

class SystemException(NASException):
    def __init__ (self, message = None):
        if not message:
            message = 'Unknown'

        super(SystemException, self).__init__(E_SYSTEM_GENERAL, [message])

class ServiceAlreadyRunningException(NASException):
    def __init__ (self, message = None):
        if not message:
            message = 'Unknown'

        super(SystemException, self).__init__(E_SYSTEM_GENERAL, [message])

class ObjectDuplicateException(NASException):
    def __init__ (self, object):
        super(ObjectDuplicateException, self).__init__(E_OBJ_DUPLICATE, [object])

class ObjectCreationFailedException(NASException):
    def __init__ (self, object):
        super(ObjectCreationFailedException, self).__init__(E_OBJ_CREATION_FAILED, [object])

class ObjectDeletionFailedException(NASException):
    def __init__ (self, object):
        super(ObjectDeletionFailedException, self).__init__(E_OBJ_DELETION_FAILED, [object])

class ObjectModificationFailedException(NASException):
    def __init__ (self, object):
        super(ObjectModificationFailedException, self).__init__(E_OBJ_MODIFICATION_FAILED, [object])

class ObjectNotFoundException(NASException):
    def __init__ (self, object):
        super(ObjectNotFoundException, self).__init__(E_OBJ_NOT_FOUND, [object])

class CommandNotFoundException(NASException):
    def __init__ (self, command):
        super(CommandNotFoundException, self).__init__(E_EXEC_CMD_NOT_FOUND, [command])

class ExcutionFailedException(NASException):
    def __init__ (self, command, exitcode, stdout, stderr):
        super(ExcutionFailedException, self).__init__(E_EXEC_FAILED,
                {
                    'command': command
                }
            )
        self._exitcode = exitcode
        self._stdout = stdout.strip()
        self._stderr = stderr.strip()

    @property 
    def exitcode(self):
        return self._exitcode
    @property 
    def stdout(self):
        return self._stdout
    @property 
    def stderr(self):
        return self._stderr

    def to_json(self):
        return {
            'code': self._code,
            'type': self._type,
            'title': "", 
            'message': self._errors % self._params,
            'trace': '%s\nExitcode: %d\nStdout:\n%s\nStderr:\n%s' % (self.traceback(), self._exitcode, self._stdout, self._stderr)
        }

class InvalidParamException(NASException):
    def __init__ (self, given_opt, expected_opts):
        if isinstance(expects_opts, list):
            expected_opts = ', '.join(expected_opts)

        super(ExcutionFailedException, self).__init__(E_MISC_INVALID_PARAM, [given_opt, expected_opts])


# xml config

class ConfObjNotFoundException(NASException):
    def __init__ (self, xpath_query):
        super(ConfObjNotFoundException, self).__init__(E_CONFIG_GET_OBJ_FAILED, [xpath_query])


class ConfObjDuplicateException(NASException):
    def __init__ (self, xpath_query):
        super(ConfObjDuplicateException, self).__init__(E_CONFIG_OBJ_DUPLICATE, [xpath_query])

class ConfObjSetFailedException(NASException):
    def __init__ (self, xpath_query, conf_dict):
        super(ConfObjSetFailedException, self).__init__(E_CONFIG_SET_OBJ_FAILED, [xpath_query, conf_dict])

class ConfDeletionFailedException(NASException):
    def __init__ (self, object):
        super(ObjectDeletionFailedException, self).__init__(E_OBJ_DELETION_FAILED, [object])

class ConfModificationFailedException(NASException):
    def __init__ (self, object):
        super(ObjectModificationFailedException, self).__init__(E_OBJ_MODIFICATION_FAILED, [object])


# stolen and lifted from flumotion log module
def _get_exception_message(exception, frame = -1, filename = None):
    """
    Return a short message based on an exception, useful for debugging.
    Tries to find where the exception was triggered.
    """
    import traceback

    stack = traceback.extract_tb(sys.exc_info()[2])
    if filename:
        stack = [f for f in stack if f[0].find(filename) > -1]

    # badly raised exceptions can come without a stack
    if stack:
        (filename, line, func, text) = stack[frame]
    else:
        (filename, line, func, text) = ('no stack', 0, 'none', '')

    exc = exception.__class__.__name__
    msg = ""
    # a shortcut to extract a useful message out of most exceptions
    # for now
    if str(exception):
        msg = ": %s" % str(exception)
    return "exception %(exc)s at %(filename)s:%(line)s: %(func)s()%(msg)s" \
        % locals()
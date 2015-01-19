#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab
'''
Copyright (C) 2013 Malgn Techology Co., Ltd., Youn sok Choi

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

import exception
import logging

def make_json_data(item = None, messages = None):
    if isinstance(item, list):
        total = len(item)
        return {
            'response': {
            'total': total,
            'data': item
            }, 
            'messages': messages
        }
    else:
        return {'response': item, 'messages' : messages}

def 

def _create_json_response(json_response = None, messages = None):
    return {'response': json_response, 'messages' : messages}

def _create_json_list_response(list_items = None, messages = None):
    result = list_items
    total = len(list_items) if list_items is not None else 0
    return {
        'response': {
        'total': total,
        'data': result if result is not None else []
        }, 
        'messages': messages
    }

class jsonmethod(object):
    def __init__(self, is_list = False):
        self._is_list = is_list

    def _handle_managed_exception(self, ex):
        logging.error("%s:\n %s" % (ex.__class__.__name__, ex.traceback()))
        return {
            'response': None,
            'messages': {
                'type': "error",
                'text' : ex.to_json()
            }
        }

    def _handle_unmanaged_exception(self, ex):
        import traceback
        import sys
        exc_type, exc_value, exc_tb = sys.exc_info()
        trace_message = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))
        logging.error("%s:\n %s" % (ex.__class__.__name__, trace_message))
        return {
            'response': None,
            'messages': {
                'type': "error",
                'text': "%s: %s" % (ex.__class__.__name__, str(ex)),
                'trace': trace_message
            }
        }

    def __call__(self, fn):

        def f(*args, **kwargs):
            ret = None
            try:
                ret = fn(*args, **kwargs)
            except Exception, e:
                if isinstance(e, exception.NASException):
                    return self._handle_managed_exception(e)
                else:
                    return self._handle_unmanaged_exception(e)

            if self._is_list:
                if ret:
                    return _create_json_list_response(list_items = ret)
                else:
                    return _create_json_list_response()
            else:
                return {
                    'response': ret,
                    'messages': None
                }

        return f

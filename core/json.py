#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab

from util import enum

ResponseTypes = enum(ERROR = 'error', SUCCESS = 'success', WARNING = 'warning')

def make_json_data(item = None, messages = None):
    if not messages:
        messages = make_json_message()
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

def make_json_message(type = ResponseTypes.SUCCESS, text = None):
    return {
        'type': type,
        'text' : text
    }
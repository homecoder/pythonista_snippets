# -*- coding: utf-8 -*-
#!python2
"""
ui components - cache

The cache component is primarily intended for ingestion by
the scripts in this package, however it can be useful to
any developer who wishes to cache/save ui component(s) state.

Intention: For items such as TabView and PageView, since we
have a limited amount of memory to work with we like to cache
the state of any views which are not shown on screen.

There is (will be) an option to disable the cache entirely, 
or specify views which either do not require cache at all, or
views which should not be unloaded.
"""

import datetime
import errno
import gzip
import json
import os
import pickle
import sys
#from future.builtins import *

class CacheJSONEncoder (json.JSONEncoder):
    def __init__(self):
        super(CacheJSONEncoder, self).__init__()
        
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif isinstance(obj, datetime.date):
            return obj.isoformat()
        elif isinstance(obj, datetime.timedelta):
            return (datetime.datetime.min + obj).time().isoformat()
        else:
            return super(DateTimeEncoder, self).default(obj)

class CacheView (object):
    """
    Main Class for Caching Functionality
    """
    
    def __init__(self, **kwargs):
        """
        Class Initializer
        """
        
        # Do we want to only cache ui.View items?
        self.require_uiview = kwargs.pop(
            'require_uiview', 
            True,
        )
        
        """
        # Hold this idea
        self.cache_folder = kwargs.pop(
            'cache_folder',
            os.path.join(
                os.path.dirname(
                    os.path.realpath(__file__)
                ),
                '.viewcache',
            )
        )
        """
        self.cache_folder = kwargs.pop(
            'cache_folder',
            os.path.join(
                os.path.expanduser('~'),
                '.{}.viewcache'.format(
                    str(
                        os.path.basename(sys.argv[0])
                    ).rstrip('.py')
                ),
            )
        )
        
        
        # Make the directory if it doesn't exist
        if not os.path.exists(self.cache_folder):
            try:
                os.makedirs(self.cache_folder)
            except FileExistsError:
                # This shouldn't fire, but just in case..
                pass
                
    
    def _cache_file(self, name):
        return os.path.join(
            self.cache_folder, '{}.cache'.format(name)
        )
        
    def dump(self, view, name=None):
        if not name:
            try:
                name = vew.name
            except AttributeError:
                raise AttributeError('Name required for all objects which do not have a name attribute set.')

        try:
            with gzip.open(self._cache_file(name), 'wb') as f:
                pickle.dump(f, pickle.HIGHEST_PROTOCOL)
            return True
        except pickle.PickleError as e:
            pass
        except Exception as e:
            raise e
    
    def dump_json(self, view, name=None):
        # Use json ste encoder
        if not name:
            try:
                name = vew.name
            except AttributeError:
                raise AttributeError('Name required for all objects which do not have a name attribute set.')
        
        try:
            cache_file = '{}.jcache'.format(
                str(self._cache_file(name)).rstrip('.cache')
            )
            
            
            with gzip.open(cache_file, 'wb') as f:
                json.dump(f, cls=CacheJSONEncoder)
            return True
        except IOError as e:
            pass
        except Exception as e:
            raise e

    def load(self, name):
        """
        Load a cached view
        """
        
        cache_file = self._cache_file(name)
        
        # Check if pickled exists, if not, try json version
        if not os.path.exists(cache_file):
            cache_file = '{}.jcache'.format(
                str(self._cache_file(name)).rstrip('.cache')
            )
        
        try:
            with gzip.open(cache_file, 'rb') as f:
                return pickle.load(f)
        except IOError as e:
            if e.errno == errno.ENOENT:
                return False
            else:
                raise e
        
if __name__ == '__main__':
    """
    If executed directly; shouldn't be
    """
    raise NotImplementedError('This file should be run directly')

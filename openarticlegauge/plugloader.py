"""
module that's specifically for loading classes from string representations of their
module paths.

"""

'''
DEPRECATED - remove shortly

from openarticlegauge import config
import logging, os, imp

log = logging.getLogger(__name__)

def load(callable_path):
    """
    Load the module or class defined by the callable_path.  This will attempt first to
    load the module from the PYTHONPATH as-is, and if unsuccessful will search the
    various configured namespaces (see config) and prefixes which might yield the
    module.
    
    For example:
    
    openarticlegauge.plugin.bmc - will load the plugin directly from the installed application
    
    plugin.bmc -- will attempt to load the plugin from the installed application but will fail
        as it is missing the openarticlegauge prefix.  It will then look to see which other
        prefixes it should try, find openarticlegauge in configuration (hopefully!), and search
        for openarticlegauge.plugin.bmc, resulting in a successful load of the module
    
    arguments:
    callable_path -- the module or classpath to load
    
    returns:
    None if no module or class could be found
    A class (not an instance) or a module if one could be found at the callable_path or at one of the variations
        defined by the configuration
    
    """
    if callable_path is None:
        log.debug("attempted to load plugin with no plugin path")
        return None
    
    # split out the callable and the modpath
    components = callable_path.split(".")
    call = components[-1:][0]
    modpath = ".".join(components[:-1])
    log.debug("loading plugin from modpath: " + modpath + ", and callable: " + call)
    
    if modpath is not None and modpath != "":
        # try to load the callable
        call_able = _load_callable(modpath, call)
        
        # if success then return
        if call_able is not None:
            log.debug("loaded plugin from " + modpath + ": " + str(call_able))
            return call_able
    
    # if we don't find the callable, then we may need to look in one of the 
    # other search contexts as defined in the config
    for search_prefix in config.module_search_list:
        nm = search_prefix + "." + modpath
        call_able = _load_callable(nm, call)
        if call_able is not None:
            log.debug("loaded plugin from " + modpath + ": " + str(call_able))
            return call_able
    
    # couldn't load a plugin
    log.debug("unable to load plugin " + call + " from " + modpath)
    return None

def _load_callable(modpath, call):
    """
    Does the business of actually loading the class/module from the parent module path
    and the name of the callable.
    
    For example, if attempting to load openarticlegauge.plugins.bmc.BMCPlugin, this
    method would be called as:
    
    _load_callable("openarticlegauge.plugins.bmc", "BMCPlugin")
    
    arguments:
    modpath -- the parent module path of the thing to be loaded
    call -- the callable (module/class) within the parent module to be loaded
    
    returns:
    None if the callable couldn't be found in the modpath or if some other load error occurs
    A class (not an instance) or a module if one is found
    
    """
    # now, do some introspection to get a handle on the callable
    try:
        mod = __import__(modpath, fromlist=[call])
        call_able = getattr(mod, call)
        return call_able
    except ImportError as e:
        # in this case it's possible that it's just a context thing, and
        # the class we're trying to load is in a different package.
        log.debug("import error loading " + call + " from " + modpath + " - path may not be accessible or available in this context")
        return None
    except AttributeError as e:
        # found the module but failed to load the attribute (probably the
        # callable isn't in that module)
        log.error("attribute error loading " + call + " from " + modpath + " - path is valid, but callable isn't part of that module")
        #raise e
        return None

"""
NOTE: these might be useful to someone in the future, but we don't need them
right now, so leaving them commented out

def get_info(callable_path):
    if callable_path is None:
        log.debug("attempted to load plugin with no plugin path")
        return None
    
    # callable_path is a function in a module, and the module itself holds
    # the info, so we need to just load the module
    components = callable_path.split(".")
    modpath = ".".join(components[:-1])
    
    if modpath == "" or modpath is None:
        return None, None
    
    # ok, so now we know the path to the module, load it
    module = load(modpath)
    
    name = "unknown"
    version = -1
    if hasattr(module, "__name__"):
        name = module.__name__.split(".")[-1]
    if hasattr(module, "__version__"):
        version = module.__version__
    
    return name, version
    
def load_sibling(callable_path, sibling_name):
    if callable_path is None:
        log.debug("attempted to load plugin with no plugin path")
        return None
    
    components = callable_path.split(".")
    call = components[-1:][0]
    modpath = ".".join(components[:-1])
    
    # construct the new callable
    sibling = modpath + "." + sibling_name
    return load(sibling)
"""
'''

import config
import logging

log = logging.getLogger(__name__)

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
    
def load(callable_path):
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

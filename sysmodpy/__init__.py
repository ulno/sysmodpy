"""
Support library for structured object oriented development with a dash of story driven modeling.
Initial main goals are the decoration of typed python classes with convenience functions
and bidirectional referential integraty for associations.

Creation reason:
    My (ulno's) students had a hard time making the switch to Java but all had
    decent Python programming experience, so why not bring some of the good things of Java
    to Python?

Author: ulno (http://ulno.net)
Inception date: 2020-10-01
"""
from __future__ import annotations
from typing import List, Set
import re

def _set(self, attrib : str, val, ext=None):
    """
    Generic set function for one side of class associations.
    :param self: the local object instance
    :param attrib: a string with the name of the local attribute that is changed
    :param val: the new value
    :param ext: potential external object of associated class that is affected
    :return: returns the given object to allow constructing fluent style
    """
    # TODO: consider adding property change listener support
    old_value = getattr(self, attrib, None)
    if old_value == val: # check if update
        return self # if not, just return
    if ext: # bidirectional
        exec(f"ext.remove_{attrib}({old_value})")
        setattr(self, attrib, val)
        exec(f"ext.add_{attrib}({self})")
    else: # unidirectional
        setattr(self, attrib, val); # TODO: check if there is a better way than using a string as attribute here (also for all functions below)
    return self

def _remove_single(self, attrib : str, val, ext=None, ext_name=None):
    """
    Generic remove function for one side of class associations in a local to-1 association
    :param self: the local object instance
    :param attrib: a string with the name of the local attribute that is changed
    :param val: the value/object to be removed
    :param ext: potential external object of associated class that is affected
    :param ext_name: name of the attribute in external associated class that stores this association
    :return: returns the given object to allow constructing fluent style
    """
    # TODO: consider adding property change listener support
    old_value = getattr(self, attrib, None)
    if old_value == None: # already removed
        return self # if not, just return
    if ext: # bidirectional
        setattr(self, attrib, None)
        exec(f"ext.remove_{ext_name}(self)")
    else: # unidirectional
        setattr(self, attrib, None);
    return self

def _remove_from_container(self, attrib : str, val, ext=None, ext_name=None):
    """
    Generic remove function for one side of class associations in a local to-n association
    :param self: the local object instance
    :param attrib: a string with the name of the local attribute that is changed
    :param val: the value/object to be removed
    :param ext: potential external object of associated class that is affected
    :param ext_name: name of the attribute in external associated class that stores this association
    :return: returns the given object to allow constructing fluent style
    """
    # TODO: consider adding property change listener support
    container = getattr(self, attrib, None)
    if container is None:
        container = set() # TODO: look at annotations if we should create a set or a list here
        setattr(self, attrib, container) # make sure, there is a container
    if not val in container: # check if update necessary (already removed?)
        return self # if not, just return
    container.remove(val)
    if ext: # bidirectional
        exec(f"ext.remove_{ext_name}(self)")
    return self

def _add(self, attrib : str, val, ext=None, ext_name=None):
    """
    Generic add function for one side of class associations in a to-many association
    :param self: the local object instance
    :param attrib: a string with the name of the local attribute that is changed
    :param val: the value/object to be added to the container
    :param ext: potential external object of associated class that is affected
    :param ext_name: name of the attribute in external associated class that stores this association
    :return: returns the given object to allow constructing fluent style
    """
    # TODO: consider adding property change listener support
    container = getattr(self, attrib, None)
    if container is None:
        container = set() # TODO: look at annotations if we should create a set or a list here
        setattr(self, attrib, container) # make sure, there is a container
    if val in container: # check if update necessary
        return self # if not, just return
    container.add(val)
    if ext: # bidirectional
        exec(f"ext.add_{ext_name}({self})") # TODO: n:n - so far only n:1?
    return self

def _container_check(elem: str) -> (str, str):
    container = None
    m = re.match("(Set|List)\[(\w+)\]", elem)
    if m:  # pay attention to Set and List - this is a to-many end of an association
        container = m[1]
        elem_type_str = m[2]
    else:
        elem_type_str = elem
    return elem_type_str, container


def decorate(*class_or_classes) -> None:
    """
    Do the actual analysis of one or a list of classes and decorate them with
    convenience functions.
    :param class_or_classes: a single class or list or set of classes
    :return:
    """

    # make sure, we have a set of classes
    if type(class_or_classes[0]) is list or type(class_or_classes[0]) is set:
        classes = set(class_or_classes[0])
    else:
        classes = set(class_or_classes)

    classes_dict={}
    for c in classes:
        classes_dict[c.__name__] = c

    for c in classes:
        print(c.__name__)
        for annotation in c.__annotations__:
            elem = c.__annotations__[annotation]
            print(f"{annotation} - {elem}")
            elem_type_str, container = _container_check(elem)

            exec(f"c.get_{annotation} = lambda self: self.{annotation}") # always generate getter

            if elem_type_str in classes_dict: # seems to be an association between two classes that we want to decorate
                # check if there is association in referenced class
                bidirectional = False
                ext_elem = None
                for ext_annotation in classes_dict[elem_type_str].__annotations__:
                    ext_elem = classes_dict[elem_type_str].__annotations__[ext_annotation]
                    ext_type_str, ext_container = _container_check(ext_elem)
                    if ext_type_str == c.__name__: # that's a match # TODO: add logic to distinguish different associations between same classes
                        bidirectional = True
                        break # TODO: support multiple different associations between same classes
                if bidirectional:
                    if container: # local to-many end
                        if getattr(c, annotation, None) is None:
                            setattr(c, annotation, None) # make sure there is a default attribute
                        exec(f"c.add_{annotation} = lambda self, value: _add(self,\"{annotation}\",value,self.{annotation},\"{ext_annotation}\")")
                        exec(f"c.with_{annotation} = c.add_{annotation}")
                        exec(f"c.remove_{annotation} = lambda self, value: _remove_from_container(self,\"{annotation}\",value,self.{annotation},\"{ext_annotation}\")")
                    else: # local to-one end
                        exec(f"c.set_{annotation} = lambda self, value: _set(self,\"{annotation}\",value,self.{annotation})")
                        exec(f"c.add_{annotation} = c.set_{annotation}")
                        exec(f"c.with_{annotation} = c.set_{annotation}")
                        exec(f"c.remove_{annotation} = lambda self, value: _remove_single(self,\"{annotation}\",value,self.{annotation},\"{ext_annotation}\")")
                        # TODO: more association logic
            else: # "just" an attribute or external class
                # generate attribute functions - "normal" getters and setters
                exec(f"c.set_{annotation} = lambda self, value: _set(self,\"{annotation}\",value)")
                exec(f"c.with_{annotation} = c.set_{annotation}")
            c.__oo_helper_decorated__ = True

        print()
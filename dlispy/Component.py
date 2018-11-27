ABSATER = 'ABSATER'
ATTRIB = 'ATTRIB'
INVATR = 'INVATR'
OBJECT = 'OBJECT'
RDSET = 'RDSET'
RSET = 'RSET'
SET = 'SET'

ComponentRole = {
    '000': ABSATER,
    '001': ATTRIB,
    '010': INVATR,
    '011': OBJECT,
    '100': 'reserved',
    '101': RDSET,
    '110': RSET,
    '111': SET
}

"""
-   An EFLR begins with a Set components. Type in Set is mandatory, name is optional. 
    -   A Redundant Set is an identical copy of some Set written previously in the same Logical File, including the Set 
    Name and Type. If a Redundant Set is has a null Name, then the Set of which it is a copy must be the only Set in the
     same Logical File of the same Type, excluding other Redundant Sets, preceding the given Redundant Set.

    -   A Replacement Set has the same Type and (non-null) Name, the same Template, and the same Objects (none added, 
    none deleted) in the same order as a Set written previously in the same Logical File. However, the Attributes of the
     Replacement Set reflect all updates that may have been applied since the original Set was written. A Replacement 
     Set can be written anywhere in a Logical File following the original Set that it replaces. There may be any number 
     of Replacement Sets for a given original Set.


 
-   Then Template follows Set. Template is just a collection of Attribute Components and/or Invariant Attribute 
    Components. This define the structures of the objects in this Set. All Components in the Template must have 
    distinct, non-null Labels.
    
-   Object components follows the Template. Object name is manadatory,
 
-   Attribute component. 
    -   All Attributes in the same "column" of a Set must have the same Attribute Label, namely, 
    the one specified in the Template Attribute Component. Therefore, Attribute Components that follow Object Components 
    must not have Attribute Labels (because it is already defined in Template).
     
    -   The remaining Characteristics may be freely specified by an Object's Attribute Components. Any Characteristic 
    not present assumes the local default value as specified in the corresponding Attribute Component in the Template. 
    
    -   Missing Attribute Components imply that local defaults should be used for the Characteristics of the 
    corresponding Attribute. Since Attribute order is important within a Set, only trailing Attribute Components can be 
    omitted.
    
    -   An Attribute is considered to be Absent for an Object when its Attribute Component is 
    replaced by an Absent Attribute Component. An Absent Attribute is one for which no
     information is provided, not even default meaning.
"""


class Component(object):
    """
    Represent Component in RP 66, super class for set, object, attribute
    """
    def toJSON(self):
        return self.__dict__


class Object(Component):
    """
    Object. Each object only have two things: name and a list of attributes.
    """
    def __init__(self):
        self._name = None
        self._attributes= []

    @property
    def name(self):
        """
        :return:
        :rtype: ObName
        """
        return self._name

    @property
    def attributes(self):
        return self._attributes

    def __str__(self):
        attrStr = "\n    ".join(map(str, self.attributes))
        return "Object[name:{} with attributes:\n{}]".format(self.name, attrStr)


class Attribute(Component):
    """
    Represent Attribute in RP66.
    """

    def __init__(self):
        self._label = ''
        self._count = 1
        # default rep code is 19.
        self._repCode = 19
        self._units = ''
        self._value = None


    def clone(self, attr):
        attr._label = self._label
        attr._count = self._count
        attr._repCode = self._repCode
        attr._units = self._units
        attr._value = self._value
        return attr

    def __str__(self):
        return "Attribute[label:{} count:{} repCode:{} units:{} value:{}]".\
            format(self._label, self._count, self._repCode, self._units, self._value)

    @property
    def value(self):
        return self._value

    @property
    def label(self):
        return self._label

    @property
    def count(self):
        return self._count

    @property
    def repCode(self):
        return self._repCode

    @property
    def units(self):
        return self._units




class AbsentAttribute(Attribute):
    """
    Represent Absent Attribute.
    """

    def __init__(self, attr):
        self._label = attr._label
        self._count = attr._count
        self._repCode = attr._repCode
        self._units = attr._units
        self._value = attr._value

class InvariantAttribute(Attribute):
    """
    Represent Invariant attribute.
    """
    pass

class Set(Component):
    """
    Represent set. Set is central piece in EFLR, each set has a name, type and a template which defines attributes each
    of objects should have, then a list of objects.
    """
    def __init__(self):
        self._type = None
        self._name = None
        self.template = None
        self.objects = []

    @property
    def type(self):
        return self._type

    @property
    def name(self):
        return self._name

    def __str__(self):
        return 'Set[type:{} name:{} numOfObjects:{}]'.format(self._type, self._name, len(self.objects))

class RedundantSet(Set):
    """
    Represent Redundant set.
    """
    pass


class ReplacementSet(Set):
    """
    Represent replacementset.
    """
    pass

class Template(object):
    """
    Template. Template only contains a list of attribute which should be included in each objects in the same set.
     It is similar to database columns.
    """
    def __init__(self):
        self._attrList = []

    @property
    def attrList(self):
        return self._attrList

    def __str__(self):
        attrListStr = '\n    '.join(map(str, self._attrList))
        return "Template with attributes [\n{}]".format(attrListStr)

    def toJSON(self):
       return dict(attributeList=self._attrList)
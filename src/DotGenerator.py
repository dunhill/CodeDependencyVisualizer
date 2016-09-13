import hashlib
import logging


class UmlNS:
    def __init__(self, fqn_):
        self.fqn = fqn_
        self.children = {}

    def getId(self):
        return "id" + str(hashlib.md5(self.fqn).hexdigest())


class UmlClass:
    def __init__(self):
        self.fqn = None
        self.parents = []
        self.privateFields = []
        self.privateMethods = []
        self.publicFields = []
        self.publicMethods = []
        self.protectedFields = []
        self.protectedMethods = []

    def addParentByFQN(self, fullyQualifiedClassName):
        self.parents.append(fullyQualifiedClassName)

    def getId(self):
        return "id" + str(hashlib.md5(self.fqn).hexdigest())


class DotGenerator:
    _showPrivMembers = False
    _showProtMembers = False
    _showPubMembers = False
    _drawAssociations = False
    _drawInheritances = False
    _drawDependencies = False
    _groupByNamespace = False

    def __init__(self):
        self.classes = {}
        self.rootNS = UmlNS("")

    def addClass(self, aClass):
        self.classes[aClass.fqn] = aClass

        # add namespace heirarchy
        ns_tokens = aClass.fqn.split("::")
        cur = self.rootNS.children
        for i in range(len(ns_tokens)):
            fqn = "::".join(ns_tokens[:i+1])
            if fqn in cur:
                child = cur[fqn]
            else:
                child = UmlNS(fqn)
                cur[fqn] = child
            cur = child.children

    def _genFields(self, accessPrefix, fields):
        ret = "".join([(accessPrefix + fieldName + ": " + fieldType + "\l") for fieldName, fieldType in fields])
        return ret

    def _genMethods(self, accessPrefix, methods):
        return "".join([(accessPrefix + methodName + methodArgs + " : " + returnType + "\l") for (returnType, methodName, methodArgs, argsTypes) in methods])

    def _genClass(self, aClass, ident):
        identStr = "  " * ident;
        c = identStr + (aClass.getId()+" [ \n" +
             identStr + "  label = \"{" + aClass.fqn)

        if self._showPubMembers:
            pubFields = self._genFields('+ ', aClass.publicFields)
            pubMethods = self._genMethods('+ ', aClass.publicMethods)

            if len(pubFields) != 0 or len(pubMethods) != 0:
                c += "|" + pubFields + pubMethods

        if self._showProtMembers:
            protFields = self._genFields('# ', aClass.protectedFields)
            protMethods = self._genMethods('# ', aClass.protectedMethods)

            if len(protFields) != 0 or len(protMethods) != 0:
                c += "|" + protFields + protMethods

        if self._showPrivMembers:
            privateFields = self._genFields('- ', aClass.privateFields)
            privateMethods = self._genMethods('- ', aClass.privateMethods)

            if len(privateFields) != 0 or len(privateMethods) != 0:
                c += "|" + privateFields + privateMethods

        c += "}\"\n"
        c += identStr + "]\n"
        c = c.replace('<', '\\<')
        c = c.replace('>', '\\>')
        return c

    def _mergeSingleNamespaces(self, ns):
        if len(ns.children) == 1 and ns.fqn not in self.classes:
            childKey, childValue = ns.children.popitem()
            ns.fqn = childValue.fqn
            ns.children = childValue.children
            self._mergeSingleNamespaces(ns)
        else:
            for ignoredKey, childNS in ns.children.iteritems():
                self._mergeSingleNamespaces(childNS)

    def _genNamespace(self, ns, ident=1):
        if len(ns.children) == 0 and ns.fqn == "":
            return ""
        elif len(ns.children) == 0:
            return self._genClass(self.classes[ns.fqn], ident)
        elif ns.fqn == "":
            c = ""
            for fqn, ns in ns.children.iteritems():
                c += self._genNamespace(ns, ident)
            return c
        else:
            identStr = "  " * ident;
            c = identStr + "subgraph cluster_" + ns.getId() + " {\n"
            c += identStr + "  label = \"" + ns.fqn + "\"\n"
            if ns.fqn in self.classes:
                c += self._genClass(self.classes[ns.fqn], ident+1)
            for fqn, ns in ns.children.iteritems():
                c += self._genNamespace(ns, ident+1)
            c += identStr + "}\n"
            return c

    def _genAssociations(self, aClass):
        edges = set()
        for fieldName, fieldType in aClass.privateFields:
            if fieldType in self.classes:
                c = self.classes[fieldType]
                edges.add(aClass.getId() + "->" + c.getId())
        for fieldName, fieldType in aClass.publicFields:
            if fieldType in self.classes:
                c = self.classes[fieldType]
                edges.add(aClass.getId() + "->" + c.getId())

        edgesJoined = "\n".join(edges)
        return edgesJoined+"\n" if edgesJoined != "" else ""

    def _genDependencies(self, aClass):
        edges = set()
        for ignoreRet, ignoreName, ignoreArgs, argTypes in aClass.privateMethods:
            for argType in argTypes:
                if argType in self.classes:
                    c = self.classes[argType]
                    edges.add(aClass.getId() + "->" + c.getId())
        for ignoreRet, ignoreName, ignoreArgs, argTypes in aClass.publicMethods:
            for argType in argTypes:
                if argType in self.classes:
                    c = self.classes[argType]
                    edges.add(aClass.getId() + "->" + c.getId())

        edgesJoined = "\n".join(edges)
        return edgesJoined+"\n" if edgesJoined != "" else ""

    def _genInheritances(self, aClass):
        edges = ""
        for parent in aClass.parents:
            if parent in self.classes:
                c = self.classes[parent]
                edges += (aClass.getId() + "->" + c.getId() + "\n")
        return edges

    def setDrawInheritances(self, enable):
        self._drawInheritances = enable

    def setDrawAssociations(self, enable):
        self._drawAssociations = enable

    def setDrawDependencies(self, enable):
        self._drawDependencies = enable

    def setShowPrivMethods(self, enable):
        self._showPrivMembers = enable

    def setShowProtMethods(self, enable):
        self._showProtMembers = enable

    def setShowPubMethods(self, enable):
        self._showPubMembers = enable

    def setGroupByNamespaces(self, enable):
        self._groupByNamespace = enable

    def generate(self):
        dotContent = ("digraph dependencies {\n" +
                      "  fontname = \"Bitstream Vera Sans\"\n" +
                      "  fontsize = 8\n" +
                      "  node [\n" +
                      "    fontname = \"Bitstream Vera Sans\"\n" +
                      "    fontsize = 8\n" +
                      "    shape = \"record\"\n" +
                      "  ]\n" +
                      "  edge [\n" +
                      "    fontname = \"Bitstream Vera Sans\"\n" +
                      "    fontsize = 8\n" +
                      "  ]\n"
                      )

        if self._groupByNamespace:
            self._mergeSingleNamespaces(self.rootNS)
            dotContent += self._genNamespace(self.rootNS)
        else:
            for ignoredKey, value in self.classes.iteritems():
                dotContent += self._genClass(value, 1)

        # dependencies
        if self._drawDependencies:
            dependencies = ""
            for key, aClass in self.classes.iteritems():
                dependencies += self._genDependencies(aClass)

            if dependencies != "":
                dotContent += ("\nedge [style = dashed, arrowhead = open]\n")
                dotContent += dependencies

        # associations
        if self._drawAssociations:
            associations = ""
            for key, aClass in self.classes.iteritems():
                associations += self._genAssociations(aClass)

            if associations != "":
                dotContent += ("\nedge [style = solid, arrowhead = open]\n")
                dotContent += associations

        # inheritances
        if self._drawInheritances:
            inheritances = ""
            for key, aClass in self.classes.iteritems():
                inheritances += self._genInheritances(aClass)

            if inheritances != "":
                dotContent += ("\nedge [style = solid, arrowhead = empty]\n")
                dotContent += inheritances

        dotContent += "}\n"
        return dotContent

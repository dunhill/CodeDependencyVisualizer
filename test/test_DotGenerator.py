from DotGenerator import *

import sys

dot = DotGenerator()
dot.setDrawInheritances(True)
dot.setDrawAssociations(True)
dot.setDrawDependencies(True)
dot.setShowPrivMethods(True)
dot.setShowProtMethods(True)
dot.setShowPubMethods(True)

privateFields=[("aa", "int"),("bb","void*"),("cc","NS1::BClass"),("dd", "void")]
privateMethods=[("void", "privateMethod1", "(int, NS1::BClass*)", ["NS1::BClass"]), ("NS1::BClass", "privateMethod2", "(void)", ["NS1::BClass"])]
publicFields=[("publicField1","CClass"), ("publicField2", "none")]
publicMethods=[("void", "publicMethod1", "(int, DClass*)", ["DClass"]), ("void", "publicMethod2", "(void)", [])]

c1 = UmlClass()
c1.fqn = "NS1::AClass"
c1.privateFields = privateFields
c1.privateMethods = privateMethods
c1.publicFields = publicFields
c1.publicMethods = publicMethods
dot.addClass(c1)

c2 = UmlClass()
c2.fqn = "NS1::BClass"
c2.parents.append(c1.fqn)
dot.addClass(c2)

c3 = UmlClass()
c3.fqn = "CClass"
dot.addClass(c3)

c4 = UmlClass()
c4.fqn = "DClass"
dot.addClass(c4)

outputDotFile = ['uml2.dot', sys.argv[1]][len(sys.argv) == 2]

with open(outputDotFile, "w") as dotfile:
    dotfile.write(dot.generate())

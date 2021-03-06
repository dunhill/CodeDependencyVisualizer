CodeDependencyVisualizer
========================

This tool is intended for reverse engineering UML class diagrams out of existing C++ code. It can generate class diagrams with inheritances, associations and weaker dependencies.

You might also take a look at blogpost: http://gernotklingler.com/blog/libclang-reverse-engineering-uml-class-diagrams/

Dependencies
------------
- python 2.7
- clang version 3.5
- graphvitz (for the dot tool) to be able to transform the generated dot file to an image

Just tested on Linux.

Usage
-----
For usage information run:
python ./CodeDependencyVisualizer.py --help
```
usage: CodeDependencyVisualizer.py [-h] -d D [-o OUTFILE]
                                   [-u WITHUNUSEDHEADERS] [-a] [-i] [-r] [-p]
                                   [-t] [-P]
                                   [-I INCLUDEDIRS [INCLUDEDIRS ...]]
                                   [--namespaces] [-v]
                                   [--excludeClasses EXCLUDECLASSES]
                                   [--includeClasses INCLUDECLASSES]

CodeDependencyVisualizer (CDV)

optional arguments:
  -h, --help            show this help message and exit
  -d D                  directory with source files to parse (searches
                        recusively)
  -o OUTFILE, --outFile OUTFILE
                        output file name / name of generated dot file
  -u WITHUNUSEDHEADERS, --withUnusedHeaders WITHUNUSEDHEADERS
                        parse unused header files (slow)
  -a, --associations    draw class member assiciations
  -i, --inheritances    draw class inheritances
  -r, --dependencies    draw class dependencies
  -p, --privMembers     show private members
  -t, --protMembers     show protected members
  -P, --pubMembers      show public members
  -I INCLUDEDIRS [INCLUDEDIRS ...], --includeDirs INCLUDEDIRS [INCLUDEDIRS ...]
                        additional search path(s) for include files (seperated
                        by space)
  --namespaces          group classes by namespaces
  -v, --verbose         print verbose information for debugging purposes
  --excludeClasses EXCLUDECLASSES
                        classes matching this pattern will be excluded
  --includeClasses INCLUDECLASSES
                        only classes matching this pattern will be included
```

Examples
--------
```
./CodeDependencyVisualizer.py -airptP --verbose -d dummyCppProject -I dummyCppProject/subfolder"
```
The command above just creates the file 'uml.dot'. To convert the dot file to an svg image run the dot tool:
```
dot -T svg -o uml.svg uml.dot
```

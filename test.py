from core.find_dependencies import get_dependencies_map
from core.dependency_graph import DirectoryViz

from PyQt5 import QtWidgets
import sys


if __name__ == '__main__':
    source = 'C:\\Users\\RPOP\\PycharmProjects\\PyModuleDependencies'
    source = 'C:\\Users\\RPOP\\PycharmProjects\\pygames'
    mod_map = get_dependencies_map(source)
    # for name, module in mod_map.iteritems():
    #     print module.name
    #     print module.path
    #     print [m.name for m in module.parents] # used by
    #     print [m.name for m in module.children] # uses
    app = QtWidgets.QApplication(sys.argv)
    w = DirectoryViz()
    w.graph_directory_tree(source)
    for script in mod_map.values():
        for ref in script.children:
            w.graph_connection(script.path, ref.path)
    w.show()
    app.exec_()
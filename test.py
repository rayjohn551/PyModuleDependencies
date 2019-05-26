from core.findDependencies import get_dependencies_map

if __name__ == '__main__':
    source = 'C:\\Users\\RPOP\\PycharmProjects\\PyModuleDependencies\\testPackage'
    mod_map = get_dependencies_map(source)
    for name, module in mod_map.iteritems():
        print module.name
        print module.path
        print [m.name for m in module.parents] # used by
        print [m.name for m in module.children] # uses

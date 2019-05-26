import os
import ast
import sys


class ModVisitor(ast.NodeVisitor):
    def __init__(self):
        self.modules = []

    def generic_visit(self, node):
        # print node
        super(ModVisitor, self).generic_visit(node)

    def visit_Import(self, node):
        self.modules.extend([(n.name,[]) for n in node.names])

    def visit_ImportFrom(self, node):
        source_module = node.module
        modules_or_objects = [n.name for n in node.names]
        self.modules.append((source_module,modules_or_objects))


class ModuleDep(object):
    def __init__(self, name='', path='', parents=None, children=None):
        self.name = name
        self.path = path
        self.parents = parents or set()
        self.children = children or set()


def get_file_name(path):
    return path.split('\\')[-1].split('.')[0]


def get_file_dir(path):
    return '\\'.join(path.split('\\')[:-1])


def dir_or_pyfile(path):
    if os.path.isdir(path):
        return path, True
    pyfile = path + '.py'
    if os.path.exists(pyfile):
        return pyfile, False
    return None, False


def resolve_path_locality(module_name, current_dir, root_dir, current_only=False, include_sys_path=False):
    local_path = module_name.replace('.', '\\')

    paths_to_check = [os.path.join(current_dir, local_path)]
    if not current_only:
        paths_to_check.append(os.path.join(get_file_dir(current_dir), local_path)) # relative path
        paths_to_check.append(os.path.join(root_dir, local_path)) # root path
        paths_to_check.append(os.path.join(get_file_dir(root_dir), local_path)) # absolute path
        if include_sys_path:
            paths_to_check.extend([os.path.join(sys_dir, local_path) for sys_dir in sys.path])

    for path in paths_to_check:
        # print path
        valid, is_dir = dir_or_pyfile(path)
        if valid:
            return valid, is_dir

    return None, False


def main():
    source_path = 'C:\\Users\\RPOP\\PycharmProjects\\PyModuleDependencies\\testPackage'
    all_files = []
    all_dirs = [source_path]
    for root, dirs, files in os.walk(source_path):
        for d in dirs:
            all_dirs.append(str(os.path.join(root, d)))
        for f in files:
            if f.endswith('.py') and '__' not in f:# and 'absoluteImportObjFromOtherModule' in f:
                all_files.append(str(os.path.join(root, f)))
    module_map = {}  # name : moduleObj

    for script in all_files:
        v = ModVisitor()
        code = ast.parse(open(script,'r').read())
        v.visit(code)
        name = get_file_name(script)
        if name not in module_map.keys():
            module_map[name] = ModuleDep(name=name,path=script)
        for mod, subs in v.modules:
            mod_path, is_dir = resolve_path_locality(mod, get_file_dir(script), source_path)
            if not mod_path:  # not valid dir or file
                continue
            if is_dir:
                for sub in subs:
                    sub_path, is_dir = resolve_path_locality(sub, mod_path, source_path)
                    if not sub_path:
                        continue
                    if is_dir:   # edge case logic for package imports?
                        continue
                    if sub not in module_map.keys():
                        module_map[sub] = ModuleDep(name=sub, path=sub_path)
                    module_map[name].children.update({module_map[sub]})
                    module_map[sub].parents.update({module_map[name]})
            else:
                mod_name = get_file_name(mod_path)
                if mod_name not in module_map.keys():
                    module_map[mod_name] = ModuleDep(name=mod_name,path=mod_path)
                module_map[name].children.update({module_map[mod_name]})
                module_map[mod_name].parents.update({module_map[name]})

    print '-'*100
    for name, module in module_map.iteritems():
        print module.name
        print module.path
        print [m.name for m in module.parents] # used by
        print [m.name for m in module.children] # uses

    print 'finished!'


if __name__ == '__main__':
    main()

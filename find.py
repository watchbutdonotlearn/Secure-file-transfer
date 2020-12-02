from modulefinder import ModuleFinder

finder = ModuleFinder()
finder.run_script('gui.py')

print('Loaded modules:')
for name, mod in finder.modules.items():
    print(name)

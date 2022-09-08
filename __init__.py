bl_info = {
    "name": "blendit",
    "authon": "imaginelenses",
    "description": "Version control for Blender.",
    "blender": (3, 2, 0),
    "category": "Blendit"
}

import os
import sys
import importlib
import subprocess

# Ensure pip is installed
try:
    import pip
except ModuleNotFoundError:
    # Installing pip
    import ensurepip
    ensurepip._main()

# Ensure Dulwich is installed
try:
    from dulwich import porcelain as git
except ModuleNotFoundError:
    # ../lib/pythonX.XX/os.py -> ../bin/pythonX.XX
    pyVerion = os.__file__.split("/")[-2]
    executable = os.path.join("/", *os.__file__.split("/")[:-3], "bin", pyVerion)
    
    # Upgrade pip
    try:
        subprocess.check_call([executable, "-m", "pip", "install", "-U", "pip"])
    except subprocess.CalledProcessError as e:
        print(f"Pip is upto data. {e}")

    # Install Dulwich https://www.dulwich.io/
    subprocess.check_call([executable, "-m", "pip", "install", "dulwich", "--no-cache-dir"])
    
    from dulwich import porcelain as git

if (git.__name__ == "dulwich.porcelain"):
    print("Dulwich is installed.")

# Local imports implemented to support Blender refreshes
modulesNames = ["newProject", "openProject", "reports", "startMenu", "subscriptions", "commitsPanel"]
for module in modulesNames:
    if module in sys.modules:
        importlib.reload(sys.modules[module])
    else:
        globals()[module] = importlib.import_module(f"{__name__}.{module}")

import bpy
from bpy.app.handlers import persistent


@persistent
def loadPreferencesHandler(_):
    print("Changing Preference Defaults!")

    prefs = bpy.context.preferences
    prefs.use_preferences_save = False

    view = prefs.view
    view.show_splash = True


@persistent
def savePreHandler(_):
    # Create project if not already created
    if not bpy.path.abspath("//"):
        bpy.ops.blendit.new_project('INVOKE_DEFAULT')


@persistent
def savePostHandler(_):
    filepath = bpy.path.abspath("//")
    filename = bpy.path.basename(bpy.data.filepath).split(".")[0]

    commands = reports.getCommands()

    with open(os.path.join(filepath, f"{filename}.py"), "a") as file: 
        for command in commands:
            file.write(f"\t{command}\n")
    
    reports.clearReports()


@persistent
def loadPostHandler(_):
    bpy.ops.wm.splash('INVOKE_DEFAULT')
    
    # Message bus subscription
    subscriptions.unsubscribe()


def register():
    print("Registering to Change Defaults")
    bpy.app.handlers.load_post.append(loadPostHandler)
    bpy.app.handlers.save_pre.append(savePreHandler)
    bpy.app.handlers.save_post.append(savePostHandler)
    bpy.app.handlers.load_factory_preferences_post.append(loadPreferencesHandler)
    
    for moduleName in modulesNames:
        if hasattr(globals()[moduleName], "register"):
            globals()[moduleName].register()


def unregister():
    print("Unregistering to Change Defaults")
    bpy.app.handlers.load_post.remove(loadPostHandler)
    bpy.app.handlers.save_pre.remove(savePreHandler)
    bpy.app.handlers.save_post.remove(savePostHandler)
    bpy.app.handlers.load_factory_preferences_post.remove(loadPreferencesHandler)

    for module in modulesNames:
        if hasattr(globals()[module], "unregister"):
            globals()[module].unregister()

    # Message bus unsubscription
    subscriptions.unsubscribe()
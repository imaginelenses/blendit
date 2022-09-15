import os
import sys
import importlib

import bpy
from bpy.app import handlers
from bpy.app.handlers import persistent

# Local imports implemented to support Blender refreshes
modulesNames = ("reports", "subscriptions")
for module in modulesNames:
    if module in sys.modules:
        importlib.reload(sys.modules[module])
    else:
        parent = ".".join(__name__.split(".")[:-1])
        globals()[module] = importlib.import_module(f"{parent}.{module}")


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

    # Apply all transforms
    # bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    commands = reports.getCommands()

    with open(os.path.join(filepath, f"{filename}.py"), "a") as file: 
        for command in commands:
            file.write(f"\t{command}\n")
    
    reports.clearReports()


@persistent
def loadPostHandler(_):
    bpy.ops.wm.splash('INVOKE_DEFAULT')
    
    # Message bus subscription
    subscriptions.subscribe()


def register():
    print("Registering to Change Defaults")
    handlers.load_post.append(loadPostHandler)
    handlers.save_pre.append(savePreHandler)
    handlers.save_post.append(savePostHandler)
    handlers.load_factory_preferences_post.append(loadPreferencesHandler)


def unregister():
    print("Unregistering to Change Defaults")
    handlers.load_post.remove(loadPostHandler)
    handlers.save_pre.remove(savePreHandler)
    handlers.save_post.remove(savePostHandler)
    handlers.load_factory_preferences_post.remove(loadPreferencesHandler)

    # Message bus unsubscription
    subscriptions.unsubscribe()
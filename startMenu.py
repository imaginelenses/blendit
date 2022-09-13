import sys
import importlib

import bpy

# Local imports implemented to support Blender refreshes
modulesNames = ("newProject", "openProject")
for module in modulesNames:
    if module in sys.modules:
        importlib.reload(sys.modules[module])
    else:
        parent = '.'.join(__name__.split('.')[:-1])
        globals()[module] = importlib.import_module(f"{parent}.{module}")


def drawFileMenu(self, context, layout=None):
    if not layout:
        layout = self.layout
    
    layout.operator(newProject.BlenditNewProject.bl_idname, 
                    text="New Project", icon=newProject.NEW_PROJECT_ICON)
    layout.operator(openProject.BlenditOpenProject.bl_idname, 
                    text="Open Project", icon=openProject.OPEN_PROJECT_ICON)
    layout.separator()


def drawStartMenu(self, context):
    layout = self.layout
    layout.emboss = 'PULLDOWN_MENU'

    split = layout.split()
    
    col1 = split.column()
    col1.label(text="Blendit")

    drawFileMenu(self, context, col1)

    col2 = split.column()
    col2.label(text="Getting Started")

    col2.operator("wm.url_open", text="Blendit Website", 
                  icon='URL').url = "https://imaginelenses.com"
    col2.operator("wm.url_open", text="About Git", 
                  icon='URL').url = "https://git-scm.com/about"

    col2.separator()


def register():
    bpy.types.TOPBAR_MT_file.prepend(drawFileMenu)
    bpy.types.WM_MT_splash.prepend(drawStartMenu)

def unregister():
    bpy.types.TOPBAR_MT_file.remove(drawFileMenu)
    bpy.types.WM_MT_splash.remove(drawStartMenu)
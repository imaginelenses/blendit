import os
import sys
import importlib

import bpy
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty

import pygit2 as git
from pygit2._pygit2 import GitError

# Local imports implemented to support Blender refreshes
modulesNames = ("gitHelpers", "reports", "subscriptions", "appHandlers")
for module in modulesNames:
    if module in sys.modules:
        importlib.reload(sys.modules[module])
    else:
        parent = '.'.join(__name__.split('.')[:-1])
        globals()[module] = importlib.import_module(f"{parent}.{module}")


OPEN_PROJECT_ICON = 'FILE_FOLDER'


class BlenditOpenProject(bpy.types.Operator, ExportHelper):
    """Open a Blendit project."""
    
    bl_label = "Open existing Project"
    bl_idname = "blendit.open_project"
    
    # ExportHelper mixin class uses this
    filename_ext = ""

    filter_glob: StringProperty(
        options={'HIDDEN'},
        # Max internal buffer length, longer would be clamped.
        maxlen=255,
    )
    
    filepath: StringProperty(
        default="/",
        options={'HIDDEN'},
        subtype='DIR_PATH'
    )
    
    filename: StringProperty(
        name="Name",
        description="Name of the project",
        options={'TEXTEDIT_UPDATE'},
        subtype='FILE_NAME'
    )

    # Get global/default git config if .gitconfig or .git/config exists
    try:
        defaultConfig = git.Config.get_global_config()
    except OSError:
        defaultConfig = {}
    
    defaultUser = (defaultConfig["user.name"] 
            if "user.name"  in defaultConfig else "Artist")
            
    defaultEmail = (defaultConfig["user.email"] 
            if "user.email" in defaultConfig else "artist@example.com")
    
    username: StringProperty(
        name="User",
        default=defaultUser,
        description="Username of the artist.",
        options={'TEXTEDIT_UPDATE'},
    )
    
    email: StringProperty(
        name="Email",
        default=defaultEmail,
        description="Email of the artist.",
        options={'TEXTEDIT_UPDATE'},
    )


    def draw(self, context):
        self.username = self.defaultUser
        self.email = self.defaultEmail

        layout = self.layout.box()        
        layout.label(text="Open Project", icon=OPEN_PROJECT_ICON)

        # Get repo user details
        try:
            repo = git.Repository(self.filepath)
            if "user.name" in repo.config and "user.email" in repo.config:
                self.username = repo.config["user.name"]
                self.email = repo.config["user.email"]
        except GitError:
            layout.label(text="Cannot find Blendit project at this location.",
                         icon="ERROR")

        if not self.username.strip():
            layout.label(text="Username cannot be empty.", icon="ERROR")
        layout.prop(self, "username")
        
        if not self.email.strip():
            layout.label(text="Email cannot be empty.", icon="ERROR")
        layout.prop(self, "email")

    
    def execute(self, context):
        filepath = self.filepath.strip()
        filename = filepath.split("/")[-2]
        username = self.username.strip()
        email = self.email.strip()

        if not filepath:
            self.report({'ERROR_INVALID_INPUT'}, "Path cannot be empty.")
            return {'CANCELLED'}

        if not username:
            self.report({'ERROR_INVALID_INPUT'}, "User cannot be empty.")
            return {'CANCELLED'}

        if not email:
            self.report({'ERROR_INVALID_INPUT'}, "Email cannot be empty.")
            return {'CANCELLED'}

        # Configure git repo
        if username != self.defaultUser or email != self.defaultEmail:
            repo = git.Repository(filepath)
            gitHelpers.configUser(repo, username, email)
        
        try:
            regenFile(filepath, filename)
        except FileNotFoundError:
            self.report({'ERROR_INVALID_INPUT'}, "Blendit projecy not found.")
            return {'CANCELLED'}

        return {'FINISHED'}


def regenFile(filepath, filename):
    # Load new blend file
    bpy.ops.wm.read_homefile(app_template="blendit")

    # Unsubscribe message busses
    subscriptions.unsubscribe()

    # Import python file as a module named regen
    regen = importRegen(filepath, filename)

    # Regenerate blend file
    window = bpy.context.window_manager.windows[0]
    area = window.screen.areas[0]
    with bpy.context.temp_override(window=window, area=area):
        # Current area type
        currentType = area.type

        # Change area type to INFO and delete all content                
        area.type = 'VIEW_3D'
        
        regen.executeCommands()

        # Restore area type
        area.type = currentType
    
    # Clear reports
    reports.clearReports()

    # Unregister save pre handler
    bpy.app.handlers.save_pre.remove(appHandlers.savePreHandler)

    # Save .blend file
    bpy.ops.wm.save_mainfile(filepath=os.path.join(filepath, f"{filename}.blend"))

    # Re-register save pre handler
    bpy.app.handlers.save_pre.append(appHandlers.savePreHandler)

    # Re-subscribe to message busses
    subscriptions.subscribe()


def importRegen(filepath, filename):
    """ Import python file as a module named regen """
    
    from importlib import util

    spec = util.spec_from_file_location("regen", os.path.join(filepath, f"{filename}.py"))
    regen = util.module_from_spec(spec)
    
    spec.loader.exec_module(regen)

    return regen

def register():
    bpy.utils.register_class(BlenditOpenProject)

def unregister():
    bpy.utils.unregister_class(BlenditOpenProject)

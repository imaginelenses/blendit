import os
import sys
import importlib

import bpy
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty

from dulwich import porcelain as git
import dulwich.config
import dulwich.server
import dulwich.repo
import dulwich.errors

# Local imports implemented to support Blender refreshes
modulesNames = ["gitHelpers", "reports", "subscriptions"]
for module in modulesNames:
    if module in sys.modules:
        importlib.reload(sys.modules[module])
    else:
        parent = '.'.join(__name__.split('.')[:-1])
        globals()[module] = importlib.import_module(f"{parent}.{module}")


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
        subtype='FILE_NAME'
    )

    # Get global/default git config if .gitconfig or .git/config exists
    defaultConfig = dulwich.config.StackedConfig(dulwich.server.FileSystemBackend()).default()
    try:
        defaultUser = defaultConfig.get("user", "name").decode("utf-8")
    except KeyError:
        defaultUser = "Artist"
    try:
        defaultEmail = defaultConfig.get("user", "email").decode("utf-8")
    except KeyError:
        defaultEmail = "artist@example.com"
    
    username: StringProperty(
        name="User",
        default=defaultUser,
        description="Username of the artist.",
    )
    
    email: StringProperty(
        name="Email",
        default=defaultEmail,
        description="Email of the artist.",
    )


    def draw(self, context):
        self.username = self.defaultUser
        self.email = self.defaultEmail

        layout = self.layout.box()
        
        layout.label(text="Open Project")


        # Get repo user details
        try:
            repo = dulwich.repo.Repo(root=self.filepath, bare=False)
            git.status(repo)
            try:
                config = repo.get_config()
                self.username = config.get("user", "name").decode("utf-8")
                self.email = config.get("user", "email").decode("utf-8")
            except KeyError:
                pass
            repo.close()
        except dulwich.errors.NotGitRepository:
            layout.label(text="Cannot find Blendit project at this location.", icon="ERROR")

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
            repo = dulwich.repo.Repo(filepath)
            gitHelpers.configUser(repo, username, email)
        
        # Unsubscribe message busses
        subscriptions.unsubscribe()

        # Import python file as a module named regen
        regen = importRegen(filepath, filename)

        # Regenerate blend file
        area = context.screen.areas[0]
        with context.temp_override(area=area):
            # Current area type
            currentType = area.type

            # Change area type to INFO and delete all content                
            area.type = 'VIEW_3D'
            
            regen.executeCommands()

            # Restore area type
            area.type = currentType
        
        # Clear reports
        reports.clearReports()

        # Save .blend file
        bpy.ops.wm.save_mainfile(filepath=os.path.join(filepath, f"{filename}.blend"))

        # Re-subscribe to message busses
        subscriptions.subscribe()

        return {'FINISHED'}


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

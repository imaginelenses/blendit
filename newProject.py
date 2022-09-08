import os
import sys
import importlib

import bpy
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty

from dulwich import porcelain as git
import dulwich.config
import dulwich.server

# Local imports implemented to support Blender refreshes
modulesNames = ["gitHelpers"]
for module in modulesNames:
    if module in sys.modules:
        importlib.reload(sys.modules[module])
    else:
        parent = '.'.join(__name__.split('.')[:-1])
        globals()[module] = importlib.import_module(f"{parent}.{module}")


class BlenditNewProject(bpy.types.Operator, ExportHelper):
    """Create a Blendit project."""
    
    bl_label = "Create New Project"
    bl_idname = "blendit.new_project"
    
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
    
    location: StringProperty(
        name="Location",
        description="Location of the project"
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
        description="Username of the artist",
    )
    
    email: StringProperty(
        name="Email",
        default=defaultEmail,
        description="Email of the artist",
    )
    

    def draw(self, context):
        layout = self.layout.box()
        
        layout.label(text="Create New Project")
        
        if not self.filename.strip():
            layout.label(text="Name cannot be empty.", icon="ERROR")
        row = layout.row()
        row.enabled = False
        row.prop(self, "filename")
        
        if not self.filepath.strip():
            layout.label(text="Location cannot be empty.", icon="ERROR")
        self.location = self.filepath
        row = layout.row()
        row.enabled = False
        row.prop(self, "location")
        
        if not self.username.strip():
            layout.label(text="Username cannot be empty.", icon="ERROR")
        layout.prop(self, "username")
        
        if not self.email.strip():
            layout.label(text="Email cannot be empty.", icon="ERROR")
        layout.prop(self, "email")
        
    
    def execute(self, context):
        filename = self.filename.strip()
        filepath = self.filepath.strip()
        username = self.username.strip()
        email = self.email.strip()
        
        if not filename:
            self.report({'ERROR_INVALID_INPUT'}, "Name cannot be empty.")
            return {'CANCELLED'}

        if not filepath:
            self.report({'ERROR_INVALID_INPUT'}, "Path cannot be empty.")
            return {'CANCELLED'}

        if not username:
            self.report({'ERROR_INVALID_INPUT'}, "User cannot be empty.")
            return {'CANCELLED'}

        if not email:
            self.report({'ERROR_INVALID_INPUT'}, "Email cannot be empty.")
            return {'CANCELLED'}
        
        print(f"Dir Path: {filepath}")
        self.report({'DEBUG'}, filepath)
        
        # Make directory
        try:
            os.mkdir(os.path.abspath(filepath))
        except FileNotFoundError:
            self.report({'ERROR_INVALID_INPUT'}, "Invalid directory path.")
            return {'CANCELLED'}
        
        # Make assets directory
        os.mkdir(os.path.join(filepath, "assets"))

        # Make .gitignore file
        gitHelpers.makeGitIgnore(filepath)

        # Init git repo
        repo = git.init(filepath)
        
        # Configure git repo
        if username != self.defaultUser or email != self.defaultEmail:
            gitHelpers.configUser(repo, username, email)

        # Clear info before saving .blend file
        area = context.screen.areas[0]
        with context.temp_override(area=area):
            # Current area type
            currentType = area.type

            # Change area type to INFO and delete all content                
            area.type = 'INFO'
            bpy.ops.info.select_all(action='SELECT')
            bpy.ops.info.report_delete()
            bpy.ops.info.select_all(action='DESELECT')

            # Restore area type
            area.type = currentType

        # Init python file
        with open(os.path.join(filepath, f"{filename}.py"), "w") as file:
            file.write("import bpy\n\n")
            file.write("def executeCommands():\n")
            file.write("\tpass\n")

        # Save .blend file
        bpy.ops.wm.save_mainfile(filepath=os.path.join(filepath, f"{filename}.blend"))

        # Initial commit
        git.commit(repo=repo, message="Initial commit - created project")

        return {'FINISHED'}


def register():
    bpy.utils.register_class(BlenditNewProject)

def unregister():
    bpy.utils.unregister_class(BlenditNewProject)

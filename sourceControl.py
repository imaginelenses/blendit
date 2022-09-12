import os
import sys
import importlib

import bpy
from bpy.types import Operator
from bpy.props import StringProperty

import pygit2 as git
from pygit2._pygit2 import GitError

# Local imports implemented to support Blender refreshes
modulesNames = ("gitHelpers", )
for module in modulesNames:
    if module in sys.modules:
        importlib.reload(sys.modules[module])
    else:
        parent = '.'.join(__name__.split('.')[:-1])
        globals()[module] = importlib.import_module(f"{parent}.{module}")


class BlenditNewBranch(Operator):
    """Create New Branch."""

    bl_label = __doc__
    bl_idname = "blendit.new_branch"

    name: StringProperty(
        name="",
        options={'TEXTEDIT_UPDATE'},
        description="Name of new Branch."
    )

    def invoke(self, context, event):
        filepath = bpy.path.abspath("//")
        filename = bpy.path.basename(bpy.data.filepath).split(".")[0]

        # Save .blend file (Writes commands to Python file and clears reports)
        bpy.ops.wm.save_mainfile(filepath=os.path.join(filepath, f"{filename}.blend"))

        # Get repo
        try:
            repo = git.Repository(filepath)
        except GitError:
            return {'CANCELLED'}

        # Get last commit
        commit = repo[repo.head.target]

        # Create new Branch
        repo.branches.create(self.name.strip(), commit)

        # Clear branch name property
        self.newBranchName = ""
        if context.window_manager.blendit.newBranchName:
            context.window_manager.blendit.newBranchName = ""

        return {'FINISHED'}


class BlenditSwitchToCommit(Operator):
    """Switch to Commit"""

    bl_label = __doc__
    bl_idname = "blendit.switch_to_commit"

    id: StringProperty(
        name="",
        description="ID of commit to switch to"
    )

    def invoke(self, context, event):
        # TODO Switch to commit
        print(f"Switch to commit. {self.id}")
        return {'FINISHED'}


class BlenditCommit(Operator):
    """Commit Changes."""
    
    bl_label = __doc__
    bl_idname = "blendit.commit"

    message: StringProperty(
        name="",
        options={'TEXTEDIT_UPDATE'},
        description="A short description of the changes made"
    )

    def invoke(self, context, event):
        filepath = bpy.path.abspath("//")
        filename = bpy.path.basename(bpy.data.filepath).split(".")[0]

        # Save .blend file (Writes commands to Python file and clears reports)
        bpy.ops.wm.save_mainfile(filepath=os.path.join(filepath, f"{filename}.blend"))

        # Commit changes
        try:
            repo = git.Repository(filepath)
        except GitError:
            return {'CANCELLED'}

        gitHelpers.commit(repo, self.message)

        # Clear commit message property
        self.message = ""
        if context.window_manager.blendit.commitMessage:
            context.window_manager.blendit.commitMessage = ""

        return {'FINISHED'}


classes = (BlenditNewBranch, BlenditSwitchToCommit, BlenditCommit)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
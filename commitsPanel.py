import sys
import importlib
from datetime import datetime

import bpy
from bpy.types import Panel, PropertyGroup, UIList
from bpy.props import (CollectionProperty, EnumProperty, IntProperty,
                       PointerProperty, StringProperty)

import pygit2 as git
from pygit2._pygit2 import GitError

# Local imports implemented to support Blender refreshes
modulesNames = ("gitHelpers", "openProject", "sourceControl")
for module in modulesNames:
    if module in sys.modules:
        importlib.reload(sys.modules[module])
    else:
        parent = '.'.join(__name__.split('.')[:-1])
        globals()[module] = importlib.import_module(f"{parent}.{module}")


BRANCH_ICON = 'IPO_BEZIER'
NEW_BRANCH_ICON = 'ADD'
CLEAR_ICON = 'X'
COMMENT_ICON = 'LAYER_USED'


class BlenditCommitsListItem(PropertyGroup):
    id: StringProperty(description="Unique ID of commit")
    name: StringProperty(description="Name of commiter")
    email: StringProperty(description="Email of commiter")
    date: StringProperty(description="Date of commit")
    message: StringProperty(description="Commit message")


class BlenditPanelData(PropertyGroup):
    def getBranches(self, context):
        filepath = bpy.path.abspath("//")
        try:
            repo = git.Repository(filepath)
        except GitError:
            return []

        branches = repo.listall_branches()
        activeBranch = repo.head.shorthand

        branchList = []
        for index, branch in enumerate(branches):
            if branch == activeBranch:
                index = -1
            branchList.append((branch, branch, f"Branch: '{branch}'", 
                               BRANCH_ICON, index))

        return branchList

    def setActiveBranch(self, context):
        filepath = bpy.path.abspath("//")
        filename = bpy.path.basename(bpy.data.filepath).split(".")[0]

        try:
            repo = git.Repository(filepath)
        except GitError:
            return

        # Ensure value is not active branch
        value = context.window_manager.blendit.branches
        activeBranch = repo.head.shorthand
        if value == activeBranch:
            return

        # Get branch fullname
        branch = repo.lookup_branch(value)
        if not branch:
            return

        # Checkout branch
        ref = repo.lookup_reference(branch.name)
        repo.checkout(ref)

        # Regen file
        openProject.regenFile(filepath, filename)

    branches: EnumProperty(
        name="Branch",
        description="Current Branch",
        items=getBranches,
        default=-1,
        options={'ANIMATABLE'},
        update=setActiveBranch     
    )

    newBranchName: StringProperty(
        name="Name",
        options={'TEXTEDIT_UPDATE'},
        description="Name of new Branch"
    )

    commitMessage: StringProperty(
        name="",
        options={'TEXTEDIT_UPDATE'},
        description="A short description of the changes made"
    )

    commitsList: CollectionProperty(type=BlenditCommitsListItem)

    commitsListIndex: IntProperty(default=0)


class BlenditPanelMixin:
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'


class BlenditPanel(BlenditPanelMixin, Panel):
    bl_idname = "BLENDIT_PT_panel"
    bl_label = "Blendit"

    def draw(self, context):
        pass


class BlenditCommitsList(UIList):
    """List of Commits in project."""

    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        
        split = layout.split(factor=0.825)
        
        col1 = split.column()
        col1.label(text=item.message, icon=COMMENT_ICON)

        # Get last mofied string
        commitTime = datetime.strptime(item.date, gitHelpers.GIT_TIME_FORMAT)
        lastModified = gitHelpers.getLastModifiedStr(commitTime)

        col2 = split.column()
        col2.label(text=lastModified)


class BlenditNewBranchPanel(BlenditPanelMixin, Panel):
    """Add New Branch"""

    bl_idname = "BLENDIT_PT_new_branch_panel"
    bl_label = ""
    bl_options = {'INSTANCED'}

    def draw(self, context):
        layout = self.layout
        
        layout.label(text="New Branch", icon=BRANCH_ICON)

        layout.prop(context.window_manager.blendit, "newBranchName")
        name = context.window_manager.blendit.newBranchName
        
        row = layout.row()
        if not name:
            row.enabled = False

        branch = row.operator(sourceControl.BlenditNewBranch.bl_idname, 
                              text="Create Branch")
        branch.name = name


class BlenditSubPanel1(BlenditPanelMixin, Panel):
    bl_idname = "BLENDIT_PT_sub_panel_1"
    bl_parent_id = BlenditPanel.bl_idname
    bl_label = ""
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw_header(self, context):
        layout = self.layout

        row = layout.row(align=True)
        row.prop(context.window_manager.blendit, "branches")
        
        col = row.column()
        col.scale_x = 0.8
        col.popover(BlenditNewBranchPanel.bl_idname, icon=NEW_BRANCH_ICON)

    def draw(self, context):
        filepath = bpy.path.abspath("//")
        filename = bpy.path.basename(bpy.data.filepath).split(".")[0]

        layout = self.layout
        blendit = context.window_manager.blendit

        # List of Commits
        row = layout.row()
        row.template_list(
            listtype_name="BlenditCommitsList",
            # "" takes the name of the class used to define the UIList 
            list_id="", 
            dataptr=blendit,
            propname="commitsList",
            active_dataptr=blendit,
            active_propname="commitsListIndex",
            item_dyntip_propname="message",
            sort_lock=True,
        )

        if blendit.commitsList and blendit.commitsListIndex != 0:
            try:
                repo = git.Repository(filepath)
            except GitError:
                return

            if bpy.data.is_dirty:
                row = layout.row()
                row.label(text="Unsaved will be lost.", icon='ERROR')

            if repo.status_file(f"{filename}.py") != git.GIT_STATUS_CURRENT:
                row = layout.row()
                row.label(text="Uncommited will be lost.", icon='ERROR')

            row = layout.row()
            switch = row.operator(sourceControl.BlenditRevertToCommit.bl_idname, 
                                  text="Revert to Commit")
            switch.id = blendit.commitsList[blendit.commitsListIndex]["id"]
        
        # Add commits to list
        bpy.app.timers.register(addCommitsToList)


def addCommitsToList():
    """Add commits to list"""

    # Get list
    commitsList = bpy.context.window_manager.blendit.commitsList
    
    # Clear list
    commitsList.clear()

    # Get commits
    filepath = bpy.path.abspath("//")
    try:
        repo = git.Repository(filepath)
    except GitError:
        return

    commits = gitHelpers.getCommits(repo)
    for commit in commits:
        item = commitsList.add()
        item.id = commit["id"]
        item.name = commit["name"]
        item.email = commit["email"]
        item.date = commit["date"]
        item.message = commit["message"]


class BlenditSubPanel2(BlenditPanelMixin, Panel):
    bl_idname = "BLENDIT_PT_sub_panel_2"
    bl_parent_id = BlenditPanel.bl_idname
    bl_label = ""
    bl_options = {'HIDE_HEADER'}

    def draw(self, context):
        layout = self.layout
        layout.alignment = 'CENTER'

        row = layout.row()
        
        col1 = row.column()
        col1.scale_x = 0.5
        col1.label(text="Message: ")
        
        col2 = row.column()
        col2.prop(context.window_manager.blendit, "commitMessage")

        row = layout.row()
        message = context.window_manager.blendit.commitMessage
        if not message:
            row.enabled = False

        commit = row.operator(sourceControl.BlenditCommit.bl_idname, 
                               text="Commit Changes")
        commit.message = message


"""ORDER MATTERS"""
classes = (BlenditCommitsListItem, BlenditPanelData, BlenditPanel, 
           BlenditCommitsList, BlenditNewBranchPanel, BlenditSubPanel1, 
           BlenditSubPanel2)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.WindowManager.blendit = PointerProperty(type=BlenditPanelData)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
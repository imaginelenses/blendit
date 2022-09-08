import os
import sys
import importlib
from datetime import datetime, timezone

import bpy
from bpy.types import Operator, Panel, PropertyGroup, UIList
from bpy.props import CollectionProperty, EnumProperty, IntProperty, PointerProperty, StringProperty

from dulwich import porcelain as git
from dulwich.errors import NotGitRepository

# Local imports implemented to support Blender refreshes
modulesNames = ["gitHelpers"]
for module in modulesNames:
    if module in sys.modules:
        importlib.reload(sys.modules[module])
    else:
        parent = '.'.join(__name__.split('.')[:-1])
        globals()[module] = importlib.import_module(f"{parent}.{module}")


class BlenditCommitsListItem(PropertyGroup):
    commit: StringProperty(description="Unique ID of commit")
    author: StringProperty(description="Author of commit")
    date: StringProperty(description="Date of commit")
    message: StringProperty(description="Commit message")


class BlenditPanelData(PropertyGroup):
    def getBranches(self, context):
        filepath = bpy.path.abspath("//")

        try:
            branches = git.branch_list(filepath)
        except NotGitRepository:
            return []

        activeBranch = git.active_branch(filepath).decode("utf-8")

        branchList = []
        for index, branch in enumerate(branches):
            branch = branch.decode("utf-8")
            if branch == activeBranch:
                index = -1
            branchList.append((branch, branch, f"Branch: '{branch}'", 'IPO_BEZIER', index))

        return branchList

    def setActiveBranch(self, value):
        # TODO change branch 
        pass

    branches: EnumProperty(
        name="Branch",
        description="Current Branch.",
        items=getBranches,
        default=-1,
        options={'ANIMATABLE'},
        update=None,
        get=None,
        set=None       
    )

    commitMessage: StringProperty(
        name="",
        description="A short description of the changes made."
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
        col1.label(text=item.message, icon='LAYER_USED')

        col2 = split.column()

        """
            Get time difference
            Format: Sun Sep 04 2022 19:53:39 +0530
        """
        now = datetime.now(timezone.utc)
        commitTime = datetime.strptime(item.date, "%a %b %d %Y %X %z")
        delta = now - commitTime

        days = delta.days
        if days <= 0:
            hours = delta.seconds // 3600
            if hours <= 0:
                mins = (delta.seconds // 60) % 60
                if mins <= 0:
                    secs = delta.seconds - hours * 3600 - mins * 60
                    if secs <= 0:
                        col2.label(text="now")
                    
                    # Secs
                    elif secs == 1:
                        col2.label(text=f"{mins} sec")
                    else:
                        col2.label(text=f"{mins} sec")

                # Mins
                elif mins == 1:
                    col2.label(text=f"{mins} min")
                else:
                    col2.label(text=f"{mins} mins")

            # Hours
            elif hours == 1:
                col2.label(text=f"{hours} hr")
            else:
                col2.label(text=f"{hours} hrs")
        
        # Days
        elif days == 1:
            col2.label(text=f"{days} day")
        else:
            col2.label(text=f"{days} days")


class BlenditSubPanel1(BlenditPanelMixin, Panel):
    bl_idname = "BLENDIT_PT_sub_panel_1"
    bl_parent_id = BlenditPanel.bl_idname
    bl_label = ""
    bl_options = {'HEADER_LAYOUT_EXPAND', 'DEFAULT_CLOSED'}
    
    def draw_header(self, context):
        layout = self.layout
        layout.alignment = 'LEFT'
        layout.prop(context.scene.blendit, "branches")
 
    def draw(self, context):
        layout = self.layout
        blendit = context.scene.blendit

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
            row = layout.row()
            # TODO Switch to Commit
            row.label(text="TODO Switch to Commit")

        # Add commits to list
        bpy.app.timers.register(addCommitsToList)


def addCommitsToList():
    commitsList = bpy.context.scene.blendit.commitsList
    
    # Clear list
    commitsList.clear()

    # Get commits
    filepath = bpy.path.abspath("//")
    commits = gitHelpers.getCommits(filepath)
    for commit in commits:
        item = commitsList.add()
        item.commit = commit["commit"]
        item.author = commit["author"]
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
        col2.prop(context.scene.blendit, "commitMessage")

        row = layout.row()
        message = context.scene.blendit.commitMessage
        if not message:
            row.enabled = False

        col1 = row.column()
        commit = col1.operator(BlenditCommit.bl_idname, text="Commit Changes")
        commit.message = message

        col2 = row.column()
        col2.operator(BlenditCancelCommit.bl_idname, text="Cancel")


class BlenditCommit(Operator):
    """Commit changes."""
    
    bl_label = "Create New Project"
    bl_idname = "blendit.commit"

    message: StringProperty(
        name="",
        default="Message",
        description="A short description of the changes made"
    )

    def invoke(self, context, event):
        filepath = bpy.path.abspath("//")
        filename = bpy.path.basename(bpy.data.filepath).split(".")[0]

        # Save .blend file (Writes commands to Python file and clears reports)
        bpy.ops.wm.save_mainfile(filepath=os.path.join(filepath, f"{filename}.blend"))
        print(self.message)
        return {'FINISHED'}


class BlenditCancelCommit(Operator):
    """Clear Commit message."""

    bl_label = "Create New Project"
    bl_idname = "blendit.cancel_commit"

    def invoke(self, context, event):
        context.scene.blendit.commitMessage = ""
        return {'FINISHED'}


classes = (BlenditCommitsListItem, BlenditPanelData, BlenditPanel, BlenditCommitsList, 
           BlenditSubPanel1, BlenditSubPanel2, BlenditCommit, BlenditCancelCommit)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.blendit = PointerProperty(type=BlenditPanelData)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
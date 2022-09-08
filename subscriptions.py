import os
import functools

import bpy


class BlenditSubscriber:
    """Subscriber to different event publishers"""
    
    def __repr__(self):
        return self.__doc__
        

blenditSubscriber = BlenditSubscriber()


def writeToFile(lines):
    """Writes list of lines to associated python file"""

    filepath = bpy.path.abspath("//")
    filename = bpy.path.basename(bpy.data.filepath).split(".")[0]

    # Save .blend file (Writes commands to Python file and clears reports)
    bpy.ops.wm.save_mainfile(filepath=os.path.join(filepath, f"{filename}.blend"))

    # Append lines to Python file
    with open(os.path.join(filepath, f"{filename}.py"), "a") as file:
        for line in lines:
            file.write(f"\t{line}\n")


def activeObjectCallback():
    """Called when active object changes"""

    # Apply all transforms
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    objectsToSelect  = bpy.context.view_layer.objects.selected.keys()
    objectToActivate = bpy.context.view_layer.objects.active.__repr__()
    lines = [
        "[obj.select_set(False) for obj in bpy.context.view_layer.objects.selected.values()]",
        f"[bpy.context.view_layer.objects.get(obj).select_set(True) for obj in {objectsToSelect}]",
        f"bpy.context.view_layer.objects.active = {objectToActivate}"
        "bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)"
    ]
    bpy.app.timers.register(functools.partial(writeToFile, lines))


def subscribe():
    """Subscribes to different event publishers"""

    # Active Object
    bpy.msgbus.subscribe_rna(
        key=(bpy.types.LayerObjects, "active"),
        owner=blenditSubscriber,
        args=(),
        notify=activeObjectCallback,
        options={'PERSISTENT'}
    )


def unsubscribe():
    """Unsubscribes to all event publishers"""
    bpy.msgbus.clear_by_owner(blenditSubscriber)

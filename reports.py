import bpy


def getReports():
    """Returns a list of reports as seen in the Info area"""
    
    area = bpy.context.screen.areas[0]
    with bpy.context.temp_override(area=area):
        # Current area type
        currentType = area.type

        # Copy all info to clipboard
        area.type = 'INFO'
        bpy.ops.info.select_all(action='SELECT')
        bpy.ops.info.report_copy()
        bpy.ops.info.select_all(action='DESELECT')

        # Restore context
        area.type = currentType
        
    # Transfer from clipboard
    reports = bpy.context.window_manager.clipboard
    return reports.splitlines()


def ignoreReport(report):
    """Returns True if report should be ignored, else False"""

    ignoreReportList = [
        "bpy.context.space_data.",
        "bpy.data.window_managers["
    ]
    for s in ignoreReportList:
        if report.startswith(s):
            return True
    return False


def getCommands():
    """Extract executable commands from reports"""

    reports = getReports()
    commands = []
    for i in range(len(reports)):
        report = reports[i]
        if (report.startswith("Deleted") and
            reports[i - 1] != "bpy.ops.object.delete(use_global=True, confirm=False)"):
            commands.append("bpy.ops.object.delete(use_global=False, confirm=False)")
            continue
        
        if not report.startswith("bpy."):
            continue
        
        if ignoreReport(report):
            continue
        
        commands.append(report)
        
        if report == "bpy.ops.material.new()":
            commands.append("bpy.context.object.active_material = bpy.data.materials[-1]")

    return commands


def clearReports():
    """Clears reports seen in the Info area"""

    area = bpy.context.screen.areas[0]
    with bpy.context.temp_override(area=area):
        # Current area type
        currentType = area.type

        # Clear all reports
        area.type = 'INFO'
        bpy.ops.info.select_all(action='SELECT')
        bpy.ops.info.report_delete()

        # Restore context
        area.type = currentType
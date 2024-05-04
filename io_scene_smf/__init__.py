 # ##### BEGIN LICENSE BLOCK #####
#
# This program is licensed under Creative Commons BY-NC-SA:
# https://creativecommons.org/licenses/by-nc-sa/3.0/
#
# Created by Dummiesman, 2022
#
# ##### END LICENSE BLOCK #####

bl_info = {
    "name": "4x4 Evolution SMF Format",
    "author": "Dummiesman",
    "version": (1, 0, 1),
    "blender": (3, 1, 0),
    "location": "File > Import-Export",
    "description": "Import-Export SMF files",
    "warning": "",
    "doc_url": "https://github.com/Dummiesman/SMFImportExport/",
    "tracker_url": "https://github.com/Dummiesman/SMFImportExport/",
    "support": 'COMMUNITY',
    "category": "Import-Export"}

import bpy
import textwrap

import io_scene_smf.import_tex as import_tex

from bpy.props import (
        BoolProperty,
        EnumProperty,
        FloatProperty,
        StringProperty,
        CollectionProperty,
        )
from bpy_extras.io_utils import (
        ImportHelper,
        ExportHelper,
        )

class ImportSMF(bpy.types.Operator, ImportHelper):
    """Import from SMF file format (.smf)"""
    bl_idname = "import_scene.smf"
    bl_label = 'Import SMF Model'
    bl_options = {'UNDO'}

    filename_ext = ".smf"
    filter_glob: StringProperty(default="*.smf", options={'HIDDEN'})

    def execute(self, context):
        from . import import_smf
        keywords = self.as_keywords(ignore=("axis_forward",
                                            "axis_up",
                                            "filter_glob",
                                            "check_existing",
                                            ))

        return import_smf.load(self, context, **keywords)


class ExportSMF(bpy.types.Operator, ExportHelper):
    """Export to SMF file format (.smf)"""
    bl_idname = "export_scene.smf"
    bl_label = 'Export SMF Model'

    filename_ext = ".smf"
    filter_glob: StringProperty(
        default="*.smf",
        options={'HIDDEN'},
    )

    apply_modifiers: BoolProperty(
        name="Apply Modifiers",
        default=True
    )

    enable_switching: BoolProperty(
        name="Enable LOD Switching",
        description="Enable LOD switching (Only used on scenes with OPAQUEL or TRANSL)",
        default=False
    )

    switch_height: FloatProperty(
        name = "Switch Height",
        description="The on-screen height at which the object will switch to low LOD (Only used on scenes with OPAQUEL or TRANSL)",
        default = 50.0,
        min = 0
    )

    use_v1_materials: BoolProperty(
        name="Use v1 Materials",
        description="Export v1 materials, using TIF textures and bump textures",
        default=False
    )

    def execute(self, context):
        from . import export_smf

        keywords = self.as_keywords(ignore=("axis_forward",
                                            "axis_up",
                                            "filter_glob",
                                            "check_existing",
                                            ))

        return export_smf.save(self, context, **keywords)


# Add to a menu
def menu_func_export(self, context):
    self.layout.operator(ExportSMF.bl_idname, text="4x4 Evolution (.smf)")

def menu_func_import(self, context):
    self.layout.operator(ImportSMF.bl_idname, text="4x4 Evolution (.smf)")

# Register factories
classes = (
    ImportSMF,
    ExportSMF
)

def register():
    import_tex.register()

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    import_tex.unregister()

    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()

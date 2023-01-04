 # ##### BEGIN LICENSE BLOCK #####
#
# This program is licensed under Creative Commons BY-NC-SA:
# https://creativecommons.org/licenses/by-nc-sa/3.0/
#
# Created by Dummiesman, 2022
#
# ##### END LICENSE BLOCK #####

import bpy
import math
import os

from bpy.props import StringProperty
from bpy_extras.io_utils import ImportHelper

class ImportEVOTexture(bpy.types.Operator, ImportHelper):
    """Import image from Terminal Reality RAW/OPA/ACT file format"""
    bl_idname = "import_texture.evo_tex"
    bl_label = 'Import RAW Image'
    bl_options = {'UNDO'}

    filename_ext = ".raw"
    filter_glob: StringProperty(default="*.raw", options={'HIDDEN'})

    def execute(self, context):
        keywords = self.as_keywords(ignore=("axis_forward",
                                            "axis_up",
                                            "filter_glob",
                                            "check_existing",
                                            ))
        filepath = self.properties.filepath
        image_name = bpy.path.display_name_from_filepath(self.properties.filepath)

        image_data = None
        opacity_data = None
        image_colors = None

        # read file data
        with open(filepath, mode='rb') as file:
            image_data = file.read()

        if len(image_data) % 2 != 0:
            raise Exception("Cannot determine the size of this RAW file.")

        # read additional file data
        opacity_path = os.path.splitext(filepath)[0] + ".OPA"
        colortable_path = os.path.splitext(filepath)[0] + ".ACT"

        if not os.path.exists(colortable_path):
            raise Exception("Missing ACT file.")

        with open(colortable_path, mode='rb') as file:
            image_colors = file.read()

        if os.path.exists(opacity_path):
            with open(opacity_path, mode='rb') as file:
                opacity_data = file.read()
            if len(opacity_data) != len(image_data):
                print("WARN: opacity_data is not the same size as image_data, it will be discarded.")
                opacity_data = None

        # deal with file data
        image_size = int(math.sqrt(len(image_data)))

        im = bpy.data.images.new(name=image_name, width=image_size, height=image_size, alpha=(opacity_data is not None))
        pixels = list(im.pixels)

        for y in range(image_size):
            for x in range(image_size):
                flipped_y = image_size - y - 1

                b_pixel_index = 4 * ((flipped_y * image_size) + x)
                pixel_index = (y * image_size) + x

                color_index = image_data[pixel_index]
                pixel_color = (image_colors[(color_index * 3):((color_index * 3) + 3)])
                pixel_alpha = 255 if opacity_data is None else opacity_data[pixel_index]

                pixels[b_pixel_index] = pixel_color[0] / 255.0
                pixels[b_pixel_index+1] = pixel_color[1] / 255.0
                pixels[b_pixel_index+2] = pixel_color[2] / 255.0
                pixels[b_pixel_index+3] = pixel_alpha / 255.0

        im.pixels = pixels[:]
        im.update()

        return {'FINISHED'}

class ImportEVOTextureMenu(bpy.types.Menu):
    bl_idname = "TERMINALREALITY_MT_import_tex_menu"
    bl_label = "Terminal Reality Tools"

    def draw(self, context):
        layout = self.layout
        layout.operator("import_texture.evo_tex")

    def menu_draw(self, context):
        self.layout.menu("TERMINALREALITY_MT_import_tex_menu")


def register():
    bpy.utils.register_class(ImportEVOTextureMenu)
    bpy.utils.register_class(ImportEVOTexture)
    bpy.types.TOPBAR_MT_editor_menus.append(ImportEVOTextureMenu.menu_draw)


def unregister():
    bpy.types.TOPBAR_MT_editor_menus.remove(ImportEVOTextureMenu.menu_draw)
    bpy.utils.unregister_class(ImportEVOTexture)
    bpy.utils.unregister_class(ImportEVOTextureMenu)
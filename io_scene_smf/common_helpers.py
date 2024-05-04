 # ##### BEGIN LICENSE BLOCK #####
#
# This program is licensed under Creative Commons BY-NC-SA:
# https://creativecommons.org/licenses/by-nc-sa/3.0/
#
# Created by Dummiesman, 2022
#
# ##### END LICENSE BLOCK #####

import bpy
import os
from bpy_extras import  node_shader_utils

def get_image_file(image):
    return os.path.splitext(image.name)[0]

def get_material_parameters(mat):
    mat_wrap = node_shader_utils.PrincipledBSDFWrapper(mat)
    mat_reflective = mat_wrap.specular > 0.01
    mat_transparent = mat.blend_method != 'OPAQUE'
    
    texture = mat_wrap.base_color_texture
    bump_texture = mat_wrap.normalmap_texture

    mat_texture_name = None
    mat_normal_name = None
    if texture is not None and texture.image is not None:
        mat_texture_name = get_image_file(texture.image)
    if bump_texture is not None and bump_texture.image is not None:
        mat_normal_name = get_image_file(bump_texture.image)

    return (mat_texture_name, mat_normal_name, mat_reflective, mat_transparent)


def find_existing_material(texture_name, bump_texture_name, reflective, transparent):
    for mat in bpy.data.materials:
        mat_texture_name, mat_bump_texture_name, mat_reflective, mat_transparent = get_material_parameters(mat)
        if mat_texture_name == texture_name and mat_bump_texture_name == bump_texture_name\
        and mat_reflective == reflective and mat_transparent == transparent:
            return mat

    return None


def create_material(texture_name, bump_texture_name, art_path, reflective = False, transparent = False):
    # create a new material
    # find existing texture(s)
    main_texture_image = None
    bump_texture_image = None

    main_image_path = None
    bump_image_path = None

    if bump_texture_name is not None:
        main_image_path = os.path.join(art_path, texture_name + ".TIF")
        bump_image_path = os.path.join(art_path, bump_texture_name + ".TIF")
        main_texture_image = bpy.data.images.get(texture_name)
        bump_texture_image = bpy.data.images.get(bump_texture_name)
    else:
        main_image_path = os.path.join(art_path, texture_name + ".RAW")
        main_texture_image = bpy.data.images.get(texture_name)

    # load image(s) if they're not already loaded
    if main_texture_image is None and os.path.exists(main_image_path):
        if main_image_path.endswith(".TIF"):
            main_texture_image = bpy.data.images.load(main_image_path)
            if main_texture_image is not None:
                main_texture_image.name = os.path.splitext(main_texture_image.name)[0]
        else:
            bpy.ops.import_texture.evo_tex(filepath=main_image_path)
            main_texture_image = bpy.data.images.get(texture_name)
    if bump_texture_image is None and bump_image_path is not None and os.path.exists(bump_image_path):
        bump_texture_image = bpy.data.images.load(bump_image_path)
        if bump_texture_image is not None:
            bump_texture_image.name = os.path.splitext(bump_texture_image.name)[0]
            bump_texture_image.colorspace_settings.name = 'Non-Color'

    # setup material
    mtl = bpy.data.materials.new(name=texture_name)
    mat_wrap = node_shader_utils.PrincipledBSDFWrapper(mtl, is_readonly=False) 

    mtl.specular_intensity = 0.1 if reflective else 0
    mtl.use_nodes = True
    mtl.use_backface_culling = True
    mtl.specular_intensity = 0.5 if reflective else 0
    mtl.blend_method = 'BLEND' if transparent else 'OPAQUE'

    mat_wrap.specular = 0.1 if reflective else 0
    mat_wrap.roughness = 0

    # add texture(s)
    if main_texture_image is not None:
        mat_wrap.base_color_texture.image = main_texture_image
        mat_wrap.alpha_texture.image = main_texture_image
    if bump_texture_image is not None:
        mat_wrap.normalmap_texture.image = bump_texture_image

    return mtl

def get_or_create_material(texture_name, bump_texture_name, art_path, reflective = False, transparent = False):
    # look for an existing material first
    existing_material = find_existing_material(texture_name, bump_texture_name, reflective, transparent)
    if existing_material is not None:
        return existing_material

    return create_material(texture_name, bump_texture_name, art_path, reflective, transparent)
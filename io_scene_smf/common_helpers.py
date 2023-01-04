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

def get_image_file(image):
    return os.path.splitext(image.name)[0]

def get_material_parameters(mat):
    # data
    mat_texture_name = None
    mat_normal_name = None
    mat_reflective = False
    mat_transparent = False

    # get principled node
    root_node = None
    if mat.node_tree is not None:
        for node in mat.node_tree.nodes:
            if node.type == "BSDF_PRINCIPLED":
                root_node = node
                break

    if root_node is not None:
        # grab image name
        diffuse_input = root_node.inputs["Base Color"]
        if len(diffuse_input.links) > 0:
            color_input_node = diffuse_input.links[0].from_node
            if color_input_node.type == "TEX_IMAGE" and color_input_node.image is not None:
                mat_texture_name = get_image_file(color_input_node.image)

        #  grab normal map name
        normal_input = root_node.inputs["Normal"]
        if len(normal_input.links) > 0:
            normal_input_node = normal_input.links[0].from_node
            if normal_input_node.type == "NORMAL_MAP":
                normal_color_input = normal_input_node.inputs["Color"]
                if len(normal_color_input.links) > 0:
                    normal_color_input_node = normal_color_input.links[0].from_node
                    if normal_color_input_node.type == "TEX_IMAGE" and normal_color_input_node.image is not None:
                        mat_normal_name = get_image_file(normal_color_input_node.image)


        # grab reflectivity and transparency parameters
        mat_reflective = root_node.inputs["Specular"].default_value > 0.01
        mat_transparent = mat.blend_method != 'OPAQUE'

    return (mat_texture_name, mat_normal_name, mat_reflective, mat_transparent)


def find_existing_material(texture_name, bump_texture_name, reflective, transparent):
    for mat in bpy.data.materials:
        mat_texture_name, mat_bump_texture_name, mat_reflective, mat_transparent = get_material_parameters(mat)
        if mat_texture_name == texture_name and mat_bump_texture_name == bump_texture_name\
        and mat_reflective == reflective and mat_transparent == transparent:
            return mat

    return None


def get_material(texture_name, bump_texture_name, art_path, reflective = False, transparent = False):
    # look for an existing material first
    existing_material = find_existing_material(texture_name, bump_texture_name, reflective, transparent)
    if existing_material is not None:
        return existing_material

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
    mtl.specular_intensity = 0.1 if reflective else 0

    mtl.use_nodes = True
    mtl.use_backface_culling = True
    mtl.specular_intensity = 0.5 if reflective else 0

    bsdf = mtl.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Specular'].default_value = 0.1 if reflective else 0
    bsdf.inputs['Roughness'].default_value = 0

    mtl.blend_method = 'BLEND' if transparent else 'OPAQUE'

    # add texture(s)
    tex_image_node = None
    if main_texture_image is not None:
        tex_image_node = mtl.node_tree.nodes.new('ShaderNodeTexImage')
        tex_image_node.image = main_texture_image
        mtl.node_tree.links.new(bsdf.inputs['Base Color'], tex_image_node.outputs['Color'])
        mtl.node_tree.links.new(bsdf.inputs['Alpha'], tex_image_node.outputs['Alpha'])
    if bump_texture_image is not None:
        tex_image_node = mtl.node_tree.nodes.new('ShaderNodeTexImage')
        normal_map_node = mtl.node_tree.nodes.new('ShaderNodeNormalMap')
        tex_image_node.image = bump_texture_image
        mtl.node_tree.links.new(normal_map_node.inputs['Color'], tex_image_node.outputs['Color'])
        mtl.node_tree.links.new(bsdf.inputs['Normal'], normal_map_node.outputs['Normal'])

    return mtl
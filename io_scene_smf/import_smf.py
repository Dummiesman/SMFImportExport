 # ##### BEGIN LICENSE BLOCK #####
#
# This program is licensed under Creative Commons BY-NC-SA:
# https://creativecommons.org/licenses/by-nc-sa/3.0/
#
# Created by Dummiesman, 2022
#
# ##### END LICENSE BLOCK #####

import bpy, bmesh
import os, time

import io_scene_smf.common_helpers as helper

######################################################
# IMPORT MAIN FILES
######################################################
def read_line(file):
    line = file.readline()
    if line is not None:
        return line[:-1]
    else:
        return None

def read_smf_file(file, filepath):
    scn = bpy.context.scene

    # get art folder path for texture loading
    game_dir = os.path.abspath(os.path.join(os.path.dirname(filepath), ".."))
    art_dir = os.path.join(game_dir, "ART")

    # read header
    header = read_line(file)
    if header != "C3DModel":
        raise Exception(f"Incorrect header. Expected 'C3DModel', got '{header}'")

    version = int(read_line(file))
    object_count = int(read_line(file))
    if version >= 4:
        lod_info = read_line(file)

    for x in range(object_count):
        # read object
        object_name = read_line(file)
        object_visible = True
        if version >= 2:
            object_visible = bool(int(read_line(file)))
        obj_version = int(read_line(file))

        if obj_version != 1:
            raise Exception(f"Incorrect object version. Expected 1, got {obj_version}")

        # add a mesh and link it to the scene
        me = bpy.data.meshes.new(f"{object_name}Mesh")
        ob = bpy.data.objects.new(object_name, me)

        bm = bmesh.new()
        bm.from_mesh(me)
        uv_layer = bm.loops.layers.uv.new()

        scn.collection.objects.link(ob)
        ob.hide_set(not object_visible)

        # read mesh data
        obj_info = [int(v) for v in read_line(file).split(",")]

        material_bump_name = None
        material_name = None
        material_info_line = read_line(file)

        if material_info_line == "v1":
            # bump material
            material_info_line = read_line(file)
            material_bump_name = read_line(file)[1:-1].split(".")[0]

        material_info = material_info_line.split(",")
        material_name = material_info[5].split(".")[0]
        material_is_transparent = material_info[3] == "1"
        material_is_reflective = material_info[4] == "1"

        num_verts = obj_info[0]
        num_frames = obj_info[1]
        num_faces = obj_info[2]

        # for merging vertices with the same position and normal
        vertex_remap_table = {}
        vertex_remap_index_table = {}
        remapped_vertices = []
        uvs = []

        # read verts
        for y in range(num_verts):
            vert_data = [float(v) for v in read_line(file).split(",")]
            vx, vy, vz, nx, ny, nz, u, v = vert_data
            uvs.append((u, 1 - v))

            # remap vertex
            co = (vx * -1.0, vz * -1.0, vy)
            normal = (nx * -1.0, nz * -1.0, ny)

            pos_hash = str(co)
            nrm_hash = str(normal)
            vertex_hash = pos_hash + "|" + nrm_hash

            if vertex_hash in vertex_remap_table:
                bmvert = remapped_vertices[vertex_remap_table[vertex_hash]]
                vertex_remap_index_table[y] = vertex_remap_table[vertex_hash]
                remapped_vertices.append(bmvert)
            else:
                # add vertex to mesh
                bmvert = bm.verts.new(co)
                bmvert.normal = normal

                # add to tables
                vertex_remap_table[vertex_hash] = len(remapped_vertices)
                vertex_remap_index_table[y] = len(remapped_vertices)
                remapped_vertices.append(bmvert)

        # skip frames for now
        for y in range(max(num_frames - 1, 0)):
            for yy in range(num_verts):
                file.readline()

        # read faces
        for y in range(num_faces):
            face_indices = [int(v) for v in read_line(file).split(",")]
            face_indices.reverse()

            try:
                face = bm.faces.new([remapped_vertices[idx] for idx in face_indices])
                face.smooth = True

                # set uvs and colors
                face.loops[0][uv_layer].uv = uvs[face_indices[0]]
                face.loops[1][uv_layer].uv = uvs[face_indices[1]]
                face.loops[2][uv_layer].uv = uvs[face_indices[2]]

            except Exception as e:
                print(str(e))

        # create the material
        mtl = helper.get_material(material_name, material_bump_name, art_dir, material_is_reflective, material_is_transparent)
        ob.data.materials.append(mtl)

        # clean up
        bm.to_mesh(me)
        bm.free()


######################################################
# IMPORT
######################################################
def load_smf(filepath,
             context):

    print("importing SMF: %r..." % (filepath))

    if bpy.ops.object.select_all.poll():
        bpy.ops.object.select_all(action='DESELECT')

    time1 = time.perf_counter()
    file = open(filepath, 'r')

    # start reading our smf file
    read_smf_file(file, filepath)

    print(" done in %.4f sec." % (time.perf_counter() - time1))
    file.close()


def load(operator,
         context,
         filepath="",
         ):

    load_smf(filepath,
             context,
             )

    return {'FINISHED'}

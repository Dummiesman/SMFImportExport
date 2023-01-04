 # ##### BEGIN LICENSE BLOCK #####
#
# This program is licensed under Creative Commons BY-NC-SA:
# https://creativecommons.org/licenses/by-nc-sa/3.0/
#
# Created by Dummiesman, 2022
#
# ##### END LICENSE BLOCK #####

import time
import bpy, bmesh

import io_scene_smf.common_helpers as helper

######################################################
# EXPORT MAIN FILES
######################################################
def export_smf(file, apply_modifiers, enable_switching, switch_height, use_v1_materials):
    export_objects = [ob for ob in bpy.context.scene.objects if ob.type == 'MESH']

    file.write("C3DModel\n")
    file.write("4\n") # version
    file.write(f"{len(export_objects)}\n")
    file.write(f"{int(enable_switching)},{switch_height:.6f}\n")

    for ob in export_objects:
        # write header
        file.write(f"{ob.name}\n")
        file.write(f"{int(not ob.hide_get())}\n")
        file.write("1\n") # object version

        # create temp mesh
        temp_mesh = None
        if apply_modifiers:
            dg = bpy.context.evaluated_depsgraph_get()
            eval_obj = ob.evaluated_get(dg)
            temp_mesh = eval_obj.to_mesh()
        else:
            temp_mesh = ob.to_mesh()

        # get bmesh
        bm = bmesh.new()
        bm.from_mesh(temp_mesh)
        bm.verts.ensure_lookup_table()
        bm_tris = bm.calc_loop_triangles()
        uv_layer = bm.loops.layers.uv.verify()

        # translate vertices to world
        for vert in bm.verts:
            vert.co = ob.matrix_world @ vert.co

        # calculate split geometry
        verts = []
        loop_to_vert_map = {}
        loop_index_to_vert_map = {}

        for tri_loops in bm_tris:
            for loop in tri_loops:
                # prepare our hash entry
                uv_hash =  str(loop[uv_layer].uv)
                pos_hash = str(loop.vert.co)
                nrm_hash = str(loop.vert.normal)

                loop_hash = uv_hash + "|" + pos_hash + "|" + nrm_hash

                # add to the table
                if not loop_hash in loop_to_vert_map:
                    vert_tup = (loop.vert.co.x * -1.0, loop.vert.co.z, loop.vert.co.y * -1.0,
                                loop.vert.normal.x, loop.vert.normal.z * -1.0, loop.vert.normal.y,
                                loop[uv_layer].uv[0], 1.0 - loop[uv_layer].uv[1])

                    loop_to_vert_map[loop_hash] = len(verts)
                    loop_index_to_vert_map[loop.index] = len(verts)

                    verts.append(vert_tup)
                else:
                    loop_index_to_vert_map[loop.index] = loop_to_vert_map[loop_hash]

        # write geometry info
        num_verts = len(verts)
        num_faces = len(bm_tris)
        num_frames = 1

        file.write(f"{num_verts},{num_frames},{num_faces},0\n")

        # write material info
        mat_texture_name = None
        mat_bump_texture_name = None
        mat_reflective = False
        mat_transparent = False
        texture_extension = ".TIF" if use_v1_materials else ".RAW"

        if len(ob.data.materials) > 0:
            mat_texture_name, mat_bump_texture_name, mat_reflective, mat_transparent = helper.get_material_parameters(ob.data.materials[0])

        mat_texture_name = f"NULL.{texture_extension}" if mat_texture_name is None else mat_texture_name + texture_extension
        mat_bump_texture_name = "" if mat_bump_texture_name is None else mat_bump_texture_name + texture_extension

        if use_v1_materials:
            file.write("v1\n")
        file.write(f"1.000000,1.000000,32.000000,{int(mat_transparent)},{int(mat_reflective)},{mat_texture_name}\n")
        if use_v1_materials:
            file.write(f"\"{mat_bump_texture_name}\"\n")

        # write geometry
        for x in range(num_verts):
            x, y, z, nx, ny, nz, u, v = verts[x]
            file.write(f"{x:.6f},{y:.6f},{z:.6f},{nx:.6f},{ny:.6f},{nz:.6f},{u:.6f},{v:.6f}\n")
        for x in range(num_faces):
            face = bm_tris[x]
            indices = (loop_index_to_vert_map[face[2].index], loop_index_to_vert_map[face[1].index], loop_index_to_vert_map[face[0].index])
            file.write(f"{indices[0]},{indices[1]},{indices[2]}\n")

        # clean up
        bm.free()

    # finish off
    file.close()


######################################################
# EXPORT
######################################################
def save(operator,
         context,
         filepath="",
         apply_modifiers=False,
         enable_switching=False,
         switch_height=50.0,
         use_v1_materials = False,
         ):

    print("exporting SMF: %r..." % (filepath))
    time1 = time.perf_counter()

    # write smf
    file = open(filepath, 'w')
    export_smf(file, apply_modifiers, enable_switching, switch_height, use_v1_materials)

    # smf export complete
    print(" done in %.4f sec." % (time.perf_counter() - time1))

    return {'FINISHED'}

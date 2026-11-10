"""
Ateneo+ 3D Doctor Character Builder (Blender 5.2 Z-Up -> Y-Up GLTF Architecture)
Construye el avatar anatómico tridimensional del médico con bata clínica, estetoscopio,
credencial institucional y pivotes cinemáticos para animación procedural en Three.js.
"""

import os
import math
from pathlib import Path
import bpy


def clean_blender_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    if bpy.context.scene.collection.objects:
        for obj in list(bpy.context.scene.collection.objects):
            bpy.data.objects.remove(obj, do_unlink=True)


def make_material(name, rgb, metallic=0.0, roughness=0.5, emission=None, emission_strength=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        if "Base Color" in bsdf.inputs:
            bsdf.inputs["Base Color"].default_value = (rgb[0], rgb[1], rgb[2], 1.0)
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = metallic
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = roughness
        if emission is not None and emission_strength > 0:
            esock = "Emission Color" if "Emission Color" in bsdf.inputs else "Emission"
            if esock in bsdf.inputs:
                bsdf.inputs[esock].default_value = (emission[0], emission[1], emission[2], 1.0)
            if "Emission Strength" in bsdf.inputs:
                bsdf.inputs["Emission Strength"].default_value = emission_strength
    return mat


def parent_to(child, parent):
    if not parent:
        return
    child.parent = parent
    bpy.context.view_layer.update()
    child.matrix_parent_inverse = parent.matrix_world.inverted()


def add_empty(name, loc_xyz, parent=None):
    empty = bpy.data.objects.new(name, None)
    empty.empty_display_type = 'ARROWS'
    empty.empty_display_size = 0.15
    empty.location = loc_xyz
    bpy.context.collection.objects.link(empty)
    if parent:
        parent_to(empty, parent)
    return empty


def add_box(name, loc_xyz, dim_xyz, mat, bevel_width=0.008, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc_xyz)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (dim_xyz[0], dim_xyz[1], dim_xyz[2])
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if mat:
        obj.data.materials.append(mat)
    if bevel_width > 0:
        bev = obj.modifiers.new(name="Bevel", type='BEVEL')
        bev.width = bevel_width
        bev.segments = 2
        bev.limit_method = 'ANGLE'
    if parent:
        parent_to(obj, parent)
    return obj


def add_cylinder(name, loc_xyz, radius, length, mat, rot_xyz=(0.0, 0.0, 0.0), vertices=16, parent=None):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices,
        radius=radius,
        depth=length,
        location=loc_xyz,
        rotation=rot_xyz
    )
    obj = bpy.context.active_object
    obj.name = name
    if mat:
        obj.data.materials.append(mat)
    bpy.ops.object.shade_smooth()
    if parent:
        parent_to(obj, parent)
    return obj


def add_sphere(name, loc_xyz, radius, scale_xyz, mat, parent=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=14, radius=radius, location=loc_xyz)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale_xyz
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if mat:
        obj.data.materials.append(mat)
    bpy.ops.object.shade_smooth()
    if parent:
        parent_to(obj, parent)
    return obj


def build_doctor_character(output_glb: Path):
    clean_blender_scene()

    # Materiales clínicos de alta fidelidad
    mats = {
        "coat": make_material("Mat_DoctorCoat", (0.97, 0.98, 1.00), metallic=0.02, roughness=0.38),
        "scrubs": make_material("Mat_DoctorScrubs", (0.05, 0.48, 0.75), metallic=0.0, roughness=0.68),
        "pants": make_material("Mat_DoctorPants", (0.10, 0.14, 0.22), metallic=0.0, roughness=0.78),
        "shoes": make_material("Mat_DoctorShoes", (0.07, 0.08, 0.10), metallic=0.08, roughness=0.55),
        "sole": make_material("Mat_ShoeSole", (0.92, 0.94, 0.96), metallic=0.0, roughness=0.45),
        "skin": make_material("Mat_DoctorSkin", (0.92, 0.77, 0.68), metallic=0.0, roughness=0.56),
        "hair": make_material("Mat_DoctorHair", (0.14, 0.11, 0.10), metallic=0.0, roughness=0.82),
        "gloves": make_material("Mat_DoctorGloves", (0.22, 0.65, 0.90), metallic=0.05, roughness=0.32),
        "stetho_tube": make_material("Mat_StethoscopeTube", (0.06, 0.09, 0.16), metallic=0.1, roughness=0.45),
        "chrome": make_material("Mat_StethoscopeChrome", (0.92, 0.95, 0.98), metallic=0.96, roughness=0.12),
        "badge": make_material("Mat_IDBadge", (0.95, 0.96, 0.98), metallic=0.1, roughness=0.3),
        "badge_cyan": make_material("Mat_BadgeStripe", (0.04, 0.72, 0.88), emission=(0.04, 0.72, 0.88), emission_strength=1.5),
        "mask": make_material("Mat_SurgicalMask", (0.38, 0.76, 0.88), metallic=0.0, roughness=0.62),
    }

    # Raíz Principal del Avatar (a nivel de suelo Z = 0)
    root = add_empty("Doctor_Root", (0.0, 0.0, 0.0))

    # =========================================================================
    # 1. PELVIS Y TORSO CON BATA CLÍNICA (Z = 0.90 a 1.48)
    # =========================================================================
    hips_pivot = add_empty("Doctor_Hips_Pivot", (0.0, 0.0, 0.90), parent=root)

    # Pijama quirúrgico interior (Scrubs)
    add_box("Doctor_Torso_Scrubs", (0.0, 0.0, 1.18), (0.36, 0.22, 0.44), mats["scrubs"], bevel_width=0.02, parent=hips_pivot)

    # Bata médica blanca (capa exterior sobre hombros, espalda y costados)
    add_box("Doctor_Coat_Back", (0.0, -0.015, 1.20), (0.39, 0.235, 0.46), mats["coat"], bevel_width=0.025, parent=hips_pivot)

    # Solapa izquierda y derecha de la bata (abierta en V mostrando el pijama interior)
    add_box("Doctor_Coat_Lapel_L", (-0.12, 0.105, 1.24), (0.13, 0.025, 0.36), mats["coat"], bevel_width=0.008, parent=hips_pivot)
    add_box("Doctor_Coat_Lapel_R", (0.12, 0.105, 1.24), (0.13, 0.025, 0.36), mats["coat"], bevel_width=0.008, parent=hips_pivot)

    # Faldones de la bata médica (caen desde la cintura Z = 0.96 hasta Z = 0.64)
    add_box("Doctor_Coat_Skirt_Back", (0.0, -0.02, 0.80), (0.39, 0.24, 0.32), mats["coat"], bevel_width=0.02, parent=hips_pivot)
    add_box("Doctor_Coat_Skirt_Left", (-0.16, 0.02, 0.80), (0.09, 0.22, 0.32), mats["coat"], bevel_width=0.015, parent=hips_pivot)
    add_box("Doctor_Coat_Skirt_Right", (0.16, 0.02, 0.80), (0.09, 0.22, 0.32), mats["coat"], bevel_width=0.015, parent=hips_pivot)

    # Bolsillo superior izquierdo con gafete y bolígrafo
    add_box("Doctor_Pocket", (-0.11, 0.115, 1.25), (0.08, 0.012, 0.09), mats["coat"], bevel_width=0.004, parent=hips_pivot)
    add_cylinder("Doctor_Pen_Body", (-0.08, 0.122, 1.28), 0.004, 0.06, mats["scrubs"], parent=hips_pivot)
    add_cylinder("Doctor_Pen_Clip", (-0.08, 0.127, 1.29), 0.002, 0.03, mats["chrome"], parent=hips_pivot)

    # Credencial Institucional Ateneo+ en el bolsillo
    add_box("Doctor_Badge_Card", (-0.12, 0.122, 1.23), (0.055, 0.006, 0.075), mats["badge"], bevel_width=0.002, parent=hips_pivot)
    add_box("Doctor_Badge_CyanStripe", (-0.12, 0.125, 1.255), (0.055, 0.004, 0.018), mats["badge_cyan"], bevel_width=0.001, parent=hips_pivot)
    add_box("Doctor_Badge_Clip", (-0.12, 0.124, 1.272), (0.02, 0.008, 0.012), mats["chrome"], bevel_width=0.002, parent=hips_pivot)

    # =========================================================================
    # 2. ESTETOSCOPIO CLÍNICO 3D (Z = 1.15 a 1.48)
    # =========================================================================
    # Tubo flexible contorneando la nuca y cayendo sobre el pecho
    add_cylinder("Doctor_Stetho_NeckLoop", (0.0, -0.06, 1.44), 0.008, 0.18, mats["stetho_tube"], rot_xyz=(0, math.pi / 2, 0), vertices=12, parent=hips_pivot)
    add_cylinder("Doctor_Stetho_Tube_L", (-0.09, 0.04, 1.34), 0.007, 0.22, mats["stetho_tube"], rot_xyz=(math.pi / 12, 0, 0), vertices=12, parent=hips_pivot)
    add_cylinder("Doctor_Stetho_Tube_R", (0.08, 0.04, 1.30), 0.007, 0.28, mats["stetho_tube"], rot_xyz=(math.pi / 14, 0, -math.pi / 24), vertices=12, parent=hips_pivot)
    # Pieza pectoral (campana y diafragma en cromo reflectante)
    add_cylinder("Doctor_Stetho_Chestpiece", (0.07, 0.118, 1.16), 0.024, 0.014, mats["chrome"], rot_xyz=(math.pi / 2, 0, 0), vertices=16, parent=hips_pivot)

    # =========================================================================
    # 3. CUELLO Y CABEZA ANATÓMICA (Z = 1.46 a 1.76)
    # =========================================================================
    head_pivot = add_empty("Doctor_Head_Pivot", (0.0, 0.0, 1.46), parent=hips_pivot)

    # Cuello clínico
    add_cylinder("Doctor_Neck", (0.0, 0.0, 1.48), 0.056, 0.09, mats["skin"], vertices=16, parent=head_pivot)

    # Cabeza estilizada
    add_sphere("Doctor_Head", (0.0, 0.02, 1.62), 0.108, (0.88, 1.05, 1.12), mats["skin"], parent=head_pivot)

    # Cabello prolijo profesional
    add_sphere("Doctor_Hair_Top", (0.0, 0.01, 1.68), 0.112, (0.92, 1.08, 0.85), mats["hair"], parent=head_pivot)
    add_sphere("Doctor_Hair_Back", (0.0, -0.05, 1.62), 0.108, (0.89, 0.88, 1.05), mats["hair"], parent=head_pivot)

    # Mascarilla quirúrgica celeste Ateneo+
    add_box("Doctor_Mask", (0.0, 0.105, 1.58), (0.13, 0.035, 0.075), mats["mask"], bevel_width=0.01, parent=head_pivot)

    # =========================================================================
    # 4. EXTREMIDADES SUPERIORES (BRAZOS) CON PIVOTES EN HOMBROS
    # =========================================================================
    # Brazo Izquierdo (Pivote en hombro X = -0.23, Y = 0.0, Z = 1.42)
    arm_l_pivot = add_empty("Doctor_Arm_L_Pivot", (-0.23, 0.0, 1.42), parent=hips_pivot)
    # Hombro y manga de la bata
    add_sphere("Doctor_Shoulder_L", (-0.23, 0.0, 1.42), 0.068, (1.0, 1.0, 1.1), mats["coat"], parent=arm_l_pivot)
    add_cylinder("Doctor_Arm_Upper_L", (-0.24, 0.0, 1.28), 0.056, 0.24, mats["coat"], parent=arm_l_pivot)
    add_cylinder("Doctor_Arm_Lower_L", (-0.24, 0.02, 1.06), 0.048, 0.22, mats["coat"], parent=arm_l_pivot)
    # Mano con guante de nitrilo clínico celeste
    add_sphere("Doctor_Hand_L", (-0.24, 0.03, 0.92), 0.046, (0.8, 1.1, 1.3), mats["gloves"], parent=arm_l_pivot)

    # Brazo Derecho (Pivote en hombro X = +0.23, Y = 0.0, Z = 1.42)
    arm_r_pivot = add_empty("Doctor_Arm_R_Pivot", (0.23, 0.0, 1.42), parent=hips_pivot)
    # Hombro y manga de la bata
    add_sphere("Doctor_Shoulder_R", (0.23, 0.0, 1.42), 0.068, (1.0, 1.0, 1.1), mats["coat"], parent=arm_r_pivot)
    add_cylinder("Doctor_Arm_Upper_R", (0.24, 0.0, 1.28), 0.056, 0.24, mats["coat"], parent=arm_r_pivot)
    add_cylinder("Doctor_Arm_Lower_R", (0.24, 0.02, 1.06), 0.048, 0.22, mats["coat"], parent=arm_r_pivot)
    # Mano con guante de nitrilo clínico celeste
    add_sphere("Doctor_Hand_R", (0.24, 0.03, 0.92), 0.046, (0.8, 1.1, 1.3), mats["gloves"], parent=arm_r_pivot)

    # =========================================================================
    # 5. EXTREMIDADES INFERIORES (PIERNAS) CON PIVOTES EN CADERAS
    # =========================================================================
    # Pierna Izquierda (Pivote en cadera X = -0.11, Y = 0.0, Z = 0.86)
    leg_l_pivot = add_empty("Doctor_Leg_L_Pivot", (-0.11, 0.0, 0.86), parent=hips_pivot)
    # Muslo y pantalón
    add_cylinder("Doctor_Thigh_L", (-0.11, 0.0, 0.68), 0.072, 0.32, mats["pants"], parent=leg_l_pivot)
    # Pantorrilla y bota del pantalón
    add_cylinder("Doctor_Calf_L", (-0.11, 0.0, 0.36), 0.064, 0.36, mats["pants"], parent=leg_l_pivot)
    # Calzado clínico ortopédico negro con suela blanca
    add_box("Doctor_Shoe_Upper_L", (-0.11, 0.04, 0.08), (0.11, 0.24, 0.10), mats["shoes"], bevel_width=0.015, parent=leg_l_pivot)
    add_box("Doctor_Shoe_Sole_L", (-0.11, 0.04, 0.02), (0.115, 0.245, 0.035), mats["sole"], bevel_width=0.005, parent=leg_l_pivot)

    # Pierna Derecha (Pivote en cadera X = +0.11, Y = 0.0, Z = 0.86)
    leg_r_pivot = add_empty("Doctor_Leg_R_Pivot", (0.11, 0.0, 0.86), parent=hips_pivot)
    # Muslo y pantalón
    add_cylinder("Doctor_Thigh_R", (0.11, 0.0, 0.68), 0.072, 0.32, mats["pants"], parent=leg_r_pivot)
    # Pantorrilla y bota del pantalón
    add_cylinder("Doctor_Calf_R", (0.11, 0.0, 0.36), 0.064, 0.36, mats["pants"], parent=leg_r_pivot)
    # Calzado clínico ortopédico negro con suela blanca
    add_box("Doctor_Shoe_Upper_R", (0.11, 0.04, 0.08), (0.11, 0.24, 0.10), mats["shoes"], bevel_width=0.015, parent=leg_r_pivot)
    add_box("Doctor_Shoe_Sole_R", (0.11, 0.04, 0.02), (0.115, 0.245, 0.035), mats["sole"], bevel_width=0.005, parent=leg_r_pivot)

    # Guardar archivo .blend para archivo de fuentes editable
    blend_path = Path("assets_src/blender/doctor_character.blend").resolve()
    os.makedirs(blend_path.parent, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
    print(f"Archivo .blend guardado en: {blend_path}")

    # Exportación GLB canónica con eje Y-Up para Three.js
    os.makedirs(output_glb.parent, exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=str(output_glb),
        export_format='GLB',
        use_selection=False,
        export_apply=False,  # Preservar jerarquía de nodos parent-child y pivotes
        export_yup=True
    )
    print(f"Modelo 3D exportado exitosamente a: {output_glb}")


if __name__ == "__main__":
    out_path = Path("frontend/public/models/doctor_character.glb").resolve()
    build_doctor_character(out_path)

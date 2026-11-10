"""
Ateneo+ Master 3D Hospital Builder (Blender 5.2 Z-Up Canonical Architecture)
Construye el Complejo Hospitalario Universitario completo (Exterior + Interior Integrado) sin parches:
1. Edificio Hospitalario de 3 Plantas + Coronamiento Institucional:
   - Fachada arquitectónica luminosa en paneles compuestos blancos Alucobond, franjas azul clínico y muro cortina.
   - Tipografía vectorial 3D extruida real ("HOSPITAL UNIVERSITARIO ATENEO+" y "URGENCIAS 24H") sin pixelación.
   - Portal de admisión en Planta Baja con abertura física real en el muro Oeste (X = -12.0) y puertas corredizas
     automáticas de cristal templado abiertas de par en par, conectando físicamente el exterior con el interior.
   - Ventanales de planta baja con vidrio translúcido real que permite ver hacia los cubículos interiores.
   - Marquesina estructural de Urgencias (Porte-Cochère) con columnas de acero satinado y plafones LED.
   - Cruces médicas tridimensionales retroiluminadas en el frontis superior y marquesina.
2. Entorno Urbano, Plaza de Acceso y Bahía de Ambulancias (X = -42.0 a -12.0):
   - Acera peatonal a nivel cero (Z = 0.0) continua con el piso del pabellón interior, bolardos de acero y guía azul.
   - Calzada asfáltica con paso de cebra peatonal, líneas viales y bahía de emergencia.
   - Ambulancia de Soporte Vital Avanzado (SVA) modelada en 3D estacionada en el encuadre derecho (Y = -6.0).
   - Tótem directorio hospitalario, jardineras arquitectónicas con árboles y farolas LED en el encuadre izquierdo.
3. Interior del Pabellón de Urgencias y Choque (X = -12.0 a +12.0, Y = -9.0 a +9.0):
   - 6 Cubículos clínicos completos con camas articuladas, pacientes hospitalizados, monitores ECG, portasueros y gases.
   - Central de Enfermería y Triaje al fondo del corredor principal (X = +9.8, Y = 0.0).
"""

import os
import math
from pathlib import Path
import bpy
import numpy as np


# ===========================================================================
# 1. GENERACIÓN DE TEXTURAS PBR EN ALTA RESOLUCIÓN
# ===========================================================================

def save_blender_image(name, width, height, rgba_array, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    img = bpy.data.images.new(name=name, width=width, height=height, alpha=True, float_buffer=False)
    flat = np.clip(rgba_array, 0.0, 1.0).astype(np.float32).flatten()
    img.pixels.foreach_set(flat)
    img.filepath_raw = str(filepath)
    img.file_format = 'PNG'
    img.save()
    return filepath


def generate_all_textures(tex_dir: Path):
    os.makedirs(tex_dir, exist_ok=True)
    np.random.seed(101)

    # 1. Textura de Suelo Vinílico Hospitalario Interior y Acera Técnica (512x512)
    W, H = 512, 512
    tile_px = W // 4
    gx = np.arange(W) % tile_px
    gy = np.arange(H) % tile_px
    xx, yy = np.meshgrid(gx, gy)
    dist_edge = np.minimum(np.minimum(xx, tile_px - xx), np.minimum(yy, tile_px - yy))
    is_seam = dist_edge < 2

    noise = np.random.uniform(-0.012, 0.012, (H, W, 1)).astype(np.float32)
    specks = (np.random.rand(H, W, 1) > 0.97).astype(np.float32) * (-0.035)
    tile_col = np.array([0.89, 0.91, 0.93], dtype=np.float32) + noise + specks
    seam_col = np.array([0.74, 0.78, 0.82], dtype=np.float32)

    floor_rgb = np.where(is_seam[:, :, None], seam_col, tile_col)
    floor_rgba = np.dstack([floor_rgb, np.ones((H, W, 1), dtype=np.float32)])
    save_blender_image("Floor_Albedo", W, H, floor_rgba, tex_dir / "floor_basecolor.png")

    floor_rough_v = np.where(is_seam, 0.65, 0.20).astype(np.float32)
    floor_rough = np.dstack([floor_rough_v] * 3 + [np.ones((H, W), dtype=np.float32)])
    save_blender_image("Floor_Rough", W, H, floor_rough, tex_dir / "floor_roughness.png")

    # 2. Textura de Asfalto Exterior para Calzada y Bahía de Ambulancias (512x512)
    asp_noise = np.random.normal(0.0, 0.022, (H, W, 1)).astype(np.float32)
    asp_pebbles = (np.random.rand(H, W, 1) > 0.92).astype(np.float32) * 0.035
    asp_rgb = np.clip(np.array([0.20, 0.22, 0.25], dtype=np.float32) + asp_noise + asp_pebbles, 0.12, 0.34)
    asp_rgba = np.dstack([asp_rgb, np.ones((H, W, 1), dtype=np.float32)])
    save_blender_image("Asphalt_Albedo", W, H, asp_rgba, tex_dir / "asphalt_basecolor.png")

    # 3. Textura de Pantalla de Monitor Multiparamétrico UCI (512x512)
    MW, MH = 512, 512
    mon = np.zeros((MH, MW, 3), dtype=np.float32)
    mon[:] = np.array([0.02, 0.05, 0.09], dtype=np.float32)

    gmask = ((np.arange(MW) % 32 == 0)[:, None] | (np.arange(MH) % 32 == 0)[None, :]).T
    mon[gmask] = np.array([0.05, 0.12, 0.18], dtype=np.float32)

    t = np.linspace(0, 12 * math.pi, 360)
    ecg_wave = np.sin(t) * 6.0
    for pk in [50, 130, 210, 290]:
        for dx in range(-6, 7):
            idx = pk + dx
            if 0 <= idx < 360:
                if dx == 0:
                    ecg_wave[idx] += 48.0
                elif abs(dx) <= 2:
                    ecg_wave[idx] -= 15.0

    for ix in range(360):
        iy = int(np.clip(380 + ecg_wave[ix], 0, MH - 1))
        mon[max(0, iy - 3):min(MH, iy + 4), 20 + ix] = np.array([0.15, 0.98, 0.35], dtype=np.float32)

    pleth = (np.sin(t * 0.75) ** 2) * 32.0
    for ix in range(360):
        iy = int(np.clip(240 + pleth[ix], 0, MH - 1))
        mon[max(0, iy - 3):min(MH, iy + 4), 20 + ix] = np.array([0.10, 0.82, 0.98], dtype=np.float32)

    resp = np.sin(t * 0.35) * 20.0
    for ix in range(360):
        iy = int(np.clip(110 + resp[ix], 0, MH - 1))
        mon[max(0, iy - 3):min(MH, iy + 4), 20 + ix] = np.array([0.98, 0.82, 0.18], dtype=np.float32)

    mon[350:440, 400:490] = np.array([0.15, 0.95, 0.35], dtype=np.float32)
    mon[220:310, 400:490] = np.array([0.10, 0.82, 0.98], dtype=np.float32)
    mon[90:180, 400:490] = np.array([0.98, 0.82, 0.18], dtype=np.float32)

    mon_rgba = np.dstack([mon, np.ones((MH, MW, 1), dtype=np.float32)])
    save_blender_image("ECG_Screen", MW, MH, mon_rgba, tex_dir / "ecg_screen.png")


# ===========================================================================
# 2. UTILIDADES DE MATERIALES, TEXTO 3D VECTORIAL Y GEOMETRÍA Z-UP
# ===========================================================================

def make_material(name, color, metallic=0.0, roughness=0.4, emission=None, emission_strength=0.0, alpha=1.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
        bsdf.inputs["Metallic"].default_value = metallic
        bsdf.inputs["Roughness"].default_value = roughness
        if alpha < 1.0:
            if "Alpha" in bsdf.inputs:
                bsdf.inputs["Alpha"].default_value = alpha
            if hasattr(mat, "blend_method"):
                mat.blend_method = 'BLEND'
            if hasattr(mat, "surface_render_method"):
                mat.surface_render_method = 'BLENDED'
        if emission is not None and emission_strength > 0:
            esock = "Emission Color" if "Emission Color" in bsdf.inputs else "Emission"
            if esock in bsdf.inputs:
                bsdf.inputs[esock].default_value = (emission[0], emission[1], emission[2], 1.0)
            if "Emission Strength" in bsdf.inputs:
                bsdf.inputs["Emission Strength"].default_value = emission_strength
    return mat


def make_textured_material(name, albedo_path, rough_path=None, emissive=False, emission_strength=2.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.get("Principled BSDF")

    tex = nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(str(albedo_path))
    links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])

    if emissive:
        esock = "Emission Color" if "Emission Color" in bsdf.inputs else "Emission"
        if esock in bsdf.inputs:
            links.new(tex.outputs["Color"], bsdf.inputs[esock])
        if "Emission Strength" in bsdf.inputs:
            bsdf.inputs["Emission Strength"].default_value = emission_strength

    if rough_path and os.path.exists(rough_path):
        rtex = nodes.new("ShaderNodeTexImage")
        rtex.image = bpy.data.images.load(str(rough_path))
        rtex.image.colorspace_settings.name = 'Non-Color'
        links.new(rtex.outputs["Color"], bsdf.inputs["Roughness"])
    else:
        bsdf.inputs["Roughness"].default_value = 0.25

    return mat


def scale_object_uvs(obj, su, sv):
    mesh = obj.data
    if not mesh.uv_layers:
        return
    uv_layer = mesh.uv_layers.active.data
    for loop in uv_layer:
        loop.uv[0] *= su
        loop.uv[1] *= sv


def add_3d_text(name, text_str, loc_xyz, size, extrude, mat):
    """
    Crea tipografía vectorial 3D extruida en malla real (cero pixelación)
    orientada hacia el Oeste (-X) para leerse de izquierda (+Y) a derecha (-Y).
    """
    font_curve = bpy.data.curves.new(type="FONT", name=f"{name}_Curve")
    font_curve.body = text_str
    font_curve.size = size
    font_curve.extrude = extrude
    font_curve.bevel_depth = 0.003
    font_curve.align_x = 'CENTER'
    font_curve.align_y = 'CENTER'

    text_obj = bpy.data.objects.new(name=name, object_data=font_curve)
    bpy.context.collection.objects.link(text_obj)

    bpy.ops.object.select_all(action='DESELECT')
    text_obj.select_set(True)
    bpy.context.view_layer.objects.active = text_obj

    # 1. Convertir primero la curva tipográfica a malla poligonal real
    bpy.ops.object.convert(target='MESH')
    mesh_obj = bpy.context.active_object
    mesh_obj.name = name

    # 2. Rotar 90° en X para poner el texto vertical (altura en +Z, normal en -Y)
    mesh_obj.rotation_euler = (math.pi / 2.0, 0.0, 0.0)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

    # 3. Rotar -90° en Z para que mire hacia -X y se lea de +Y (izquierda) a -Y (derecha)
    mesh_obj.rotation_euler = (0.0, 0.0, -math.pi / 2.0)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

    mesh_obj.location = loc_xyz
    if mat:
        mesh_obj.data.materials.append(mat)
    return mesh_obj


def add_screen_plane(name, loc_xyz, width, height, mat, rot_z=0.0):
    """Crea un plano vertical con UVs correctamente orientados (U horizontal, V vertical) para pantallas."""
    mesh = bpy.data.meshes.new(name=name)
    obj = bpy.data.objects.new(name=name, object_data=mesh)
    bpy.context.collection.objects.link(obj)

    hw = width / 2.0
    hh = height / 2.0
    verts = [(-hw, 0.0, -hh), (hw, 0.0, -hh), (hw, 0.0, hh), (-hw, 0.0, hh)]
    faces = [(0, 1, 2, 3)]
    mesh.from_pydata(verts, [], faces)
    mesh.update()

    uv_layer = mesh.uv_layers.new(name="UVMap")
    mesh.uv_layers.active = uv_layer
    uvs = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
    for i, loop in enumerate(uv_layer.data):
        loop.uv = uvs[i]

    obj.location = loc_xyz
    obj.rotation_euler = (0.0, 0.0, rot_z)
    if mat:
        obj.data.materials.append(mat)
    return obj


def add_box(name, loc_xyz, dim_xyz, mat, bevel_width=0.01, rot_z=0.0, uv_scale=None):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc_xyz, rotation=(0.0, 0.0, rot_z))
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

    if uv_scale:
        scale_object_uvs(obj, uv_scale[0], uv_scale[1])

    return obj


def add_cylinder(name, loc_xyz, radius, length, mat, rot_xyz=(0.0, 0.0, 0.0), vertices=16):
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
    return obj


def add_sphere(name, loc_xyz, radius, scale_xyz, mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=18, ring_count=12, radius=radius, location=loc_xyz)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale_xyz
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if mat:
        obj.data.materials.append(mat)
    bpy.ops.object.shade_smooth()
    return obj


def create_pleated_curtain(name, x_pos, y_start, y_end, z_bottom, z_top, mat):
    mesh = bpy.data.meshes.new(name=name)
    obj = bpy.data.objects.new(name=name, object_data=mesh)
    bpy.context.collection.objects.link(obj)

    steps_y = 28
    steps_z = 5
    ys = np.linspace(y_start, y_end, steps_y)
    zs = np.linspace(z_bottom, z_top, steps_z)

    verts = []
    for z in zs:
        for i, y in enumerate(ys):
            wx = x_pos + math.sin(i * 1.1) * 0.06
            verts.append((wx, float(y), float(z)))

    faces = []
    for j in range(steps_z - 1):
        for i in range(steps_y - 1):
            p1 = j * steps_y + i
            p2 = p1 + 1
            p3 = (j + 1) * steps_y + (i + 1)
            p4 = (j + 1) * steps_y + i
            faces.append((p1, p2, p3, p4))

    mesh.from_pydata(verts, [], faces)
    mesh.update()
    if mat:
        obj.data.materials.append(mat)
    return obj


# ===========================================================================
# 3. CONSTRUCCIÓN DE SUB-ENSAMBLAJES HOSPITALARIOS (INTERIOR Y EXTERIOR)
# ===========================================================================

def build_complete_patient_bay(bay_id, bx, by, is_north_wall, mats):
    dir_sign = 1.0 if is_north_wall else -1.0

    # 1. Bastidor Inferior y Ruedas Clínicas
    add_box(f"{bay_id}_BaseFrame", (bx, by, 0.22), (0.92, 1.95, 0.08), mats["steel"], bevel_width=0.015)
    add_cylinder(f"{bay_id}_LiftCol1", (bx, by - 0.55 * dir_sign, 0.35), 0.07, 0.26, mats["steel"])
    add_cylinder(f"{bay_id}_LiftCol2", (bx, by + 0.55 * dir_sign, 0.35), 0.07, 0.26, mats["steel"])

    for wx_off in [-0.42, 0.42]:
        for wy_off in [-0.85, 0.85]:
            add_cylinder(
                f"{bay_id}_Wheel_{wx_off}_{wy_off}",
                (bx + wx_off, by + wy_off, 0.08),
                0.08, 0.05, mats["rubber"],
                rot_xyz=(0.0, math.pi / 2, 0.0)
            )
            add_cylinder(
                f"{bay_id}_Fork_{wx_off}_{wy_off}",
                (bx + wx_off, by + wy_off, 0.15),
                0.025, 0.10, mats["steel"]
            )

    # 2. Plataforma y Colchón Médico
    add_box(f"{bay_id}_Deck", (bx, by, 0.48), (1.02, 2.12, 0.06), mats["white_plastic"], bevel_width=0.015)
    add_box(f"{bay_id}_Mattress", (bx, by, 0.58), (0.96, 2.02, 0.15), mats["mattress"], bevel_width=0.035)
    add_box(f"{bay_id}_Sheet", (bx, by - 0.15 * dir_sign, 0.66), (0.98, 1.65, 0.04), mats["sheet"], bevel_width=0.015)
    add_box(f"{bay_id}_Blanket", (bx, by - 0.42 * dir_sign, 0.68), (0.99, 1.05, 0.05), mats["blanket"], bevel_width=0.02)

    head_y = by + 0.76 * dir_sign
    add_box(f"{bay_id}_Pillow", (bx, head_y, 0.70), (0.62, 0.36, 0.09), mats["sheet"], bevel_width=0.03)

    # 3. Cabecero y Piecero Ergonómicos
    hb_y = by + 1.06 * dir_sign
    fb_y = by - 1.06 * dir_sign
    add_box(f"{bay_id}_Headboard", (bx, hb_y, 0.78), (1.04, 0.06, 0.52), mats["white_plastic"], bevel_width=0.02)
    add_box(f"{bay_id}_HeadboardAccent", (bx, hb_y - 0.01 * dir_sign, 0.82), (0.78, 0.07, 0.28), mats["teal_plastic"], bevel_width=0.01)

    add_box(f"{bay_id}_Footboard", (bx, fb_y, 0.70), (1.04, 0.06, 0.40), mats["white_plastic"], bevel_width=0.02)
    add_box(f"{bay_id}_FootboardChart", (bx, fb_y - 0.03 * dir_sign, 0.70), (0.42, 0.03, 0.24), mats["teal_plastic"], bevel_width=0.008)

    # 4. Barandillas Laterales Divididas
    for sx in [-0.51, 0.51]:
        for sy_off in [-0.42, 0.42]:
            add_box(
                f"{bay_id}_SideRail_{sx}_{sy_off}",
                (bx + sx, by + sy_off, 0.76),
                (0.03, 0.68, 0.24),
                mats["white_plastic"],
                bevel_width=0.01
            )
            add_box(
                f"{bay_id}_RailTop_{sx}_{sy_off}",
                (bx + sx, by + sy_off, 0.89),
                (0.035, 0.70, 0.035),
                mats["teal_plastic"],
                bevel_width=0.01
            )

    # 5. PACIENTE ANATÓMICO ACOSTADO EN LA CAMA
    add_sphere(f"{bay_id}_PatientHead", (bx, by + 0.72 * dir_sign, 0.83), 0.115, (0.92, 1.08, 1.0), mats["skin"])
    add_sphere(f"{bay_id}_PatientHair", (bx, by + 0.75 * dir_sign, 0.87), 0.112, (0.94, 1.02, 0.85), mats["hair"])
    add_cylinder(f"{bay_id}_PatientNeck", (bx, by + 0.56 * dir_sign, 0.76), 0.055, 0.12, mats["skin"], rot_xyz=(math.pi / 2, 0, 0))
    add_box(f"{bay_id}_PatientTorso", (bx, by + 0.26 * dir_sign, 0.76), (0.40, 0.52, 0.17), mats["gown"], bevel_width=0.05)
    for arm_x in [-0.26, 0.26]:
        add_cylinder(
            f"{bay_id}_PatientArm_{arm_x}",
            (bx + arm_x, by + 0.20 * dir_sign, 0.73),
            0.048, 0.48, mats["gown"],
            rot_xyz=(math.pi / 2, 0, 0)
        )
        add_sphere(
            f"{bay_id}_PatientHand_{arm_x}",
            (bx + arm_x, by - 0.06 * dir_sign, 0.72),
            0.045, (0.8, 1.3, 0.5), mats["skin"]
        )
    add_box(f"{bay_id}_PatientLegsUnderBlanket", (bx, by - 0.38 * dir_sign, 0.73), (0.36, 0.78, 0.12), mats["blanket"], bevel_width=0.04)

    # 6. Monitor Multiparamétrico UCI con Pantalla Horizontal Bien Orientada
    mon_x = bx + 0.78
    mon_y = by + 0.65 * dir_sign
    add_cylinder(f"{bay_id}_MonitorStand", (mon_x, mon_y, 0.72), 0.025, 1.44, mats["steel"])
    add_cylinder(f"{bay_id}_MonitorBase", (mon_x, mon_y, 0.02), 0.22, 0.04, mats["steel"])
    mon_angle = -0.35 if is_north_wall else (math.pi + 0.35)
    add_box(f"{bay_id}_MonitorBody", (mon_x, mon_y, 1.48), (0.48, 0.10, 0.36), mats["dark_metal"], bevel_width=0.015, rot_z=mon_angle)

    dx_norm = math.sin(mon_angle) * 0.055
    dy_norm = -math.cos(mon_angle) * 0.055
    add_screen_plane(
        f"{bay_id}_MonitorScreenPlane",
        (mon_x + dx_norm, mon_y + dy_norm, 1.48),
        0.42, 0.29,
        mats["ecg_screen"],
        rot_z=mon_angle
    )

    is_red_code = bay_id in ("Bed_01", "Bed_02")
    add_cylinder(
        f"{bay_id}_AlarmLamp",
        (mon_x, mon_y, 1.69),
        0.03, 0.06,
        mats["red_alarm"] if is_red_code else mats["cyan_led"]
    )

    # 7. Portasuero Telescópico y Bolsa de Infusión IV
    iv_x = bx - 0.72
    iv_y = by + 0.80 * dir_sign
    add_cylinder(f"{bay_id}_IVBase", (iv_x, iv_y, 0.02), 0.20, 0.03, mats["steel"])
    add_cylinder(f"{bay_id}_IVPole", (iv_x, iv_y, 0.98), 0.014, 1.92, mats["steel"])
    add_box(f"{bay_id}_IVBag", (iv_x + 0.08, iv_y, 1.78), (0.10, 0.05, 0.22), mats["iv_bag"], bevel_width=0.015)

    # 8. Velador Clínico y Mesa Puente
    cab_x = bx - 0.95
    cab_y = by + 0.35 * dir_sign
    add_box(f"{bay_id}_CabinetBody", (cab_x, cab_y, 0.42), (0.48, 0.48, 0.82), mats["white_plastic"], bevel_width=0.015)
    add_box(f"{bay_id}_CabinetTop", (cab_x, cab_y, 0.84), (0.52, 0.52, 0.04), mats["teal_plastic"], bevel_width=0.01)

    # 9. Consola Mural de Gases Medicinales
    wall_y = by + 3.55 * dir_sign
    add_box(f"{bay_id}_HeadwallConsole", (bx, wall_y, 1.52), (1.75, 0.08, 0.28), mats["steel"], bevel_width=0.01)
    add_cylinder(f"{bay_id}_GasO2", (bx - 0.38, wall_y - 0.05 * dir_sign, 1.52), 0.035, 0.04, mats["gas_o2"], rot_xyz=(math.pi / 2, 0, 0))
    add_cylinder(f"{bay_id}_GasAir", (bx, wall_y - 0.05 * dir_sign, 1.52), 0.035, 0.04, mats["gas_air"], rot_xyz=(math.pi / 2, 0, 0))
    add_cylinder(f"{bay_id}_GasVac", (bx + 0.38, wall_y - 0.05 * dir_sign, 1.52), 0.035, 0.04, mats["gas_vac"], rot_xyz=(math.pi / 2, 0, 0))


def build_emergency_ambulance(ax, ay, mats):
    """Construye una Ambulancia de Soporte Vital Avanzado (SVA) estacionada en la bahía de urgencias."""
    # Orientada a lo largo del eje Y (frente mirando hacia +Y / Centro de la plaza)
    # 1. Módulo Sanitario Trasero (Caja clínica)
    add_box("Amb_BoxBody", (ax, ay - 0.65, 1.48), (2.25, 4.10, 2.15), mats["facade_white"], bevel_width=0.04)
    add_box("Amb_StripeRed", (ax, ay - 0.65, 1.12), (2.27, 4.12, 0.24), mats["crash_red"], bevel_width=0.01)
    add_box("Amb_StripeBlue", (ax, ay - 0.65, 1.85), (2.27, 4.12, 0.16), mats["facade_blue"], bevel_width=0.01)

    # Cruces médicas laterales en la ambulancia
    for side_x in [-1.14, 1.14]:
        add_box(f"Amb_CrossV_{side_x}", (ax + side_x, ay - 0.85, 1.50), (0.02, 0.18, 0.52), mats["crash_red"], bevel_width=0.005)
        add_box(f"Amb_CrossH_{side_x}", (ax + side_x, ay - 0.85, 1.50), (0.02, 0.52, 0.18), mats["crash_red"], bevel_width=0.005)

    # Ventana lateral polarizada del módulo médico
    add_box("Amb_SideWindow", (ax - 1.14, ay + 0.35, 1.65), (0.02, 1.10, 0.58), mats["curtain_glass"], bevel_width=0.005)

    # 2. Cabina del Conductor mirando hacia +Y
    add_box("Amb_Cabin", (ax, ay + 2.15, 1.18), (2.12, 1.65, 1.55), mats["facade_white"], bevel_width=0.05)
    add_box("Amb_Hood", (ax, ay + 3.30, 0.82), (2.06, 0.95, 0.82), mats["facade_white"], bevel_width=0.05)
    add_box("Amb_Windshield", (ax, ay + 2.75, 1.42), (1.88, 0.55, 0.68), mats["curtain_glass"], bevel_width=0.02)
    add_box("Amb_Grille", (ax, ay + 3.78, 0.74), (1.35, 0.06, 0.42), mats["dark_metal"], bevel_width=0.01)
    add_box("Amb_BumperFront", (ax, ay + 3.82, 0.42), (2.14, 0.18, 0.22), mats["dark_metal"], bevel_width=0.02)
    add_box("Amb_BumperRear", (ax, ay - 2.74, 0.42), (2.28, 0.16, 0.22), mats["dark_metal"], bevel_width=0.02)

    for lx in [-0.76, 0.76]:
        add_box(f"Amb_Headlight_{lx}", (ax + lx, ay + 3.78, 0.82), (0.32, 0.06, 0.18), mats["led_panel"], bevel_width=0.01)

    # Torreta de Emergencia LED Bicolor (Rojo / Azul) en el techo
    add_box("Amb_LightbarBase", (ax, ay + 1.25, 2.60), (1.45, 0.28, 0.08), mats["steel"], bevel_width=0.01)
    add_box("Amb_SirenRed", (ax - 0.38, ay + 1.25, 2.68), (0.55, 0.22, 0.12), mats["red_alarm"], bevel_width=0.02)
    add_box("Amb_SirenBlue", (ax + 0.38, ay + 1.25, 2.68), (0.55, 0.22, 0.12), mats["cyan_led"], bevel_width=0.02)

    # 3. Ruedas con Neumáticos y Llantas de Acero
    for wx in [-1.02, 1.02]:
        for wy in [ay + 2.65, ay - 1.45]:
            add_cylinder(
                f"Amb_Tire_{wx}_{wy}",
                (ax + wx, wy, 0.42),
                0.42, 0.28, mats["rubber"],
                rot_xyz=(0.0, math.pi / 2, 0.0),
                vertices=24
            )
            add_cylinder(
                f"Amb_Rim_{wx}_{wy}",
                (ax + wx + (0.02 if wx > 0 else -0.02), wy, 0.42),
                0.24, 0.29, mats["steel"],
                rot_xyz=(0.0, math.pi / 2, 0.0),
                vertices=16
            )


def build_hospital_exterior_and_plaza(RX, RY, RZ, mats):
    """
    Construye toda la arquitectura exterior del Complejo Hospitalario Universitario Ateneo+
    y su explanada urbana de acceso con puertas abiertas hacia el Pabellón de Urgencias.
    """
    west_x = -RX / 2.0  # X = -12.0 (Plano de fachada principal de entrada)

    # =========================================================================
    # A. MURO OESTE DE PLANTA BAJA CON PORTAL REAL ABIERTO Y VENTANALES
    # =========================================================================
    # 1. Dintel superior continuo sobre toda la fachada Oeste de planta baja (Z = 2.75 a 3.80)
    add_box("Wall_West_Lintel", (west_x, 0.0, 3.275), (0.28, RY, 1.05), mats["facade_white"], bevel_width=0.01)

    # 2. Pilares esquineros Norte y Sur (Y en [-9.0, -7.8] y [7.8, 9.0], altura Z = 0 a 2.75)
    for side_tag, y_c in [("South", -8.40), ("North", 8.40)]:
        add_box(f"Wall_West_CornerWainscot_{side_tag}", (west_x, y_c, 0.55), (0.28, 1.20, 1.10), mats["wall_wainscot"], bevel_width=0.01)
        add_box(f"Wall_West_CornerUpper_{side_tag}", (west_x, y_c, 1.925), (0.28, 1.20, 1.65), mats["facade_white"], bevel_width=0.01)

    # 3. Antepechos inferiores bajo los ventanales de planta baja (Y en [-7.8, -3.45] y [3.45, 7.8], Z = 0 a 1.10)
    for side_tag, y_c in [("South", -5.625), ("North", 5.625)]:
        add_box(f"Wall_West_WindowSill_{side_tag}", (west_x, y_c, 0.55), (0.28, 4.35, 1.10), mats["wall_wainscot"], bevel_width=0.01)
        add_box(f"Baseboard_West_{side_tag}", (west_x + 0.15, y_c, 0.08), (0.04, 4.35, 0.16), mats["baseboard"], bevel_width=0.005)
        add_box(f"BumperRail_West_{side_tag}", (west_x + 0.16, y_c, 0.92), (0.04, 4.20, 0.14), mats["steel"], bevel_width=0.01)

    # 4. Pilares intermedios entre ventanales y el portal de puertas automáticas (Y = -3.625 y +3.625)
    for side_tag, y_c in [("South", -3.625), ("North", 3.625)]:
        add_box(f"Wall_West_MidPier_{side_tag}", (west_x, y_c, 1.925), (0.30, 0.35, 1.65), mats["facade_white"], bevel_width=0.01)

    # 5. Ventanales traslúcidos reales en Planta Baja (permiten ver el interior desde afuera)
    for side_tag, y_c in [("South", -5.80), ("North", 5.80)]:
        add_box(f"GroundWin_FrameTop_{side_tag}", (west_x, y_c, 2.72), (0.16, 3.95, 0.06), mats["steel"], bevel_width=0.005)
        add_box(f"GroundWin_FrameBot_{side_tag}", (west_x, y_c, 1.12), (0.16, 3.95, 0.06), mats["steel"], bevel_width=0.005)
        add_box(f"GroundWin_Glass_{side_tag}", (west_x, y_c, 1.92), (0.04, 3.90, 1.56), mats["clear_glass"], bevel_width=0.0)
        for mul_y in [y_c - 1.30, y_c, y_c + 1.30]:
            add_box(f"GroundWin_Mullion_{side_tag}_{mul_y:.1f}", (west_x, mul_y, 1.92), (0.10, 0.05, 1.58), mats["steel"], bevel_width=0.005)

    # 6. SISTEMA DE PUERTAS AUTOMÁTICAS DE ADMISION DE URGENCIAS (ABIERTAS DE PAR EN PAR)
    add_box("AutoDoor_HeaderBox", (west_x - 0.06, 0.0, 2.70), (0.24, 7.00, 0.18), mats["steel"], bevel_width=0.01)
    for side_tag, jy in [("Left", -1.80), ("Right", 1.80)]:
        add_box(f"AutoDoor_Jamb_{side_tag}", (west_x, jy, 1.35), (0.28, 0.08, 2.70), mats["steel"], bevel_width=0.01)

    # Hojas fijas laterales de cristal templado
    for side_tag, fy in [("Left", -2.65), ("Right", 2.65)]:
        add_box(f"AutoDoor_FixedGlass_{side_tag}", (west_x, fy, 1.32), (0.04, 1.60, 2.60), mats["clear_glass"], bevel_width=0.0)
        add_box(f"AutoDoor_FixedRailBot_{side_tag}", (west_x, fy, 0.06), (0.08, 1.62, 0.12), mats["steel"], bevel_width=0.005)

    # Hojas corredizas automáticas DESLIZADAS EN POSICIÓN ABIERTA (en Y = -2.55 y Y = +2.55)
    for side_tag, oy in [("OpenLeft", -2.55), ("OpenRight", 2.55)]:
        dx = west_x - 0.10
        add_box(f"AutoDoor_SlidingGlass_{side_tag}", (dx, oy, 1.32), (0.04, 1.65, 2.56), mats["clear_glass"], bevel_width=0.0)
        add_box(f"AutoDoor_SlidingFrameTop_{side_tag}", (dx, oy, 2.58), (0.07, 1.68, 0.08), mats["steel"], bevel_width=0.005)
        add_box(f"AutoDoor_SlidingFrameBot_{side_tag}", (dx, oy, 0.08), (0.07, 1.68, 0.14), mats["steel"], bevel_width=0.005)
        add_box(f"AutoDoor_SlidingStileIn_{side_tag}", (dx, oy + (0.81 if oy < 0 else -0.81), 1.32), (0.07, 0.06, 2.56), mats["steel"], bevel_width=0.005)
        add_box(f"AutoDoor_SlidingStileOut_{side_tag}", (dx, oy + (-0.81 if oy < 0 else 0.81), 1.32), (0.07, 0.06, 2.56), mats["steel"], bevel_width=0.005)
        add_box(f"AutoDoor_SafetyBar_{side_tag}", (dx - 0.03, oy, 1.05), (0.03, 1.45, 0.05), mats["steel"], bevel_width=0.005)

    # =========================================================================
    # B. EDIFICIO HOSPITALARIO MULTINIVEL (ALAS LATERALES, PISOS 2 Y 3, CORONA)
    # =========================================================================
    # Alas laterales de Planta Baja (amplían la fachada principal a 28m de ancho: Y en [-14.0, 14.0])
    for wing_tag, wy_c in [("SouthWing", -11.5), ("NorthWing", 11.5)]:
        add_box(f"Hospital_GroundWing_{wing_tag}", (-2.0, wy_c, 2.0), (20.0, 5.0, 4.0), mats["facade_white"], bevel_width=0.02)
        add_box(f"Hospital_WingPlinth_{wing_tag}", (-2.05, wy_c, 0.55), (20.1, 5.05, 1.10), mats["wall_wainscot"], bevel_width=0.01)
        add_box(f"Hospital_WingWindow_{wing_tag}", (west_x - 0.04, wy_c, 2.05), (0.12, 3.20, 1.55), mats["curtain_glass"], bevel_width=0.01)
        add_box(f"Hospital_WingFrame_{wing_tag}", (west_x - 0.06, wy_c, 2.05), (0.14, 3.30, 0.08), mats["steel"], bevel_width=0.005)

    # Volumen Superior del Hospital (Pisos 2 y 3: Z = 4.0 a 10.6, ancho Y = 28.0m, fondo X = 24.0m)
    add_box("Hospital_UpperCore", (0.0, 0.0, 7.30), (23.8, 27.6, 6.60), mats["facade_white"], bevel_width=0.02)

    # Muro Cortina de Cristal Reflectante Luminoso en la Fachada Oeste (Pisos 2 y 3)
    add_box("Hospital_CurtainWall_West", (west_x - 0.06, 0.0, 7.30), (0.12, 26.4, 6.10), mats["curtain_glass"], bevel_width=0.0)

    # Franjas Arquitectónicas Horizontales (Forjados entre plantas en Z = 4.0, 7.3 y Cornisa en Z = 10.55)
    for f_idx, fz in enumerate([4.02, 7.30, 10.55]):
        add_box(f"Hospital_SlabBand_{f_idx}", (west_x - 0.22, 0.0, fz), (0.55, 28.2, 0.48), mats["facade_white"], bevel_width=0.02)
        add_box(f"Hospital_SlabAccent_{f_idx}", (west_x - 0.48, 0.0, fz), (0.08, 28.25, 0.14), mats["facade_blue"], bevel_width=0.01)

    # Columnas Estructurales Verticales Blancas y Montantes de Aluminio en la Fachada
    for col_y in [-13.6, -9.0, -4.4, 4.4, 9.0, 13.6]:
        add_box(f"Hospital_FacadeColumn_{col_y}", (west_x - 0.22, col_y, 5.35), (0.48, 0.56, 10.70), mats["facade_white"], bevel_width=0.02)
        add_box(f"Hospital_ColumnFin_{col_y}", (west_x - 0.48, col_y, 7.30), (0.08, 0.16, 6.40), mats["facade_blue"], bevel_width=0.01)

    for mul_y in np.linspace(-12.4, 12.4, 15):
        add_box(f"Hospital_CurtainMullion_{mul_y:.1f}", (west_x - 0.14, float(mul_y), 7.30), (0.06, 0.05, 6.20), mats["steel"], bevel_width=0.005)

    # Frontis Central Superior (Coronamiento Institucional: Z = 10.6 a 12.6, Y en [-7.5, 7.5])
    add_box("Hospital_CrownTower", (west_x - 0.18, 0.0, 11.65), (2.20, 15.2, 1.90), mats["facade_white"], bevel_width=0.02)
    add_box("Hospital_CrownCap", (west_x - 0.28, 0.0, 12.68), (2.45, 15.5, 0.22), mats["facade_blue"], bevel_width=0.01)
    add_box("Hospital_CrownSignBoard", (west_x - 1.30, 0.0, 11.65), (0.10, 11.4, 1.35), mats["facade_blue"], bevel_width=0.02)

    # Tipografía Vectorial 3D Extruida en el Frontis Superior: "HOSPITAL ATENEO+"
    add_3d_text(
        "Hospital_Crown3DText",
        "HOSPITAL ATENEO+",
        (west_x - 1.36, 0.0, 11.65),
        size=0.82,
        extrude=0.05,
        mat=mats["led_panel"]
    )

    # Cruces Médicas Luminosas 3D a ambos lados del Frontis Superior (Y = -6.45 y +6.45)
    for cy_cross in [-6.45, 6.45]:
        add_box(f"Hospital_CrownCrossV_{cy_cross}", (west_x - 1.34, cy_cross, 11.65), (0.12, 0.30, 1.02), mats["cyan_led"], bevel_width=0.01)
        add_box(f"Hospital_CrownCrossH_{cy_cross}", (west_x - 1.34, cy_cross, 11.65), (0.12, 1.02, 0.30), mats["cyan_led"], bevel_width=0.01)

    # =========================================================================
    # C. MARQUESINA DE ADMISION DE URGENCIAS (PORTE-COCHÈRE: X = -18.2 a -12.0)
    # =========================================================================
    canopy_x = -15.10
    add_box("Canopy_RoofDeck", (canopy_x, 0.0, 3.62), (6.40, 11.2, 0.34), mats["facade_white"], bevel_width=0.02)
    add_box("Canopy_UpperTrim", (canopy_x, 0.0, 3.83), (6.50, 11.4, 0.10), mats["facade_blue"], bevel_width=0.01)

    # Letrero Arquitectónico 3D en la Marquesina: "URGENCIAS 24H" con letras vectoriales extruidas reales
    add_box("Canopy_SignFrame", (-18.32, 0.0, 3.68), (0.12, 6.80, 0.76), mats["facade_white"], bevel_width=0.015)
    add_box("Canopy_SignRedBoard", (-18.36, 0.0, 3.68), (0.10, 6.60, 0.62), mats["crash_red"], bevel_width=0.01)
    add_3d_text(
        "Canopy_Urgencias3DText",
        "URGENCIAS 24H",
        (-18.42, 0.0, 3.68),
        size=0.46,
        extrude=0.04,
        mat=mats["led_panel"]
    )
    for cy_u in [-2.75, 2.75]:
        add_box(f"Canopy_UrgCrossV_{cy_u}", (-18.42, cy_u, 3.68), (0.06, 0.12, 0.38), mats["led_panel"], bevel_width=0.005)
        add_box(f"Canopy_UrgCrossH_{cy_u}", (-18.42, cy_u, 3.68), (0.06, 0.38, 0.12), mats["led_panel"], bevel_width=0.005)

    # Columnas estructurales cilíndricas de acero satinado luminoso
    for cx_col in [-17.6, -14.2]:
        for cy_col in [-4.8, 4.8]:
            add_cylinder(f"Canopy_Column_{cx_col}_{cy_col}", (cx_col, cy_col, 1.75), 0.20, 3.50, mats["satin_pillar"], vertices=24)
            add_cylinder(f"Canopy_ColBase_{cx_col}_{cy_col}", (cx_col, cy_col, 0.18), 0.26, 0.36, mats["facade_blue"], vertices=24)

    # Plafones LED bajo la marquesina iluminando la entrada abierta
    for lx_c in [-17.0, -15.0, -13.2]:
        for ly_c in [-2.4, 0.0, 2.4]:
            add_box(f"Canopy_Downlight_{lx_c}_{ly_c}", (lx_c, ly_c, 3.44), (0.65, 0.65, 0.03), mats["led_panel"], bevel_width=0.005)

    # =========================================================================
    # D. EXPLANADA EXTERIOR, CALZADA ASFÁLTICA, PASO PEATONAL Y JARDINERÍA
    # =========================================================================
    # 1. Acera Peatonal y Plaza de Entrada a Nivel Cero (Z = 0.0, continua con el piso del pabellón)
    add_box("Exterior_SidewalkPlaza", (-15.5, 0.0, -0.10), (7.0, 38.0, 0.20), mats["floor"], bevel_width=0.0, uv_scale=(6.0, 24.0))

    # Franja guía azul exterior que conecta el paso de cebra con el corredor interior
    add_box("Exterior_GuideCarpet", (-15.5, 0.0, 0.003), (7.0, 2.20, 0.004), mats["corridor_stripe"], bevel_width=0.0)
    add_box("Exterior_GuideBorderN", (-15.5, 1.15, 0.004), (7.0, 0.08, 0.004), mats["corridor_border"], bevel_width=0.0)
    add_box("Exterior_GuideBorderS", (-15.5, -1.15, 0.004), (7.0, 0.08, 0.004), mats["corridor_border"], bevel_width=0.0)

    # 2. Calzada Asfáltica de Ambulancias y Gran Explanada Oeste (X = -46.0 a -19.0)
    add_box("Exterior_AsphaltRoad", (-32.5, 0.0, -0.11), (27.0, 52.0, 0.20), mats["asphalt"], bevel_width=0.0, uv_scale=(14.0, 26.0))

    # Paso de Cebra Peatonal (Rayas blancas desde X = -29.0 hasta X = -19.5 frente a la entrada)
    for zebra_y in np.linspace(-2.1, 2.1, 7):
        add_box(f"Road_Crosswalk_{zebra_y:.2f}", (-24.2, float(zebra_y), 0.002), (7.5, 0.36, 0.004), mats["corridor_border"], bevel_width=0.0)

    # Isla / Plaza Peatonal de Inicio (X = -38.0 a -29.0, donde inicia el médico)
    add_box("Exterior_ArrivalPlaza", (-33.5, 0.0, -0.095), (9.0, 18.0, 0.20), mats["floor"], bevel_width=0.0, uv_scale=(6.0, 12.0))

    # Bolardos de Acero Satinado con Anillo Luminoso Cyan protegiendo la acera
    for bol_y in [-8.5, -6.2, -3.4, 3.4, 6.2, 8.5]:
        add_cylinder(f"Plaza_Bollard_{bol_y}", (-18.7, bol_y, 0.45), 0.09, 0.90, mats["satin_pillar"], vertices=16)
        add_cylinder(f"Plaza_BollardLight_{bol_y}", (-18.7, bol_y, 0.78), 0.095, 0.06, mats["cyan_led"], vertices=16)

    # 3. Ambulancia 3D Estacionada en la Bahía Derecha del Encuadre (X = -22.2, Y = -6.8)
    build_emergency_ambulance(-22.2, -6.8, mats)

    # 4. Tótem Institucional Luminoso a la Izquierda del Encuadre (X = -22.5, Y = +5.8)
    add_box("Totem_Base", (-22.5, 5.8, 0.20), (0.65, 1.45, 0.40), mats["dark_metal"], bevel_width=0.02)
    add_box("Totem_Body", (-22.5, 5.8, 1.85), (0.32, 1.25, 2.90), mats["facade_blue"], bevel_width=0.02)
    add_box("Totem_WhiteAccent", (-22.5, 5.8, 1.85), (0.34, 1.05, 2.60), mats["facade_white"], bevel_width=0.01)
    add_box("Totem_CrossV", (-22.68, 5.8, 2.45), (0.04, 0.16, 0.52), mats["crash_red"], bevel_width=0.005)
    add_box("Totem_CrossH", (-22.68, 5.8, 2.45), (0.04, 0.52, 0.16), mats["crash_red"], bevel_width=0.005)
    add_3d_text("Totem_Text", "ATENEO+", (-22.69, 5.8, 1.65), size=0.22, extrude=0.02, mat=mats["facade_blue"])

    # 5. Jardineras Arquitectónicas de Hormigón y Árboles del Campus Clínico
    tree_positions = [
        (-16.0, -9.8), (-16.0, 9.8),
        (-26.5, -11.2), (-26.5, 9.5),
    ]
    for idx, (tx, ty) in enumerate(tree_positions):
        add_box(f"Planter_Box_{idx}", (tx, ty, 0.28), (2.4, 2.4, 0.56), mats["facade_white"], bevel_width=0.02)
        add_box(f"Planter_Soil_{idx}", (tx, ty, 0.52), (2.1, 2.1, 0.10), mats["soil"], bevel_width=0.01)
        add_cylinder(f"Tree_Trunk_{idx}", (tx, ty, 1.65), 0.16, 2.30, mats["wood_trunk"], vertices=12)
        add_sphere(f"Tree_CanopyMain_{idx}", (tx, ty, 3.35), 1.35, (1.0, 1.0, 0.92), mats["foliage"])
        add_sphere(f"Tree_CanopyTop_{idx}", (tx + 0.25, ty - 0.20, 4.15), 0.95, (1.0, 1.0, 0.88), mats["foliage"])

    # 6. Farolas LED de Iluminación Exterior del Campus
    for idx, (lx, ly) in enumerate([(-27.5, -4.8), (-27.5, 4.8), (-19.5, -12.5), (-19.5, 12.5)]):
        add_cylinder(f"StreetLight_Pole_{idx}", (lx, ly, 2.60), 0.07, 5.20, mats["satin_pillar"], vertices=12)
        add_box(f"StreetLight_Arm_{idx}", (lx + 0.45, ly, 5.15), (1.05, 0.16, 0.10), mats["satin_pillar"], bevel_width=0.01)
        add_box(f"StreetLight_Lamp_{idx}", (lx + 0.72, ly, 5.09), (0.48, 0.24, 0.04), mats["led_panel"], bevel_width=0.005)


# ===========================================================================
# 4. CONSTRUCCIÓN GENERAL DEL COMPLEJO HOSPITALARIO (INTERIOR + EXTERIOR)
# ===========================================================================

def build_master_hospital(tex_dir: Path):
    bpy.ops.wm.read_factory_settings(use_empty=True)

    mats = {
        "floor": make_textured_material("Mat_FloorVinyl", tex_dir / "floor_basecolor.png", tex_dir / "floor_roughness.png"),
        "asphalt": make_textured_material("Mat_AsphaltRoad", tex_dir / "asphalt_basecolor.png"),
        "corridor_stripe": make_material("Mat_CorridorStripe", (0.14, 0.44, 0.68), metallic=0.05, roughness=0.25),
        "corridor_border": make_material("Mat_CorridorBorder", (0.95, 0.97, 0.99), metallic=0.0, roughness=0.25),
        "wall_upper": make_material("Mat_WallUpper", (0.94, 0.95, 0.96), metallic=0.0, roughness=0.55),
        "wall_wainscot": make_material("Mat_WallWainscot", (0.22, 0.38, 0.48), metallic=0.05, roughness=0.32),
        "baseboard": make_material("Mat_Baseboard", (0.18, 0.22, 0.26), metallic=0.1, roughness=0.4),
        "ceiling": make_material("Mat_CeilingAcoustic", (0.96, 0.97, 0.98), metallic=0.0, roughness=0.75),
        "led_panel": make_material("Mat_LedPanel", (1.0, 1.0, 1.0), emission=(0.96, 0.99, 1.0), emission_strength=3.0),
        "steel": make_material("Mat_SurgicalSteel", (0.82, 0.85, 0.88), metallic=0.82, roughness=0.22),
        "satin_pillar": make_material("Mat_SatinAluminum", (0.90, 0.93, 0.96), metallic=0.45, roughness=0.28, emission=(0.88, 0.92, 0.96), emission_strength=0.28),
        "dark_metal": make_material("Mat_DarkChassis", (0.15, 0.19, 0.24), metallic=0.5, roughness=0.35),
        "white_plastic": make_material("Mat_WhitePolymer", (0.95, 0.96, 0.98), metallic=0.05, roughness=0.28),
        "teal_plastic": make_material("Mat_MedicalTeal", (0.12, 0.46, 0.62), metallic=0.08, roughness=0.30),
        "facade_white": make_material("Mat_FacadeAlucobond", (0.95, 0.97, 0.99), metallic=0.08, roughness=0.30, emission=(0.92, 0.95, 0.98), emission_strength=0.32),
        "facade_blue": make_material("Mat_FacadeMedicalBlue", (0.08, 0.36, 0.68), metallic=0.15, roughness=0.26, emission=(0.06, 0.28, 0.56), emission_strength=0.35),
        "curtain_glass": make_material("Mat_CurtainWallGlass", (0.28, 0.58, 0.82), metallic=0.55, roughness=0.08, emission=(0.18, 0.42, 0.65), emission_strength=0.55),
        "clear_glass": make_material("Mat_ClearPortalGlass", (0.78, 0.92, 0.98), metallic=0.10, roughness=0.05, alpha=0.22),
        "mattress": make_material("Mat_Mattress", (0.14, 0.32, 0.52), metallic=0.0, roughness=0.45),
        "sheet": make_material("Mat_SheetWhite", (0.97, 0.98, 0.99), metallic=0.0, roughness=0.75),
        "blanket": make_material("Mat_BlanketBlue", (0.62, 0.80, 0.92), metallic=0.0, roughness=0.70),
        "curtain": make_material("Mat_PrivacyCurtain", (0.68, 0.84, 0.86), metallic=0.0, roughness=0.80),
        "skin": make_material("Mat_PatientSkin", (0.92, 0.78, 0.70), metallic=0.0, roughness=0.55),
        "hair": make_material("Mat_PatientHair", (0.18, 0.15, 0.14), metallic=0.0, roughness=0.80),
        "gown": make_material("Mat_HospitalGown", (0.52, 0.76, 0.90), metallic=0.0, roughness=0.72),
        "rubber": make_material("Mat_RubberCaster", (0.10, 0.11, 0.13), metallic=0.05, roughness=0.70),
        "ecg_screen": make_textured_material("Mat_ECGMonitor", tex_dir / "ecg_screen.png", emissive=True, emission_strength=2.0),
        "red_alarm": make_material("Mat_RedAlarm", (0.95, 0.12, 0.12), emission=(1.0, 0.15, 0.15), emission_strength=3.5),
        "cyan_led": make_material("Mat_CyanStatus", (0.10, 0.75, 0.95), emission=(0.10, 0.82, 1.0), emission_strength=2.8),
        "exit_green": make_material("Mat_ExitSign", (0.08, 0.78, 0.32), emission=(0.10, 0.90, 0.38), emission_strength=2.8),
        "iv_bag": make_material("Mat_SalineBag", (0.85, 0.93, 0.98), metallic=0.0, roughness=0.15),
        "glass_window": make_material("Mat_DaylightWindow", (0.88, 0.95, 1.0), roughness=0.1, emission=(0.82, 0.93, 1.0), emission_strength=2.2),
        "crash_red": make_material("Mat_CrashCartRed", (0.84, 0.10, 0.14), metallic=0.15, roughness=0.28, emission=(0.75, 0.08, 0.12), emission_strength=0.45),
        "gas_o2": make_material("Mat_GasO2", (0.12, 0.68, 0.28), metallic=0.4, roughness=0.3),
        "gas_air": make_material("Mat_GasAir", (0.92, 0.76, 0.12), metallic=0.4, roughness=0.3),
        "gas_vac": make_material("Mat_GasVac", (0.95, 0.95, 0.95), metallic=0.4, roughness=0.3),
        "foliage": make_material("Mat_TreeFoliage", (0.18, 0.48, 0.24), metallic=0.0, roughness=0.80, emission=(0.12, 0.34, 0.16), emission_strength=0.18),
        "wood_trunk": make_material("Mat_TreeTrunk", (0.36, 0.25, 0.16), metallic=0.0, roughness=0.88),
        "soil": make_material("Mat_PlanterSoil", (0.20, 0.16, 0.13), metallic=0.0, roughness=0.92),
    }

    RX = 24.0
    RY = 18.0
    RZ = 3.8

    # 1. SUELO INTERIOR DEL PABELLÓN CON BALDOSAS A ESCALA MÉTRICA
    add_box("Ward_Floor", (0, 0, -0.10), (RX, RY, 0.20), mats["floor"], bevel_width=0.0, uv_scale=(16.0, 12.0))

    # Franja de circulación central despejada desde la puerta abierta hasta la central de enfermería
    add_box("Corridor_CenterStripe", (-0.5, 0, 0.003), (RX - 1.0, 2.2, 0.004), mats["corridor_stripe"], bevel_width=0.0)
    add_box("Corridor_BorderNorth", (-0.5, 1.15, 0.004), (RX - 1.0, 0.08, 0.004), mats["corridor_border"], bevel_width=0.0)
    add_box("Corridor_BorderSouth", (-0.5, -1.15, 0.004), (RX - 1.0, 0.08, 0.004), mats["corridor_border"], bevel_width=0.0)

    # 2. TECHO ACÚSTICO Y PANELES LED EMPOTRADOS
    add_box("Ward_Ceiling", (0, 0, RZ + 0.10), (RX, RY, 0.20), mats["ceiling"], bevel_width=0.0)

    for lx in [-7.5, -2.5, 2.5, 7.5]:
        for ly in [-5.0, 0.0, 5.0]:
            add_box(f"Troffer_Frame_{lx}_{ly}", (lx, ly, RZ - 0.01), (1.6, 0.8, 0.03), mats["steel"], bevel_width=0.005)
            add_box(f"Troffer_LED_{lx}_{ly}", (lx, ly, RZ - 0.025), (1.48, 0.68, 0.02), mats["led_panel"], bevel_width=0.0)

    for bx_beam in [-3.5, 3.5]:
        add_box(f"Ceiling_Beam_{bx_beam}", (bx_beam, 0, RZ - 0.08), (0.28, RY, 0.16), mats["wall_upper"], bevel_width=0.01)

    # 3. MUROS NORTE, SUR Y ESTE
    for side, y_pos, in_sign in [("North", RY / 2, -1.0), ("South", -RY / 2, 1.0)]:
        add_box(f"Baseboard_{side}", (0, y_pos + 0.13 * in_sign, 0.08), (RX, 0.04, 0.16), mats["baseboard"], bevel_width=0.005)
        add_box(f"Wall_Wainscot_{side}", (0, y_pos, 0.65), (RX, 0.24, 1.30), mats["wall_wainscot"], bevel_width=0.01)
        add_box(f"Wall_Upper_{side}", (0, y_pos, 2.55), (RX, 0.24, 2.50), mats["wall_upper"], bevel_width=0.01)
        add_box(f"BumperRail_{side}", (0, y_pos + 0.14 * in_sign, 0.92), (RX - 0.6, 0.04, 0.14), mats["steel"], bevel_width=0.01)

    x_east = RX / 2.0
    in_east = -1.0
    add_box("Baseboard_East", (x_east + 0.13 * in_east, 0, 0.08), (0.04, RY, 0.16), mats["baseboard"], bevel_width=0.005)
    add_box("Wall_Wainscot_East", (x_east, 0, 0.65), (0.24, RY, 1.30), mats["wall_wainscot"], bevel_width=0.01)
    add_box("Wall_Upper_East", (x_east, 0, 2.55), (0.24, RY, 2.50), mats["wall_upper"], bevel_width=0.01)
    add_box("BumperRail_East", (x_east + 0.14 * in_east, 0, 0.92), (0.04, RY - 0.6, 0.14), mats["steel"], bevel_width=0.01)

    door_east_x = x_east + 0.15 * in_east
    add_box("DoorFrame_East", (door_east_x, 0, 1.25), (0.08, 2.50, 2.50), mats["steel"], bevel_width=0.01)
    for d_idx, dy in enumerate([-0.58, 0.58]):
        add_box(f"DoorLeaf_East_{d_idx}", (door_east_x + 0.01 * in_east, dy, 1.22), (0.05, 1.12, 2.40), mats["teal_plastic"], bevel_width=0.01)
        add_box(f"DoorWindow_East_{d_idx}", (door_east_x + 0.035 * in_east, dy, 1.62), (0.02, 0.36, 0.55), mats["glass_window"], bevel_width=0.005)
        add_box(f"DoorKickplate_East_{d_idx}", (door_east_x + 0.035 * in_east, dy, 0.22), (0.02, 1.06, 0.36), mats["steel"], bevel_width=0.005)
        add_box(f"DoorPushBar_East_{d_idx}", (door_east_x + 0.05 * in_east, dy, 1.02), (0.04, 0.85, 0.04), mats["steel"], bevel_width=0.008)
    add_box("ExitSign_East", (door_east_x + 0.03 * in_east, 0, 2.68), (0.06, 0.85, 0.22), mats["exit_green"], bevel_width=0.005)
    for wy in [-5.2, 5.2]:
        add_box(f"WindowFrame_East_{wy}", (door_east_x, wy, 2.25), (0.08, 2.8, 1.45), mats["steel"], bevel_width=0.01)
        add_box(f"WindowGlass_East_{wy}", (door_east_x + 0.035 * in_east, wy, 2.25), (0.02, 2.65, 1.30), mats["glass_window"], bevel_width=0.0)

    # 4. CONSTRUCCIÓN DE LA FACHADA HOSPITALARIA EXTERIOR, PUERTAS ABIERTAS Y EXPLANADA URBANA
    build_hospital_exterior_and_plaza(RX, RY, RZ, mats)

    # 5. CONSTRUCCIÓN DE LAS 6 BAHÍAS DE PACIENTES EN EL INTERIOR
    bays = [
        ("Bed_01", -7.0, 5.2, True),
        ("Bed_02", -7.0, -5.2, False),
        ("Bed_03", 0.0, 5.2, True),
        ("Bed_04", 0.0, -5.2, False),
        ("Bed_05", 7.0, 5.2, True),
        ("Bed_06", 7.0, -5.2, False),
    ]
    for bay_id, bx, by, is_north in bays:
        build_complete_patient_bay(bay_id, bx, by, is_north, mats)

    # 6. CORTINAS DIVISORIAS DE PRIVACIDAD ENTRE CUBÍCULOS
    for div_x in [-3.5, 3.5]:
        add_box(f"CurtainRail_North_{div_x}", (div_x, 5.5, RZ - 0.18), (0.04, 6.2, 0.04), mats["steel"], bevel_width=0.005)
        add_box(f"CurtainRail_South_{div_x}", (div_x, -5.5, RZ - 0.18), (0.04, 6.2, 0.04), mats["steel"], bevel_width=0.005)
        create_pleated_curtain(f"Curtain_North_{div_x}", div_x, 4.4, 8.6, 0.35, RZ - 0.20, mats["curtain"])
        create_pleated_curtain(f"Curtain_South_{div_x}", div_x, -8.6, -4.4, 0.35, RZ - 0.20, mats["curtain"])

    # 7. ESTACIÓN DE CONTROL Y TRIAJE DE ENFERMERÍA (Al fondo Este del corredor: X = +9.8, Y = 0)
    st_x, st_y = 9.8, 0.0
    add_box("NurseStation_Body", (st_x, st_y, 0.52), (1.3, 3.4, 1.04), mats["white_plastic"], bevel_width=0.02)
    add_box("NurseStation_FrontPanel", (st_x - 0.66, st_y, 0.50), (0.04, 3.2, 0.85), mats["teal_plastic"], bevel_width=0.01)
    add_box("NurseStation_Counter", (st_x, st_y, 1.06), (1.45, 3.6, 0.05), mats["steel"], bevel_width=0.01)

    for m_dy in [-0.75, 0.75]:
        add_box(f"Desk_Monitor_{m_dy}", (st_x - 0.20, st_y + m_dy, 1.28), (0.08, 0.52, 0.34), mats["dark_metal"], bevel_width=0.01)
        add_screen_plane(
            f"Desk_ScreenPlane_{m_dy}",
            (st_x - 0.25, st_y + m_dy, 1.28),
            0.46, 0.29,
            mats["ecg_screen"],
            rot_z=-math.pi / 2
        )

    # 8. CARROS DE PARO CARDIORRESPIRATORIO (ACLS CRASH CARTS)
    for cart_idx, (cx, cy) in enumerate([(-3.9, 7.8), (3.9, 7.8)]):
        add_box(f"CrashCart_Body_{cart_idx}", (cx, cy, 0.52), (0.72, 0.56, 0.88), mats["crash_red"], bevel_width=0.015)
        add_box(f"CrashCart_Top_{cart_idx}", (cx, cy, 0.98), (0.76, 0.60, 0.04), mats["steel"], bevel_width=0.01)
        add_box(f"CrashCart_Defib_{cart_idx}", (cx, cy, 1.14), (0.34, 0.28, 0.26), mats["dark_metal"], bevel_width=0.01)
        add_cylinder(f"CrashCart_O2_{cart_idx}", (cx + 0.42, cy, 0.55), 0.07, 0.68, mats["gas_o2"])


def render_verification_preview(preview_path: Path):
    scene = bpy.context.scene

    # Mundo con Cielo Diurno Clínico Luminoso para el Render de Verificación
    world = bpy.data.worlds.new("HospitalWorld")
    scene.world = world
    world.use_nodes = True
    bg_node = world.node_tree.nodes.get("Background")
    if bg_node:
        bg_node.inputs[0].default_value = (0.76, 0.86, 0.96, 1.0)
        bg_node.inputs[1].default_value = 1.2

    # Sol frontal desde el Oeste iluminando directamente la fachada del hospital
    sun_data = bpy.data.lights.new(name="PreviewSun", type='SUN')
    sun_data.energy = 3.2
    sun_obj = bpy.data.objects.new(name="PreviewSun", object_data=sun_data)
    bpy.context.collection.objects.link(sun_obj)
    sun_obj.location = (-40.0, -10.0, 28.0)
    sun_obj.rotation_euler = (math.radians(52.0), math.radians(48.0), math.radians(-15.0))

    for lx in [-16.0, -7.0, 0.0, 7.0]:
        for ly in [-3.5, 0.0, 3.5]:
            light_data = bpy.data.lights.new(name=f"PreviewLight_{lx}_{ly}", type='POINT')
            light_data.energy = 380.0
            light_data.shadow_soft_size = 0.8
            light_obj = bpy.data.objects.new(name=f"PreviewLight_{lx}_{ly}", object_data=light_data)
            bpy.context.collection.objects.link(light_obj)
            light_obj.location = (lx, ly, 3.4)

    # Cámara en la posición inicial exterior del jugador (-33.5, 0, 1.62) viendo todo el edificio y puertas abiertas
    cam_data = bpy.data.cameras.new(name="VerificationCam")
    cam_data.lens = 19.0
    cam_obj = bpy.data.objects.new(name="VerificationCam", object_data=cam_data)
    bpy.context.collection.objects.link(cam_obj)
    cam_obj.location = (-33.5, 0.0, 1.62)
    cam_obj.rotation_euler = (math.radians(95.5), 0.0, math.radians(-90.0))
    scene.camera = cam_obj

    scene.render.engine = 'BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items.keys() else 'BLENDER_EEVEE'
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.filepath = str(preview_path)
    bpy.ops.render.render(write_still=True)
    print(f"Render de verificación guardado en: {preview_path}")

    bpy.data.objects.remove(cam_obj, do_unlink=True)
    bpy.data.objects.remove(sun_obj, do_unlink=True)
    for obj in list(bpy.data.objects):
        if obj.name.startswith("PreviewLight_"):
            bpy.data.objects.remove(obj, do_unlink=True)


def export_all(blend_path: Path, glb_path: Path, preview_path: Path):
    os.makedirs(os.path.dirname(blend_path), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))

    try:
        render_verification_preview(preview_path)
    except Exception as e:
        print(f"Aviso en render preview: {e}")

    os.makedirs(os.path.dirname(glb_path), exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=str(glb_path),
        export_format='GLB',
        use_selection=False,
        export_apply=True,
        export_yup=True
    )
    print(f"GLB final exportado a: {glb_path}")


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent.parent
    tex_dir = root / "assets_src" / "textures"
    blend_out = root / "assets_src" / "blender" / "hospital_ward.blend"
    glb_out = root / "frontend" / "public" / "models" / "hospital_ward.glb"
    preview_out = root / "assets_src" / "blender" / "preview_render.png"

    generate_all_textures(tex_dir)
    build_master_hospital(tex_dir)
    export_all(blend_out, glb_out, preview_out)

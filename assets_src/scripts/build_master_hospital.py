"""
Ateneo+ Master 3D Hospital Builder (Blender 5.2 Z-Up Canonical Architecture)
Construye el Pabellón de Urgencias y Choque Hospitalario con coordenadas nativas Z-Up de Blender:
- Suelo con baldosas hospitalarias a escala métrica real (UV tiling 16x12) y pasillo central.
- Muros perimetrales con friso sanitario inferior, rieles antichoque, ventanales clínicos con persianas y puertas dobles.
- Techo acústico con plafones LED empotrados.
- 6 Cubículos clínicos completos: Cama articulada, Paciente hospitalizado con bata y manta,
  Monitor multiparamétrico ECG con ondas horizontales, Portasuero con bolsa IV, Velador clínico y Cabecero de gases.
- Cortinas divisorias plisadas con riel de techo.
- Central de Enfermería y Triaje al fondo del corredor principal (X = +9.6, Y = 0) mirando hacia toda la sala.
- Renderiza una captura de verificación desde la posición exacta de inicio del jugador (-9.5, 0, 1.68).
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

    # 1. Textura de Suelo Vinílico Hospitalario (512x512, 4x4 baldosas por repetición)
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

    # 2. Textura de Pantalla de Monitor Multiparamétrico UCI (512x512)
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
# 2. UTILIDADES DE MATERIALES Y GEOMETRÍA Z-UP
# ===========================================================================

def make_material(name, color, metallic=0.0, roughness=0.4, emission=None, emission_strength=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
        bsdf.inputs["Metallic"].default_value = metallic
        bsdf.inputs["Roughness"].default_value = roughness
        if emission is not None and emission_strength > 0:
            esock = "Emission Color" if "Emission Color" in bsdf.inputs else "Emission"
            if esock in bsdf.inputs:
                bsdf.inputs[esock].default_value = (emission[0], emission[1], emission[2], 1.0)
            if "Emission Strength" in bsdf.inputs:
                bsdf.inputs["Emission Strength"].default_value = emission_strength
    return mat


def make_textured_material(name, albedo_path, rough_path=None, emissive=False):
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
            bsdf.inputs["Emission Strength"].default_value = 2.0

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


def add_screen_plane(name, loc_xyz, width, height, mat, rot_z=0.0):
    """Crea un plano vertical con UVs correctamente orientados (U horizontal, V vertical) para pantallas."""
    mesh = bpy.data.meshes.new(name=name)
    obj = bpy.data.objects.new(name=name, object_data=mesh)
    bpy.context.collection.objects.link(obj)

    hw = width / 2.0
    hh = height / 2.0
    # Plano en X-Z mirando hacia -Y por defecto, luego rotado por rot_z
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
# 3. CONSTRUCCIÓN DE SUB-ENSAMBLAJES HOSPITALARIOS
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

    # Plano emisivo de pantalla con UVs horizontales exactas
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
    wall_y = by + 3.55 * dir_sign  # Adosado a la pared norte (Y=+8.75) o sur (Y=-8.75)
    add_box(f"{bay_id}_HeadwallConsole", (bx, wall_y, 1.52), (1.75, 0.08, 0.28), mats["steel"], bevel_width=0.01)
    add_cylinder(f"{bay_id}_GasO2", (bx - 0.38, wall_y - 0.05 * dir_sign, 1.52), 0.035, 0.04, mats["gas_o2"], rot_xyz=(math.pi / 2, 0, 0))
    add_cylinder(f"{bay_id}_GasAir", (bx, wall_y - 0.05 * dir_sign, 1.52), 0.035, 0.04, mats["gas_air"], rot_xyz=(math.pi / 2, 0, 0))
    add_cylinder(f"{bay_id}_GasVac", (bx + 0.38, wall_y - 0.05 * dir_sign, 1.52), 0.035, 0.04, mats["gas_vac"], rot_xyz=(math.pi / 2, 0, 0))


# ===========================================================================
# 4. CONSTRUCCIÓN GENERAL DEL PABELLÓN HOSPITALARIO
# ===========================================================================

def build_master_hospital(tex_dir: Path):
    bpy.ops.wm.read_factory_settings(use_empty=True)

    mats = {
        "floor": make_textured_material("Mat_FloorVinyl", tex_dir / "floor_basecolor.png", tex_dir / "floor_roughness.png"),
        "corridor_stripe": make_material("Mat_CorridorStripe", (0.14, 0.44, 0.68), metallic=0.05, roughness=0.25),
        "corridor_border": make_material("Mat_CorridorBorder", (0.95, 0.97, 0.99), metallic=0.0, roughness=0.25),
        "wall_upper": make_material("Mat_WallUpper", (0.94, 0.95, 0.96), metallic=0.0, roughness=0.55),
        "wall_wainscot": make_material("Mat_WallWainscot", (0.22, 0.38, 0.48), metallic=0.05, roughness=0.32),
        "baseboard": make_material("Mat_Baseboard", (0.18, 0.22, 0.26), metallic=0.1, roughness=0.4),
        "ceiling": make_material("Mat_CeilingAcoustic", (0.96, 0.97, 0.98), metallic=0.0, roughness=0.75),
        "led_panel": make_material("Mat_LedPanel", (1.0, 1.0, 1.0), emission=(0.95, 0.98, 1.0), emission_strength=2.8),
        "steel": make_material("Mat_SurgicalSteel", (0.82, 0.85, 0.88), metallic=0.88, roughness=0.20),
        "dark_metal": make_material("Mat_DarkChassis", (0.15, 0.19, 0.24), metallic=0.5, roughness=0.35),
        "white_plastic": make_material("Mat_WhitePolymer", (0.95, 0.96, 0.98), metallic=0.05, roughness=0.28),
        "teal_plastic": make_material("Mat_MedicalTeal", (0.12, 0.46, 0.62), metallic=0.08, roughness=0.30),
        "mattress": make_material("Mat_Mattress", (0.14, 0.32, 0.52), metallic=0.0, roughness=0.45),
        "sheet": make_material("Mat_SheetWhite", (0.97, 0.98, 0.99), metallic=0.0, roughness=0.75),
        "blanket": make_material("Mat_BlanketBlue", (0.62, 0.80, 0.92), metallic=0.0, roughness=0.70),
        "curtain": make_material("Mat_PrivacyCurtain", (0.68, 0.84, 0.86), metallic=0.0, roughness=0.80),
        "skin": make_material("Mat_PatientSkin", (0.92, 0.78, 0.70), metallic=0.0, roughness=0.55),
        "hair": make_material("Mat_PatientHair", (0.18, 0.15, 0.14), metallic=0.0, roughness=0.80),
        "gown": make_material("Mat_HospitalGown", (0.52, 0.76, 0.90), metallic=0.0, roughness=0.72),
        "rubber": make_material("Mat_RubberCaster", (0.10, 0.11, 0.13), metallic=0.05, roughness=0.70),
        "ecg_screen": make_textured_material("Mat_ECGMonitor", tex_dir / "ecg_screen.png", emissive=True),
        "red_alarm": make_material("Mat_RedAlarm", (0.95, 0.12, 0.12), emission=(1.0, 0.15, 0.15), emission_strength=3.5),
        "cyan_led": make_material("Mat_CyanStatus", (0.10, 0.75, 0.95), emission=(0.10, 0.80, 1.0), emission_strength=2.2),
        "exit_green": make_material("Mat_ExitSign", (0.08, 0.78, 0.32), emission=(0.10, 0.90, 0.38), emission_strength=2.8),
        "iv_bag": make_material("Mat_SalineBag", (0.85, 0.93, 0.98), metallic=0.0, roughness=0.15),
        "glass_window": make_material("Mat_DaylightWindow", (0.88, 0.95, 1.0), roughness=0.1, emission=(0.82, 0.93, 1.0), emission_strength=2.2),
        "crash_red": make_material("Mat_CrashCartRed", (0.82, 0.12, 0.14), metallic=0.25, roughness=0.28),
        "gas_o2": make_material("Mat_GasO2", (0.12, 0.68, 0.28), metallic=0.4, roughness=0.3),
        "gas_air": make_material("Mat_GasAir", (0.92, 0.76, 0.12), metallic=0.4, roughness=0.3),
        "gas_vac": make_material("Mat_GasVac", (0.95, 0.95, 0.95), metallic=0.4, roughness=0.3),
    }

    RX = 24.0
    RY = 18.0
    RZ = 3.8

    # 1. SUELO CON BALDOSAS A ESCALA MÉTRICA
    add_box("Ward_Floor", (0, 0, -0.10), (RX, RY, 0.20), mats["floor"], bevel_width=0.0, uv_scale=(16.0, 12.0))

    # Franja de circulación central despejada de punta a punta
    add_box("Corridor_CenterStripe", (-0.5, 0, 0.003), (RX - 2.0, 2.2, 0.004), mats["corridor_stripe"], bevel_width=0.0)
    add_box("Corridor_BorderNorth", (-0.5, 1.15, 0.004), (RX - 2.0, 0.08, 0.004), mats["corridor_border"], bevel_width=0.0)
    add_box("Corridor_BorderSouth", (-0.5, -1.15, 0.004), (RX - 2.0, 0.08, 0.004), mats["corridor_border"], bevel_width=0.0)

    # 2. TECHO ACÚSTICO Y PANELES LED EMPOTRADOS
    add_box("Ward_Ceiling", (0, 0, RZ + 0.10), (RX, RY, 0.20), mats["ceiling"], bevel_width=0.0)

    for lx in [-7.5, -2.5, 2.5, 7.5]:
        for ly in [-5.0, 0.0, 5.0]:
            add_box(f"Troffer_Frame_{lx}_{ly}", (lx, ly, RZ - 0.01), (1.6, 0.8, 0.03), mats["steel"], bevel_width=0.005)
            add_box(f"Troffer_LED_{lx}_{ly}", (lx, ly, RZ - 0.025), (1.48, 0.68, 0.02), mats["led_panel"], bevel_width=0.0)

    for bx_beam in [-3.5, 3.5]:
        add_box(f"Ceiling_Beam_{bx_beam}", (bx_beam, 0, RZ - 0.08), (0.28, RY, 0.16), mats["wall_upper"], bevel_width=0.01)

    # 3. MUROS PERIMETRALES
    for side, y_pos, in_sign in [("North", RY / 2, -1.0), ("South", -RY / 2, 1.0)]:
        add_box(f"Baseboard_{side}", (0, y_pos + 0.13 * in_sign, 0.08), (RX, 0.04, 0.16), mats["baseboard"], bevel_width=0.005)
        add_box(f"Wall_Wainscot_{side}", (0, y_pos, 0.65), (RX, 0.24, 1.30), mats["wall_wainscot"], bevel_width=0.01)
        add_box(f"Wall_Upper_{side}", (0, y_pos, 2.55), (RX, 0.24, 2.50), mats["wall_upper"], bevel_width=0.01)
        add_box(f"BumperRail_{side}", (0, y_pos + 0.14 * in_sign, 0.92), (RX - 0.6, 0.04, 0.14), mats["steel"], bevel_width=0.01)

    for side, x_pos, in_sign in [("West", -RX / 2, 1.0), ("East", RX / 2, -1.0)]:
        add_box(f"Baseboard_{side}", (x_pos + 0.13 * in_sign, 0, 0.08), (0.04, RY, 0.16), mats["baseboard"], bevel_width=0.005)
        add_box(f"Wall_Wainscot_{side}", (x_pos, 0, 0.65), (0.24, RY, 1.30), mats["wall_wainscot"], bevel_width=0.01)
        add_box(f"Wall_Upper_{side}", (x_pos, 0, 2.55), (0.24, RY, 2.50), mats["wall_upper"], bevel_width=0.01)
        add_box(f"BumperRail_{side}", (x_pos + 0.14 * in_sign, 0, 0.92), (0.04, RY - 0.6, 0.14), mats["steel"], bevel_width=0.01)

        # Puertas Dobles Hospitalarias (Sobresaliendo limpiamente 16cm hacia adentro del muro)
        door_x = x_pos + 0.15 * in_sign
        add_box(f"DoorFrame_{side}", (door_x, 0, 1.25), (0.08, 2.50, 2.50), mats["steel"], bevel_width=0.01)
        for d_idx, dy in enumerate([-0.58, 0.58]):
            add_box(f"DoorLeaf_{side}_{d_idx}", (door_x + 0.01 * in_sign, dy, 1.22), (0.05, 1.12, 2.40), mats["teal_plastic"], bevel_width=0.01)
            add_box(f"DoorWindow_{side}_{d_idx}", (door_x + 0.035 * in_sign, dy, 1.62), (0.02, 0.36, 0.55), mats["glass_window"], bevel_width=0.005)
            add_box(f"DoorKickplate_{side}_{d_idx}", (door_x + 0.035 * in_sign, dy, 0.22), (0.02, 1.06, 0.36), mats["steel"], bevel_width=0.005)
            add_box(f"DoorPushBar_{side}_{d_idx}", (door_x + 0.05 * in_sign, dy, 1.02), (0.04, 0.85, 0.04), mats["steel"], bevel_width=0.008)

        add_box(f"ExitSign_{side}", (door_x + 0.03 * in_sign, 0, 2.68), (0.06, 0.85, 0.22), mats["exit_green"], bevel_width=0.005)

        # Ventanales clínicos luminosos con marco metálico
        for wy in [-5.2, 5.2]:
            add_box(f"WindowFrame_{side}_{wy}", (door_x, wy, 2.25), (0.08, 2.8, 1.45), mats["steel"], bevel_width=0.01)
            add_box(f"WindowGlass_{side}_{wy}", (door_x + 0.035 * in_sign, wy, 2.25), (0.02, 2.65, 1.30), mats["glass_window"], bevel_width=0.0)

    # 4. CONSTRUCCIÓN DE LAS 6 BAHÍAS DE PACIENTES
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

    # 5. CORTINAS DIVISORIAS DE PRIVACIDAD ENTRE CUBÍCULOS
    for div_x in [-3.5, 3.5]:
        add_box(f"CurtainRail_North_{div_x}", (div_x, 5.5, RZ - 0.18), (0.04, 6.2, 0.04), mats["steel"], bevel_width=0.005)
        add_box(f"CurtainRail_South_{div_x}", (div_x, -5.5, RZ - 0.18), (0.04, 6.2, 0.04), mats["steel"], bevel_width=0.005)
        create_pleated_curtain(f"Curtain_North_{div_x}", div_x, 4.4, 8.6, 0.35, RZ - 0.20, mats["curtain"])
        create_pleated_curtain(f"Curtain_South_{div_x}", div_x, -8.6, -4.4, 0.35, RZ - 0.20, mats["curtain"])

    # 6. ESTACIÓN DE CONTROL Y TRIAJE DE ENFERMERÍA (Al fondo Este del corredor: X = +9.8, Y = 0)
    # Así el corredor central queda 100% libre y simétrico mirando desde la entrada Oeste
    st_x, st_y = 9.8, 0.0
    add_box("NurseStation_Body", (st_x, st_y, 0.52), (1.3, 3.4, 1.04), mats["white_plastic"], bevel_width=0.02)
    add_box("NurseStation_FrontPanel", (st_x - 0.66, st_y, 0.50), (0.04, 3.2, 0.85), mats["teal_plastic"], bevel_width=0.01)
    add_box("NurseStation_Counter", (st_x, st_y, 1.06), (1.45, 3.6, 0.05), mats["steel"], bevel_width=0.01)

    for m_dy in [-0.75, 0.75]:
        add_box(f"Desk_Monitor_{m_dy}", (st_x - 0.20, st_y + m_dy, 1.28), (0.08, 0.52, 0.34), mats["dark_metal"], bevel_width=0.01)
        # Pantalla mirando hacia el corredor Oeste (-X -> rot_z = -pi/2)
        add_screen_plane(
            f"Desk_ScreenPlane_{m_dy}",
            (st_x - 0.25, st_y + m_dy, 1.28),
            0.46, 0.29,
            mats["ecg_screen"],
            rot_z=-math.pi / 2
        )

    # 7. CARROS DE PARO CARDIORRESPIRATORIO (ACLS CRASH CARTS)
    for cart_idx, (cx, cy) in enumerate([(-3.9, 7.8), (3.9, 7.8)]):
        add_box(f"CrashCart_Body_{cart_idx}", (cx, cy, 0.52), (0.72, 0.56, 0.88), mats["crash_red"], bevel_width=0.015)
        add_box(f"CrashCart_Top_{cart_idx}", (cx, cy, 0.98), (0.76, 0.60, 0.04), mats["steel"], bevel_width=0.01)
        add_box(f"CrashCart_Defib_{cart_idx}", (cx, cy, 1.14), (0.34, 0.28, 0.26), mats["dark_metal"], bevel_width=0.01)
        add_cylinder(f"CrashCart_O2_{cart_idx}", (cx + 0.42, cy, 0.55), 0.07, 0.68, mats["gas_o2"])


def render_verification_preview(preview_path: Path):
    scene = bpy.context.scene

    for lx in [-7.0, 0.0, 7.0]:
        for ly in [-3.5, 3.5]:
            light_data = bpy.data.lights.new(name=f"PreviewLight_{lx}_{ly}", type='POINT')
            light_data.energy = 380.0
            light_data.shadow_soft_size = 0.8
            light_obj = bpy.data.objects.new(name=f"PreviewLight_{lx}_{ly}", object_data=light_data)
            bpy.context.collection.objects.link(light_obj)
            light_obj.location = (lx, ly, 3.4)

    # Cámara en la posición inicial exacta del jugador (-9.2, 0, 1.68) mirando por el corredor (+X)
    cam_data = bpy.data.cameras.new(name="VerificationCam")
    cam_data.lens = 22.0
    cam_obj = bpy.data.objects.new(name="VerificationCam", object_data=cam_data)
    bpy.context.collection.objects.link(cam_obj)
    cam_obj.location = (-9.2, 0.0, 1.68)
    cam_obj.rotation_euler = (math.radians(88.0), 0.0, math.radians(-90.0))
    scene.camera = cam_obj

    scene.render.engine = 'BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items.keys() else 'BLENDER_EEVEE'
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.filepath = str(preview_path)
    bpy.ops.render.render(write_still=True)
    print(f"Render de verificación guardado en: {preview_path}")

    bpy.data.objects.remove(cam_obj, do_unlink=True)
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

from netgen.occ import *
from ngsolve import *
from collections import defaultdict
from ngsolve.internal import visoptions, viewoptions, Rotate, Zoom
from quantiphy import Quantity
from PIL import Image, ImageDraw, ImageFont
import ffmpeg
import os, shutil, csv
import netgen.gui
import numpy as np
import math
import gc

ngsglobals.msg_level = -1
SetNumThreads(5)

os.makedirs("tmp", exist_ok=True)

def simulate(x, phi, filename, permittivity, meshfaktor):
    pivot = Pnt(0,0,x)
    rot_axis = Axis(pivot,Vec(0,1,0))

    phi_rad = math.radians(phi)
    tilt_normal = Vec(math.sin(phi_rad),0,math.cos(phi_rad))

    minus = Box( Pnt(-5.5,-5.5,-0.08), Pnt(5.5,5.5,0) ).bc("minus").mat("Alu")
    plus = Box(Pnt(-5.5,-5.5,x), Pnt(5.5,5.5,(x+0.08))).bc("plus").mat("Alu")
    unten = Box((-8,-8,-3), Pnt(8,8,0)).bc("unten").mat("PLA")-minus
    oben = Box((-8,-8,x), Pnt(8,8,(x+3))).bc("oben").mat("PLA")-plus
    
    weight = Box(Pnt(-5,-5,(x+3)),Pnt(5,5,(x+5))).bc("weight").mat("XXX")

    pl = plus.Rotate(rot_axis,phi)
    ob = oben.Rotate(rot_axis,phi)
    wei = weight.Rotate(rot_axis,phi)

    inside = Box( Pnt(-5.5,-5.5,0), Pnt(5.5,5.5,x+5))
    cut = HalfSpace(pivot,tilt_normal)
    ins = (inside*cut-pl-ob).bc("inside").mat("KST")
    
    h = 5
    r = 1
    master_zyl = Cylinder(Pnt(0, 0, 0), Vec(0, 0, 1), r, h)
    
    pos = 6.8
    verschiebungen = [
        Vec(pos, pos, 0),
        Vec(pos, -pos, 0),
        Vec(-pos, pos, 0),
        Vec(-pos, -pos, 0)
    ]

    zyl_list = []
    for v in verschiebungen:
        zyl_list.append(master_zyl.Move(v))

    zyl_fused = zyl_list[0]
    for z in zyl_list[1:]:
        zyl_fused = zyl_fused + z
        
    u_ob = (unten + zyl_fused).bc("unten").mat("PLA")
    o_ob = (ob - zyl_fused-pl).bc("oben").mat("PLA")

    air = Sphere(Pnt(0, 0, 0), 18) -(pl + minus + u_ob + o_ob + ins + wei)
    air = air.mat("air")

    inside.maxh = 1
    u_ob.maxh = 1
    o_ob.maxh = 1
 
    minus.edges.maxh = 1
    inside.vertices.hpref = 1
    minus.faces.Max(Z).edges.hpref = 1
    pl.faces.Max(Z).edges.hpref = 1

    u_ob.edges.hpref = 1
    u_ob.vertices.hpref = 1
    u_ob.faces.Max(Z).edges.hpref = 1
    o_ob.faces.Max(Z).edges.hpref = 1

    geo = OCCGeometry(Glue([air, minus, pl, o_ob, u_ob,ins,wei]))
    mesh = Mesh(geo.GenerateMesh(maxh=2))
    Draw(mesh)
    mesh.Curve(1)
    mesh.RefineHP(meshfaktor)

    diel_perm = defaultdict(lambda: -1)
    diel_perm["air"] = 1.0
    diel_perm["KST"] = 2.5
    diel_perm["PLA"] = 3.0
    diel_perm["XXX"] = permittivity
    diel_perm_cf = CoefficientFunction([ diel_perm[mat] for mat in mesh.GetMaterials() ] )

    voltage = 4
    potential = defaultdict(lambda: 0)
    potential["plus"] = voltage/2
    potential["minus"] = -voltage/2
    potential_cf = [ potential[bnd] for bnd in mesh.GetBoundaries() ]
    potential_str = "plus|minus"

    dirichlet_str = "air|plus|minus|ob|u_ob|ins|wei"

    eps0 = 8.8541878128E-12
    scale = 0.01 #=> Geometrie Angaben in Zentimeter


    fes = H1(mesh, order=3, dirichlet=dirichlet_str)
    (ut,vt) = fes.TnT()
    a = BilinearForm(fes)
    a += diel_perm_cf*grad(ut)*grad(vt)*dx
    a.Assemble()

    u = GridFunction(fes, name="Potential")
    u.Set(potential_cf, definedon=mesh.Boundaries(potential_str))
    f = u.vec.CreateVector()
    f.data = a.mat * u.vec
    u.vec.data -= a.mat.Inverse(fes.FreeDofs(), inverse="sparsecholesky") * f

    E = -Grad(u)/scale

    cap = eps0*Integrate(E*E*diel_perm_cf, mesh, VOL) / voltage**2 *scale*scale*scale

    if filename is not None:
        fileName1 = "tmp/ef.png"
        fileName2 = "tmp/p.png"

        Draw(u)
        Rotate(-60,160)
        Zoom(50)
        viewoptions.clipping.enable = 1
        visoptions.clipsolution = "scal"
        visoptions.usetexture = 1
        visoptions.lineartexture = 1
        viewoptions.drawnetgenlogo = 0
        visoptions.autoscale = 0
        visoptions.mmaxval = 2
        visoptions.mminval = -2
        viewoptions.clipping.onlydomain = 1

        netgen.Redraw(blocking=True, fr=1e8)
        image = netgen.libngguipy.Snapshot(10,10)
        netgen.gui.Snapshot(w=950,h=1020, filename=fileName1)
        
        Draw(E, mesh, "E")
        visoptions.scalfunction = "E:0"
        visoptions.autoscale = 0
        visoptions.mmaxval = 100
        visoptions.mminval = 0
        viewoptions.clipping.onlydomain = 0

        netgen.Redraw(blocking=True, fr=1e8)
        image = netgen.libngguipy.Snapshot(10,10)
        netgen.gui.Snapshot(w=950,h=1020, filename=fileName2)



        im1 = Image.open(fileName1)
        draw = ImageDraw.Draw(im1)
        draw.text((im1.width/2, im1.height*0.95), "Ele. Potential", anchor="mm", fill =(0, 0, 0), font=ImageFont.truetype('Sanford.ttf', 24))

        im2 = Image.open(fileName2)
        draw = ImageDraw.Draw(im2)
        draw.text((im2.width/2, im2.height*0.95), "Betrag der ele. Feldstärke", anchor="mm", fill =(0, 0, 0), font=ImageFont.truetype('Sanford.ttf', 24))

        dst = Image.new('RGB', (im1.width + im2.width+20, im1.height))
        dst.paste(im1, (0, 0))
        dst.paste(im2, (im1.width+20, 0))

        draw = ImageDraw.Draw(dst)
        draw.text((im1.width + im2.width+20, 3), "Abstand="+str(x)+" cm C="+str(Quantity(str(cap), 'F')), anchor="rt", fill =(0, 0, 0), font=ImageFont.truetype('Sanford.ttf', 24))
        
        dst.save(filename)    
        
        im1.close()
        im2.close()
        dst.close()
        
    return cap


with open('capacity_angle_sweep.csv', 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    csvwriter.writerow(["Distance","Angle", "Capacity","Meshfaktor"]) 
    
    caps = []
    meshfaktor = 2
    

    for index, angle in enumerate(np.linspace(0, 5, 10)): 
        frame_filename = f"tmp/s{index:03d}.png"
        
        cap = simulate(0.5, angle, frame_filename, 1, meshfaktor)
        
        caps.append(cap)
        csvwriter.writerow([0.5, angle, cap, meshfaktor])
        csvfile.flush()
        gc.collect()

try:
    (
        ffmpeg
        .input("tmp/s%03d.png", framerate=2, start_number=0)
        .output("capacity_sweep.mp4", pix_fmt='yuv420p', vcodec='libx264', crf=23)
        .run(overwrite_output=True, quiet=True)
    )
    print("'capacity_sweep.mp4' gespeichert")
except ffmpeg.Error as e:
    print("ehler bei der Videoerstellung:", e.stderr.decode('utf8') if e.stderr else e)


shutil.rmtree("tmp", ignore_errors=True)
print("Fertig")
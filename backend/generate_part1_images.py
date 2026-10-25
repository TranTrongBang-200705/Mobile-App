import os
from PIL import Image, ImageDraw, ImageFont

os.makedirs("pcat/image_cache", exist_ok=True)

def draw_lab_scene():
    width, height = 800, 560
    img = Image.new("RGB", (width, height), color=(240, 244, 248))
    draw = ImageDraw.Draw(img)

    # Background wall & tile pattern
    draw.rectangle([0, 0, width, 320], fill=(230, 238, 245))
    for y in range(40, 320, 40):
        draw.line([0, y, width, y], fill=(215, 225, 235), width=1)
    for x in range(40, width, 60):
        draw.line([x, 0, x, 320], fill=(215, 225, 235), width=1)

    # Shelf on the wall
    draw.rectangle([50, 80, 750, 95], fill=(180, 190, 200), outline=(140, 150, 160), width=2)
    # Chemical bottles on shelf
    bottle_colors = [(65, 131, 215), (38, 166, 154), (239, 108, 0), (142, 68, 173), (46, 204, 113)]
    for i, col in enumerate(bottle_colors):
        bx = 100 + i * 130
        draw.rectangle([bx, 45, bx + 35, 80], fill=col, outline=(50, 50, 50), width=1)
        draw.rectangle([bx + 10, 35, bx + 25, 45], fill=(200, 200, 200), outline=(50, 50, 50), width=1)
        draw.rectangle([bx + 5, 55, bx + 30, 70], fill=(255, 255, 255)) # Label

    # Lab Bench / Countertop
    draw.rectangle([0, 320, width, 560], fill=(210, 218, 226))
    draw.rectangle([0, 320, width, 345], fill=(74, 105, 189)) # Surface edge
    # Cabinets under bench
    for cx in [20, 280, 540]:
        draw.rectangle([cx, 360, cx + 240, 540], fill=(189, 195, 199), outline=(127, 140, 141), width=2)
        draw.ellipse([cx + 215, 440, cx + 225, 450], fill=(44, 62, 80)) # Handles

    # Lab Glassware & Equipment on bench
    # Erlenmeyer Flask
    draw.polygon([(100, 320), (160, 320), (138, 240), (122, 240)], fill=(220, 240, 255, 180), outline=(52, 73, 94), width=2)
    draw.rectangle([122, 225, 138, 240], fill=(220, 240, 255), outline=(52, 73, 94), width=2)
    draw.polygon([(106, 318), (154, 318), (142, 275), (118, 275)], fill=(52, 152, 219)) # Liquid

    # Test Tube Rack
    draw.rectangle([200, 280, 320, 320], fill=(211, 84, 0), outline=(150, 60, 0), width=2)
    for i in range(5):
        tx = 215 + i * 22
        tcol = [(231, 76, 60), (46, 204, 113), (155, 89, 182), (241, 196, 15), (52, 152, 219)][i]
        draw.rectangle([tx, 220, tx + 14, 310], fill=(240, 248, 255), outline=(50, 50, 50), width=1)
        draw.rectangle([tx, 250, tx + 14, 308], fill=tcol) # Fluid

    # Microscope
    draw.rectangle([380, 300, 480, 320], fill=(44, 62, 80)) # Base
    draw.rectangle([450, 200, 475, 300], fill=(52, 73, 94)) # Arm
    draw.ellipse([395, 230, 455, 250], fill=(127, 140, 141), outline=(44, 62, 80), width=2) # Stage
    draw.polygon([(410, 160), (450, 200), (435, 215), (395, 175)], fill=(44, 62, 80)) # Tube
    draw.rectangle([390, 150, 415, 168], fill=(189, 195, 199)) # Eyepiece

    # Researcher (Scientist in Lab Coat)
    # Head & Safety Goggles
    draw.ellipse([580, 150, 640, 210], fill=(245, 205, 178)) # Face
    draw.ellipse([575, 140, 645, 180], fill=(50, 40, 30)) # Hair
    draw.rectangle([585, 170, 635, 185], fill=(174, 214, 241), outline=(41, 128, 185), width=2) # Goggles
    draw.line([575, 177, 645, 177], fill=(41, 128, 185), width=2) # Strap
    # White Lab Coat
    draw.polygon([(560, 220), (660, 220), (680, 370), (540, 370)], fill=(255, 255, 255), outline=(180, 190, 200), width=2)
    draw.line([610, 220, 610, 370], fill=(200, 200, 200), width=2) # Seam
    # Arms holding clipboard/pen
    draw.polygon([(540, 240), (570, 310), (590, 290), (560, 230)], fill=(255, 255, 255), outline=(180, 190, 200), width=2)
    draw.rectangle([570, 280, 620, 330], fill=(139, 69, 19), outline=(90, 40, 10), width=2) # Clipboard
    draw.rectangle([575, 285, 615, 325], fill=(255, 255, 255)) # Paper notes

    # Caption Banner
    draw.rectangle([0, 510, width, 560], fill=(30, 41, 59))
    draw.text((20, 522), "TOEIC PART 1 - PHOTOGRAPH: RESEARCH LABORATORY EXPERIMENT", fill=(255, 255, 255))

    img.save("pcat/image_cache/0.png")
    print("Saved pcat/image_cache/0.png")


def draw_construction_scene():
    width, height = 800, 560
    img = Image.new("RGB", (width, height), color=(220, 235, 245)) # Sky
    draw = ImageDraw.Draw(img)

    # Distant skyline / construction frame
    draw.rectangle([0, 280, width, 560], fill=(160, 150, 135)) # Ground dirt / concrete
    # Steel frame building
    for col_x in [100, 220, 340, 460]:
        draw.rectangle([col_x, 60, col_x + 16, 320], fill=(192, 57, 43)) # Orange/red steel beam
    for beam_y in [90, 170, 250]:
        draw.rectangle([80, beam_y, 480, beam_y + 14], fill=(192, 57, 43))
    # Scaffolding cross-bracing
    for i in range(3):
        x1 = 100 + i * 120
        x2 = x1 + 120
        draw.line([x1, 90, x2, 170], fill=(211, 84, 0), width=3)
        draw.line([x1, 170, x2, 90], fill=(211, 84, 0), width=3)
        draw.line([x1, 170, x2, 250], fill=(211, 84, 0), width=3)
        draw.line([x1, 250, x2, 170], fill=(211, 84, 0), width=3)

    # Tower crane in distance
    draw.rectangle([680, 40, 695, 300], fill=(243, 156, 18))
    draw.rectangle([550, 40, 780, 52], fill=(243, 156, 18))
    draw.line([688, 40, 580, 48], fill=(100, 100, 100), width=2)
    draw.line([688, 40, 760, 48], fill=(100, 100, 100), width=2)
    draw.line([600, 52, 600, 120], fill=(50, 50, 50), width=2) # Cable
    draw.rectangle([595, 120, 605, 130], fill=(50, 50, 50)) # Hook

    # Safety cones on ground
    for cone_x in [80, 220, 720]:
        draw.polygon([(cone_x + 15, 360), (cone_x + 30, 410), (cone_x, 410)], fill=(230, 81, 0))
        draw.rectangle([cone_x + 6, 385, cone_x + 24, 395], fill=(255, 255, 255))
        draw.rectangle([cone_x - 4, 410, cone_x + 34, 416], fill=(50, 50, 50))

    # Foreground Engineer / Inspector examining Blueprint
    # Safety Helmet (Hard Hat)
    draw.ellipse([430, 180, 490, 225], fill=(255, 214, 0), outline=(200, 160, 0), width=2)
    draw.rectangle([420, 215, 500, 225], fill=(255, 214, 0), outline=(200, 160, 0), width=2) # Brim
    # Face
    draw.ellipse([438, 215, 482, 260], fill=(245, 205, 178))
    # Safety Vest & Torso
    draw.polygon([(410, 260), (510, 260), (530, 420), (390, 420)], fill=(255, 109, 0)) # Fluorescent Orange
    # Reflective silver stripes on vest
    draw.rectangle([425, 265, 440, 415], fill=(238, 238, 238), outline=(189, 189, 189), width=1)
    draw.rectangle([480, 265, 495, 415], fill=(238, 238, 238), outline=(189, 189, 189), width=1)
    draw.rectangle([395, 350, 525, 365], fill=(238, 238, 238), outline=(189, 189, 189), width=1)

    # Blueprints held open in both hands
    draw.polygon([(360, 310), (480, 320), (470, 390), (350, 380)], fill=(41, 128, 185), outline=(21, 67, 96), width=2) # Blueprint sheet
    # Blueprint lines / architectural schematics
    for ly in [330, 345, 360, 375]:
        draw.line([370, ly, 460, ly + 8], fill=(255, 255, 255), width=2)
    draw.rectangle([385, 335, 425, 365], outline=(255, 255, 255), width=1)
    # Hands holding blueprint
    draw.ellipse([345, 340, 365, 360], fill=(245, 205, 178))
    draw.ellipse([465, 350, 485, 370], fill=(245, 205, 178))

    # Caption Banner
    draw.rectangle([0, 510, width, 560], fill=(30, 41, 59))
    draw.text((20, 522), "TOEIC PART 1 - PHOTOGRAPH: EXAMINING BLUEPRINT AT CONSTRUCTION SITE", fill=(255, 255, 255))

    img.save("pcat/image_cache/1.png")
    print("Saved pcat/image_cache/1.png")


def draw_railway_scene():
    width, height = 800, 560
    img = Image.new("RGB", (width, height), color=(210, 230, 245)) # Afternoon sky
    draw = ImageDraw.Draw(img)

    # Railway tracks (Left side)
    draw.polygon([(0, 280), (300, 280), (220, 560), (0, 560)], fill=(90, 85, 80)) # Gravel ballast
    # Rails
    draw.line([40, 280, 20, 560], fill=(189, 195, 199), width=5)
    draw.line([160, 280, 110, 560], fill=(189, 195, 199), width=5)
    # Railway ties / sleepers
    for ty in range(290, 550, 22):
        draw.line([10, ty, 190, ty], fill=(62, 39, 35), width=4)

    # Platform Edge & Surface (Right side)
    draw.polygon([(300, 280), (width, 280), (width, 560), (220, 560)], fill=(200, 205, 210))
    # Yellow Safety Line along platform edge
    draw.line([298, 280, 218, 560], fill=(255, 214, 0), width=10)

    # Overhead Platform Canopy / Roof
    draw.polygon([(260, 40), (width, 40), (width, 100), (280, 120)], fill=(52, 73, 94))
    # Canopy Support Pillars
    draw.rectangle([420, 100, 436, 400], fill=(44, 62, 80))
    draw.rectangle([680, 100, 696, 400], fill=(44, 62, 80))

    # Electronic Departure Board hanging from canopy
    draw.rectangle([480, 90, 620, 150], fill=(20, 20, 20), outline=(100, 100, 100), width=2)
    draw.text((490, 98), "PLATFORM 2", fill=(255, 214, 0))
    draw.text((490, 115), "14:15 EXPRESS", fill=(46, 204, 113))
    draw.text((490, 132), "ON TIME", fill=(255, 255, 255))

    # Clock on pillar
    draw.ellipse([405, 130, 451, 176], fill=(255, 255, 255), outline=(50, 50, 50), width=3)
    draw.line([428, 153, 428, 140], fill=(0, 0, 0), width=2) # Hour
    draw.line([428, 153, 442, 153], fill=(0, 0, 0), width=2) # Min

    # Commuter 1 with Rolling Suitcase
    # Suitcase
    draw.rectangle([340, 380, 375, 450], fill=(192, 57, 43), outline=(100, 20, 20), width=2)
    draw.rectangle([353, 345, 362, 380], fill=(120, 120, 120), width=2) # Handle
    draw.ellipse([343, 448, 351, 456], fill=(20, 20, 20)) # Wheel
    draw.ellipse([364, 448, 372, 456], fill=(20, 20, 20)) # Wheel
    # Person 1 (Standing waiting)
    draw.ellipse([375, 240, 405, 275], fill=(245, 205, 178)) # Head
    draw.rectangle([368, 275, 412, 370], fill=(41, 128, 185)) # Navy Coat
    draw.line([380, 370, 380, 445], fill=(52, 73, 94), width=7) # Leg 1
    draw.line([400, 370, 400, 445], fill=(52, 73, 94), width=7) # Leg 2

    # Commuter 2 (Sitting/Standing with Duffel Bag)
    draw.ellipse([540, 250, 570, 285], fill=(245, 205, 178))
    draw.rectangle([535, 285, 575, 370], fill=(108, 92, 231))
    draw.line([545, 370, 545, 440], fill=(45, 52, 54), width=7)
    draw.line([565, 370, 565, 440], fill=(45, 52, 54), width=7)
    # Duffel Bag on Ground
    draw.ellipse([585, 395, 635, 435], fill=(46, 204, 113), outline=(20, 100, 50), width=2)

    # Caption Banner
    draw.rectangle([0, 510, width, 560], fill=(30, 41, 59))
    draw.text((20, 522), "TOEIC PART 1 - PHOTOGRAPH: COMMUTERS WAITING ON TRAIN PLATFORM", fill=(255, 255, 255))

    img.save("pcat/image_cache/2.png")
    print("Saved pcat/image_cache/2.png")


if __name__ == "__main__":
    draw_lab_scene()
    draw_construction_scene()
    draw_railway_scene()
    print("All Part 1 images generated successfully.")

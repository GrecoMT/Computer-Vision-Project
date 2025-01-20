import os
import xml.etree.ElementTree as ET

# Percorsi delle directory
images_dir = "path-to-frames"
annotations_dir = "path-to-annotations"
labels_dir = "path-to-labels"
os.makedirs(labels_dir, exist_ok=True)


IMAGE_WIDTH = 1920
IMAGE_HEIGHT = 1088

# bounding box (25x25 pixel normalizzate)
BOX_WIDTH = 25 / IMAGE_WIDTH  
BOX_HEIGHT = 25 / IMAGE_HEIGHT  

# Trova tutti i frame disponibili con il suffisso (_1)
image_files = [f.split(".")[0] for f in os.listdir(images_dir) if f.endswith(".png") or f.endswith(".jpg")]
annotated_frames = set()

# Leggi i file XML
for xml_file in os.listdir(annotations_dir):
    if not xml_file.endswith(".xml") or xml_file.startswith("._"):
        continue
    
    video_id = os.path.splitext(xml_file)[0].split("-")[1]  # Estrai il suffisso dal nome del video
    xml_path = os.path.join(annotations_dir, xml_file)
    print(f"Processing {xml_file} with video_id: {video_id}...")
    
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"Errore durante la lettura del file XML: {xml_path}")
        print(e)
        exit(1)

    #frame
    for track in root.findall(".//track"):
        class_id = 0 

        #  frame
        for points in track.findall(".//points"):
            frame_id = int(points.get("frame"))
            coords = points.get("points")
            outside = points.get("outside")
            used_in_game = points.find("./attribute[@name='used_in_game']").text

            # Ignora annotazioni con outside="1" o used_in_game="0"
            if outside == "1" or used_in_game == "0":
                continue

            # Aggiungi il frame annotato all'elenco
            frame_name = f"frame_{frame_id:04d}_{video_id}"
            annotated_frames.add(frame_name)

            # Estrai coordinate
            x, y = map(float, coords.split(","))

            # Normalizza le coordinate del centro
            x_center = x / IMAGE_WIDTH
            y_center = y / IMAGE_HEIGHT

            # Crea annotazione YOLO
            label_file = os.path.join(labels_dir, f"{frame_name}.txt")
            with open(label_file, "a") as f:
                f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {BOX_WIDTH:.6f} {BOX_HEIGHT:.6f}\n")

# Genera file vuoti per i frame non annotati (frame senza palla)
for image_file in image_files:
    # Rimuove l'estensione e verifica il suffisso
    frame_base = image_file
    label_file = os.path.join(labels_dir, f"{frame_base}.txt")
    if frame_base not in annotated_frames:
        open(label_file, "w").close()  # Crea un file vuoto

print("Conversione completata!")

import os
import shutil
from PIL import Image

website_dir = r'H:\Meu Drive\(011)BUREAU_CRIATIVO_AUTORAL\WEBSITE'
assets_dir = os.path.join(website_dir, 'assets')

# -------------------------------------------------------------------------
# 1. SYNC ATO 01 (REVISTA HYB) WITH EXACT 24 ORDERED PAGES + GENERATE 24-PAGE PDF
# -------------------------------------------------------------------------
hyb_finais_src = r'H:\Meu Drive\(009) PROJETO O ESTRANGEIRO - TCC\03_LIVRO_DE_ARTE\Projeto_Editorial\REVISTA HYB - LATE NIGHT TALES\REVISTA HYB - FINAIS'
hyb_dst_dir = os.path.join(assets_dir, 'revista_hyb')

hyb_ordered_sources = [
    (1,  'HYB_ED01_PAG_01_CAPA.png',             '01_HYB_ED01_PAG_01_CAPA.png'),
    (2,  'HYB_ED01_PAG_02_CONTRA CAPA.png',      '02_HYB_ED01_PAG_02_CONTRA_CAPA.png'),
    (3,  'HYB_ED01_PAG_03-Nota do Editor.png',   '03_HYB_ED01_PAG_03_NOTA_DO_EDITOR.png'),
    (4,  'HYB_ED01_PAG_04_A_FLOR_DESOSSADA.png', '04_HYB_ED01_PAG_04_A_FLOR_DESOSSADA.png'),
    (5,  'HYB_ED01_PAG_05_cacto.png',            '05_HYB_ED01_PAG_05_CACTO.png'),
    (6,  'HYB_ED01_PAG_06_protea.png',           '06_HYB_ED01_PAG_06_PROTEA.png'),
    (7,  'HYB_ED01_PAG_07_bananas.png',          '07_HYB_ED01_PAG_07_BANANAS.png'),
    (8,  'HYB_ED01_PAG_08_reginai.png',          '08_HYB_ED01_PAG_08_REGINAE.png'),
    (9,  'HYB_ED01_PAG_09_papoula.png',          '09_HYB_ED01_PAG_09_PAPOULA.png'),
    (10, 'HYB_ED01_PAG_10.png',                  '10_HYB_ED01_PAG_10.png'),
    (11, 'HYB_ED01_PAG_11.png',                  '11_HYB_ED01_PAG_11.png'),
    (12, 'HYB_ED01_PAG_12.png',                  '12_HYB_ED01_PAG_12.png'),
    (13, 'HYB_ED01_PAG_13.png',                  '13_HYB_ED01_PAG_13.png'),
    (14, 'HYB_ED01_PAG_14.png',                  '14_HYB_ED01_PAG_14.png'),
    (15, 'HYB_ED01_PAG_15.png',                  '15_HYB_ED01_PAG_15.png'),
    (16, 'HYB_ED01_PAG_16.png',                  '16_HYB_ED01_PAG_16.png'),
    (17, 'HYB_ED01_PAG_17.png',                  '17_HYB_ED01_PAG_17.png'),
    (18, 'HYB_ED01_PAG_18.png',                  '18_HYB_ED01_PAG_18.png'),
    (19, 'HYB_ED01_PAG_19.png',                  '19_HYB_ED01_PAG_19.png'),
    (20, 'HYB_ED01_PAG_20.png',                  '20_HYB_ED01_PAG_20.png'),
    (21, 'HYB_ED01_PAG_21.png',                  '21_HYB_ED01_PAG_21.png'),
    (22, 'HYB_ED01_PAG_22.png',                  '22_HYB_ED01_PAG_22.png'),
    (23, 'HYB_ED01_PAG_23.png',                  '23_HYB_ED01_PAG_23.png'),
    (24, 'HYB_ED01_PAG_24.png',                  '24_HYB_ED01_PAG_24.png'),
]

# Clean old mixed files in WEBSITE/assets/revista_hyb/
if os.path.exists(hyb_dst_dir):
    for f in os.listdir(hyb_dst_dir):
        fp = os.path.join(hyb_dst_dir, f)
        if os.path.isfile(fp):
            os.remove(fp)
else:
    os.makedirs(hyb_dst_dir, exist_ok=True)

pdf_images = []
for page_num, src_name, dst_name in hyb_ordered_sources:
    src_path = os.path.join(hyb_finais_src, src_name)
    dst_path = os.path.join(hyb_dst_dir, dst_name)
    shutil.copy2(src_path, dst_path)
    # Prepare RGB image for the 24-page PDF
    with Image.open(dst_path) as im:
        rgb = im.convert('RGB')
        # Downscale slightly if huge so the PDF opens fast in browsers
        if rgb.width > 1240:
            new_h = int(rgb.height * (1240 / rgb.width))
            rgb = rgb.resize((1240, new_h), Image.Resampling.LANCZOS)
        pdf_images.append(rgb)

pdf_out_path = os.path.join(hyb_dst_dir, 'REVISTA_HYB_ED01_24_PAGINAS.pdf')
if pdf_images:
    pdf_images[0].save(
        pdf_out_path,
        "PDF",
        resolution=150.0,
        save_all=True,
        append_images=pdf_images[1:]
    )
print(f"Synced 24 ordered pages + compiled {pdf_out_path} ({os.path.getsize(pdf_out_path)} bytes)")

# -------------------------------------------------------------------------
# 2. REMOVE DUPLICATES IN ATO 05 (CARR THAIS & HILMA STORIES) AND ATO 02 (SHOES)
# -------------------------------------------------------------------------
thais_dir = os.path.join(assets_dir, 'bureau', '2026-10-02-CARR THAIS')
for dup_jpg in ['001.jpg', '002.jpg', '003.jpg', '004.jpg']:
    p = os.path.join(thais_dir, dup_jpg)
    if os.path.exists(p):
        os.remove(p)
        print(f"Removed duplicate in CARR THAIS: {dup_jpg}")

hilma_dir = os.path.join(assets_dir, 'bureau', '2026-10-15-CARR hilma de domingo')
dup_stories_in_hilma = os.path.join(hilma_dir, 'STORIES.png')
if os.path.exists(dup_stories_in_hilma):
    os.remove(dup_stories_in_hilma)
    print("Removed duplicate STORIES.png from 2026-10-15-CARR hilma de domingo (kept in 2026-10-16-Stories hilma)")

# Fix the swapped detail filenames in 2026-10-15-CARR hilma de domingo so folder order matches visual artwork pairs!
# Currently:
# - POST 02 -1080x1440 (1).png is the detail of POST 05 (No. 8 - Two Circles)
# - POST 05 -1080x1440 (2).png is the detail of POST 02 (No. 5 - Pink Flower)
p2_wrong = os.path.join(hilma_dir, 'POST 02 -1080x1440 (1).png')
p5_wrong = os.path.join(hilma_dir, 'POST 05 -1080x1440 (2).png')
p2_temp = os.path.join(hilma_dir, 'TEMP_SWAP_P2.png')
if os.path.exists(p2_wrong) and os.path.exists(p5_wrong):
    # Check if they haven't been swapped yet by sampling top-center pixel color
    # Pink flower (No. 5) has white/pink petals at top center (high R, high G, high B)
    with Image.open(p5_wrong) as im5:
        r, g, b = im5.convert('RGB').getpixel((im5.width // 2, 50))
    if r > 220 and g > 200 and b > 200:
        os.rename(p2_wrong, p2_temp)
        os.rename(p5_wrong, p2_wrong)
        os.rename(p2_temp, p5_wrong)
        print("Fixed swapped detail files in 2026-10-15-CARR hilma de domingo: POST 02 detail and POST 05 detail now match their framed paintings!")

# Remove exact duplicates in shoes/
shoes_dir = os.path.join(assets_dir, 'shoes')
for dup_shoe in ['015_SHOES_2.0_010.jpg', '016_SHOES_2.0_011.jpg']:
    sp = os.path.join(shoes_dir, dup_shoe)
    if os.path.exists(sp):
        os.remove(sp)
        print(f"Removed exact duplicate in shoes/: {dup_shoe}")

print("Asset cleanup and ordering completed successfully.")

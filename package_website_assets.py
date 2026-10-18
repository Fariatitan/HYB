import os
import shutil
import json
import re
import unicodedata

base_bureau = r'H:\Meu Drive\(011)BUREAU_CRIATIVO_AUTORAL'
website_dir = os.path.join(base_bureau, 'WEBSITE')
assets_dir = os.path.join(website_dir, 'assets')
os.makedirs(assets_dir, exist_ok=True)

# 1. Copy Cover
cover_src = os.path.join(base_bureau, '01_ESTRATÉGIA_E_POSICIONAMENTO', 'CAPA_CADERNO_DE_BRANDING_BUREAU_MONUMENTAL.jpg')
cover_dst_dir = os.path.join(assets_dir, 'cover')
os.makedirs(cover_dst_dir, exist_ok=True)
cover_dst = os.path.join(cover_dst_dir, 'CAPA_CADERNO_DE_BRANDING_BUREAU_MONUMENTAL.jpg')
shutil.copy2(cover_src, cover_dst)
print(f"Copied cover: {cover_dst}")

def sanitize_filename(filename):
    name, ext = os.path.splitext(filename)
    name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('ASCII')
    name = re.sub(r'[^\w\.-]', '_', name)
    name = re.sub(r'_+', '_', name).strip('_')
    return f"{name}{ext.lower()}"

cat_path = os.path.join(website_dir, 'curated_catalog.json')
with open(cat_path, 'r', encoding='utf-8') as f:
    cat = json.load(f)

copied_count = 0
standalone_catalog = {}

for cat_key, items in cat.items():
    cat_folder = os.path.join(assets_dir, cat_key)
    os.makedirs(cat_folder, exist_ok=True)
    
    limit = 24 if cat_key in ['acervo_materico', 'revista_hyb'] else 18
    new_items = []
    seen = set()
    idx = 1
    
    for it in items:
        full_src = os.path.normpath(os.path.join(base_bureau, it['path']))
        if not os.path.exists(full_src):
            continue
        if it['name'] in seen:
            continue
        seen.add(it['name'])
        
        clean_name = f"{idx:03d}_{sanitize_filename(it['name'])}"
        dst_path = os.path.join(cat_folder, clean_name)
        shutil.copy2(full_src, dst_path)
        
        rel_asset_path = f"assets/{cat_key}/{clean_name}"
        
        it_copy = dict(it)
        it_copy['path'] = rel_asset_path
        it_copy['local_asset_path'] = rel_asset_path
        it_copy['asset_filename'] = clean_name
        new_items.append(it_copy)
        
        copied_count += 1
        idx += 1
        if len(new_items) >= limit:
            break
            
    standalone_catalog[cat_key] = new_items
    print(f"Category [{cat_key}]: copied {len(new_items)} assets into assets/{cat_key}/")

print(f"\nTotal assets copied into WEBSITE/assets/: {copied_count + 1} (including cover)")

# Overwrite curated_catalog.json in WEBSITE with standalone paths
with open(os.path.join(website_dir, 'curated_catalog.json'), 'w', encoding='utf-8') as f:
    json.dump(standalone_catalog, f, indent=2, ensure_ascii=False)
print("Updated WEBSITE/curated_catalog.json with local asset paths.")

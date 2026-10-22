import os
import json
import re
from urllib.parse import quote, unquote
from PIL import Image

website_dir = r'H:\Meu Drive\(011) HYB - STUDIO\WEBSITE'
assets_dir = os.path.join(website_dir, 'assets')
catalog_path = os.path.join(website_dir, 'curated_catalog.json')

# -------------------------------------------------------------------------
# 1. CURATORIAL NAMING & METADATA ENGINE
# -------------------------------------------------------------------------

def encode_asset_url(rel_path: str) -> str:
    """Encode path segments for HTML src attributes while preserving slashes."""
    parts = rel_path.replace('\\', '/').split('/')
    return '/'.join(quote(p) for p in parts)

def get_aspect_label(w: int, h: int) -> str:
    ratio = w / h if h else 1.0
    if ratio < 0.30:
        return "PRANCHA CONTÍNUA"
    elif 0.52 <= ratio <= 0.60:
        return "9:16 VERTICAL"
    elif 0.64 <= ratio <= 0.72:
        return "2:3 EDITORIAL"
    elif 0.73 <= ratio <= 0.83:
        return "3:4 RETRATO"
    elif 0.90 <= ratio <= 1.10:
        return "1:1 QUADRADO"
    elif 1.25 <= ratio <= 1.40:
        return "4:3 HORIZONTAL"
    elif ratio > 1.65:
        return "16:9 PANORÂMICO"
    return "FORMATO NATIVO"

def curate_item_metadata(cat_key: str, rel_path: str, idx: int, w: int, h: int):
    filename = os.path.basename(rel_path)
    name_no_ext = os.path.splitext(filename)[0]
    parts = rel_path.replace('\\', '/').split('/')
    subfolder = parts[2] if len(parts) > 3 else ""

    aspect_badge = get_aspect_label(w, h)
    series_label = ""
    title = ""
    caption = ""

    if cat_key == 'revista_hyb':
        series_label = "ATO 01 // REVISTA HYB — LATE NIGHT TALES (24 PÁGINAS)"
        hyb_24_map = {
            "01_": ("PÁGINA 01 / 24 — CAPA OFICIAL (LATE NIGHT TALES)", "Capa inaugural da Revista HYB Ed. 001: arte, imagem, processo e noites."),
            "02_": ("PÁGINA 02 / 24 — CONTRA-CAPA & EXPEDIENTE", "Segunda capa, ficha catalográfica e abertura do volume."),
            "03_": ("PÁGINA 03 / 24 — NOTA DO EDITOR (DALLIDO.1988)", "Manifesto de abertura sobre permanência editorial e o ateliê híbrido."),
            "04_": ("PÁGINA 04 / 24 — A FLOR DESOSSADA (ABERTURA)", "Introdução ao ensaio de radiografia botânica e alta costura vegetal."),
            "05_": ("PÁGINA 05 / 24 — RAIO-X BOTÂNICO: CACTO ESTRUTURAL", "Dissecação luminosa de espinhos e arquitetura interna sob fundo abissal."),
            "06_": ("PÁGINA 06 / 24 — RAIO-X BOTÂNICO: PROTEA IMPERIAL", "Morfologia translúcida e densidade têxtil da inflorescência."),
            "07_": ("PÁGINA 07 / 24 — RAIO-X BOTÂNICO: BANANEIRA TROPICAL", "Fricção entre matéria orgânica brasileira e precisão clínica de laboratório."),
            "08_": ("PÁGINA 08 / 24 — RAIO-X BOTÂNICO: STRELITZIA REGINAE", "Geometria aguda e nervuras espectrais em câmara escura."),
            "09_": ("PÁGINA 09 / 24 — RAIO-X BOTÂNICO: PAPOULA NOTURNA", "Fechamento do caderno botânico: membranas florais em suspensão."),
            "10_": ("PÁGINA 10 / 24 — CADERNO SHOES: ABERTURA", "Do fetiche à matéria artesanal: início do dossiê de calçados-escultura."),
            "11_": ("PÁGINA 11 / 24 — CADERNO SHOES: LINHA DE FORÇA", "Estudo de curvatura, couro moldado e tensão sobre o solo."),
            "12_": ("PÁGINA 12 / 24 — CADERNO SHOES: PERFIL ESTRUTURAL", "Engenharia de salto e equilíbrio tratada como escultura contemporânea."),
            "13_": ("PÁGINA 13 / 24 — CADERNO SHOES: MATÉRIA & BRILHO", "Contraste especular e acabamento artesanal em estúdio."),
            "14_": ("PÁGINA 14 / 24 — CADERNO SHOES: TENSÃO MECÂNICA", "Diálogo entre ergonomia extrema e desenho autoral."),
            "15_": ("PÁGINA 15 / 24 — CADERNO SHOES: ENSAIO COMPLETO", "Diagramação vertical integrando fotografia de produto e tipografia técnica."),
            "16_": ("PÁGINA 16 / 24 — CADERNO SHOES: FECHAMENTO", "Síntese visual do arquivo de calçados da Edição 001."),
            "17_": ("PÁGINA 17 / 24 — CRÔNICA DE ATELIÊ & NOITE", "Transição narrativa para o caderno literário e documental da revista."),
            "18_": ("PÁGINA 18 / 24 — ENSAIO MACABÉA & IMAGEM", "Diálogo entre literatura, pintura e presença dramática."),
            "19_": ("PÁGINA 19 / 24 — DÍPTICO DOCUMENTAL I: A MÁSCARA QUE CAIU NA FARIA LIMA", "Crônica 32 — Parte A: o dado falso e a engenharia de sobrevivência."),
            "20_": ("PÁGINA 20 / 24 — DÍPTICO DOCUMENTAL II: A ROSA BRANCA DE VERÔNICA", "Crônica 32 — Parte B: o retorno da galeria e a verdade curatorial."),
            "21_": ("PÁGINA 21 / 24 — BOYS & A RUA: LAMBE-LAMBE I", "Abertura do caderno urbano: cartazismo, papel rasgado e muro."),
            "22_": ("PÁGINA 22 / 24 — BOYS & A RUA: LAMBE-LAMBE II", "Pop Art contemporânea, tipografia de choque e afeto urbano."),
            "23_": ("PÁGINA 23 / 24 — BOYS & A RUA: LAMBE-LAMBE III", "Colagem ácida de rua: o pôster como pele efêmera da cidade."),
            "24_": ("PÁGINA 24 / 24 — BOYS & A RUA: LAMBE-LAMBE IV (FECHAMENTO)", "Quarta capa e encerramento da Edição 001 — Late Night Tales.")
        }
        prefix = filename[:3]
        if prefix in hyb_24_map:
            title, caption = hyb_24_map[prefix]
        else:
            title = f"PÁGINA {idx:02d} / 24 — REVISTA HYB"
            caption = "Página oficial da Edição 001 (Late Night Tales) em sequência de leitura."

    elif cat_key == 'shoes':
        series_label = "ATO 02 // CADERNO SHOES — ESCULTURA & GRAVIDADE"
        shoes_map = {
            "001_": ("SHOES 2.0 — ARQUITETURA DE SALTO #05", "Pintura autoral e escultura de calçado tratada como objeto de equilíbrio."),
            "002_": ("CADERNO SHOES — PRANCHA EDITORIAL 10", "Do fetiche à matéria artesanal: anatomia de tensão sobre o solo."),
            "003_": ("CADERNO SHOES — PRANCHA EDITORIAL 11", "Estudo de curvatura, couro moldado e gravidade zero."),
            "004_": ("CADERNO SHOES — PRANCHA EDITORIAL 12", "Rigor construtivo entre modelagem de calçado e escultura contemporânea."),
            "005_": ("CADERNO SHOES — PRANCHA EDITORIAL 13", "Contraste especular sobre superfície negra de estúdio."),
            "006_": ("CADERNO SHOES — PRANCHA EDITORIAL 14", "Diálogo entre ergonomia extrema e desenho industrial autoral."),
            "007_": ("CADERNO SHOES — PRANCHA EDITORIAL 15", "Sequência editorial de página inteira com tipografia técnica."),
            "008_": ("CADERNO SHOES — PRANCHA EDITORIAL 16", "Síntese visual do arquivo de calçados na Revista HYB."),
            "009_": ("MARY JANE — ANATOMIA AJUSTADA", "Releitura estrutural do clássico Mary Jane sob ótica escultural."),
            "010_": ("LABORATÓRIO DE FORMA — ESTUDO ESCULTURAL I", "Prototipagem visual de volume, sola e torção de materiais."),
            "011_": ("LABORATÓRIO DE FORMA — ESTUDO ESCULTURAL II", "Iluminação rasante destacando costuras e arestas de construção."),
            "012_": ("LABORATÓRIO DE FORMA — ESTUDO ESCULTURAL III", "Investigação de silhueta monolítica e peso visual."),
            "013_": ("SÉRIE SHOES 2.0 — PRANCHA #01", "Registro de catálogo de alta precisão para arquivo de design."),
            "014_": ("SÉRIE SHOES 2.0 — PRANCHA #09", "Variação cromática e acabamento acetinado de ateliê.")
        }
        prefix = filename[:4]
        if prefix in shoes_map:
            title, caption = shoes_map[prefix]
        else:
            title = f"ESCULTURA & GRAVIDADE #{idx:02d}"
            caption = "Do fetiche à matéria artesanal: anatomia, couro e salto estrutural."

    elif cat_key == 'boys_lambe':
        series_label = "ATO 03 // SÉRIE BOYS & A RUA — LAMBE-LAMBE"
        boys_map = {
            "HYB_ED01_PAG_21.png": ("BOYS & A RUA — LAMBE-LAMBE I (PÁG. 21)", "Cartazismo urbano, sobreposição de papel rasgado e presença física no muro."),
            "HYB_ED01_PAG_22.png": ("BOYS & A RUA — LAMBE-LAMBE II (PÁG. 22)", "Pop Art contemporânea, tipografia de impacto e tensão de afeto masculino."),
            "HYB_ED01_PAG_23.png": ("BOYS & A RUA — LAMBE-LAMBE III (PÁG. 23)", "Colagem ácida de rua: o pôster como pele efêmera da cidade."),
            "HYB_ED01_PAG_24.png": ("BOYS & A RUA — LAMBE-LAMBE IV (PÁG. 24)", "Fechamento do caderno urbano da Revista HYB: fricção entre galeria e calçada.")
        }
        title, caption = boys_map.get(filename, (f"LAMBE-LAMBE URBANO #{idx:02d}", "Cartazismo urbano, Pop Art contemporânea e tensão erótica/afeto."))

    elif cat_key == 'acervo_materico':
        series_label = "ATO 04 // ACERVO MATÉRICO & SÉRIES AUTORAIS"
        materico_map = {
            "001_": ("CORPO & IMPASTO — TENSÃO NOTURNA", "Óleo e carga matérica densa explorando a anatomia sob luz dramática."),
            "002_": ("ESTUDO DE PERFIL — TINTA VERMELHA", "Carmim de ateliê e gesto incisivo sobre superfície escura."),
            "004_": ("SÉRIE A DANÇA — MOVIMENTO EM ESPÁTULA I", "Coreografia de massa pictórica, atrito e velocidade do gesto."),
            "005_": ("SÉRIE A DANÇA — MOVIMENTO EM ESPÁTULA II", "Corpos em fusão cromática entre ocre, carmim e sombra profunda."),
            "006_": ("DOSSIÊ COMPLETO BEHANCE — SÉRIE A DANÇA", "Prancha contínua apresentando a narrativa curatorial e os detalhes de impasto da série A Dança."),
            "007_": ("REGISTRO DE ATELIÊ — L1010570 (MATÉRIA VIVA)", "Fotografia direta da superfície da tela: relevo, sulcos da espátula e brilho do óleo."),
            "008_": ("REGISTRO DE ATELIÊ — L1010571 (TOPOGRAFIA DO ÓLEO)", "Macro-textura comprovando a fatura manual e o relevo tridimensional da pintura."),
            "009_": ("REGISTRO DE ATELIÊ — L1010576 (CORTE & CAMADA)", "Registro documental de processo no ateliê físico de Henrique Taveira."),
            "010_": ("SÉRIE A PISTA — ARQUITETURA DA NOITE I", "A energia cinética da pista traduzida em planos de luz e massa pictórica."),
            "011_": ("SÉRIE A PISTA — ARQUITETURA DA NOITE II", "Estudo horizontal de atmosfera, fumaça luminosa e presença corporal."),
            "012_": ("SÉRIE A PISTA — FRAGMENTO CENTRAL (1:1)", "Composição quadrada de alta concentração cromática e tensão espacial."),
            "013_": ("SÉRIE A PISTA — VERTICALIDADE NOTURNA", "Confronto direto com a tela em proporção clássica de galeria."),
            "014_": ("DOSSIÊ COMPLETO BEHANCE — SÉRIE A PISTA", "Apresentação integral da série A Pista com vistas de ambientação e close-ups de textura."),
            "015_": ("REGISTRO DE ATELIÊ — L1010595 (OBRA EM PROCESSO)", "Documentação fotográfica crua do embate físico com o suporte."),
            "016_": ("CURADORIA GALERIA ESPECTRO — A PISTA (4:5)", "Peça de posicionamento editorial integrando acervo autoral e mercado de arte."),
            "017_": ("AMBIENTAÇÃO DE ACERVO — CANVAS EM MOLDURA PRETA", "Estudo de escala e presença arquitetônica da obra em parede monumental."),
            "021_": ("ESTUDO AUTORAL — COMPOSIÇÃO MATÉRICA", "Síntese entre gesto expressionista e controle estrutural de cor.")
        }
        prefix = filename[:4]
        if prefix in materico_map:
            title, caption = materico_map[prefix]
        else:
            title = f"ACERVO MATÉRICO #{idx:02d}"
            caption = "A Dança, A Pista, impasto matérico e confrontos físicos com a tela."

    elif cat_key == 'bureau':
        if filename == "001_CAPA_CADERNO_DE_BRANDING_BUREAU_MONUMENTAL.jpg":
            series_label = "PEÇA MATRIZ // MONOGRAFIA DE BRANDING"
            title = "CADERNO DE BRANDING — HYB STUDIO (CAPA MONUMENTAL)"
            caption = "Encadernação em linho carvão profundo unindo tipografia suíça, pintura matérica a óleo e arquitetura brutalista em concreto."
        elif "08-10-2026 CAMPANHA" in subfolder:
            series_label = "ATO 05 // CAMPANHA ARQUITETURA & CASES COLECIONÁVEIS"
            camp_map = {
                "cactos 01.jpg": ("CAMPANHA DESERTO & CONCRETO — 01 (MATRIZ CACTOS)", "Diálogo entre paisagismo árido, arquitetura minimalista e curadoria de arte."),
                "cactos 01a.jpg": ("CAMPANHA DESERTO & CONCRETO — 01A (DESDOBRAMENTO)", "Continuidade visual de carrossel com precisão tipográfica e respiro espacial."),
                "rochosa 02.jpg": ("CASA ROCHOSA — 02 (MATRIZ ARQUITETÔNICA)", "Arquitetura esculpida na rocha bruta: permanência, peso e silêncio visual."),
                "rochosa 02a.jpg": ("CASA ROCHOSA — 02A (DESDOBRAMENTO)", "Desdobramento editorial sobre habitar obras de arte em escala monumental."),
                "fachada 03.jpg": ("FACHADA ESPELHADA — 03 (MATRIZ MONOLÍTICA)", "Volume monolítico espelhado refletindo a topografia natural ao redor."),
                "fachada 03a.jpg": ("FACHADA ESPELHADA — 03A (DESDOBRAMENTO)", "Direção de arte comercial para posicionamento de alto padrão na Galeria Espectro.")
            }
            title, caption = camp_map.get(filename, (f"CAMPANHA CASES COLECIONÁVEIS — {name_no_ext.upper()}", "Direção criativa e narrativa visual para arquitetura e acervo."))
        elif "2026-10-10-CARR FORMATOS" in subfolder:
            series_label = "ATO 05 // SISTEMA DE ESCALA & FORMATOS DE ACERVO"
            fmt_map = {
                "01.jpg": ("GUIA DE FORMATOS & ESCALA — LÂMINA 01/05 (ABERTURA)", "Educação visual do colecionador: como a proporção da obra transforma a arquitetura."),
                "02.png": ("SISTEMA DE PROPORÇÕES — LÂMINA 02/05", "Estudo técnico de ocupação de parede, eixo visual e respiro ao redor da tela."),
                "03.png": ("SISTEMA DE PROPORÇÕES — LÂMINA 03/05", "Comparativo de formatos verticais, quadrados e panorâmicos em interiores."),
                "04.png": ("SISTEMA DE PROPORÇÕES — LÂMINA 04/05", "Curadoria de molduras, chassi e presença física do canvas."),
                "05.png": ("SISTEMA DE PROPORÇÕES — LÂMINA 05/05 (FECHAMENTO)", "Síntese comercial e convite à consultoria personalizada de acervo.")
            }
            title, caption = fmt_map.get(filename, (f"CARROSSEL FORMATOS — LÂMINA {name_no_ext}", "Design de informação e direção de arte comercial para colecionismo."))
        elif "2026-10-02-CARR THAIS" in subfolder:
            series_label = "ATO 05 // SÉRIE CURATORIAL THAIS — GALERIA ESPECTRO"
            thais_map = {
                "01.png": ("ENSAIO CURATORIAL THAIS — LÂMINA 01/04", "Fotografia de atmosfera e inserção de obra autoral em projeto residencial contemporâneo."),
                "02.png": ("ENSAIO CURATORIAL THAIS — LÂMINA 02/04", "Obra desembalada sobre couro mostarda: a materialidade da tela antes de subir à parede."),
                "03.png": ("ENSAIO CURATORIAL THAIS — LÂMINA 03/04", "Macro-detalhe de moldura em madeira natural, trama do linho e transição cromática."),
                "04.png": ("ENSAIO CURATORIAL THAIS — LÂMINA 04/04", "Composição frontal em luz rasante reafirmando a obra como centro gravitacional.")
            }
            title, caption = thais_map.get(filename, (f"SÉRIE THAIS — ATIVO {name_no_ext}", "Direção de arte e produção de carrossel de posicionamento."))
        elif "2026-10-15-CARR hilma de domingo" in subfolder:
            series_label = "ATO 05 // ENSAIO DE DOMINGO — HILMA AF KLINT (THE TEN LARGEST)"
            hilma_map = {
                "POST 01 - The Ten Largest No. 3 - Youth - 1907.jpg": ("POST 01A — THE TEN LARGEST NO. 3 (YOUTH, 1907) · OBRA EM MOLDURA", "Apresentação em moldura de madeira natural destacando a escala e o calor cromático da fase Youth."),
                "POST 01 -1080x1440.png": ("POST 01B — THE TEN LARGEST NO. 3 (YOUTH, 1907) · CORTE EDITORIAL 3:4", "Imersão nas espirais orgânicas e diagramas solares de Hilma af Klint."),
                "POST 02 - The Ten Largest No. 5 - Adulthood - 1907.jpg": ("POST 02A — THE TEN LARGEST NO. 5 (ADULTHOOD, 1907) · OBRA EM MOLDURA", "A grande flor rosa e a caligrafia espiritual em montagem de galeria."),
                "POST 02 -1080x1440 (1).png": ("POST 02B — THE TEN LARGEST NO. 5 (ADULTHOOD, 1907) · CORTE EDITORIAL 3:4", "Detalhe aproximado da flor central e dos símbolos cromáticos da maturidade."),
                "POST 03 - The Ten Largest No. 6 - 1907.jpg": ("POST 03A — THE TEN LARGEST NO. 6 (ADULTHOOD, 1907) · OBRA EM MOLDURA", "Contraste dramático do arco negro central e órbitas concêntricas em moldura."),
                "POST 03 -1080x1440 (2).png": ("POST 03B — THE TEN LARGEST NO. 6 (ADULTHOOD, 1907) · CORTE EDITORIAL 3:4", "Foco na fatura pictórica em têmpera e nas inscrições cursivas."),
                "POST 04 - The Ten Largest No. 7 - Adulthood - 1907.jpg": ("POST 04A — THE TEN LARGEST NO. 7 (ADULTHOOD, 1907) · OBRA EM MOLDURA", "Simetria monumental em amarelo imperial (I, II, III) apresentada em chassi e moldura."),
                "POST 04 -1080x1440 (2).png": ("POST 04B — THE TEN LARGEST NO. 7 (ADULTHOOD, 1907) · CORTE EDITORIAL 3:4", "Detalhe de textura e geometria sagrada da sétima tela da série de 1907."),
                "POST 05 - The Ten Largest No. 8 - Adulthood - 1907.jpg": ("POST 05A — THE TEN LARGEST NO. 8 (ADULTHOOD, 1907) · OBRA EM MOLDURA", "Fechamento do carrossel: as grandes esferas celestes em composição de acervo."),
                "POST 05 -1080x1440 (2).png": ("POST 05B — THE TEN LARGEST NO. 8 (ADULTHOOD, 1907) · CORTE EDITORIAL 3:4", "Corte aproximado das esferas e espirais que encerram o ensaio dominical.")
            }
            title, caption = hilma_map.get(filename, (f"SÉRIE HILMA AF KLINT — {name_no_ext.upper()}", "Curadoria de repertório artístico e direção editorial para marca."))
        elif "2026-10-16-Stories hilma" in subfolder:
            series_label = "ATO 05 // STORIES EDITORIAL — DIÁLOGOS GALERIA ESPECTRO"
            title = "STORIES HILMA AF KLINT — DIÁLOGOS GALERIA ESPECTRO (9:16)"
            caption = "Chamada vertical 9:16 em textura de pergaminho conectando os Stories ao ensaio curatorial."
        else:
            series_label = "ATO 05 // HYB STUDIO & CASES COLECIONÁVEIS"
            title = name_no_ext.replace('_', ' ').replace('-', ' ').upper()
            caption = "Estratégia visual, sistemas de identidade e direção de arte comercial."

    return {
        "title": title,
        "caption": caption,
        "series": series_label,
        "aspect_badge": aspect_badge,
        "subfolder": subfolder if subfolder else cat_key
    }

# -------------------------------------------------------------------------
# 2. SCAN PHYSICAL ASSETS IN WEBSITE/assets/ WITH STRICT CURATORIAL ORDERING
# -------------------------------------------------------------------------

ordered_categories = ['revista_hyb', 'shoes', 'boys_lambe', 'acervo_materico', 'bureau']
catalog = {k: [] for k in ordered_categories}

for cat_key in ordered_categories:
    cat_dir = os.path.join(assets_dir, cat_key)
    if not os.path.exists(cat_dir):
        continue

    collected_files = []
    for root, dirs, files in os.walk(cat_dir):
        dirs[:] = [d for d in dirs if 'lixo' not in d.lower()]
        if 'lixo' in root.lower():
            continue
        for f in sorted(files):
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                full_p = os.path.join(root, f)
                rel_p = os.path.relpath(full_p, website_dir).replace('\\', '/')
                collected_files.append((rel_p, full_p, f))

    if cat_key == 'bureau':
        subfolder_priority = {
            "": 0,
            "08-10-2026 CAMPANHA": 1,
            "2026-10-10-CARR FORMATOS": 2,
            "2026-10-02-CARR THAIS": 3,
            "2026-10-15-CARR hilma de domingo": 4,
            "2026-10-16-Stories hilma": 5
        }
        campanha_order = {
            "cactos 01.jpg": 1,
            "cactos 01a.jpg": 2,
            "rochosa 02.jpg": 3,
            "rochosa 02a.jpg": 4,
            "fachada 03.jpg": 5,
            "fachada 03a.jpg": 6
        }
        hilma_order = {
            "POST 01 - The Ten Largest No. 3 - Youth - 1907.jpg": 1,
            "POST 01 -1080x1440.png": 2,
            "POST 02 - The Ten Largest No. 5 - Adulthood - 1907.jpg": 3,
            "POST 02 -1080x1440 (1).png": 4,
            "POST 03 - The Ten Largest No. 6 - 1907.jpg": 5,
            "POST 03 -1080x1440 (2).png": 6,
            "POST 04 - The Ten Largest No. 7 - Adulthood - 1907.jpg": 7,
            "POST 04 -1080x1440 (2).png": 8,
            "POST 05 - The Ten Largest No. 8 - Adulthood - 1907.jpg": 9,
            "POST 05 -1080x1440 (2).png": 10
        }
        def bureau_sort_key(item):
            rel_p, _, fname = item
            parts = rel_p.split('/')
            sub = parts[2] if len(parts) > 3 else ""
            sub_prio = subfolder_priority.get(sub, 99)
            if sub == "08-10-2026 CAMPANHA":
                file_prio = campanha_order.get(fname, 99)
            elif sub == "2026-10-15-CARR hilma de domingo":
                file_prio = hilma_order.get(fname, 99)
            else:
                file_prio = 50
            return (sub_prio, file_prio, fname.lower())
        collected_files.sort(key=bureau_sort_key)
    else:
        collected_files.sort(key=lambda x: x[2].lower())

    for idx, (rel_p, full_p, fname) in enumerate(collected_files, start=1):
        with Image.open(full_p) as img:
            w, h = img.size
        ratio = round(w / h, 3) if h else 1.0
        if ratio < 0.30:
            orient = "strip"
        elif ratio < 0.88:
            orient = "vertical"
        elif ratio > 1.15:
            orient = "horizontal"
        else:
            orient = "square"

        meta = curate_item_metadata(cat_key, rel_p, idx, w, h)
        catalog[cat_key].append({
            "id": f"{cat_key}_{idx:03d}",
            "name": fname,
            "path": rel_p,
            "url": encode_asset_url(rel_p),
            "w": w,
            "h": h,
            "ratio": ratio,
            "orient": orient,
            "category": cat_key,
            "subfolder": meta["subfolder"],
            "series": meta["series"],
            "title": meta["title"],
            "caption": meta["caption"],
            "aspect_badge": meta["aspect_badge"]
        })

with open(catalog_path, 'w', encoding='utf-8') as f:
    json.dump(catalog, f, indent=2, ensure_ascii=False)

total_counts = {k: len(v) for k, v in catalog.items()}
total_all = sum(total_counts.values())
print(f"Updated curated_catalog.json successfully: {total_counts} (Total: {total_all} assets)")

# -------------------------------------------------------------------------
# 3. ACT METADATA & ZARA / BARON & BARON / PROTOTIPO-EDITORIAL CHOREOGRAPHY
# -------------------------------------------------------------------------

act_configs = [
    {
        "key": "revista_hyb",
        "num": "ATO 01",
        "code": "HYB // PUBLICAÇÃO OFICIAL (24 PÁGINAS)",
        "title": "Revista HYB — <em>Late Night Tales</em>",
        "subtitle": "Edição 001 integral com 24 páginas no leitor oficial de ateliê + download do PDF completo.",
        "quote": "“A tela exige velocidade. O ateliê exige permanência. Subvertemos a proporção efêmera do digital em lâminas de coleção.”",
        "source_path": "assets/revista_hyb/"
    },
    {
        "key": "shoes",
        "num": "ATO 02",
        "code": "SHOES // 2.0",
        "title": "Caderno Shoes — <em>Escultura &amp; Gravidade</em>",
        "subtitle": "Do fetiche à matéria artesanal. Anatomia, couro moldado e salto estrutural.",
        "quote": "“O calçado tratado não como acessório de vitrine, mas como engenharia de tensão, equilíbrio e escultura sobre o solo.”",
        "source_path": "assets/shoes/"
    },
    {
        "key": "boys_lambe",
        "num": "ATO 03",
        "code": "URBANO // LAMBE-LAMBE",
        "title": "Série Boys &amp; A Rua — <em>Lambe-Lambe</em>",
        "subtitle": "Cartazismo urbano, Pop Art contemporânea e tensão erótica/afeto.",
        "quote": "“Quando a imagem sai da câmara escura e ganha a aspereza do muro: cola, papel rasgado, tipografia de choque e presença física.”",
        "source_path": "assets/boys_lambe/"
    },
    {
        "key": "acervo_materico",
        "num": "ATO 04",
        "code": "MATÉRIA // ÓLEO & TELA",
        "title": "Acervo Matérico &amp; <em>Séries Autorais</em>",
        "subtitle": "A Dança, A Pista, impasto matérico, topografia do óleo e confrontos físicos com o linho.",
        "quote": "“A máquina não conhece a resistência física do linho nem o peso da espátula. É no atrito da matéria que o olhar se prova.”",
        "source_path": "assets/acervo_materico/"
    },
    {
        "key": "bureau",
        "num": "ATO 05",
        "code": "HYB // SISTEMAS & CASES",
        "title": "HYB Studio &amp; <em>Cases Colecionáveis</em>",
        "subtitle": "Campanhas arquitetônicas, sistemas de formatos, curadoria Galeria Espectro e dossiês de repertório.",
        "quote": "“Estratégia visual para marcas culturais, galerias e negócios autorais que recusam a estética descartável de linha de montagem.”",
        "source_path": "assets/bureau/"
    }
]

hero_cover_rel = "assets/bureau/001_CAPA_CADERNO_DE_BRANDING_BUREAU_MONUMENTAL.jpg"
hero_cover_url = encode_asset_url(hero_cover_rel)
hyb_pdf_url = "assets/revista_hyb/REVISTA_HYB_ED01_24_PAGINAS.pdf"

# Assign asymmetric 12-column choreography classes per item for VIEW [1] (Editorial Zara / Prototipo mode)
def get_editorial_col_class(cat_key: str, local_i: int, orient: str, subfolder: str) -> str:
    if orient == "strip":
        return "ed-col-full ed-strip"
    if cat_key == "revista_hyb":
        # Page 01 Cover is monumental solo; pages 02-23 form editorial diptychs/staggered spreads; page 24 closes monumental
        if local_i == 1:
            return "ed-col-solo-left"
        elif local_i == 24:
            return "ed-col-solo-right"
        else:
            pair_pos = (local_i - 2) % 6
            if pair_pos == 0:
                return "ed-col-pair-a"
            elif pair_pos == 1:
                return "ed-col-pair-b ed-stagger"
            elif pair_pos == 2:
                return "ed-col-spread-a"
            elif pair_pos == 3:
                return "ed-col-spread-b"
            elif pair_pos == 4:
                return "ed-col-asym-wide"
            else:
                return "ed-col-asym-narrow ed-stagger"
    elif cat_key == "boys_lambe":
        # 4 urban posters: staggered diptych + spread diptych
        patterns = ["ed-col-pair-a", "ed-col-pair-b ed-stagger", "ed-col-spread-a", "ed-col-spread-b"]
        return patterns[(local_i - 1) % 4]
    elif cat_key == "bureau":
        if "CAMPANHA" in subfolder or "hilma de domingo" in subfolder:
            # Strict paired spreads (Matrix + Unfolding / Framed Painting + 3:4 Detail Crop)
            return "ed-col-spread-a" if (local_i % 2 == 1) else "ed-col-spread-b"
        elif "FORMATOS" in subfolder:
            # 5-slide carousel: 1 hero + 2 pairs
            if local_i == 7:
                return "ed-col-solo-left"
            return "ed-col-pair-a" if (local_i % 2 == 1) else "ed-col-pair-b ed-stagger"
        elif "THAIS" in subfolder:
            return "ed-col-pair-a" if (local_i % 2 == 1) else "ed-col-pair-b ed-stagger"
        else:
            return "ed-col-solo-right"
    else:
        # Shoes & Acervo Materico: cadence of Solo -> Staggered Diptych -> Asymmetric Pair
        cycle = (local_i - 1) % 5
        if cycle == 0:
            return "ed-col-solo-left"
        elif cycle == 1:
            return "ed-col-pair-a"
        elif cycle == 2:
            return "ed-col-pair-b ed-stagger"
        elif cycle == 3:
            return "ed-col-asym-narrow"
        else:
            return "ed-col-asym-wide ed-stagger"

def build_acts_html():
    sections_html = []

    for act in act_configs:
        key = act["key"]
        items = catalog[key]
        count = len(items)

        plates_html = []
        current_subgroup = None

        if key == "revista_hyb":
            # Curation Zara: Display 3 iconic plates on the scroll (Cover + Botanical X-Ray diptych),
            # plus an editorial invitation card for the full 24-page interactive reader.
            # This completely avoids repeating Shoes and Boys Lambe, preserving total novel discovery.
            hyb_showcase_indices = [0, 4, 5]  # Page 01 (Cover), Page 05 (Cacto), Page 06 (Protea)
            for s_idx, cat_idx in enumerate(hyb_showcase_indices, start=1):
                item = items[cat_idx]
                ed_class = "ed-col-solo-left" if s_idx == 1 else ("ed-col-spread-a" if s_idx == 2 else "ed-col-spread-b")
                orient_class = f"orient-{item['orient']}"
                num_str = f"{cat_idx + 1:02d}/24"
                click_handler = f"openMagazineReader({cat_idx})"

                plates_html.append(f'''
                <figure class="plate {ed_class} {orient_class}" data-cat="{key}" data-id="{item['id']}" data-reveal data-view onclick="{click_handler}" tabindex="0" role="button" aria-label="Inspecionar {item['title']}">
                  <div class="plate__media">
                    <img src="{item['url']}" alt="{item['title']} — Henrique Taveira (DALLIDO.1988)" width="{item['w']}" height="{item['h']}" loading="lazy" decoding="async">
                  </div>
                  <figcaption class="plate__cap micro">
                    <span class="plate__title"><span class="mono micro--acc">{num_str}</span> {item['title']}</span>
                    <span class="plate__spec mono">{item['aspect_badge']} · {item['w']}×{item['h']}</span>
                  </figcaption>
                </figure>
                ''')

            # Append the monumental 24-page reader showcase card
            plates_html.append(f'''
            <div class="plate-magazine-card" data-cat="{key}" data-reveal>
              <div class="magazine-card__inner">
                <span class="micro mono micro--acc">EDIÇÃO INTEGRAL · 24 PÁGINAS HOMOLOGADAS</span>
                <h4 class="magazine-card__title">Revista HYB — Edição 001 · <em>Late Night Tales</em></h4>
                <p class="magazine-card__desc">A publicação completa reúne 24 pranchas originais integrando radiografia botânica, crônicas de ateliê, ensaios conceituais e cartazismo. Folheie a edição integral página por página no leitor interativo de ateliê ou baixe o PDF oficial.</p>
                <div class="magazine-card__actions">
                  <button type="button" class="btn-editorial btn-editorial--acc" onclick="openMagazineReader(0)">▶ Folhear Edição Completa (24 Páginas)</button>
                  <a href="{hyb_pdf_url}" target="_blank" rel="noopener" class="btn-editorial">⬇ Baixar PDF Oficial (24 Pág.) ↗</a>
                </div>
              </div>
            </div>
            ''')
            spec_quote_count = "24 páginas oficiais no leitor · 3 lâminas de destaque no feed"
        else:
            # For bureau, skip bureau_001 because it already crowns the website in the Hero header
            items_to_render = [it for it in items if not (key == "bureau" and it["id"] == "bureau_001")]

            for local_i, item in enumerate(items_to_render, start=1):
                if key == "bureau":
                    sub = item["subfolder"]
                    if sub != current_subgroup:
                        current_subgroup = sub
                        sub_titles = {
                            "08-10-2026 CAMPANHA": ("SÉRIE 01 // 08-10-2026 CAMPANHA", "Arquitetura Monolítica: Cactos (01/01A), Casa Rochosa (02/02A) & Fachada Espelhada (03/03A)"),
                            "2026-10-10-CARR FORMATOS": ("SÉRIE 02 // 2026-10-10-CARR FORMATOS", "Engenharia de Escala & Proporções de Acervo (Lâminas 01 a 05)"),
                            "2026-10-02-CARR THAIS": ("SÉRIE 03 // 2026-10-02-CARR THAIS", "Ensaio Curatorial Thais — Galeria Espectro (Lâminas 01 a 04)"),
                            "2026-10-15-CARR hilma de domingo": ("SÉRIE 04 // 2026-10-15-CARR HILMA DE DOMINGO", "Repertório Cultural: The Ten Largest (1907) — Pares Obra em Moldura + Corte Editorial 3:4 (01 a 05)"),
                            "2026-10-16-Stories hilma": ("SÉRIE 05 // 2026-10-16-STORIES HILMA", "Desdobramento Vertical 9:16 — Diálogos Galeria Espectro")
                        }
                        st_kicker, st_name = sub_titles.get(sub, (f"SÉRIE // {sub.upper()}", "Ativos Curados HYB Studio"))
                        plates_html.append(f'''
                        <div class="subseries-divider" data-cat="{key}" data-reveal>
                          <span class="micro mono micro--acc">{st_kicker}</span>
                          <span class="subseries-name">{st_name}</span>
                        </div>
                        ''')

                ed_class = get_editorial_col_class(key, local_i, item['orient'], item['subfolder'])
                orient_class = f"orient-{item['orient']}"
                strip_badge = '<span class="strip-badge micro mono">PRANCHA LONGA BEHANCE · CLIQUE PARA EXPANDIR</span>' if item['orient'] == 'strip' else ''
                num_str = f"{local_i:02d}"
                click_handler = f"openLightboxById('{item['id']}')"

                plates_html.append(f'''
                <figure class="plate {ed_class} {orient_class}" data-cat="{key}" data-id="{item['id']}" data-reveal data-view onclick="{click_handler}" tabindex="0" role="button" aria-label="Inspecionar {item['title']}">
                  <div class="plate__media">
                    <img src="{item['url']}" alt="{item['title']} — Henrique Taveira (DALLIDO.1988)" width="{item['w']}" height="{item['h']}" loading="lazy" decoding="async">
                    {strip_badge}
                  </div>
                  <figcaption class="plate__cap micro">
                    <span class="plate__title"><span class="mono micro--acc">{num_str}</span> {item['title']}</span>
                    <span class="plate__spec mono">{item['aspect_badge']} · {item['w']}×{item['h']}</span>
                  </figcaption>
                </figure>
                ''')
            spec_quote_count = f"{len(items_to_render)} pranchas · {act['source_path']}"

        hyb_reader_bar = ""
        if key == "revista_hyb":
            hyb_reader_bar = f'''
            <div class="hyb-bar" data-reveal>
              <div class="micro">
                <span class="micro--acc mono">MODO PUBLICAÇÃO</span> — Edição 001 completa com 24 páginas oficiais na ordem exata de leitura.
              </div>
              <div class="hyb-bar__btns">
                <button type="button" class="btn-editorial btn-editorial--acc" onclick="openMagazineReader(0)">▶ Ler Revista (24 Páginas)</button>
                <a href="{hyb_pdf_url}" target="_blank" rel="noopener" class="btn-editorial">⬇ PDF Oficial (24 Pág.) ↗</a>
              </div>
            </div>
            '''

        sections_html.append(f'''
        <section class="act-sec" id="ato-{key}" data-act-section="{key}">
          <div class="act-head g" data-reveal>
            <div class="act-head__meta micro">
              <span class="mono micro--acc">{act['num']}</span> — {act['code']}
            </div>
            <div class="act-head__main">
              <h3 class="act-head__title">{act['title']}</h3>
              <p class="act-head__sub">{act['subtitle']}</p>
            </div>
            <blockquote class="act-head__quote">
              {act['quote']}
              <span class="micro mono" style="display:block;margin-top:10px;font-style:normal">{spec_quote_count}</span>
            </blockquote>
          </div>
          {hyb_reader_bar}
          <div class="lookbook-grid" data-grid-cat="{key}">
            {''.join(plates_html)}
          </div>
        </section>
        ''')

    return '\n'.join(sections_html)

acts_html_content = build_acts_html()

# Flatten all items in exact display order for the Lightbox JS array
all_works_flat = []
for act in act_configs:
    for it in catalog[act["key"]]:
        all_works_flat.append({
            "id": it["id"],
            "cat": it["category"],
            "actNum": act["num"],
            "actTitle": re.sub(r'<[^>]+>', '', act["title"]),
            "url": it["url"],
            "path": it["path"],
            "title": it["title"],
            "caption": it["caption"],
            "series": it["series"],
            "w": it["w"],
            "h": it["h"],
            "orient": it["orient"],
            "aspect": it["aspect_badge"]
        })

works_json_str = json.dumps(all_works_flat, ensure_ascii=False)

# -------------------------------------------------------------------------
# 4. BUILD COMPLETE SELF-CONTAINED HTML DOCUMENT (PROTOTIPO-EDITORIAL + ZARA)
# -------------------------------------------------------------------------

html_document = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>HYB — STUDIO · Henrique Taveira (DALLIDO.1988) | Direção Criativa, Estratégia &amp; Acervo</title>
  <meta name="description" content="HYB — STUDIO sob direção de Henrique Taveira (DALLIDO.1988): estratégia, direção criativa, sistemas transmídia, Revista HYB (Late Night Tales) e acervo matérico.">
  <meta name="author" content="Henrique Taveira Ferreira (DALLIDO.1988)">
  <meta name="robots" content="index, follow">
  <meta name="theme-color" content="#07090c">
  <link rel="canonical" href="https://fariatitan.github.io/HYB/">

  <!-- OPEN GRAPH / SOCIAL -->
  <meta property="og:type" content="website">
  <meta property="og:locale" content="pt_BR">
  <meta property="og:url" content="https://fariatitan.github.io/HYB/">
  <meta property="og:site_name" content="HYB — STUDIO · DALLIDO.1988">
  <meta property="og:title" content="HYB — STUDIO · Henrique Taveira (DALLIDO.1988)">
  <meta property="og:description" content="Estratégia, direção criativa, linguagem e acervo autoral. A máquina propõe. O humano autoriza.">
  <meta property="og:image" content="https://fariatitan.github.io/HYB/{hero_cover_url}">
  <meta property="og:image:alt" content="Capa Monumental do Caderno de Branding — HYB STUDIO">

  <!-- TWITTER CARD -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="HYB — STUDIO · Henrique Taveira (DALLIDO.1988)">
  <meta name="twitter:description" content="Estratégia, direção criativa, Revista HYB e acervo matérico sob o Design System Soberano do HYB Studio.">
  <meta name="twitter:image" content="https://fariatitan.github.io/HYB/{hero_cover_url}">

  <!-- SCHEMA.ORG JSON-LD -->
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@graph": [
      {{
        "@type": "WebSite",
        "@id": "https://fariatitan.github.io/HYB/#website",
        "name": "HYB — STUDIO · Henrique Taveira (DALLIDO.1988)",
        "url": "https://fariatitan.github.io/HYB/"
      }},
      {{
        "@type": "Person",
        "@id": "#henrique-taveira",
        "name": "Henrique Taveira Ferreira",
        "alternateName": "DALLIDO.1988",
        "jobTitle": "Diretor Criativo, Artista Visual e Arquiteto de Marca",
        "email": "mailto:henrique992338736@gmail.com"
      }},
      {{
        "@type": "ProfessionalService",
        "@id": "#hyb-studio",
        "name": "HYB — STUDIO",
        "url": "https://fariatitan.github.io/HYB/",
        "founder": {{ "@id": "#henrique-taveira" }},
        "description": "Estrutura independente de estratégia de marca, direção criativa, desenvolvimento de linguagem e produção transmídia.",
        "areaServed": "BR"
      }}
    ]
  }}
  </script>

  <style>
    :root {{
      --bg: #07090c;
      --bg-elev: #0d1017;
      --fg: #EDECE8;
      --paper: #d9d6cd;
      --mut: #7B838C;
      --line: rgba(237, 236, 232, 0.14);
      --line-strong: rgba(237, 236, 232, 0.28);
      --acc: #FF6B1A;
      --crimson: #8e1e28;
      --pad: clamp(18px, 4.4vw, 88px);
      --gap: clamp(12px, 1.6vw, 28px);
      --sans: 'Segoe UI Light', 'Segoe UI Semilight', 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
      --serif: 'Segoe UI Light', 'Segoe UI Semilight', 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
      --mono: 'Segoe UI Light', 'Segoe UI Semilight', 'Segoe UI', ui-monospace, monospace;
    }}

    * {{ box-sizing: border-box; }}
    html {{ background: var(--bg); scroll-behavior: smooth; color-scheme: dark; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--fg);
      font-family: var(--sans);
      font-weight: 300;
      font-size: 13px;
      line-height: 1.55;
      overflow-x: hidden;
      -webkit-font-smoothing: antialiased;
      text-rendering: optimizeLegibility;
    }}
    img {{ display: block; max-width: 100%; height: auto; }}
    a {{ color: inherit; text-decoration: none; }}
    button {{ font-family: inherit; cursor: pointer; }}
    ::selection {{ background: var(--acc); color: #07090c; }}

    /* Procedural Tactile Grain Overlay (3.2% Opacity) */
    .tactile-grain {{
      position: fixed;
      inset: 0;
      width: 100vw;
      height: 100vh;
      pointer-events: none;
      z-index: 9000;
      opacity: 0.032;
      mix-blend-mode: overlay;
    }}

    /* ---------- Typography Utilities (Zero Bold) ---------- */
    .micro {{
      font-size: 10px;
      line-height: 1.3;
      letter-spacing: 0.22em;
      text-transform: uppercase;
      color: var(--mut);
      font-weight: 300;
    }}
    .micro--fg {{ color: var(--fg); }}
    .micro--acc {{ color: var(--acc); }}
    .mono {{
      font-family: var(--mono);
      font-size: 10px;
      letter-spacing: 0.12em;
    }}
    .dot {{
      display: inline-block;
      width: 5px;
      height: 5px;
      border-radius: 50%;
      background: var(--acc);
      vertical-align: middle;
      margin-right: 6px;
      animation: pulse 2.6s ease-in-out infinite;
    }}
    @keyframes pulse {{
      0%, 100% {{ opacity: 1; }}
      50% {{ opacity: 0.25; }}
    }}

    /* ---------- Peripheral Chrome (prototipo-editorial.html) ---------- */
    .topbar {{
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      height: 46px;
      z-index: 100;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      padding: 0 var(--pad);
      border-bottom: 1px solid var(--line);
      background: rgba(7, 9, 12, 0.78);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
    }}
    .topbar__nav {{
      display: none;
      align-items: center;
      gap: 22px;
    }}
    .topbar__nav a {{
      transition: color 0.3s ease;
    }}
    .topbar__nav a:hover {{
      color: var(--acc);
    }}
    @media (min-width: 1020px) {{
      .topbar__nav {{ display: flex; }}
    }}
    @media (max-width: 760px) {{
      .topbar .avail {{ display: none; }}
    }}

    .edge--l {{
      position: fixed;
      bottom: 16px;
      left: var(--pad);
      z-index: 50;
      pointer-events: none;
    }}
    @media (max-width: 900px) {{
      .edge--l {{ display: none; }}
    }}

    /* Custom Floating Magnetic Cursor */
    .cursor {{
      position: fixed;
      top: 0;
      left: 0;
      width: 78px;
      height: 78px;
      border: 1px solid rgba(255, 107, 26, 0.55);
      border-radius: 50%;
      display: grid;
      place-items: center;
      z-index: 120;
      pointer-events: none;
      opacity: 0;
      transition: opacity 0.35s ease;
      backdrop-filter: blur(4px);
      background: rgba(7, 9, 12, 0.38);
    }}
    .cursor.on {{ opacity: 1; }}
    .cursor span {{
      font-size: 9px;
      letter-spacing: 0.28em;
      text-transform: uppercase;
      color: var(--fg);
    }}
    @media (hover: none), (pointer: coarse) {{
      .cursor {{ display: none; }}
    }}

    /* ---------- Shell & 12-Col Grid ---------- */
    .sec {{
      position: relative;
      padding-left: var(--pad);
      padding-right: var(--pad);
    }}
    .g {{
      display: grid;
      grid-template-columns: repeat(12, 1fr);
      column-gap: var(--gap);
    }}
    .rule {{
      border-top: 1px solid var(--line);
    }}

    /* ---------- Reveal Animation (prototipo-editorial.html — Safe Descender Bounds) ---------- */
    [data-reveal] {{
      opacity: 0;
      transform: translateY(28px);
      clip-path: inset(12% -10% -25% -10%);
      transition: opacity 1.1s cubic-bezier(.2,.7,.2,1),
                  transform 1.1s cubic-bezier(.2,.7,.2,1),
                  clip-path 1.2s cubic-bezier(.2,.7,.2,1);
    }}
    [data-reveal].is-in {{
      opacity: 1;
      transform: none;
      clip-path: inset(-25% -10% -30% -10%);
    }}

    /* ---------- Editorial Buttons ---------- */
    .btn-editorial {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 9px 20px;
      border: 1px solid var(--line-strong);
      border-radius: 999px;
      background: transparent;
      color: var(--fg);
      font-size: 10px;
      font-weight: 300;
      letter-spacing: 0.2em;
      text-transform: uppercase;
      transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
    }}
    .btn-editorial:hover {{
      border-color: var(--acc);
      color: var(--acc);
    }}
    .btn-editorial--acc {{
      border-color: var(--acc);
      color: var(--fg);
    }}
    .btn-editorial--acc:hover {{
      background: var(--acc);
      color: #07090c;
    }}

    /* ---------- 01. HERO (prototipo-editorial.html) ---------- */
    .hero {{
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      justify-content: center;
      padding-top: 58px;
      padding-bottom: 7vh;
    }}
    .hero__meta {{
      display: flex;
      justify-content: space-between;
      gap: 18px;
      flex-wrap: wrap;
      padding-bottom: clamp(24px, 6vh, 80px);
    }}
    .hero__grid {{
      display: grid;
      grid-template-columns: repeat(12, 1fr);
      column-gap: var(--gap);
      align-items: end;
    }}
    .title {{
      margin: 0;
      padding-top: 0.08em;
      padding-bottom: 0.16em;
      font-size: clamp(32px, 7.2vw, 132px);
      line-height: 0.94;
      font-weight: 300;
      letter-spacing: -0.03em;
      text-transform: uppercase;
      overflow: visible;
    }}
    .title em {{
      font-family: var(--sans);
      font-style: italic;
      font-weight: 300;
      letter-spacing: -0.01em;
      text-transform: none;
      color: var(--acc);
      display: inline-block;
      padding-bottom: 0.08em;
    }}
    .title .l2 {{
      padding-left: clamp(14px, 11vw, 210px);
      display: block;
    }}
    .title .l3 {{
      padding-left: clamp(6px, 3.5vw, 70px);
      display: block;
    }}
    .title__wrap {{
      grid-column: 1 / span 8;
      position: relative;
      z-index: 2;
      mix-blend-mode: difference;
    }}
    .hero__fig {{
      grid-column: 8 / -1;
      margin: 0;
      overflow: hidden;
      cursor: pointer;
    }}
    .hero__fig img {{
      width: 100%;
      height: auto;
      object-fit: contain;
      transition: transform 0.9s cubic-bezier(.2,.7,.2,1);
    }}
    .hero__fig:hover img {{
      transform: scale(1.02);
    }}
    @media (max-width: 760px) {{
      .title__wrap {{ grid-column: 1 / -1; mix-blend-mode: normal; }}
      .hero__fig {{ grid-column: 1 / -1; margin-top: 32px; }}
    }}
    .hero__foot {{
      display: flex;
      justify-content: space-between;
      gap: 16px;
      align-items: flex-end;
      flex-wrap: wrap;
      padding-top: clamp(28px, 7vh, 96px);
    }}

    /* ---------- 02. MANIFESTO / POSIÇÃO ---------- */
    .manifesto {{
      padding-top: clamp(90px, 22vh, 260px);
    }}
    .manifesto__label {{
      grid-column: 1 / span 3;
    }}
    .manifesto__lead {{
      grid-column: 3 / span 8;
      margin: 0;
      font-size: clamp(19px, 2.15vw, 31px);
      font-weight: 300;
      line-height: 1.36;
      letter-spacing: -0.01em;
      color: var(--fg);
    }}
    .manifesto__quote {{
      grid-column: 8 / span 5;
      margin: clamp(40px, 8vh, 110px) 0 0;
      font-family: var(--sans);
      font-style: italic;
      font-weight: 300;
      font-size: clamp(16px, 1.45vw, 21px);
      line-height: 1.52;
      color: var(--paper);
      padding-top: 16px;
      border-top: 1px solid var(--line);
    }}
    @media (max-width: 900px) {{
      .manifesto__label, .manifesto__lead, .manifesto__quote {{ grid-column: 1 / -1; }}
      .manifesto__lead {{ margin-top: 22px; }}
    }}

    /* ---------- 03. INDEX DE ESCOPOS (Arquitetura Comercial de Alto Padrão) ---------- */
    .index {{
      padding-top: clamp(80px, 18vh, 220px);
    }}
    .rows {{
      margin-top: clamp(30px, 6vh, 64px);
      border-bottom: 1px solid var(--line);
    }}
    .row {{
      display: grid;
      grid-template-columns: 46px 1fr;
      gap: var(--gap);
      align-items: start;
      padding: clamp(24px, 4.2vh, 42px) 0;
      border-top: 1px solid var(--line);
    }}
    .row__body {{
      display: flex;
      flex-direction: column;
      gap: 12px;
    }}
    .row__head {{
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      gap: 16px;
      flex-wrap: wrap;
    }}
    .row__name {{
      margin: 0;
      font-size: clamp(20px, 2.4vw, 36px);
      font-weight: 300;
      letter-spacing: -0.02em;
      text-transform: uppercase;
      color: var(--fg);
    }}
    .row__badge {{
      padding: 3px 10px;
      border: 1px solid var(--line);
      border-radius: 999px;
      color: var(--mut);
    }}
    .row__desc {{
      margin: 0;
      max-width: 70ch;
      font-size: 13px;
      line-height: 1.6;
      color: var(--paper);
    }}
    .row__deliverables {{
      display: flex;
      flex-wrap: wrap;
      gap: 18px;
      color: var(--mut);
      padding: 6px 0;
    }}
    .row__actions {{
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
      margin-top: 6px;
    }}
    .row:hover .row__i {{
      color: var(--acc);
    }}
    .row__i {{
      transition: color 0.4s ease;
    }}
    @media (max-width: 760px) {{
      .row {{ grid-template-columns: 28px 1fr; }}
      .row__deliverables {{ flex-direction: column; gap: 6px; }}
    }}

    /* ---------- TRANSIÇÃO DE MÉTODO & INFRAESTRUTURA ---------- */
    .transition-sec {{
      padding-top: clamp(80px, 16vh, 200px);
      padding-bottom: clamp(50px, 10vh, 120px);
      border-bottom: 1px solid var(--line);
    }}
    .transition-lead {{
      align-self: center;
    }}
    .note {{
      font-family: var(--sans);
      font-style: italic;
      font-weight: 300;
      font-size: clamp(15px, 1.35vw, 20px);
      line-height: 1.55;
      color: var(--paper);
    }}
    .fig {{
      margin: 0;
      overflow: hidden;
      cursor: pointer;
    }}
    .fig img {{
      width: 100%;
      height: auto;
      display: block;
      transition: transform 0.9s cubic-bezier(.2,.7,.2,1);
    }}
    .fig:hover img {{
      transform: scale(1.018);
    }}

    /* ---------- 04. ACERVO CURATORIAL COMPLETO (5 ATOS — ZARA / BARON & BARON) ---------- */
    .archive-sec {{
      padding-top: clamp(100px, 22vh, 260px);
    }}
    .archive-bar {{
      position: sticky;
      top: 46px;
      z-index: 80;
      background: rgba(7, 9, 12, 0.88);
      backdrop-filter: blur(14px);
      -webkit-backdrop-filter: blur(14px);
      border-top: 1px solid var(--line);
      border-bottom: 1px solid var(--line);
      padding: 12px 0;
      margin-top: 32px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
      flex-wrap: wrap;
    }}
    .filter-group, .density-group {{
      display: flex;
      align-items: center;
      gap: 6px;
      flex-wrap: wrap;
    }}
    .chip {{
      background: transparent;
      border: 1px solid transparent;
      color: var(--mut);
      padding: 6px 12px;
      font-size: 10px;
      font-weight: 300;
      letter-spacing: 0.18em;
      text-transform: uppercase;
      transition: all 0.25s ease;
    }}
    .chip:hover {{
      color: var(--fg);
      border-color: var(--line);
    }}
    .chip.active {{
      color: var(--fg);
      border-color: var(--acc);
      background: rgba(255, 107, 26, 0.08);
    }}
    .chip-count {{
      font-family: var(--mono);
      font-size: 9px;
      color: var(--acc);
      margin-left: 4px;
    }}

    /* Act Section Header */
    .act-sec {{
      padding-top: clamp(72px, 15vh, 190px);
    }}
    .act-sec.hidden-act {{
      display: none !important;
    }}
    .act-head {{
      padding-bottom: clamp(28px, 6vh, 64px);
      border-bottom: 1px solid var(--line);
      align-items: end;
    }}
    .act-head__meta {{
      grid-column: 1 / span 3;
      align-self: start;
    }}
    .act-head__main {{
      grid-column: 4 / span 5;
    }}
    .act-head__title {{
      margin: 0;
      font-size: clamp(24px, 3.4vw, 52px);
      font-weight: 300;
      line-height: 1.08;
      letter-spacing: -0.02em;
      text-transform: uppercase;
    }}
    .act-head__title em {{
      font-family: var(--sans);
      font-style: italic;
      font-weight: 300;
      text-transform: none;
      color: var(--paper);
    }}
    .act-head__sub {{
      margin: 12px 0 0;
      color: var(--mut);
      font-size: 12px;
      max-width: 48ch;
    }}
    .act-head__quote {{
      grid-column: 9 / span 4;
      margin: 0;
      font-family: var(--sans);
      font-style: italic;
      font-weight: 300;
      font-size: 14px;
      line-height: 1.5;
      color: var(--paper);
      padding-left: 16px;
      border-left: 1px solid var(--acc);
    }}
    @media (max-width: 960px) {{
      .act-head__meta, .act-head__main, .act-head__quote {{
        grid-column: 1 / -1;
        margin-top: 14px;
      }}
    }}

    /* HYB Magazine Bar */
    .hyb-bar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
      flex-wrap: wrap;
      padding: 18px 0;
      border-bottom: 1px solid var(--line);
    }}
    .hyb-bar__btns {{
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }}

    /* ---------- ESCOPOS MONOLÍTICOS (ZARA-GRADE HAIRLINE ROWS) ---------- */
    .scopes-monolith {{
      padding-top: clamp(48px, 8vh, 96px);
      padding-bottom: clamp(48px, 8vh, 96px);
    }}
    .scopes-topline {{
      display: flex;
      align-items: center;
      gap: 18px;
      margin-bottom: clamp(28px, 5vh, 56px);
    }}
    .scopes-rule {{
      flex: 1;
      height: 1px;
      background: var(--line);
    }}
    .scopes-list {{
      display: flex;
      flex-direction: column;
    }}
    .scope-row {{
      display: flex;
      align-items: baseline;
      padding: clamp(24px, 3.5vh, 42px) 0;
      border-bottom: 1px solid var(--line);
      cursor: pointer;
      transition: background 0.3s ease, border-color 0.3s ease;
    }}
    .scope-row:hover {{
      background: rgba(237, 236, 232, 0.02);
      border-bottom-color: var(--mut);
    }}
    .scope-num {{
      font-family: var(--sans);
      font-size: clamp(32px, 4vw, 56px);
      font-weight: 300;
      color: var(--mut);
      width: clamp(60px, 8vw, 110px);
      flex-shrink: 0;
      line-height: 1;
      letter-spacing: -0.02em;
      transition: color 0.3s ease;
    }}
    .scope-row:hover .scope-num {{
      color: var(--acc);
    }}
    .scope-info {{
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 6px;
    }}
    .scope-name {{
      font-family: var(--sans);
      font-size: clamp(20px, 2.2vw, 32px);
      font-weight: 300;
      color: var(--fg);
      margin: 0;
      letter-spacing: -0.01em;
      transition: color 0.3s ease;
    }}
    .scope-row:hover .scope-name {{
      color: var(--paper);
    }}
    .scope-sub {{
      font-family: var(--sans);
      font-size: clamp(13px, 1.2vw, 16px);
      font-weight: 350;
      color: var(--mut);
      margin: 0;
      line-height: 1.5;
    }}
    .scope-action {{
      color: var(--mut);
      letter-spacing: 0.1em;
      font-size: 11px;
      margin-left: 16px;
      transition: color 0.3s ease;
    }}
    .scope-row:hover .scope-action {{
      color: var(--acc);
    }}

    /* ---------- LOOKBOOK — OS 5 ATOS (CONCENTRATED BENTO GRID) ---------- */
    .lookbook-topline {{
      display: flex;
      align-items: center;
      gap: 18px;
      margin-bottom: clamp(24px, 4vh, 40px);
    }}
    .lookbook-rule {{
      flex: 1;
      height: 1px;
      background: var(--line);
    }}
    .bento-lookbook {{
      display: grid;
      grid-template-columns: 1.18fr 1fr;
      grid-template-rows: auto auto auto;
      gap: 16px;
      margin-bottom: clamp(32px, 5vh, 56px);
    }}
    .bento-tile {{
      position: relative;
      border-radius: 2px;
      overflow: hidden;
      cursor: pointer;
      border: 1px solid rgba(237, 236, 232, 0.08);
      background: var(--bg-elev);
      transition: border-color 0.4s ease, transform 0.4s ease, box-shadow 0.4s ease;
    }}
    .bento-tile:hover {{
      border-color: rgba(237, 236, 232, 0.3);
      transform: translateY(-2px);
    }}
    .bento-tile.active-bento {{
      border-color: var(--acc);
      box-shadow: 0 0 0 1px var(--acc);
    }}
    .bento-tile-1 {{
      grid-column: 1 / 2;
      grid-row: 1 / 3;
      min-height: 520px;
      border-color: rgba(255, 107, 26, 0.6);
    }}
    .bento-tile-1:hover {{
      border-color: var(--acc);
    }}
    .bento-tile-2 {{
      grid-column: 2 / 3;
      grid-row: 1 / 2;
      min-height: 250px;
    }}
    .bento-tile-3 {{
      grid-column: 2 / 3;
      grid-row: 2 / 3;
      min-height: 250px;
    }}
    .bento-tile-4 {{
      grid-column: 1 / 2;
      grid-row: 3 / 4;
      min-height: 250px;
    }}
    .bento-tile-5 {{
      grid-column: 2 / 3;
      grid-row: 3 / 4;
      min-height: 250px;
    }}
    @media (max-width: 900px) {{
      .bento-lookbook {{
        grid-template-columns: 1fr;
        grid-template-rows: auto;
      }}
      .bento-tile-1, .bento-tile-2, .bento-tile-3, .bento-tile-4, .bento-tile-5 {{
        grid-column: 1 / -1;
        grid-row: auto;
        min-height: 260px;
      }}
    }}
    .bento-bg {{
      position: absolute;
      inset: 0;
      background-size: cover;
      background-position: center;
      transition: transform 0.7s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.5s ease;
      opacity: 0.65;
    }}
    .bento-tile:hover .bento-bg {{
      transform: scale(1.04);
      opacity: 0.85;
    }}
    .bento-scrim {{
      position: absolute;
      inset: 0;
      background: linear-gradient(180deg, rgba(10, 12, 16, 0.45) 0%, rgba(10, 12, 16, 0.85) 70%, #0A0C10 100%);
      pointer-events: none;
    }}
    .bento-content {{
      position: relative;
      z-index: 2;
      height: 100%;
      box-sizing: border-box;
      padding: clamp(24px, 3.2vw, 44px);
      display: flex;
      flex-direction: column;
      justify-content: flex-end;
      align-items: flex-start;
      gap: 6px;
    }}
    .bento-tag {{
      color: var(--mut);
      letter-spacing: 0.12em;
      font-size: 11px;
      margin-bottom: 2px;
    }}
    .bento-title {{
      font-family: var(--sans);
      font-size: clamp(20px, 2vw, 30px);
      font-weight: 300;
      color: var(--fg);
      margin: 0;
      letter-spacing: -0.01em;
      line-height: 1.25;
    }}
    .bento-desc {{
      font-family: var(--sans);
      font-size: clamp(12px, 1.1vw, 14px);
      font-weight: 350;
      color: var(--mut);
      margin: 0 0 12px 0;
      max-width: 440px;
      line-height: 1.5;
    }}
    .bento-link {{
      color: var(--acc);
      letter-spacing: 0.08em;
      font-size: 11px;
      transition: opacity 0.3s ease;
    }}
    .bento-tile:hover .bento-link {{
      opacity: 0.85;
    }}

    /* Drawer Header */
    .drawer-control {{
      margin-top: 16px;
      margin-bottom: 24px;
      padding: 18px 0;
      border-top: 1px solid var(--line);
      border-bottom: 1px solid var(--line);
    }}
    .drawer-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
      flex-wrap: wrap;
    }}
    .drawer-actions {{
      display: flex;
      gap: 10px;
      align-items: center;
      flex-wrap: wrap;
    }}

    /* Act Sections Drawer Visibility */
    .act-sec {{
      display: none;
    }}
    .act-sec.is-active-act {{
      display: block;
      animation: actFadeIn 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }}
    @keyframes actFadeIn {{
      from {{ opacity: 0; transform: translateY(20px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}

    /* Magazine Showcase Card (Full-width callout inside grid) */
    .plate-magazine-card {{
      grid-column: 1 / -1;
      background: var(--bg-elev);
      border: 1px solid var(--line);
      padding: clamp(32px, 5vw, 64px);
      margin-top: clamp(20px, 3vh, 40px);
      display: flex;
      flex-direction: column;
      gap: 16px;
    }}
    .magazine-card__title {{
      font-family: var(--sans);
      font-size: clamp(22px, 2.5vw, 36px);
      font-weight: 300;
      color: var(--fg);
      margin: 0;
      letter-spacing: -0.01em;
    }}
    .magazine-card__title em {{
      font-style: italic;
      color: var(--paper);
    }}
    .magazine-card__desc {{
      font-family: var(--sans);
      font-size: clamp(14px, 1.2vw, 17px);
      font-weight: 350;
      color: var(--paper);
      opacity: 0.85;
      max-width: 720px;
      line-height: 1.6;
      margin: 0;
    }}
    .magazine-card__actions {{
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
      margin-top: 8px;
    }}

    /* Subseries Divider in Act 05 */
    .subseries-divider {{
      grid-column: 1 / -1;
      margin-top: clamp(36px, 7vh, 84px);
      padding-top: 14px;
      border-top: 1px solid var(--line);
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      gap: 16px;
      flex-wrap: wrap;
    }}
    .subseries-name {{
      font-family: var(--sans);
      font-style: italic;
      font-weight: 300;
      font-size: 15px;
      color: var(--paper);
    }}

    /* ---------- LOOKBOOK GRID (ZARA / BARON & BARON FLOATING PLATES) ---------- */
    .lookbook-grid {{
      display: grid;
      grid-template-columns: repeat(12, 1fr);
      column-gap: var(--gap);
      row-gap: clamp(38px, 8vh, 104px);
      margin-top: clamp(32px, 6vh, 72px);
      align-items: start;
    }}

    /* Pure Floating Plate — Zero Boxed Card */
    .plate {{
      margin: 0;
      cursor: pointer;
      position: relative;
    }}
    .plate__media {{
      position: relative;
      overflow: hidden;
      background: transparent;
    }}
    .plate__media img {{
      width: 100%;
      height: auto;
      display: block;
      transition: transform 0.85s cubic-bezier(.2,.7,.2,1);
    }}
    .plate:hover .plate__media img {{
      transform: scale(1.016);
    }}
    /* Long Behance Strips */
    .plate.orient-strip .plate__media {{
      max-height: 640px;
      overflow: hidden;
      position: relative;
    }}
    .plate.orient-strip .plate__media::after {{
      content: "";
      position: absolute;
      left: 0;
      right: 0;
      bottom: 0;
      height: 110px;
      background: linear-gradient(to bottom, transparent, #07090c);
      pointer-events: none;
    }}
    .strip-badge {{
      position: absolute;
      bottom: 14px;
      left: 14px;
      z-index: 3;
      background: rgba(7, 9, 12, 0.85);
      border: 1px solid var(--acc);
      color: var(--fg);
      padding: 5px 12px;
    }}

    /* Surgical 1-Line Catalog Caption (Zara / prototipo-editorial style) */
    .plate__cap {{
      margin-top: 10px;
      padding-top: 9px;
      border-top: 1px solid var(--line);
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      gap: 12px;
      transition: border-color 0.35s ease;
    }}
    .plate:hover .plate__cap {{
      border-color: var(--acc);
    }}
    .plate__title {{
      color: var(--fg);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      max-width: 74%;
    }}
    .plate__spec {{
      color: var(--mut);
      flex-shrink: 0;
    }}

    /* VIEW [1]: EDITORIAL ASYMMETRIC CHOREOGRAPHY (Default) */
    .ed-col-solo-left   {{ grid-column: 1 / span 8; }}
    .ed-col-solo-right  {{ grid-column: 5 / span 8; }}
    .ed-col-solo-center {{ grid-column: 3 / span 8; }}
    .ed-col-pair-a      {{ grid-column: 1 / span 6; }}
    .ed-col-pair-b      {{ grid-column: 7 / span 6; }}
    .ed-col-spread-a    {{ grid-column: 2 / span 5; }}
    .ed-col-spread-b    {{ grid-column: 7 / span 5; }}
    .ed-col-asym-wide   {{ grid-column: 1 / span 7; }}
    .ed-col-asym-narrow {{ grid-column: 8 / span 5; }}
    .ed-col-full        {{ grid-column: 1 / -1; }}
    .ed-stagger         {{ margin-top: clamp(32px, 9vh, 110px); }}

    /* VIEW [2]: DIPTYCH (2 Equal Columns) */
    body[data-density="2"] .lookbook-grid .plate {{
      grid-column: span 6 !important;
      margin-top: 0 !important;
    }}
    body[data-density="2"] .lookbook-grid .plate.orient-strip {{
      grid-column: 1 / -1 !important;
    }}

    /* VIEW [4]: INDEX CONTACT SHEET (4 Compact Columns) */
    body[data-density="4"] .lookbook-grid {{
      row-gap: 28px;
    }}
    body[data-density="4"] .lookbook-grid .plate {{
      grid-column: span 3 !important;
      margin-top: 0 !important;
    }}
    body[data-density="4"] .lookbook-grid .plate__title {{
      max-width: 100%;
    }}
    body[data-density="4"] .lookbook-grid .plate__spec {{
      display: none;
    }}

    @media (max-width: 960px) {{
      .ed-col-solo-left, .ed-col-solo-right, .ed-col-solo-center,
      .ed-col-asym-wide, .ed-col-asym-narrow {{
        grid-column: 1 / -1;
      }}
      .ed-col-pair-a, .ed-col-spread-a {{ grid-column: 1 / span 6; }}
      .ed-col-pair-b, .ed-col-spread-b {{ grid-column: 7 / span 6; }}
      .ed-stagger {{ margin-top: 28px; }}
      body[data-density="4"] .lookbook-grid .plate {{
        grid-column: span 6 !important;
      }}
    }}
    @media (max-width: 640px) {{
      .lookbook-grid .plate {{
        grid-column: 1 / -1 !important;
        margin-top: 0 !important;
      }}
      body[data-density="2"] .lookbook-grid .plate,
      body[data-density="4"] .lookbook-grid .plate {{
        grid-column: 1 / -1 !important;
      }}
    }}

    /* ---------- 05. COMO TRABALHAMOS / PILLARS (prototipo-editorial.html) ---------- */
    .services {{
      padding-top: clamp(90px, 20vh, 250px);
    }}
    .pillars {{
      margin-top: clamp(34px, 7vh, 84px);
      border-top: 1px solid var(--line);
    }}
    .pillar {{
      display: grid;
      grid-template-columns: 46px minmax(0, 1fr) minmax(0, 1.2fr);
      gap: var(--gap);
      padding: clamp(18px, 3.6vh, 34px) 0;
      border-bottom: 1px solid var(--line);
      align-items: start;
    }}
    .pillar__name {{
      font-size: clamp(16px, 1.6vw, 23px);
      letter-spacing: 0.03em;
      text-transform: uppercase;
      font-weight: 300;
    }}
    .pillar__txt {{
      color: var(--mut);
      max-width: 48ch;
    }}
    @media (max-width: 760px) {{
      .pillar {{ grid-template-columns: 30px minmax(0, 1fr); }}
      .pillar__txt {{ grid-column: 2; }}
    }}

    /* ---------- TICKER (prototipo-editorial.html) ---------- */
    .ticker {{
      margin-top: clamp(80px, 18vh, 220px);
      border-top: 1px solid var(--line);
      border-bottom: 1px solid var(--line);
      padding: 16px 0;
      overflow: hidden;
    }}
    .ticker__in {{
      display: flex;
      white-space: nowrap;
      animation: slide 46s linear infinite;
    }}
    .ticker__in span {{
      padding-right: 52px;
      font-size: 11px;
      letter-spacing: 0.34em;
      text-transform: uppercase;
      color: var(--mut);
    }}
    @keyframes slide {{
      from {{ transform: translateX(0); }}
      to {{ transform: translateX(-50%); }}
    }}

    /* ---------- 06. CONTATO & BRIEFING ---------- */
    .contact {{
      padding-top: clamp(90px, 22vh, 260px);
      padding-bottom: clamp(60px, 12vh, 150px);
    }}
    .contact__big {{
      margin: 0;
      font-size: clamp(40px, 8.4vw, 148px);
      line-height: 0.88;
      font-weight: 300;
      letter-spacing: -0.035em;
      text-transform: uppercase;
    }}
    .contact__big a {{
      border-bottom: 1px solid transparent;
      transition: border-color 0.4s ease, color 0.4s ease;
    }}
    .contact__big a:hover {{
      color: var(--acc);
      border-color: var(--acc);
    }}

    .brief-box {{
      margin-top: clamp(36px, 7vh, 80px);
      padding-top: 28px;
      border-top: 1px solid var(--line);
      display: grid;
      grid-template-columns: repeat(12, 1fr);
      gap: var(--gap);
    }}
    .brief-field {{
      grid-column: span 5;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }}
    .brief-actions {{
      grid-column: span 2;
      display: flex;
      flex-direction: column;
      justify-content: flex-end;
      gap: 8px;
    }}
    .brief-input {{
      background: transparent;
      border: none;
      border-bottom: 1px solid var(--line-strong);
      color: var(--fg);
      font-family: var(--sans);
      font-weight: 300;
      font-size: 13px;
      padding: 10px 0;
      outline: none;
    }}
    .brief-input:focus {{
      border-color: var(--acc);
    }}
    .brief-input option {{
      background: #0d1017;
      color: var(--fg);
    }}
    @media (max-width: 900px) {{
      .brief-field, .brief-actions {{ grid-column: 1 / -1; }}
    }}

    /* ---------- FOOTER (prototipo-editorial.html) ---------- */
    .foot {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: var(--gap);
      padding-top: 26px;
      padding-bottom: 40px;
      border-top: 1px solid var(--line);
    }}
    .foot ul {{
      list-style: none;
      margin: 12px 0 0;
      padding: 0;
      display: grid;
      gap: 7px;
    }}
    .foot a {{
      border-bottom: 1px solid transparent;
      transition: color 0.25s ease;
    }}
    .foot a:hover {{
      color: var(--acc);
    }}
    @media (max-width: 860px) {{
      .foot {{ grid-template-columns: repeat(2, 1fr); row-gap: 34px; }}
    }}
    @media (max-width: 480px) {{
      .foot {{ grid-template-columns: 1fr; }}
    }}

    /* ---------- MUSEUM LIGHTBOX & 24-PAGE MAGAZINE READER ---------- */
    .lightbox {{
      position: fixed;
      inset: 0;
      z-index: 9500;
      background: rgba(7, 9, 12, 0.96);
      backdrop-filter: blur(18px);
      -webkit-backdrop-filter: blur(18px);
      display: none;
      flex-direction: column;
      justify-content: space-between;
    }}
    .lightbox.open {{
      display: flex;
    }}
    .lb-top {{
      height: 52px;
      padding: 0 var(--pad);
      border-bottom: 1px solid var(--line);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
    }}
    .lb-stage {{
      flex: 1;
      position: relative;
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: auto;
      padding: 24px var(--pad);
    }}
    .lb-stage.strip-mode {{
      align-items: flex-start;
    }}
    .lb-stage img {{
      max-width: 90vw;
      max-height: 76vh;
      width: auto;
      height: auto;
      object-fit: contain;
      box-shadow: 0 24px 64px rgba(0, 0, 0, 0.85);
    }}
    .lb-stage.strip-mode img {{
      max-height: none;
      width: min(980px, 90vw);
    }}
    .lb-arrow {{
      position: fixed;
      top: 50%;
      transform: translateY(-50%);
      background: rgba(7, 9, 12, 0.75);
      border: 1px solid var(--line-strong);
      color: var(--fg);
      width: 44px;
      height: 44px;
      border-radius: 50%;
      display: grid;
      place-items: center;
      z-index: 9510;
      transition: border-color 0.25s ease, color 0.25s ease;
    }}
    .lb-arrow:hover {{
      border-color: var(--acc);
      color: var(--acc);
    }}
    .lb-arrow--prev {{ left: 20px; }}
    .lb-arrow--next {{ right: 20px; }}
    .lb-foot {{
      padding: 14px var(--pad);
      border-top: 1px solid var(--line);
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      gap: 20px;
      flex-wrap: wrap;
    }}
    .lb-title {{
      font-size: 14px;
      font-weight: 300;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--fg);
      margin: 0;
    }}
    .lb-caption {{
      margin: 4px 0 0;
      font-size: 12px;
      color: var(--mut);
    }}
  </style>
</head>
<body data-density="2">

  <!-- Procedural SVG Surface Texture (Optimized 2.5% Opacity) -->
  <svg class="tactile-grain" aria-hidden="true">
    <filter id="hyb-tactile-noise">
      <feTurbulence type="fractalNoise" baseFrequency="0.78" numOctaves="3" stitchTiles="stitch" />
      <feColorMatrix type="saturate" values="0" />
    </filter>
    <rect width="100%" height="100%" filter="url(#hyb-tactile-noise)" />
  </svg>

  <!-- TOPBAR CHROME (prototipo-editorial.html) -->
  <div class="topbar micro">
    <a href="#topo" class="micro--fg">HYB — STUDIO <span class="mono micro--acc">// HTF</span></a>
    <nav class="topbar__nav" aria-label="Navegação Principal">
      <a href="#posicao">01 Posição</a>
      <a href="#escopos">02 Escopos</a>
      <a href="#lookbook">03 Lookbook (5 Atos)</a>
      <a href="#ato-revista_hyb" onclick="openMagazineReader(0)">Revista HYB (24 Pág.)</a>
      <a href="#contato">04 Contato</a>
    </nav>
    <span class="avail"><span class="dot"></span>Novos projetos sob consulta</span>
    <span class="mono" data-clock>São Paulo —:—</span>
  </div>

  <!-- READING PROGRESS INDICATOR (DISCREET & UNCLUTTERED) -->
  <div class="edge edge--l micro mono" data-prog>000%</div>

  <!-- FLOATING MAGNETIC CURSOR -->
  <div class="cursor" data-cursor><span>Ver</span></div>

  <!-- 01. HERO (prototipo-editorial.html) -->
  <header class="sec hero" id="topo">
    <div class="hero__meta micro">
      <span>01 — Posicionamento</span>
      <span class="mono">HYB — STUDIO · Henrique Taveira (DALLIDO.1988)</span>
      <span class="mono">São Paulo · 2026</span>
    </div>
    <div class="hero__grid">
      <div class="title__wrap">
        <h1 class="title" data-reveal>
          <span>Estratégia,</span>
          <span class="l2">direção criativa</span>
          <span class="l3">e <em>linguagem</em></span>
        </h1>
      </div>
      <figure class="hero__fig fig" data-reveal data-view onclick="openLightboxById('bureau_001')" title="Inspecionar Peça Matriz">
        <img src="{hero_cover_url}" alt="Capa Monumental do Caderno de Branding — HYB STUDIO">
      </figure>
    </div>
    <div class="hero__foot micro">
      <span>Pensamento estratégico · Direção criativa · Conteúdo · Execução</span>
      <div style="display:flex;gap:10px;flex-wrap:wrap">
        <button type="button" class="btn-editorial btn-editorial--acc" onclick="openMagazineReader(0)">▶ Revista HYB (24 Pág.)</button>
        <a href="#acervo" class="btn-editorial">Explorar Acervo ({total_all} Obras) ↓</a>
      </div>
      <span class="mono">A máquina propõe. O humano autoriza.</span>
    </div>
  </header>

  <!-- 02. POSIÇÃO / MANIFESTO (prototipo-editorial.html) -->
  <section class="sec manifesto g" id="posicao">
    <div class="manifesto__label micro" data-reveal><span class="mono micro--acc">02</span> — Posição</div>
    <p class="manifesto__lead" data-reveal>Um estúdio criativo autoral (HYB) que combina pensamento estratégico, direção de arte com repertório plástico de ateliê e produção de conteúdo para negócios que recusam o genérico. A operação é híbrida por natureza: estratégia, criação, edição e execução acontecem no mesmo lugar, com clareza de processo e coerência entre conceito e entrega.</p>
    <blockquote class="manifesto__quote" data-reveal>“A diferenciação não está no discurso: está no portfólio, na qualidade do raciocínio, na linguagem, na coerência entre conceito e execução e na clareza de processo.”</blockquote>
  </section>

  <!-- 03. ESCOPOS (MONOLITHIC ZARA-GRADE ROWS) -->
  <section class="sec scopes-monolith" id="escopos">
    <div class="scopes-topline" data-reveal>
      <span class="micro mono micro--acc">ESCOPOS</span>
      <div class="scopes-rule"></div>
    </div>
    <div class="scopes-list">
      <div class="scope-row" data-reveal onclick="selectServiceModalidade('01. Diagnóstico de Comunicação')">
        <span class="scope-num">01</span>
        <div class="scope-info">
          <h3 class="scope-name">Diagnóstico de Comunicação</h3>
          <p class="scope-sub">Auditoria estratégica de linguagem e posicionamento.</p>
        </div>
        <span class="scope-action micro mono">CONSULTAR ↗</span>
      </div>

      <div class="scope-row" data-reveal onclick="selectServiceModalidade('02. Estratégia & Direção Criativa')">
        <span class="scope-num">02</span>
        <div class="scope-info">
          <h3 class="scope-name">Estratégia Criativa &amp; DNA</h3>
          <p class="scope-sub">Construção de identidade e território de marca.</p>
        </div>
        <span class="scope-action micro mono">CONSULTAR ↗</span>
      </div>

      <div class="scope-row" data-reveal onclick="selectServiceModalidade('03. Conteúdo & Presença Digital')">
        <span class="scope-num">03</span>
        <div class="scope-info">
          <h3 class="scope-name">Retainer Editorial de Conteúdo</h3>
          <p class="scope-sub">Direção contínua de imagem, texto e publicação.</p>
        </div>
        <span class="scope-action micro mono">CONSULTAR ↗</span>
      </div>

      <div class="scope-row" data-reveal onclick="selectServiceModalidade('04. HYB Integrado')">
        <span class="scope-num">04</span>
        <div class="scope-info">
          <h3 class="scope-name">Direção Integrada HYB</h3>
          <p class="scope-sub">Estrutura completa de direção criativa e estratégia.</p>
        </div>
        <span class="scope-action micro mono">CONSULTAR ↗</span>
      </div>
    </div>
  </section>

  <!-- TRANSIÇÃO EDITORIAL: INFRAESTRUTURA & CURADORIA HUMANA -->
  <section class="sec transition-sec g" id="metodo">
    <div class="micro transition-kicker" data-reveal style="grid-column: 1 / span 3">
      <span class="mono micro--acc">MÉTODO</span> — Ateliê Híbrido
    </div>
    <div class="transition-lead" data-reveal style="grid-column: 4 / span 8">
      <p class="note" style="margin: 0; font-size: clamp(17px, 1.8vw, 26px); line-height: 1.45;">
        “A máquina propõe na velocidade da luz; a mão humana julga, corta e assina no tempo da matéria. Ferramentas digitais e inteligência artificial entram como infraestrutura de trabalho — nunca como substituto do repertório, da autoria ou do rigor estético.”
      </p>
      <div class="micro" style="margin-top: 24px; padding-top: 14px; border-top: 1px solid var(--line); display: flex; justify-content: space-between; gap: 16px; flex-wrap: wrap;">
        <span>5 Atos Editoriais · {total_all} Obras Catalogadas · Sem Intermediários</span>
        <a href="#acervo" class="micro--acc">Explorar Acervo Curatorial ↓</a>
      </div>
    </div>
  </section>

  <!-- 04. LOOKBOOK — OS 5 ATOS (CONCENTRATED BENTO GRID) -->
  <section class="sec archive-sec" id="lookbook">
    <div class="lookbook-topline" data-reveal>
      <span class="micro mono micro--acc">LOOKBOOK — OS 5 ATOS</span>
      <div class="lookbook-rule"></div>
    </div>

    <!-- Asymmetrical Bento Grid (Concentrated Portals) -->
    <div class="bento-lookbook" data-reveal>
      <!-- ATO 01: REVISTA HYB (Featured Tall Tile on Left) -->
      <div class="bento-tile bento-tile-1" data-bento-act="revista_hyb" onclick="openActPortal('revista_hyb')">
        <div class="bento-bg" style="background-image: url('assets/revista_hyb/01_HYB_ED01_PAG_01_CAPA.png')"></div>
        <div class="bento-scrim"></div>
        <div class="bento-content">
          <span class="micro mono bento-tag">ATO 01</span>
          <h3 class="bento-title">Revista HYB</h3>
          <p class="bento-desc">Magazine editorial. Publicação impressa e digital.</p>
          <span class="bento-link micro mono">↗ ACESSAR EDIÇÃO</span>
        </div>
      </div>

      <!-- ATO 02: CALÇADOS ESCULTÓRICOS (Top Right) -->
      <div class="bento-tile bento-tile-2" data-bento-act="shoes" onclick="openActPortal('shoes')">
        <div class="bento-bg" style="background-image: url('assets/shoes/001_SHOES_2.0_005.jpg')"></div>
        <div class="bento-scrim"></div>
        <div class="bento-content">
          <span class="micro mono bento-tag">ATO 02</span>
          <h3 class="bento-title">Design de Calçados Escultóricos</h3>
          <p class="bento-desc">Forma, matéria e função como linguagem.</p>
          <span class="bento-link micro mono">↗ EXPLORAR ATO</span>
        </div>
      </div>

      <!-- ATO 03: LAMBE-LAMBE URBANO (Middle Right) -->
      <div class="bento-tile bento-tile-3" data-bento-act="boys_lambe" onclick="openActPortal('boys_lambe')">
        <div class="bento-bg" style="background-image: url('assets/boys_lambe/HYB_ED01_PAG_21.png')"></div>
        <div class="bento-scrim"></div>
        <div class="bento-content">
          <span class="micro mono bento-tag">ATO 03</span>
          <h3 class="bento-title">Lambe-lambe Urbano</h3>
          <p class="bento-desc">Intervenção gráfica. Rua como suporte.</p>
          <span class="bento-link micro mono">↗ EXPLORAR ATO</span>
        </div>
      </div>

      <!-- ATO 04: ÓLEO SOBRE LINHO CRU (Bottom Left) -->
      <div class="bento-tile bento-tile-4" data-bento-act="acervo_materico" onclick="openActPortal('acervo_materico')">
        <div class="bento-bg" style="background-image: url('assets/acervo_materico/007_L1010570.jpg')"></div>
        <div class="bento-scrim"></div>
        <div class="bento-content">
          <span class="micro mono bento-tag">ATO 04</span>
          <h3 class="bento-title">Óleo sobre Linho Cru</h3>
          <p class="bento-desc">Pintura. Gesto e pigmento como manifesto.</p>
          <span class="bento-link micro mono">↗ EXPLORAR ATO</span>
        </div>
      </div>

      <!-- ATO 05: CASES MONOLÍTICOS ARQUITETÔNICOS (Bottom Right) -->
      <div class="bento-tile bento-tile-5" data-bento-act="bureau" onclick="openActPortal('bureau')">
        <div class="bento-bg" style="background-image: url('assets/bureau/08-10-2026%20CAMPANHA/rochosa%2002.jpg')"></div>
        <div class="bento-scrim"></div>
        <div class="bento-content">
          <span class="micro mono bento-tag">ATO 05</span>
          <h3 class="bento-title">Cases Monolíticos Arquitetônicos</h3>
          <p class="bento-desc">Estratégia e direção em escala de marca.</p>
          <span class="bento-link micro mono">↗ EXPLORAR ATO</span>
        </div>
      </div>
    </div>

    <!-- Active Drawer Controller -->
    <div id="actDrawerControl" class="drawer-control" style="display: none;" data-reveal>
      <div class="drawer-header">
        <span class="micro mono micro--acc" id="drawerActTitle">ACERVO ABERTO</span>
        <div class="drawer-actions">
          <button type="button" class="btn-editorial btn-editorial--acc" id="drawerInspectBtn" onclick="inspectCurrentAct()">▶ Inspecionar Obras</button>
          <button type="button" class="btn-editorial" onclick="closeActDrawer()">Fechar Acervo ✕</button>
        </div>
      </div>
    </div>

    {acts_html_content}
  </section>



  <!-- TICKER (prototipo-editorial.html) -->
  <div class="ticker" aria-hidden="true">
    <div class="ticker__in">
      <span>Estratégia</span><span>Direção criativa</span><span>Linguagem</span><span>Revista HYB</span><span>Acervo Matérico</span><span>Curadoria</span>
      <span>Estratégia</span><span>Direção criativa</span><span>Linguagem</span><span>Revista HYB</span><span>Acervo Matérico</span><span>Curadoria</span>
    </div>
  </div>

  <!-- 06. CONTATO (prototipo-editorial.html) -->
  <section class="sec contact" id="contato">
    <div class="micro" data-reveal><span class="mono micro--acc">06</span> — Contato &amp; Diagnóstico</div>
    <h2 class="contact__big" data-reveal style="margin-top:clamp(20px,5vh,60px)">
      <a href="mailto:henrique992338736@gmail.com">Vamos falar</a>
    </h2>
    <div class="g" data-reveal style="margin-top:clamp(34px,8vh,96px)">
      <p class="note" style="grid-column:1 / span 6;margin:0">Cada projeto é definido por escopo, prazo e faixas sob consulta. Conte o contexto, o momento da marca e o que precisa mudar.</p>
      <div class="micro" style="grid-column:9 / span 4">
        Novos projetos &amp; Consultoria<br>
        <span class="mono micro--fg">henrique992338736@gmail.com</span><br>
        <span class="mono">henrique950704952@gmail.com</span><br>
        <span class="mono">+55 11 95070-4952</span>
      </div>
    </div>

    <!-- Interactive Briefing Dispatch -->
    <div class="brief-box" data-reveal>
      <div class="brief-field">
        <label class="micro" for="modalidadeSelect">Modalidade de interesse</label>
        <select id="modalidadeSelect" class="brief-input">
          <option value="01. Diagnóstico de Comunicação">01. Diagnóstico de Comunicação (Projeto único)</option>
          <option value="02. Estratégia & Direção Criativa">02. Estratégia &amp; Direção Criativa (Projeto único)</option>
          <option value="03. Conteúdo & Presença Digital">03. Conteúdo &amp; Presença Digital (Mensal)</option>
          <option value="04. HYB Integrado" selected>04. HYB Integrado (Direção Completa Mensal)</option>
          <option value="05. Aquisição de Obra / Acervo Autoral">05. Aquisição de Obra / Acervo Fine-Art</option>
        </select>
      </div>
      <div class="brief-field">
        <label class="micro" for="contextoInput">Marca, link atual ou necessidade principal</label>
        <input type="text" id="contextoInput" class="brief-input" placeholder="Ex.: Reposicionamento editorial, direção criativa ou diagnóstico...">
      </div>
      <div class="brief-actions">
        <button type="button" class="btn-editorial btn-editorial--acc" onclick="dispararEmailDiagnostico()">Enviar por E-mail ↗</button>
        <button type="button" class="btn-editorial" id="copyBriefBtn" onclick="copiarMensagemBriefing()">Copiar Briefing</button>
      </div>
    </div>
  </section>

  <!-- FOOTER (prototipo-editorial.html) -->
  <footer class="sec">
    <div class="foot micro">
      <div>Escopos
        <ul>
          <li><a href="#escopo-01">01 Diagnóstico de comunicação</a></li>
          <li><a href="#escopo-02">02 Estratégia e direção criativa</a></li>
          <li><a href="#escopo-03">03 Conteúdo e presença digital</a></li>
          <li><a href="#escopo-04">04 HYB Integrado</a></li>
        </ul>
      </div>
      <div>Acervo (5 Atos)
        <ul>
          <li><a href="#ato-revista_hyb">Ato 01 — Revista HYB (24 Pág.)</a></li>
          <li><a href="#ato-shoes">Ato 02 — Caderno Shoes</a></li>
          <li><a href="#ato-boys_lambe">Ato 03 — Boys &amp; A Rua</a></li>
          <li><a href="#ato-acervo_materico">Ato 04 — Acervo Matérico</a></li>
          <li><a href="#ato-bureau">Ato 05 — HYB &amp; Cases</a></li>
        </ul>
      </div>
      <div>Como trabalhamos
        <ul>
          <li><a href="#servicos">Prazos e revisões</a></li>
          <li><a href="#servicos">Demandas extras</a></li>
          <li><a href="#servicos">Mídia paga e terceiros</a></li>
          <li><a href="#uso-de-ia">Uso de IA &amp; Curadoria</a></li>
        </ul>
      </div>
      <div>Contato &amp; Redes
        <ul>
          <li><a href="mailto:henrique992338736@gmail.com">henrique992338736@gmail.com</a></li>
          <li><a href="tel:+5511950704952">+55 11 95070-4952</a></li>
          <li><a href="https://instagram.com/dallido.1988" target="_blank" rel="noreferrer">@dallido.1988 ↗</a></li>
          <li><a href="https://instagram.com/fariatitan" target="_blank" rel="noreferrer">@fariatitan ↗</a></li>
        </ul>
      </div>
    </div>
    <div class="micro mono" style="display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;padding:18px 0 36px">
      <span>© 2026 HYB — STUDIO · Henrique Taveira Ferreira (DALLIDO.1988)</span>
      <span>São Paulo · Brasil</span>
      <span data-prog>000%</span>
    </div>
  </footer>

  <!-- MUSEUM LIGHTBOX & 24-PAGE MAGAZINE READER MODAL -->
  <div class="lightbox" id="museumLightbox" role="dialog" aria-modal="true" aria-label="Inspeção de Obra">
    <div class="lb-top micro">
      <div>
        <span class="mono micro--acc" id="lbCounter">01 / {total_all}</span>
        <span style="margin-left:14px" id="lbSeries">SÉRIE</span>
      </div>
      <div style="display:flex;align-items:center;gap:10px">
        <a href="{hyb_pdf_url}" target="_blank" rel="noopener" id="lbPdfLink" class="btn-editorial" style="display:none">⬇ PDF Completo (24 Pág.) ↗</a>
        <button type="button" class="btn-editorial" onclick="closeLightbox()">Fechar [ESC]</button>
      </div>
    </div>

    <div class="lb-stage" id="lbStage" onclick="handleStageClick(event)">
      <button type="button" class="lb-arrow lb-arrow--prev" onclick="stepLightbox(-1)" aria-label="Anterior">←</button>
      <img id="lbImage" src="" alt="">
      <button type="button" class="lb-arrow lb-arrow--next" onclick="stepLightbox(1)" aria-label="Próxima">→</button>
    </div>

    <div class="lb-foot">
      <div>
        <h4 class="lb-title" id="lbTitle">Título</h4>
        <p class="lb-caption" id="lbCaption">Legenda</p>
      </div>
      <div class="micro mono" id="lbSpecs">PROPORÇÃO · DIMENSÕES</div>
    </div>
  </div>

  <!-- SCRIPTS: PROTOTIPO-EDITORIAL INTERACTIONS + ZARA DENSITY + LIGHTBOX -->
  <script>
    const ALL_WORKS = {works_json_str};
    let currentFilter = 'all';
    let currentFilteredWorks = [...ALL_WORKS];
    let currentLightboxIndex = 0;

    // 1. Prototipo-Editorial Reveal, Progress, Live Clock & Magnetic Cursor
    (function() {{
      var els = Array.prototype.slice.call(document.querySelectorAll('[data-reveal]'));
      if ('IntersectionObserver' in window) {{
        var io = new IntersectionObserver(function(entries) {{
          entries.forEach(function(e) {{
            if (e.isIntersecting) {{
              e.target.classList.add('is-in');
              io.unobserve(e.target);
            }}
          }});
        }}, {{ rootMargin: '0px 0px -6% 0px', threshold: 0.03 }});
        els.forEach(function(el) {{ io.observe(el); }});
      }} else {{
        els.forEach(function(el) {{ el.classList.add('is-in'); }});
      }}

      var progs = document.querySelectorAll('[data-prog]');
      function onScroll() {{
        var h = document.documentElement.scrollHeight - window.innerHeight;
        var v = h > 0 ? (window.pageYOffset / h) * 100 : 0;
        var t = ('00' + Math.round(v)).slice(-3) + '%';
        Array.prototype.forEach.call(progs, function(p) {{ p.textContent = t; }});
      }}
      window.addEventListener('scroll', onScroll, {{ passive: true }});
      onScroll();

      var clock = document.querySelector('[data-clock]');
      function tick() {{
        if (!clock) return;
        try {{
          clock.textContent = 'São Paulo ' + new Date().toLocaleTimeString('pt-BR', {{
            timeZone: 'America/Sao_Paulo',
            hour: '2-digit',
            minute: '2-digit'
          }});
        }} catch (e) {{
          clock.textContent = 'São Paulo';
        }}
      }}
      tick();
      setInterval(tick, 20000);

      var cur = document.querySelector('[data-cursor]');
      Array.prototype.forEach.call(document.querySelectorAll('[data-view]'), function(fig) {{
        fig.addEventListener('mouseenter', function() {{ if (cur) cur.classList.add('on'); }});
        fig.addEventListener('mouseleave', function() {{ if (cur) cur.classList.remove('on'); }});
        fig.addEventListener('mousemove', function(ev) {{
          if (cur) cur.style.transform = 'translate3d(' + ev.clientX + 'px,' + (ev.clientY - 39) + 'px,0) translate(-50%,-50%)';
        }});
      }});
    }})();

    // 2. Zara Grid Density Switcher ([1] Editorial, [2] Diptych, [4] Index)
    function setGridDensity(mode) {{
      document.body.setAttribute('data-density', mode);
      document.querySelectorAll('[data-view-btn]').forEach(function(btn) {{
        btn.classList.toggle('active', btn.getAttribute('data-view-btn') === mode);
      }});
    }}

    // 3. Category Filtering
    function filterCatalog(catKey) {{
      currentFilter = catKey;
      document.querySelectorAll('[data-filter]').forEach(function(btn) {{
        btn.classList.toggle('active', btn.getAttribute('data-filter') === catKey);
      }});

      document.querySelectorAll('[data-act-section]').forEach(function(sec) {{
        var secKey = sec.getAttribute('data-act-section');
        if (catKey === 'all' || secKey === catKey) {{
          sec.classList.remove('hidden-act');
        }} else {{
          sec.classList.add('hidden-act');
        }}
      }});

      if (catKey === 'all') {{
        currentFilteredWorks = [...ALL_WORKS];
      }} else {{
        currentFilteredWorks = ALL_WORKS.filter(function(w) {{ return w.cat === catKey; }});
      }}
    }}

    // 4. Lightbox & 24-Page Magazine Reader
    function openLightboxById(workId) {{
      var idx = currentFilteredWorks.findIndex(function(w) {{ return w.id === workId; }});
      if (idx === -1) {{
        currentFilteredWorks = [...ALL_WORKS];
        idx = currentFilteredWorks.findIndex(function(w) {{ return w.id === workId; }});
      }}
      if (idx === -1) idx = 0;
      currentLightboxIndex = idx;
      renderLightboxSlide();
      document.getElementById('museumLightbox').classList.add('open');
      document.body.style.overflow = 'hidden';
    }}

    function openMagazineReader(pageZeroIndex) {{
      currentFilteredWorks = ALL_WORKS.filter(function(w) {{ return w.cat === 'revista_hyb'; }});
      currentLightboxIndex = Math.max(0, Math.min(pageZeroIndex || 0, currentFilteredWorks.length - 1));
      renderLightboxSlide();
      document.getElementById('museumLightbox').classList.add('open');
      document.body.style.overflow = 'hidden';
    }}

    function renderLightboxSlide() {{
      if (!currentFilteredWorks.length) return;
      var item = currentFilteredWorks[currentLightboxIndex];
      var imgEl = document.getElementById('lbImage');
      var stageEl = document.getElementById('lbStage');
      var pdfBtn = document.getElementById('lbPdfLink');

      imgEl.src = item.url;
      imgEl.alt = item.title;

      if (item.orient === 'strip') {{
        stageEl.classList.add('strip-mode');
        stageEl.scrollTop = 0;
      }} else {{
        stageEl.classList.remove('strip-mode');
      }}

      if (item.cat === 'revista_hyb') {{
        pdfBtn.style.display = 'inline-flex';
        document.getElementById('lbCounter').textContent = 'PÁGINA ' + String(currentLightboxIndex + 1).padStart(2, '0') + ' / ' + String(currentFilteredWorks.length).padStart(2, '0');
      }} else {{
        pdfBtn.style.display = 'none';
        document.getElementById('lbCounter').textContent = String(currentLightboxIndex + 1).padStart(2, '0') + ' / ' + String(currentFilteredWorks.length).padStart(2, '0');
      }}

      document.getElementById('lbSeries').textContent = item.series;
      document.getElementById('lbTitle').textContent = item.title;
      document.getElementById('lbCaption').textContent = item.caption;
      document.getElementById('lbSpecs').textContent = item.aspect + ' · ' + item.w + '×' + item.h + 'PX · ' + item.path;
    }}

    function stepLightbox(delta) {{
      if (!currentFilteredWorks.length) return;
      currentLightboxIndex = (currentLightboxIndex + delta + currentFilteredWorks.length) % currentFilteredWorks.length;
      renderLightboxSlide();
    }}

    function closeLightbox() {{
      document.getElementById('museumLightbox').classList.remove('open');
      document.body.style.overflow = '';
    }}

    function handleStageClick(e) {{
      if (e.target.id === 'lbStage') closeLightbox();
    }}

    document.addEventListener('keydown', function(e) {{
      var lb = document.getElementById('museumLightbox');
      if (!lb.classList.contains('open')) return;
      if (e.key === 'Escape') closeLightbox();
      else if (e.key === 'ArrowRight') stepLightbox(1);
      else if (e.key === 'ArrowLeft') stepLightbox(-1);
    }});

    // 5. Briefing & Contact Dispatch
    function selectServiceModalidade(modalidadeNome) {{
      var sel = document.getElementById('modalidadeSelect');
      if (sel) sel.value = modalidadeNome;
      var contatoSec = document.getElementById('contato');
      if (contatoSec) contatoSec.scrollIntoView({{ behavior: 'smooth' }});
      setTimeout(function() {{
        var input = document.getElementById('contextoInput');
        if (input) input.focus();
      }}, 650);
    }}

    function montarTextoBriefing() {{
      var mod = document.getElementById('modalidadeSelect').value;
      var ctx = document.getElementById('contextoInput').value.trim();
      var msg = 'Olá, Henrique. Acessei o site oficial do Bureau Criativo Autoral e gostaria de solicitar informações sobre:\\n\\n• Modalidade: ' + mod;
      if (ctx) msg += '\\n• Contexto / Projeto: ' + ctx;
      msg += '\\n\\nAguardo retorno para agendarmos uma conversa inicial.';
      return msg;
    }}

    function dispararEmailDiagnostico() {{
      var mod = document.getElementById('modalidadeSelect').value;
      var subject = encodeURIComponent('[HYB — STUDIO] Solicitação — ' + mod);
      var body = encodeURIComponent(montarTextoBriefing());
      window.location.href = 'mailto:henrique992338736@gmail.com?subject=' + subject + '&body=' + body;
    }}

    function copiarMensagemBriefing() {{
      var texto = montarTextoBriefing();
      var btn = document.getElementById('copyBriefBtn');
      if (navigator.clipboard && navigator.clipboard.writeText) {{
        navigator.clipboard.writeText(texto).then(function() {{
          var orig = btn.textContent;
          btn.textContent = 'Copiado [✓]';
          setTimeout(function() {{ btn.textContent = orig; }}, 2400);
        }});
      }}
    }}
  </script>
</body>
</html>
'''

# Write primary outputs in WEBSITE/
index_out = os.path.join(website_dir, 'index.html')
mirror_out = os.path.join(website_dir, 'PORTFOLIO_SITE_ATELIE_BUREAU.html')

with open(index_out, 'w', encoding='utf-8') as f:
    f.write(html_document)

with open(mirror_out, 'w', encoding='utf-8') as f:
    f.write(html_document)

# Also update the root mirrors in (011)BUREAU_CRIATIVO_AUTORAL so neither is stale
parent_bureau = os.path.dirname(website_dir)
html_parent_mirror = html_document.replace('"assets/', '"WEBSITE/assets/').replace("'assets/", "'WEBSITE/assets/")
with open(os.path.join(parent_bureau, 'index.html'), 'w', encoding='utf-8') as f:
    f.write(html_parent_mirror)
with open(os.path.join(parent_bureau, 'PORTFOLIO_SITE_ATELIE_BUREAU.html'), 'w', encoding='utf-8') as f:
    f.write(html_parent_mirror)

# Ensure robots.txt, sitemap.xml, .nojekyll and .gitignore exist in WEBSITE/
robots_out = os.path.join(website_dir, 'robots.txt')
with open(robots_out, 'w', encoding='utf-8') as f:
    f.write("User-agent: *\nAllow: /\nSitemap: https://fariatitan.github.io/HYB/sitemap.xml\n")

sitemap_out = os.path.join(website_dir, 'sitemap.xml')
with open(sitemap_out, 'w', encoding='utf-8') as f:
    f.write('''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://fariatitan.github.io/HYB/</loc>
    <lastmod>2026-10-17</lastmod>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://fariatitan.github.io/HYB/assets/revista_hyb/REVISTA_HYB_ED01_24_PAGINAS.pdf</loc>
    <lastmod>2026-10-17</lastmod>
    <priority>0.8</priority>
  </url>
</urlset>
''')

nojekyll_out = os.path.join(website_dir, '.nojekyll')
with open(nojekyll_out, 'w', encoding='utf-8') as f:
    f.write("")

gitignore_out = os.path.join(website_dir, '.gitignore')
with open(gitignore_out, 'w', encoding='utf-8') as f:
    f.write("**/LIXO/\n**/lixo/\n__pycache__/\n*.pyc\ndesktop.ini\nThumbs.db\n.DS_Store\n")

# Automated Self-Audit
assert '../' not in html_document, "ERROR: Found '../' parent path in HTML!"
assert 'lixo' not in html_document.lower(), "ERROR: Found 'LIXO' reference in HTML!"
assert 'lixo' not in json.dumps(catalog).lower(), "ERROR: Found 'LIXO' reference in curated_catalog.json!"
assert 'data:image/' not in html_document.lower(), "ERROR: Found forbidden Base64 embedded image!"
assert not re.search(r'font-weight\s*:\s*([6789]00|bold)', html_document, re.I), "ERROR: Found forbidden bold font-weight!"
assert not re.search(r'(Georgia|Times New Roman|Playfair|Cinzel|Didot)', html_document, re.I), "ERROR: Found non-Segoe serif font!"
assert os.path.exists(os.path.join(website_dir, hyb_pdf_url.replace('/', os.sep))), "ERROR: Missing 24-page PDF!"

img_srcs = [s for s in re.findall(r'<img[^>]+src="([^"]+)"', html_document) if s]
for s in img_srcs:
    disk_path = os.path.join(website_dir, unquote(s).replace('/', os.sep))
    assert os.path.exists(disk_path), f"ERROR: Missing image on disk: {disk_path}"

print(f"Generated autonomous editorial website in {website_dir}:")
print(f" - index.html ({len(html_document)} bytes)")
print(f" - PORTFOLIO_SITE_ATELIE_BUREAU.html ({len(html_document)} bytes)")
print(f" - curated_catalog.json ({total_all} curated items)")
print(f" - {hyb_pdf_url} (24-page Magazine PDF)")
print(f"SELF-AUDIT PASSED: {len(img_srcs)} <img> tags + 24-page PDF verified on disk | 100% Segoe UI Light/Semilight | 0 '../' paths | 0 Base64 blobs | 0 'LIXO' files | 0 bold weights.")

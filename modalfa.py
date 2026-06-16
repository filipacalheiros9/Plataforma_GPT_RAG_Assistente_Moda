import requests
from bs4 import BeautifulSoup
import csv
import time

base_url = "https://mo-online.com/on/demandware.store/Sites-mo-Site/pt_PT/Search-ShowAjax"

data = []

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "pt-PT,pt;q=0.9"
}

LIMIT = 300
count = 0


def clean_price(price_str):
    if not price_str or "N/A" in price_str:
        return ""
    return price_str.replace("€", "").replace(",", ".").strip()


def normalize_category(cat):
    if not cat:
        return ""
    cat = cat.strip()
    if cat.lower() == "shirts":
        return "T-shirts"
    return cat


def build_description(name, categoria, subcategoria, color):
    parts = [name]

    if categoria and categoria.lower() not in name.lower():
        parts.append(categoria)

    if subcategoria and subcategoria.lower() not in name.lower():
        parts.append(subcategoria)

    if color and color.lower() not in name.lower():
        parts.append(f"cor {color}")

    return " ".join(parts).strip()


for page in range(0, 10):
    start = page * 12
    url = f"{base_url}?cgid=823631&start={start}&sz=12"

    print(f"A processar página {page+1}")

    response = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(response.text, "html.parser")

    products = soup.find_all("div", class_="product-tile")

    if not products:
        break

    for p in products:
        if count >= LIMIT:
            break

        name_tag = p.find("a", class_="link")
        name = name_tag.get_text(strip=True) if name_tag else ""

        link = "https://mo-online.com" + name_tag["href"] if name_tag else ""

        price_tag = p.find("span", class_="value")
        price_raw = price_tag.get_text(strip=True) if price_tag else ""
        price = clean_price(price_raw)

        img_tag = p.find("img")
        image = img_tag["src"] if img_tag else ""

        color = ""
        categoria_principal = ""
        subcategoria = ""

        if link:
            try:
                prod_response = requests.get(link, headers=headers, timeout=15)
                prod_soup = BeautifulSoup(prod_response.text, "html.parser")

                title_tag = prod_soup.find("title")
                if title_tag:
                    title_text = title_tag.get_text()
                    parts = title_text.split(",")
                    if len(parts) >= 3:
                        color = parts[-1].replace("| MO Online", "").strip()

                desc_tag = prod_soup.find("meta", {"name": "description"})
                if desc_tag:
                    descricao_raw = desc_tag.get("content", "")

                    if "-" in descricao_raw:
                        categoria_texto = descricao_raw.split("-")[-1]
                        categoria_texto = categoria_texto.replace("MO Online", "").strip()

                        if " | " in categoria_texto:
                            partes = categoria_texto.split(" | ")
                            categoria_principal = normalize_category(partes[0])
                            subcategoria = normalize_category(partes[1])
                        else:
                            categoria_principal = normalize_category(categoria_texto)
                            subcategoria = ""

            except Exception:
                print(f"Erro no produto: {link}")

        descricao = build_description(
            name,
            categoria_principal,
            subcategoria,
            color
        )

        data.append([
            name,
            price,
            link,
            image,
            color,
            categoria_principal,
            subcategoria,
            descricao
        ])

        count += 1
        print(f"Produto {count} guardado")

        time.sleep(0.3)

    if count >= LIMIT:
        break

print(f"Total produtos: {len(data)}")

with open("produtos_mo_final.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "Nome",
        "Preço",
        "Link",
        "Imagem",
        "Cor",
        "Categoria_Principal",
        "Subcategoria",
        "Descricao"
    ])
    writer.writerows(data)

print("CSV final criado com sucesso!")

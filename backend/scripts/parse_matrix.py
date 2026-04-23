import json
import re

def parse_matrix(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    matrix = {
        "eixos_cognitivos": [],
        "areas": []
    }

    # Parse Eixos Cognitivos
    eixos_section = re.search(r"EIXOS COGNITIVOS.*?\n(.*?)(?=\nMatriz de Referência)", content, re.DOTALL)
    if eixos_section:
        eixos_lines = eixos_section.group(1).strip().split('\n')
        for line in eixos_lines:
            match = re.match(r"([IVX]+)\.\s+(.*?)\s+\((.*?)\):\s+(.*)", line)
            if match:
                matrix["eixos_cognitivos"].append({
                    "id": match.group(3),
                    "nome": match.group(2),
                    "descricao": match.group(4)
                })

    # Parse Areas
    area_sections = re.split(r"Matriz de Referência de ", content)[1:]
    for section in area_sections:
        lines = section.strip().split('\n')
        area_name = lines[0].strip()
        area = {"nome": area_name, "competencias": []}
        
        current_comp = None
        for line in lines[1:]:
            line = line.strip()
            if not line: continue
            
            comp_match = re.match(r"Competência de área (\d+)\s*-\s*(.*)", line)
            if comp_match:
                # Determinar prefixo da área para o ID da competência
                prefix = "LC" if "Linguagens" in area_name else "MT" if "Matemática" in area_name else "CN" if "Ciências da Natureza" in area_name else "CH"
                current_comp = {
                    "id": f"{prefix}_C{comp_match.group(1)}",
                    "descricao": comp_match.group(2),
                    "habilidades": []
                }
                area["competencias"].append(current_comp)
            
            skill_match = re.match(r"H(\d+)\s*–?\s*-?\s*(.*)", line)
            if skill_match and current_comp is not None:
                current_comp["habilidades"].append({
                    "id": f"H{skill_match.group(1)}",
                    "descricao": skill_match.group(2)
                })
        
        matrix["areas"].append(area)

    return matrix

if __name__ == "__main__":
    data = parse_matrix("scripts/matrix_raw.txt")
    with open("scripts/enem_matrix_full.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("Matriz parseada com sucesso!")

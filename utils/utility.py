import json
import logging
import sys
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Set, Tuple, Union

def normalize_value(val: Any) -> Any:
    """
    Normalize values for comparison:
      - If the value is None or a string equal to "None" or "null" (case-insensitive), return an empty string.
      - Otherwise, return the original value.
    """
    if val is None:
        return ""
    if isinstance(val, str) and val.strip().lower() in {"none", "null"}:
        return ""
    return val

def calculate_metrics(gold_norms: Set[Tuple], pred_norms: Set[Tuple]) -> Tuple[float, float, float]:
    """
    Compute precision, recall, and F1 based on the leaf tuples (gold_norms and pred_norms).

    Before computing, remove any leaves that are "empty" (after normalization).
    Logs detailed information about the gold, predicted, and correct leaves.
    """
    # Remove empty leaves (if all parts of the tuple are empty)
    gold_norms = {t for t in gold_norms if any(normalize_value(x) for x in t)}
    pred_norms = {t for t in pred_norms if any(normalize_value(x) for x in t)}
    
    correct = gold_norms.intersection(pred_norms)
    precision = len(correct) / len(pred_norms) if pred_norms else (1.0 if not gold_norms else 0.0)
    recall = len(correct) / len(gold_norms) if gold_norms else (1.0 if not pred_norms else 0.0)
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    
    logging.debug(f"Metrics Calculation:\n  Gold Leaves: {sorted(gold_norms)}\n  Pred Leaves: {sorted(pred_norms)}\n  Correct Leaves: {sorted(correct)}\n  Precision: {precision:.3f}, Recall: {recall:.3f}, F1: {f1:.3f}")
    return precision, recall, f1

def setup_logger(log_file_path: Path) -> None:
    """
    Sets up logging to both console (INFO) and a file (DEBUG).
    """
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    console_handler.setFormatter(console_format)

    file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    file_handler.setFormatter(file_format)

    if logger.hasHandlers():
        logger.handlers.clear()

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

def sanitize_path_segment(name: str) -> str:
    """
    Replaces problematic characters (like '/') with underscores
    so the string can safely be used as a folder/file name.
    """
    return re.sub(r"[^a-zA-Z0-9_\-]", "_", name)

def get_next_experiment_number(experiments_dir: Path) -> str:
    """
    Generates a 3-digit experiment prefix based on existing folders, e.g. '000','001', etc.
    Looks for directories named like: 'NNN_...' and increments from the max found.
    If none found, returns '000'.
    """
    if not experiments_dir.exists():
        return "000"

    pattern = r"^(\d{3})_"
    nums = []

    for subf in experiments_dir.iterdir():
        if subf.is_dir():
            match = re.match(pattern, subf.name)
            if match:
                nums.append(int(match.group(1)))

    if not nums:
        return "000"
    return f"{max(nums)+1:03d}"

def create_experiment_folder(model_name: str, dataset_name: str) -> Path:
    """
    Creates an experiment folder under 'experiments' with the naming convention:
      NNN_DD_MM_YY_HH_mm_model_dataset
    """
    experiments_dir = Path.cwd() / "experiments"
    experiments_dir.mkdir(exist_ok=True)

    # 1) Get the next 3-digit experiment number
    experiment_num = get_next_experiment_number(experiments_dir)

    # 2) Date/time part
    dt_str = datetime.now().strftime("%d_%m_%y_%H_%M")

    # 3) Sanitize model/dataset
    safe_model_name = sanitize_path_segment(model_name)
    safe_dataset_name = sanitize_path_segment(dataset_name)

    # 4) Combine them
    folder_name = f"{experiment_num}_{dt_str}_{safe_model_name}_{safe_dataset_name}"
    experiment_path = experiments_dir / folder_name
    experiment_path.mkdir(exist_ok=True)

    return experiment_path

def load_dataset(dataset_path: str) -> List[Dict[str, Any]]:
    """
    Loads the dataset JSON from the given path.
    """
    with open(dataset_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

def clean_trailing_commas(s: str) -> str:
    """
    Remove vírgulas finais antes de '}' ou ']' em blocos JSON.
    """
    return re.sub(r',\s*([\}\]])', r'\1', s)

def fix_missing_braces(s: str) -> str:
    """
    Adiciona chaves de fechamento se o número de chaves de abertura for maior que o de fechamento.
    """
    open_braces = s.count("{")
    close_braces = s.count("}")
    if open_braces > close_braces:
        s += "}" * (open_braces - close_braces)
    return s

def fix_missing_commas_between_keys(s: str) -> str:
    """
    Insere vírgula faltante entre pares chave–valor.
    Se uma linha que inicia com uma chave (") for encontrada e a linha anterior não terminar com uma vírgula,
    essa função adiciona uma vírgula ao final da linha anterior.
    """
    lines = s.splitlines()
    fixed_lines = []
    for i, line in enumerate(lines):
        if i > 0 and line.lstrip().startswith('"'):
            # Procura a última linha não vazia
            j = i - 1
            while j >= 0 and not lines[j].strip():
                j -= 1
            if j >= 0:
                # Se a linha anterior não terminar com vírgula, insere uma
                if not fixed_lines[-1].rstrip().endswith(','):
                    fixed_lines[-1] = fixed_lines[-1].rstrip() + ','
        fixed_lines.append(line)
    return "\n".join(fixed_lines)

def extract_json_from_response(response_text: str) -> Union[Dict, List, Dict[str, str]]:
    """
    Extrai objeto(s) JSON de uma string de resposta de forma robusta.

    Procedimentos:
      1. Tenta extrair blocos JSON formatados em markdown (ex: ```json ... ```).
      2. Se não encontrar, usa um método de contagem de chaves para localizar o primeiro bloco JSON completo.
      3. Se ainda não encontrar, e se o texto contiver padrões de chave–valor mas estiver sem as chaves externas,
         tenta envolver o texto em chaves e, antes de fazer o parse, aplica:
            - Inserção de vírgulas faltantes entre pares chave–valor.
            - Remoção de vírgulas finais.
            - Correção de chaves de fechamento ausentes.
    
    Se múltiplos blocos JSON forem encontrados e todos forem dicionários, eles serão mesclados em um único dicionário.
    Caso contrário, se nenhum JSON válido for encontrado, retorna {"error": "No valid JSON found"}.
    """
    json_blocks = []

    # 1. Extração via markdown.
    markdown_pattern = r"```(?:json)?\s*(\{.*?\})\s*```"
    markdown_matches = re.findall(markdown_pattern, response_text, re.DOTALL)
    if markdown_matches:
        for match in markdown_matches:
            cleaned = match.strip()
            cleaned = re.sub(r'[\n\r\t]+', ' ', cleaned)
            cleaned = re.sub(r'\s+', ' ', cleaned)
            cleaned = cleaned.replace('“', '"').replace('”', '"')
            cleaned = fix_missing_commas_between_keys(cleaned)
            cleaned = clean_trailing_commas(cleaned)
            cleaned = fix_missing_braces(cleaned)
            try:
                json_obj = json.loads(cleaned)
                json_blocks.append(json_obj)
            except json.JSONDecodeError:
                continue
    else:
        # 2. Fallback: usar contagem de chaves.
        brace_count = 0
        json_start = None
        for i, char in enumerate(response_text):
            if char == '{':
                if brace_count == 0:
                    json_start = i
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0 and json_start is not None:
                    json_block = response_text[json_start:i + 1]
                    cleaned_json_block = re.sub(r'[\n\r\t]+', ' ', json_block)
                    cleaned_json_block = re.sub(r'\s+', ' ', cleaned_json_block)
                    cleaned_json_block = cleaned_json_block.replace('“', '"').replace('”', '"')
                    cleaned_json_block = fix_missing_commas_between_keys(cleaned_json_block)
                    cleaned_json_block = clean_trailing_commas(cleaned_json_block)
                    cleaned_json_block = fix_missing_braces(cleaned_json_block)
                    try:
                        json_obj = json.loads(cleaned_json_block)
                        json_blocks.append(json_obj)
                    except json.JSONDecodeError:
                        continue
                    json_start = None

    if json_blocks:
        if len(json_blocks) == 1:
            return json_blocks[0]
        elif all(isinstance(block, dict) for block in json_blocks):
            merged = {}
            for block in json_blocks:
                merged.update(block)
            return merged
        else:
            return json_blocks

    # 3. Último fallback: tentar envolver o texto completo em chaves e aplicar as correções.
    cleaned_response = response_text.strip()
    if not cleaned_response.startswith('{') and ':' in cleaned_response:
        candidate = "{" + cleaned_response + "}"
        candidate = re.sub(r'[\n\r\t]+', ' ', candidate)
        candidate = re.sub(r'\s+', ' ', candidate)
        candidate = candidate.replace('“', '"').replace('”', '"')
        candidate = fix_missing_commas_between_keys(candidate)
        candidate = clean_trailing_commas(candidate)
        candidate = fix_missing_braces(candidate)
        try:
            json_obj = json.loads(candidate)
            return json_obj
        except json.JSONDecodeError:
            pass

    return {"error": "No valid JSON found"}
    
def normalize(item: Any) -> Any:
    """
    Recursively normalizes an item into a hashable structure.
    - Dictionaries are converted to sorted tuples of (key, normalized_value).
    - Lists are converted to sorted tuples of normalized elements.
    - Other types are returned as-is.
    """
    if isinstance(item, dict):
        return tuple(sorted((k, normalize(v)) for k, v in item.items()))
    elif isinstance(item, list):
        return tuple(sorted(normalize(x) for x in item))
    else:
        return item

def _flatten_list(items: List[Any]) -> Set[str]:
    """
    Flattens a list of items into a set of normalized JSON string representations.
    This allows for proper set-based comparison even if the items are nested dictionaries.
    """
    flattened = set()
    for item in items:
        flattened.add(json.dumps(normalize(item), sort_keys=True))
    return flattened

def flatten_json(obj: any, prefix: tuple = ()) -> set:
    """
    Recursively flattens a JSON structure into a set of tuples representing each leaf.
    
    - For dictionaries: each key is appended to the current path.
    - For lists: each element is processed (its own path does not include the index).
    - For primitives: the value is converted to a string and added with the path.
    
    Example:
      flatten_json({"a": {"b": 1}, "c": [2, 3]})
      might return {("a", "b", "1"), ("c", "2"), ("c", "3")}
    """
    leaves = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            leaves |= flatten_json(v, prefix + (str(k),))
    elif isinstance(obj, list):
        for elem in obj:
            leaves |= flatten_json(elem, prefix)
    else:
        leaves.add(prefix + (str(obj),))
    return leaves
from pathlib import Path

from huggingface_hub import HfApi


def read_token() -> str | None:
    path = Path(".env")
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if "=" not in line or line.lstrip().startswith("#"):
                continue
            key, value = line.split("=", 1)
            if key.strip() in {"HF_TOKEN", "HUGGINGFACE_HUB_TOKEN"}:
                return value.strip().strip('"').strip("'")
    return None


token = read_token()
api = HfApi()
matches = list(api.list_datasets(search="hotpot", token=token, limit=50))
for ds in matches:
    print(ds.id)

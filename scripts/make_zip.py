"""python scripts/make_zip.py -> dist/eval.zip (code only; skips secrets, venv, caches). Fails if over 50 MB."""
import pathlib
import zipfile

SKIP = {".git", ".venv", "__pycache__", ".pytest_cache", "dist", ".env"}
root = pathlib.Path(__file__).resolve().parent.parent
out = root / "dist" / "eval.zip"
out.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for p in sorted(root.rglob("*")):
        if p.is_file() and not SKIP & set(p.relative_to(root).parts):
            z.write(p, p.relative_to(root))
mb = out.stat().st_size / 1e6
print(f"{out} {mb:.2f} MB")
assert mb < 50, "ZIP over 50 MB limit"

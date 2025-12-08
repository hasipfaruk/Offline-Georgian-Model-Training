# scripts/download_models.py
# Download base model from HuggingFace or NeMo model zoo
import os
import sys
from pathlib import Path
import io

# Fix Windows encoding issue
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# Change to script directory
script_dir = Path(__file__).parent
project_root = script_dir.parent
os.chdir(project_root)

print("=" * 80)
print("DOWNLOAD BASE MODEL")
print("=" * 80)

# Configuration - EDIT THESE FOR YOUR PROJECT
MODEL_NAME = "stt_en_fastconformer_ctc_large"  # Change this to your base model
MODEL_PATH = f"models/{MODEL_NAME}.nemo"
HUGGINGFACE_REPO = "nvidia/stt_en_fastconformer_ctc_large"  # Change this to your model repo

print(f"\nModel: {MODEL_NAME}")
print(f"Target path: {MODEL_PATH}")
print(f"HuggingFace repo: {HUGGINGFACE_REPO}")

# Create models directory
Path("models").mkdir(exist_ok=True)

# Check if model already exists
if Path(MODEL_PATH).exists():
    print(f"\n✅ Model already exists at {MODEL_PATH}")
    print("Skipping download. Delete the file if you want to re-download.")
    sys.exit(0)

print("\n📥 Downloading model from HuggingFace...")

try:
    from huggingface_hub import hf_hub_download
    
    print(f"Downloading from: {HUGGINGFACE_REPO}")
    downloaded_path = hf_hub_download(
        repo_id=HUGGINGFACE_REPO,
        filename=f"{MODEL_NAME}.nemo",
        local_dir="models",
        local_dir_use_symlinks=False
    )
    
    print(f"\n✅ Model downloaded successfully!")
    print(f"   Location: {downloaded_path}")
    
except ImportError:
    print("\n❌ Error: huggingface_hub not installed")
    print("Install it with: pip install huggingface_hub")
    sys.exit(1)
    
except Exception as e:
    print(f"\n❌ Error downloading model: {e}")
    print("\nAlternative: Download manually from:")
    print(f"  https://huggingface.co/{HUGGINGFACE_REPO}")
    print(f"  Save as: {MODEL_PATH}")
    sys.exit(1)

print("\n" + "=" * 80)
print("✅ Setup complete! Model ready for training.")
print("=" * 80)


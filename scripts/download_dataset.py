# scripts/download_dataset.py
# Download and extract Common Voice or other datasets
import os
import sys
import tarfile
import json
from pathlib import Path
import io
import shutil

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
print("DOWNLOAD AND EXTRACT DATASET")
print("=" * 80)

# Configuration - EDIT THESE FOR YOUR PROJECT
DATASET_ARCHIVE = "mcv-scripted-ka-v23.0.tar"  # Change to your dataset archive name
EXTRACT_TO = "data"  # Where to extract the dataset
LANGUAGE_CODE = "ka"  # Language code (e.g., "ka" for Georgian, "en" for English)
DATASET_VERSION = "v23.0"  # Dataset version

print(f"\nDataset archive: {DATASET_ARCHIVE}")
print(f"Extract to: {EXTRACT_TO}")
print(f"Language code: {LANGUAGE_CODE}")

# Check if archive exists
archive_path = Path(DATASET_ARCHIVE)
if not archive_path.exists():
    print(f"\n❌ Archive not found: {DATASET_ARCHIVE}")
    print("\nPlease download the dataset archive and place it in the project root.")
    print("For Common Voice, download from: https://commonvoice.mozilla.org/")
    sys.exit(1)

# Create data directory
Path(EXTRACT_TO).mkdir(exist_ok=True)

# Check if already extracted
extracted_path = Path(EXTRACT_TO) / "mcv" / f"cv{''.join(DATASET_VERSION.split('.'))}" / LANGUAGE_CODE / LANGUAGE_CODE
if extracted_path.exists() and any(extracted_path.iterdir()):
    print(f"\n✅ Dataset already extracted at {extracted_path}")
    response = input("Re-extract? (y/N): ").strip().lower()
    if response != 'y':
        print("Skipping extraction.")
        sys.exit(0)
    else:
        print("Removing old extraction...")
        shutil.rmtree(extracted_path.parent.parent.parent, ignore_errors=True)

print(f"\n📦 Extracting archive...")
print("This may take several minutes...")

try:
    with tarfile.open(archive_path, 'r') as tar:
        # Extract with progress
        members = tar.getmembers()
        total = len(members)
        for i, member in enumerate(members, 1):
            if i % 1000 == 0:
                print(f"  Progress: {i}/{total} files ({i*100/total:.1f}%)")
            tar.extract(member, path=EXTRACT_TO)
    
    print(f"\n✅ Extraction complete!")
    print(f"   Dataset location: {extracted_path}")
    
except Exception as e:
    print(f"\n❌ Error extracting archive: {e}")
    sys.exit(1)

print("\n" + "=" * 80)
print("✅ Dataset ready! Next step: Create manifests")
print("=" * 80)


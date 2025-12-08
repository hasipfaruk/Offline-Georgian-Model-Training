# scripts/create_manifests.py
# Create manifest files from Common Voice dataset
import os
import sys
import json
import pandas as pd
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
print("CREATE MANIFEST FILES")
print("=" * 80)

# Configuration - EDIT THESE FOR YOUR PROJECT
LANGUAGE_CODE = "ka"  # Language code
DATASET_VERSION = "v23.0"  # Dataset version
DATA_DIR = Path("data") / "mcv" / f"cv{''.join(DATASET_VERSION.split('.'))}" / LANGUAGE_CODE / LANGUAGE_CODE
MANIFESTS_DIR = Path("manifests")
TRAIN_SPLIT = 0.8  # 80% for training
DEV_SPLIT = 0.1    # 10% for validation
TEST_SPLIT = 0.1    # 10% for testing

print(f"\nDataset directory: {DATA_DIR}")
print(f"Manifests directory: {MANIFESTS_DIR}")
print(f"Train/Dev/Test split: {TRAIN_SPLIT}/{DEV_SPLIT}/{TEST_SPLIT}")

# Check if dataset exists
if not DATA_DIR.exists():
    print(f"\n❌ Dataset directory not found: {DATA_DIR}")
    print("Run download_dataset.py first!")
    sys.exit(1)

# Find TSV files
tsv_files = list(DATA_DIR.glob("*.tsv"))
if not tsv_files:
    print(f"\n❌ No TSV files found in {DATA_DIR}")
    sys.exit(1)

print(f"\nFound {len(tsv_files)} TSV file(s)")

# Create manifests directory
MANIFESTS_DIR.mkdir(exist_ok=True)

# Process each TSV file
all_entries = []

for tsv_file in tsv_files:
    print(f"\n📄 Processing: {tsv_file.name}")
    
    try:
        # Read TSV file
        df = pd.read_csv(tsv_file, sep='\t', encoding='utf-8')
        print(f"   Rows: {len(df)}")
        
        # Process each row
        for idx, row in df.iterrows():
            # Get audio file path
            audio_file = DATA_DIR / "clips" / row['path']
            
            # Skip if audio file doesn't exist
            if not audio_file.exists():
                continue
            
            # Get text (handle different column names)
            text = row.get('sentence', row.get('text', row.get('transcription', '')))
            
            # Get duration if available
            duration = row.get('duration', 0.0)
            
            # Create manifest entry
            entry = {
                "audio_filepath": str(audio_file.absolute()),
                "text": str(text).strip(),
                "duration": float(duration) if duration else 0.0
            }
            
            all_entries.append(entry)
            
    except Exception as e:
        print(f"   ⚠️  Error processing {tsv_file.name}: {e}")
        continue

print(f"\n✅ Processed {len(all_entries)} entries")

if len(all_entries) == 0:
    print("\n❌ No valid entries found!")
    sys.exit(1)

# Shuffle entries
import random
random.seed(42)
random.shuffle(all_entries)

# Split into train/dev/test
total = len(all_entries)
train_end = int(total * TRAIN_SPLIT)
dev_end = train_end + int(total * DEV_SPLIT)

train_entries = all_entries[:train_end]
dev_entries = all_entries[train_end:dev_end]
test_entries = all_entries[dev_end:]

print(f"\n📊 Split:")
print(f"   Train: {len(train_entries)} entries")
print(f"   Dev:   {len(dev_entries)} entries")
print(f"   Test:  {len(test_entries)} entries")

# Write manifest files
def write_manifest(entries, filename):
    manifest_path = MANIFESTS_DIR / filename
    with open(manifest_path, 'w', encoding='utf-8') as f:
        for entry in entries:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    print(f"   ✅ Created: {manifest_path}")

print(f"\n💾 Writing manifest files...")
write_manifest(train_entries, "train.json")
write_manifest(dev_entries, "dev.json")
write_manifest(test_entries, "test.json")

print("\n" + "=" * 80)
print("✅ Manifests created! Next step: Clean and filter data")
print("=" * 80)


# scripts/fix_text_encoding.py
# Fix text encoding issues in manifests (for Common Voice datasets with hash issues)
import os
import sys
import json
import pandas as pd
from pathlib import Path
import io
import hashlib

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
print("FIX TEXT ENCODING IN MANIFESTS")
print("=" * 80)

# Configuration
LANGUAGE_CODE = "ka"
DATASET_VERSION = "v23.0"
DATA_DIR = Path("data") / "mcv" / f"cv{''.join(DATASET_VERSION.split('.'))}" / LANGUAGE_CODE / LANGUAGE_CODE
MANIFESTS_DIR = Path("manifests")
MANIFEST_FILES = ["train.json", "dev.json", "test.json"]

print(f"\nDataset directory: {DATA_DIR}")
print(f"Manifests directory: {MANIFESTS_DIR}")

# Find TSV files with actual text
tsv_files = list(DATA_DIR.glob("*.tsv"))
if not tsv_files:
    print(f"\n❌ No TSV files found in {DATA_DIR}")
    sys.exit(1)

# Load TSV to create hash -> text mapping
print(f"\n📄 Loading text from TSV files...")
hash_to_text = {}

for tsv_file in tsv_files:
    try:
        df = pd.read_csv(tsv_file, sep='\t', encoding='utf-8')
        for _, row in df.iterrows():
            # Common Voice uses hash of sentence as key
            sentence = str(row.get('sentence', row.get('text', '')))
            sentence_hash = hashlib.sha256(sentence.encode('utf-8')).hexdigest()[:8]
            hash_to_text[sentence_hash] = sentence
    except Exception as e:
        print(f"   ⚠️  Error reading {tsv_file.name}: {e}")

print(f"   Loaded {len(hash_to_text)} text entries")

# Process each manifest file
for manifest_file in MANIFEST_FILES:
    manifest_path = MANIFESTS_DIR / manifest_file
    
    if not manifest_path.exists():
        print(f"\n⚠️  Skipping {manifest_file} (not found)")
        continue
    
    print(f"\n📝 Processing: {manifest_file}")
    
    entries = []
    fixed_count = 0
    
    with open(manifest_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                original_text = str(entry.get('text', ''))
                
                # Check if text looks like a hash (short alphanumeric)
                if len(original_text) <= 10 and original_text.isalnum():
                    # Try to find in hash mapping
                    if original_text in hash_to_text:
                        entry['text'] = hash_to_text[original_text]
                        fixed_count += 1
                
                entries.append(entry)
            except Exception as e:
                print(f"   ⚠️  Error processing line: {e}")
                continue
    
    # Write fixed manifest
    output_path = MANIFESTS_DIR / manifest_file
    with open(output_path, 'w', encoding='utf-8') as f:
        for entry in entries:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    print(f"   ✅ Fixed {fixed_count} entries")
    print(f"   ✅ Saved: {output_path}")

print("\n" + "=" * 80)
print("✅ Text encoding fixed! Next step: Clean and filter data")
print("=" * 80)


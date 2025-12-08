# scripts/clean_manifests.py
# Clean and filter manifest files
import os
import sys
import json
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
print("CLEAN AND FILTER MANIFESTS")
print("=" * 80)

# Configuration - EDIT THESE FOR YOUR PROJECT
MANIFESTS_DIR = Path("manifests")
MANIFEST_FILES = ["train.json", "dev.json", "test.json"]
OUTPUT_DIR = MANIFESTS_DIR / "clean"

# Filtering criteria
MIN_DURATION = 1.0   # Minimum audio duration in seconds
MAX_DURATION = 30.0  # Maximum audio duration in seconds
MIN_TEXT_LENGTH = 3  # Minimum text length (characters)
MAX_TEXT_LENGTH = 500  # Maximum text length (characters)

print(f"\nManifests directory: {MANIFESTS_DIR}")
print(f"Output directory: {OUTPUT_DIR}")
print(f"\nFiltering criteria:")
print(f"   Duration: {MIN_DURATION}s - {MAX_DURATION}s")
print(f"   Text length: {MIN_TEXT_LENGTH} - {MAX_TEXT_LENGTH} characters")

# Create output directory
OUTPUT_DIR.mkdir(exist_ok=True)

def clean_text(text):
    """Clean text: remove extra spaces, normalize"""
    if not text:
        return ""
    # Remove extra whitespace
    text = ' '.join(text.split())
    return text.strip()

def is_valid_entry(entry):
    """Check if entry meets filtering criteria"""
    # Check audio file exists
    audio_path = Path(entry.get('audio_filepath', ''))
    if not audio_path.exists():
        return False
    
    # Check duration
    duration = entry.get('duration', 0.0)
    if duration < MIN_DURATION or duration > MAX_DURATION:
        return False
    
    # Check text
    text = entry.get('text', '')
    text = clean_text(text)
    if len(text) < MIN_TEXT_LENGTH or len(text) > MAX_TEXT_LENGTH:
        return False
    
    # Check for empty or invalid text
    if not text or text.isspace():
        return False
    
    return True

# Process each manifest file
for manifest_file in MANIFEST_FILES:
    manifest_path = MANIFESTS_DIR / manifest_file
    
    if not manifest_path.exists():
        print(f"\n⚠️  Skipping {manifest_file} (not found)")
        continue
    
    print(f"\n📝 Processing: {manifest_file}")
    
    entries = []
    valid_count = 0
    invalid_count = 0
    
    with open(manifest_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                
                # Clean text
                entry['text'] = clean_text(entry.get('text', ''))
                
                # Check if valid
                if is_valid_entry(entry):
                    entries.append(entry)
                    valid_count += 1
                else:
                    invalid_count += 1
                    
            except Exception as e:
                invalid_count += 1
                continue
    
    # Write cleaned manifest
    output_path = OUTPUT_DIR / manifest_file
    with open(output_path, 'w', encoding='utf-8') as f:
        for entry in entries:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    print(f"   ✅ Valid entries: {valid_count}")
    print(f"   ❌ Filtered out: {invalid_count}")
    print(f"   ✅ Saved: {output_path}")

print("\n" + "=" * 80)
print("✅ Manifests cleaned! Next step: Build tokenizer")
print("=" * 80)
print(f"\nNote: Cleaned manifests are in: {OUTPUT_DIR}")
print("Update your config to use cleaned manifests if desired.")


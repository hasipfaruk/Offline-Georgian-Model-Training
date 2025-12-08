# scripts/build_tokenizer.py
# Build SentencePiece BPE tokenizer from training data
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
print("BUILD TOKENIZER")
print("=" * 80)

# Configuration - EDIT THESE FOR YOUR PROJECT
MANIFEST_FILE = "manifests/train.json"  # Use training data for tokenizer
TOKENIZER_DIR = Path("tokenizers/tokenizer")
VOCAB_SIZE = 2048  # Vocabulary size (adjust based on language complexity)
MODEL_TYPE = "bpe"  # "bpe" or "unigram"

print(f"\nManifest file: {MANIFEST_FILE}")
print(f"Tokenizer directory: {TOKENIZER_DIR}")
print(f"Vocabulary size: {VOCAB_SIZE}")
print(f"Model type: {MODEL_TYPE}")

# Check if manifest exists
if not Path(MANIFEST_FILE).exists():
    print(f"\n❌ Manifest file not found: {MANIFEST_FILE}")
    sys.exit(1)

# Create tokenizer directory
TOKENIZER_DIR.mkdir(parents=True, exist_ok=True)

# Collect all text from manifest
print(f"\n📄 Collecting text from manifest...")
texts = []

with open(MANIFEST_FILE, 'r', encoding='utf-8') as f:
    for line in f:
        try:
            entry = json.loads(line.strip())
            text = entry.get('text', '').strip()
            if text:
                texts.append(text)
        except Exception as e:
            continue

print(f"   Collected {len(texts)} text samples")

if len(texts) == 0:
    print("\n❌ No text found in manifest!")
    sys.exit(1)

# Write text to temporary file for SentencePiece
temp_text_file = TOKENIZER_DIR / "text_corpus.txt"
print(f"\n💾 Writing text corpus to: {temp_text_file}")

with open(temp_text_file, 'w', encoding='utf-8') as f:
    for text in texts:
        f.write(text + '\n')

# Build tokenizer using SentencePiece
print(f"\n🔨 Building tokenizer...")

try:
    import sentencepiece as spm
    
    model_prefix = str(TOKENIZER_DIR / "tokenizer")
    
    spm.SentencePieceTrainer.train(
        input=str(temp_text_file),
        model_prefix=model_prefix,
        vocab_size=VOCAB_SIZE,
        model_type=MODEL_TYPE,
        character_coverage=0.9995,  # Coverage for the language
        input_sentence_size=len(texts),  # Use all sentences
        shuffle_input_sentence=True,
        normalization_rule_name='nmt_nfkc_cf',  # Normalization
        remove_extra_whitespaces=True,
    )
    
    print(f"   ✅ Tokenizer model created: {model_prefix}.model")
    print(f"   ✅ Vocabulary file created: {model_prefix}.vocab")
    
except ImportError:
    print("\n❌ Error: sentencepiece not installed")
    print("Install it with: pip install sentencepiece")
    sys.exit(1)
    
except Exception as e:
    print(f"\n❌ Error building tokenizer: {e}")
    sys.exit(1)

# Create vocabulary file for NeMo
vocab_file = TOKENIZER_DIR / "vocab.txt"
print(f"\n📝 Creating vocabulary file: {vocab_file}")

try:
    sp = spm.SentencePieceProcessor()
    sp.load(f"{model_prefix}.model")
    
    with open(vocab_file, 'w', encoding='utf-8') as f:
        for i in range(sp.get_piece_size()):
            piece = sp.id_to_piece(i)
            f.write(f"{piece}\n")
    
    print(f"   ✅ Vocabulary file created")
    
except Exception as e:
    print(f"   ⚠️  Warning: Could not create vocab.txt: {e}")

# Clean up temporary file
if temp_text_file.exists():
    temp_text_file.unlink()
    print(f"   🗑️  Removed temporary file")

print("\n" + "=" * 80)
print("✅ Tokenizer built! Ready for training")
print("=" * 80)
print(f"\nTokenizer location: {TOKENIZER_DIR}")
print("Update your training script to use this tokenizer path.")


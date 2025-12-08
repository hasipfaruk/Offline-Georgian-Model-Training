# STT Project Template

A complete template for creating a new Speech-to-Text (STT) model from scratch using NeMo and Common Voice datasets.

##  Project Structure

```
stt_project_template/
├── configs/
│   └── template_config.yaml      # Training configuration (EDIT THIS)
├── scripts/
│   ├── download_models.py        # Download base model
│   ├── download_dataset.py       # Download/extract dataset
│   ├── create_manifests.py       # Create manifest files from dataset
│   ├── fix_text_encoding.py     # Fix text encoding issues
│   ├── clean_manifests.py        # Clean and filter manifests
│   ├── build_tokenizer.py        # Build tokenizer from training data
│   └── train_template.py         # Training script (EDIT THIS)
├── manifests/                     # Dataset manifests (created by scripts)
├── models/                        # Model files (downloaded/saved here)
├── tokenizers/                    # Tokenizer files (created by scripts)
├── data/                          # Dataset files (extracted here)
└── README.md                      # This file
```

##  Quick Start Guide

### Step 1: Setup Project

1. **Copy this template folder** to your new project location:
   ```powershell
   # Copy the entire stt_project_template folder
   # Rename it to your project name (e.g., "spanish_stt", "french_stt")
   ```

2. **Edit configuration files**:
   - `configs/template_config.yaml` - Update paths and settings
   - `scripts/train_template.py` - Update model paths and names

### Step 2: Install Dependencies

```powershell
# Activate your virtual environment
.\..\nemo\Scripts\Activate.ps1

# Install PyTorch with CUDA (check your CUDA version: nvidia-smi)
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install other requirements
pip install -r requirements.txt
```

### Step 3: Download Base Model

```powershell
# Edit scripts/download_models.py first to set your model
python scripts/download_models.py
```

**Edit `download_models.py`**:
- Change `MODEL_NAME` to your base model name
- Change `HUGGINGFACE_REPO` to your model's HuggingFace repository

### Step 4: Download and Prepare Dataset

#### Option A: Common Voice Dataset

1. **Download dataset archive** from https://commonvoice.mozilla.org/
   - Place the `.tar` file in the project root

2. **Edit `download_dataset.py`**:
   - Set `DATASET_ARCHIVE` to your archive filename
   - Set `LANGUAGE_CODE` (e.g., "es" for Spanish, "fr" for French)
   - Set `DATASET_VERSION` (e.g., "v23.0")

3. **Run setup scripts in order**:
   ```powershell
   # Extract dataset
   python scripts/download_dataset.py
   
   # Create manifest files
   python scripts/create_manifests.py
   
   # Fix text encoding (if needed for Common Voice)
   python scripts/fix_text_encoding.py
   
   # Clean and filter data
   python scripts/clean_manifests.py
   ```

#### Option B: Custom Dataset

If you have a custom dataset:

1. **Create manifest files manually** in `manifests/`:
   - `train.json`, `dev.json`, `test.json`
   - Format: One JSON object per line:
     ```json
     {"audio_filepath": "path/to/audio.wav", "text": "transcription text", "duration": 5.0}
     ```

2. **Skip to Step 5** (build tokenizer)

### Step 5: Build Tokenizer

```powershell
# Edit scripts/build_tokenizer.py first
python scripts/build_tokenizer.py
```

**Edit `build_tokenizer.py`**:
- Set `MANIFEST_FILE` (use cleaned manifests if available)
- Set `VOCAB_SIZE` (2048 for most languages, increase for complex languages)
- Set `MODEL_TYPE` ("bpe" recommended)

### Step 6: Configure Training

1. **Edit `configs/template_config.yaml`**:
   - Update manifest paths
   - Adjust `batch_size` based on GPU memory
   - Set `max_epochs` (50-100 recommended)
   - Set `accelerator` ("gpu" or "cpu")

2. **Edit `scripts/train_template.py`**:
   - Set `CONFIG_FILE` path
   - Set `BASE_MODEL` path
   - Set `TOKENIZER_DIR` path
   - Set `OUTPUT_MODEL` name

### Step 7: Train Model

```powershell
python scripts/train_template.py
```

Training will:
- Automatically resume from latest checkpoint if interrupted
- Save checkpoints in `lightning_logs/`
- Save final model to `models/your_language_stt.nemo`

##  Configuration Guide

### Editing Scripts

Each script has a **CONFIGURATION** section at the top. Edit these values for your project:

#### `download_models.py`
```python
MODEL_NAME = "stt_en_fastconformer_ctc_large"  # Your base model name
HUGGINGFACE_REPO = "nvidia/stt_en_fastconformer_ctc_large"  # HuggingFace repo
```

#### `download_dataset.py`
```python
DATASET_ARCHIVE = "mcv-scripted-ka-v23.0.tar"  # Your dataset archive
LANGUAGE_CODE = "ka"  # Language code (ISO 639-1)
DATASET_VERSION = "v23.0"  # Dataset version
```

#### `create_manifests.py`
```python
LANGUAGE_CODE = "ka"  # Language code
TRAIN_SPLIT = 0.8  # 80% training
DEV_SPLIT = 0.1    # 10% validation
TEST_SPLIT = 0.1   # 10% testing
```

#### `build_tokenizer.py`
```python
MANIFEST_FILE = "manifests/train.json"  # Training data for tokenizer
VOCAB_SIZE = 2048  # Vocabulary size
MODEL_TYPE = "bpe"  # "bpe" or "unigram"
```

#### `train_template.py`
```python
CONFIG_FILE = "configs/template_config.yaml"
BASE_MODEL = "models/stt_en_fastconformer_ctc_large.nemo"
TOKENIZER_DIR = "tokenizers/tokenizer"
OUTPUT_MODEL = "models/your_language_stt.nemo"
```

### Config File Settings

Edit `configs/template_config.yaml`:

- **`batch_size`**: Start with 16, reduce if OOM errors occur
- **`max_epochs`**: 50-100 for good results
- **`lr`**: 0.001 default, reduce to 0.0005 if loss plateaus
- **`accelerator`**: "gpu" for GPU training, "cpu" for CPU
- **`precision`**: "16-mixed" for faster training, "32" for stability

##  Workflow Summary

```
1. Copy template folder → New project folder
2. Edit configuration in scripts
3. Download base model (download_models.py)
4. Download dataset (download_dataset.py)
5. Create manifests (create_manifests.py)
6. Fix encoding (fix_text_encoding.py) - if needed
7. Clean manifests (clean_manifests.py)
8. Build tokenizer (build_tokenizer.py)
9. Configure training (edit config.yaml and train_template.py)
10. Train model (train_template.py)
```

##  Expected File Structure After Setup

```
your_project/
├── configs/
│   └── template_config.yaml
├── scripts/
│   └── [all scripts]
├── manifests/
│   ├── train.json          # Created by create_manifests.py
│   ├── dev.json
│   ├── test.json
│   └── clean/              # Created by clean_manifests.py
│       ├── train.json
│       ├── dev.json
│       └── test.json
├── models/
│   ├── stt_en_fastconformer_ctc_large.nemo  # Downloaded
│   └── your_language_stt.nemo              # Trained model
├── tokenizers/
│   └── tokenizer/
│       ├── tokenizer.model
│       └── vocab.txt
├── data/
│   └── [extracted dataset files]
└── lightning_logs/          # Training checkpoints
```

##  Troubleshooting

### Model Download Fails
- Check internet connection
- Verify HuggingFace repository name
- Try downloading manually from HuggingFace website

### Dataset Extraction Fails
- Verify archive file is not corrupted
- Check available disk space
- Ensure archive is in project root

### Manifest Creation Fails
- Check TSV file format
- Verify audio files exist in dataset
- Check file paths in TSV

### Tokenizer Build Fails
- Install sentencepiece: `pip install sentencepiece`
- Check manifest file has valid text
- Reduce vocab_size if memory issues

### Training Fails
- Reduce batch_size in config
- Check GPU memory: `nvidia-smi`
- Verify all paths in train_template.py are correct
- Ensure tokenizer directory exists

##  Additional Resources

- **NeMo Documentation**: https://docs.nvidia.com/deeplearning/nemo/
- **Common Voice**: https://commonvoice.mozilla.org/
- **HuggingFace Models**: https://huggingface.co/models

##  Checklist for New Project

- [ ] Copied template folder to new project
- [ ] Edited all configuration sections in scripts
- [ ] Downloaded base model
- [ ] Downloaded/prepared dataset
- [ ] Created manifest files
- [ ] Cleaned manifests
- [ ] Built tokenizer
- [ ] Configured training script and config file
- [ ] Started training

---

**Ready to start?** Follow the steps above and you'll have a working STT model! 🚀


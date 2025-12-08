# scripts/train_template.py
# Template training script - EDIT FOR YOUR PROJECT
import sys
import os
import io
import builtins

# Fix Windows encoding issue - MUST BE FIRST
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONUTF8'] = '1'
    
    _original_open = builtins.open
    def _utf8_open(file, mode='r', buffering=-1, encoding=None, errors=None, newline=None, closefd=True, opener=None):
        if encoding is None and 'b' not in mode:
            encoding = 'utf-8'
        if errors is None and 'b' not in mode:
            errors = 'replace'
        return _original_open(file, mode, buffering, encoding, errors, newline, closefd, opener)
    builtins.open = _utf8_open
    
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'buffer'):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Now safe to import
import lightning.pytorch as pl
from omegaconf import OmegaConf
from pathlib import Path
from nemo.collections.asr.models import EncDecCTCModel

def main():
    # Change to script directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)
    
    print("=" * 80)
    print("STT MODEL TRAINING")
    print("=" * 80)

    # ========================================================================
    # CONFIGURATION - EDIT THESE FOR YOUR PROJECT
    # ========================================================================
    CONFIG_FILE = "configs/template_config.yaml"  # Your config file
    BASE_MODEL = "models/stt_en_fastconformer_ctc_large.nemo"  # Base model path
    TOKENIZER_DIR = "tokenizers/tokenizer"  # Tokenizer directory
    TOKENIZER_TYPE = "bpe"  # "bpe" or "char"
    OUTPUT_MODEL = "models/your_language_stt.nemo"  # Output model name
    # ========================================================================
    
    print(f"\nConfig: {CONFIG_FILE}")
    print(f"Base model: {BASE_MODEL}")
    print(f"Tokenizer: {TOKENIZER_DIR}")
    print(f"Output: {OUTPUT_MODEL}")

    # Load config
    if not Path(CONFIG_FILE).exists():
        print(f"\n❌ Config file not found: {CONFIG_FILE}")
        sys.exit(1)
    
    cfg = OmegaConf.load(CONFIG_FILE)

    # Fix for Windows
    if sys.platform == 'win32':
        print("\nDetected Windows platform. Setting num_workers=0")
        if 'train_ds' in cfg:
            cfg.train_ds.num_workers = 0
        if 'validation_ds' in cfg:
            cfg.validation_ds.num_workers = 0

    # Load base model
    if not Path(BASE_MODEL).exists():
        print(f"\n❌ Base model not found: {BASE_MODEL}")
        print("Run download_models.py first!")
        sys.exit(1)
    
    print("\n📥 Loading base model...")
    model = EncDecCTCModel.restore_from(BASE_MODEL)
    print("✅ Base model loaded")

    # Change tokenizer/vocab
    if not Path(TOKENIZER_DIR).exists():
        print(f"\n❌ Tokenizer not found: {TOKENIZER_DIR}")
        print("Run build_tokenizer.py first!")
        sys.exit(1)
    
    print(f"\n🔄 Changing tokenizer to: {TOKENIZER_DIR}")
    model.change_vocabulary(
        new_tokenizer_dir=TOKENIZER_DIR,
        new_tokenizer_type=TOKENIZER_TYPE,
    )
    print("✅ Tokenizer activated")

    # Setup data loaders
    print("\n📊 Setting up data loaders...")
    model.setup_training_data(cfg.train_ds)
    model.setup_validation_data(cfg.validation_ds)
    print("✅ Data loaders ready")

    # Setup optimizer
    print("\n⚙️  Setting up optimizer...")
    model.setup_optimization(cfg.optim)
    print("✅ Optimizer ready")

    # Find latest checkpoint
    checkpoint_path = None
    logs_dir = Path("lightning_logs")
    
    if logs_dir.exists():
        print("\n🔍 Searching for checkpoints...")
        all_checkpoints = []
        
        for ckpt in logs_dir.glob("**/*.ckpt"):
            try:
                import torch
                data = torch.load(ckpt, map_location='cpu', weights_only=False)
                epoch = data.get('epoch', -1)
                step = data.get('global_step', -1)
                all_checkpoints.append({'path': ckpt, 'epoch': epoch, 'step': step})
            except:
                continue
        
        if all_checkpoints:
            all_checkpoints.sort(key=lambda x: (x['epoch'], x['step']), reverse=True)
            checkpoint_path = all_checkpoints[0]['path']
            print(f"   ✅ Found checkpoint: Epoch {all_checkpoints[0]['epoch']}, Step {all_checkpoints[0]['step']}")

    # Setup callbacks
    callbacks = [
        pl.callbacks.ModelCheckpoint(
            dirpath="lightning_logs",
            filename="epoch-{epoch:02d}-val_loss-{val_loss:.3f}",
            monitor="val_loss",
            mode="min",
            save_top_k=2,
            save_last=True,
            every_n_epochs=2,
        ),
    ]
    
    if checkpoint_path is None:
        callbacks.append(
            pl.callbacks.EarlyStopping(
                monitor="val_loss",
                patience=5,
                mode="min",
            )
        )

    # Setup trainer
    trainer_kwargs = {
        'max_epochs': cfg.trainer.max_epochs,
        'accelerator': cfg.trainer.accelerator,
        'devices': cfg.trainer.devices,
        'precision': cfg.trainer.precision,
        'accumulate_grad_batches': cfg.trainer.accumulate_grad_batches,
        'gradient_clip_val': cfg.trainer.gradient_clip_val,
        'log_every_n_steps': cfg.trainer.log_every_n_steps,
        'val_check_interval': cfg.trainer.val_check_interval,
        'enable_checkpointing': cfg.trainer.enable_checkpointing,
        'enable_progress_bar': cfg.trainer.enable_progress_bar,
        'callbacks': callbacks,
    }
    
    trainer = pl.Trainer(**trainer_kwargs)
    print("✅ Trainer initialized")

    # Train
    if checkpoint_path:
        print(f"\n🔄 Resuming from checkpoint...")
        trainer.fit(model, ckpt_path=str(checkpoint_path))
    else:
        print("\n🚀 Starting training from scratch...")
        trainer.fit(model)
    
    print("\n✅ Training completed")

    # Save model
    print(f"\n💾 Saving model to: {OUTPUT_MODEL}")
    Path("models").mkdir(exist_ok=True)
    model.save_to(OUTPUT_MODEL)
    print("✅ Model saved")

if __name__ == "__main__":
    main()


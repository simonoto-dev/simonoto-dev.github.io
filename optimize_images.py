"""
Image Optimizer for Simonoto Website
=====================================
Resizes all images in Images/ to web-friendly sizes.
Backs up originals to Images_originals/ first.

Run: python optimize_images.py
"""

from PIL import Image, ImageOps
import os, shutil

SRC = os.path.join(os.path.dirname(__file__), "Images")
BACKUP = os.path.join(os.path.dirname(__file__), "Images_originals")

MAX_WIDTH = 1400
MAX_HEIGHT = 1400
JPEG_QUALITY = 82

def optimize():
    if not os.path.exists(SRC):
        print(f"ERROR: {SRC} not found")
        return
    
    # Back up originals (only once)
    if not os.path.exists(BACKUP):
        print(f"Backing up originals to {BACKUP}...")
        shutil.copytree(SRC, BACKUP)
        print("  ✓ Backup complete\n")
    else:
        print(f"Backup already exists at {BACKUP}, skipping backup\n")
    
    total_before = 0
    total_after = 0
    processed = 0
    
    for fname in sorted(os.listdir(SRC)):
        fpath = os.path.join(SRC, fname)
        if not os.path.isfile(fpath):
            continue
        
        ext = os.path.splitext(fname)[1].lower()
        if ext not in ('.jpg', '.jpeg', '.png', '.webp'):
            print(f"  SKIP  {fname}")
            continue
        
        before_size = os.path.getsize(fpath)
        total_before += before_size
        
        try:
            img = Image.open(fpath)
            
            # Fix EXIF orientation
            try:
                img = ImageOps.exif_transpose(img)
            except:
                pass
            
            orig_w, orig_h = img.size
            
            # Resize if needed
            if orig_w > MAX_WIDTH or orig_h > MAX_HEIGHT:
                ratio = min(MAX_WIDTH / orig_w, MAX_HEIGHT / orig_h)
                new_w = int(orig_w * ratio)
                new_h = int(orig_h * ratio)
                img = img.resize((new_w, new_h), Image.LANCZOS)
            
            # Save in place
            if ext == '.png':
                # Check for transparency
                if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                    img.save(fpath, 'PNG', optimize=True)
                else:
                    # Convert opaque PNGs to... still PNG (keep format consistent with HTML refs)
                    img.save(fpath, 'PNG', optimize=True)
            else:
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                img.save(fpath, 'JPEG', quality=JPEG_QUALITY, optimize=True)
            
            after_size = os.path.getsize(fpath)
            total_after += after_size
            reduction = (1 - after_size / before_size) * 100 if before_size > 0 else 0
            processed += 1
            
            size_str = f"{before_size//1024:>6}KB → {after_size//1024:>4}KB"
            dim_str = f"{img.size[0]}x{img.size[1]}"
            
            if reduction > 5:
                print(f"  ✓ {fname:<35} {size_str}  ({reduction:>4.0f}% smaller)  [{dim_str}]")
            else:
                print(f"  · {fname:<35} {size_str}  (already small)  [{dim_str}]")
                
        except Exception as e:
            print(f"  ✗ {fname}: ERROR - {e}")
    
    print(f"\n{'='*60}")
    print(f"  Processed: {processed} images")
    print(f"  Before:    {total_before/1024/1024:.1f} MB")
    print(f"  After:     {total_after/1024/1024:.1f} MB")
    print(f"  Saved:     {(total_before-total_after)/1024/1024:.1f} MB ({(1-total_after/total_before)*100:.0f}% reduction)")
    print(f"  Originals: {BACKUP}")
    print(f"{'='*60}")
    print(f"\nNow push to GitHub:")
    print(f"  cd {os.path.dirname(__file__)}")
    print(f"  git add -A")
    print(f'  git commit -m "add optimized images"')
    print(f"  git push")

if __name__ == "__main__":
    optimize()

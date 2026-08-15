from datasets import load_dataset
import json

def check_schema():
    print("Loading dataset 'th1nhng0/vietnamese-legal-documents'...")
    # Use streaming to avoid downloading the whole dataset into memory
    ds = load_dataset("th1nhng0/vietnamese-legal-documents", "metadata", streaming=True, split="train")
    
    first_item = next(iter(ds))
    
    print("\n=== Dataset Schema ===")
    for k, v in first_item.items():
        val_preview = str(v)[:100] + "..." if isinstance(v, str) and len(str(v)) > 100 else str(v)
        print(f"- {k} ({type(v).__name__}): {val_preview}")

if __name__ == "__main__":
    check_schema()

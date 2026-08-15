from datasets import load_dataset
import json

def main():
    ds = load_dataset('th1nhng0/vietnamese-legal-documents', 'content', streaming=True, split='data')
    item = next(iter(ds))
    with open('schema_content.json', 'w', encoding='utf-8') as f:
        json.dump(item, f, ensure_ascii=False, indent=2)

    ds_meta = load_dataset('th1nhng0/vietnamese-legal-documents', 'metadata', streaming=True, split='data')
    item_meta = next(iter(ds_meta))
    with open('schema_metadata.json', 'w', encoding='utf-8') as f:
        json.dump(item_meta, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()

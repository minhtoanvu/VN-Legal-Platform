import sys
import os
import asyncio
import re
from pathlib import Path

# Thêm đường dẫn project vào sys.path để import app modules
current_dir = Path(__file__).resolve().parent
backend_dir = current_dir.parent.parent
sys.path.append(str(backend_dir))

from sqlalchemy import select, text
from app.core.database import AsyncSessionLocal
from app.models.document import Document, DocumentChunk

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("Install: pip install beautifulsoup4")
    sys.exit(1)

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    try:
        from langchain.text_splitter import RecursiveCharacterTextSplitter
    except ImportError:
        print("Install: pip install langchain-text-splitters")
        sys.exit(1)


def split_by_article(html_content: str, doc_number: str) -> list[str]:
    """Bóc HTML và chia văn bản theo từng Điều."""
    if not html_content:
        return []
        
    soup = BeautifulSoup(html_content, "html.parser")
    clean_text = soup.get_text(separator="\n", strip=True)
    
    # Split theo pattern "Điều \d+." hoặc "Điều \d+:"
    pattern = r'(?=\n\s*Điều \d+[.:])'
    parts = re.split(pattern, clean_text)
    
    chunks = []
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        length_function=len,
    )
    
    for part in parts:
        part = part.strip()
        if not part:
            continue
            
        prefix = f"[{doc_number}] " if doc_number else ""
        
        if len(part) > 1000:
            sub_chunks = text_splitter.split_text(part)
            for sub in sub_chunks:
                chunks.append(prefix + sub)
        else:
            chunks.append(prefix + part)
            
    return chunks

async def main():
    print("=== Bắt đầu quá trình chia nhỏ văn bản (Chunking) ===")
    
    async with AsyncSessionLocal() as session:
        print("Xóa các chunks cũ...")
        await session.execute(text("TRUNCATE TABLE document_chunks CASCADE"))
        await session.commit()
        
        # Đếm tổng số document
        count_res = await session.execute(text("SELECT count(*) FROM documents WHERE content IS NOT NULL"))
        total_docs = count_res.scalar() or 0
        print(f"Tổng số tài liệu cần xử lý: {total_docs}")

        # Fetch từng batch để tránh OOM
        BATCH_FETCH = 100
        total_chunks = 0
        processed_docs = 0

        while processed_docs < total_docs:
            result = await session.execute(
                select(Document.id, Document.content, Document.doc_number)
                .where(Document.content != None)
                .order_by(Document.id)
                .limit(BATCH_FETCH)
                .offset(processed_docs)
            )
            docs = result.all()
            if not docs:
                break
                
            chunks_to_insert = []
            
            for doc_id, content, doc_number in docs:
                splits = split_by_article(content, doc_number)
                
                for chunk_idx, chunk_text in enumerate(splits):
                    chunk = DocumentChunk(
                        document_id=doc_id,
                        chunk_index=chunk_idx,
                        content_chunk=chunk_text,
                        token_count=len(chunk_text.split())
                    )
                    chunks_to_insert.append(chunk)
                    total_chunks += 1
                    
            if chunks_to_insert:
                session.add_all(chunks_to_insert)
                await session.commit()
                
            processed_docs += len(docs)
            print(f"Tiến độ: {processed_docs}/{total_docs} tài liệu | Số chunks đã tạo: {total_chunks}")

        print(f"=== Hoàn thành! Đã tạo tổng cộng {total_chunks} chunks. ===")

if __name__ == "__main__":
    asyncio.run(main())

import asyncio
import json
import logging
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.core.database import AsyncSessionLocal
from app.services.rag_service import rag_retrieve, _build_context
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# Mẫu câu hỏi (Test Dataset)
TEST_SAMPLES = [
    {
        "question": "Người lao động có quyền đơn phương chấm dứt hợp đồng lao động không?",
        "ground_truth": "Có, người lao động có quyền đơn phương chấm dứt hợp đồng lao động nhưng phải báo trước cho người sử dụng lao động theo quy định của pháp luật.",
        "expected_doc_id": "8e97f3b0-c83c-45c7-b50e-9446daeda7ae" # Điều 35
    },
    {
        "question": "Tuổi nghỉ hưu của người lao động trong điều kiện bình thường là bao nhiêu?",
        "ground_truth": "Tuổi nghỉ hưu của người lao động trong điều kiện lao động bình thường được điều chỉnh theo lộ trình cho đến khi nam đủ 62 tuổi vào năm 2028 và nữ đủ 60 tuổi vào năm 2035.",
        "expected_doc_id": "ff1af49e-780d-4587-b726-7c477ff8169d" # Điều 169
    }
]

async def generate_full_answer(session, question):
    from app.services.rag_service import rag_generate_stream
    chunks = []
    async for chunk in rag_generate_stream(session, question):
        if not chunk.startswith("__CITATIONS__"):
            chunks.append(chunk)
    return "".join(chunks)

def calculate_mrr_and_hit(retrieved_docs, expected_id, k=5):
    """Tính MRR@5 và Hit@5 cho 1 câu hỏi."""
    for rank, doc in enumerate(retrieved_docs[:k]):
        if str(doc.get("doc_id")) == expected_id:
            return 1.0 / (rank + 1), 1 # MRR, Hit
    return 0.0, 0

async def run_benchmark():
    log.info("Bắt đầu chạy Benchmark RAGAs...")
    
    # Khởi tạo mô hình LLM và Embedding cho Ragas Judge
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=settings.gemini_api_key)
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=settings.gemini_api_key)
    
    data_samples = {
        "question": [],
        "answer": [],
        "contexts": [],
        "ground_truth": []
    }
    
    mrr_scores = []
    hit_scores = []

    async with AsyncSessionLocal() as session:
        for i, sample in enumerate(TEST_SAMPLES):
            log.info(f"Đang xử lý câu hỏi {i+1}: {sample['question']}")
            
            # 1. Retrieve
            retrieved_docs = await rag_retrieve(session, sample["question"])
            contexts = [doc.get("snippet", "") for doc in retrieved_docs[:3]]
            
            # Tính MRR và Hit
            mrr, hit = calculate_mrr_and_hit(retrieved_docs, sample["expected_doc_id"])
            mrr_scores.append(mrr)
            hit_scores.append(hit)
            
            # 2. Generate Answer
            answer = await generate_full_answer(session, sample["question"])
            
            data_samples["question"].append(sample["question"])
            data_samples["answer"].append(answer)
            data_samples["contexts"].append(contexts)
            data_samples["ground_truth"].append(sample["ground_truth"])
            
    # Chạy Ragas Evaluate
    dataset = Dataset.from_dict(data_samples)
    log.info("Đang chấm điểm LLM bằng RAGAs (Faithfulness, Answer Relevancy)...")
    
    score = evaluate(
        dataset,
        metrics=[faithfulness, answer_relevancy],
        llm=llm,
        embeddings=embeddings
    )
    
    final_mrr = sum(mrr_scores) / len(mrr_scores) if mrr_scores else 0
    final_hit = sum(hit_scores) / len(hit_scores) if hit_scores else 0
    
    result = {
        "MRR@5": round(final_mrr, 4),
        "Hit@5": round(final_hit, 4),
        "Faithfulness": round(score["faithfulness"], 4),
        "Answer_Relevancy": round(score["answer_relevancy"], 4)
    }
    
    log.info("\n=== KẾT QUẢ BENCHMARK ===")
    print(json.dumps(result, indent=2))
    
    with open("ragas_scorecard.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
        
    log.info("Đã lưu kết quả vào ragas_scorecard.json")

if __name__ == "__main__":
    asyncio.run(run_benchmark())

"""
RRF (Reciprocal Rank Fusion) Service — Kết hợp BM25 và Semantic ranks.

Công thức: RRF_score(d) = Σ 1 / (k + rank_i)
với k = 60 (constant để giảm ảnh hưởng của outlier rank cao)
"""
from typing import List, Dict


RRF_K = 60


def reciprocal_rank_fusion(
    bm25_results: List[dict],
    semantic_results: List[dict],
    top_k: int = 10,
) -> List[dict]:
    """
    Merge 2 ranked lists bằng Reciprocal Rank Fusion.

    Args:
        bm25_results: List kết quả BM25, mỗi item có 'id' và 'rank'
        semantic_results: List kết quả Semantic Search, mỗi item có 'id' và 'rank'
        top_k: Số kết quả trả về sau fusion

    Returns:
        List đã merge và sắp xếp theo RRF score giảm dần
    """
    # Build lookup dict: id → full document info
    doc_info: Dict[str, dict] = {}
    rrf_scores: Dict[str, float] = {}

    # Xử lý BM25 results
    for item in bm25_results:
        doc_id = str(item.get("doc_id", item.get("id")))
        doc_info[doc_id] = item
        rank = item.get("rank", 999)
        rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + (1.0 / (RRF_K + rank))

    # Xử lý Semantic results
    for item in semantic_results:
        doc_id = str(item.get("doc_id", item.get("id")))
        if doc_id not in doc_info:
            doc_info[doc_id] = item
        rank = item.get("rank", 999)
        rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + (1.0 / (RRF_K + rank))

    # Sort theo RRF score giảm dần
    sorted_ids = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)

    results = []
    for new_rank, doc_id in enumerate(sorted_ids[:top_k], start=1):
        doc = doc_info[doc_id].copy()
        doc["score"] = round(rrf_scores[doc_id], 6)
        doc["rank"] = new_rank
        results.append(doc)

    return results


def merge_by_score(results_list: List[List[dict]], top_k: int = 10) -> List[dict]:
    """
    Fallback: merge nhiều result lists bằng score trực tiếp (khi chỉ có 1 source).
    """
    seen_ids = set()
    merged = []
    for results in results_list:
        for item in results:
            doc_id = str(item.get("doc_id", item.get("id")))
            if doc_id not in seen_ids:
                seen_ids.add(doc_id)
                merged.append(item)

    merged.sort(key=lambda x: x.get("score", 0), reverse=True)
    for i, item in enumerate(merged[:top_k], start=1):
        item["rank"] = i
    return merged[:top_k]

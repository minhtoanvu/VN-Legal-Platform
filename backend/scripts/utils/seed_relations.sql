CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
DO $$
DECLARE
    root_id uuid := uuid_generate_v4();
    doc1_id uuid := uuid_generate_v4();
    doc2_id uuid := uuid_generate_v4();
    doc3_id uuid := uuid_generate_v4();
    doc4_id uuid := uuid_generate_v4();
    doc5_id uuid := uuid_generate_v4();
BEGIN
    INSERT INTO documents (id, title, doc_number, doc_type, issuing_body, status, created_at) 
    VALUES (root_id, 'Văn bản gốc Minh Toàn', 'Điều MinhToan.Gốc', 'Luật', 'Quốc hội', 'active', now());

    INSERT INTO documents (id, title, doc_number, doc_type, issuing_body, status, created_at) 
    VALUES (doc1_id, 'Văn bản hướng dẫn Minh Toàn', 'Điều MinhToan.1', 'Nghị định', 'Chính phủ', 'active', now());
    
    INSERT INTO documents (id, title, doc_number, doc_type, issuing_body, status, created_at) 
    VALUES (doc2_id, 'Văn bản sửa đổi Minh Toàn', 'Điều MinhToan.2', 'Luật', 'Quốc hội', 'active', now());
    
    INSERT INTO documents (id, title, doc_number, doc_type, issuing_body, status, created_at) 
    VALUES (doc3_id, 'Văn bản thay thế Minh Toàn', 'Điều MinhToan.3', 'Luật', 'Quốc hội', 'active', now());
    
    INSERT INTO documents (id, title, doc_number, doc_type, issuing_body, status, created_at) 
    VALUES (doc4_id, 'Văn bản bãi bỏ Minh Toàn', 'Điều MinhToan.4', 'Luật', 'Quốc hội', 'expired', now());
    
    INSERT INTO documents (id, title, doc_number, doc_type, issuing_body, status, created_at) 
    VALUES (doc5_id, 'Văn bản triển khai Minh Toàn', 'Điều MinhToan.5', 'Thông tư', 'Bộ Tư pháp', 'active', now());

    INSERT INTO document_relations (id, source_doc_id, target_doc_id, relation_type, description)
    VALUES (uuid_generate_v4(), root_id, doc1_id, 'GUIDES', 'Hướng dẫn');
    
    INSERT INTO document_relations (id, source_doc_id, target_doc_id, relation_type, description)
    VALUES (uuid_generate_v4(), root_id, doc2_id, 'AMENDS', 'Sửa đổi, bổ sung');
    
    INSERT INTO document_relations (id, source_doc_id, target_doc_id, relation_type, description)
    VALUES (uuid_generate_v4(), root_id, doc3_id, 'REPLACES', 'Thay thế');
    
    INSERT INTO document_relations (id, source_doc_id, target_doc_id, relation_type, description)
    VALUES (uuid_generate_v4(), root_id, doc4_id, 'REVOKES', 'Bãi bỏ');
    
    INSERT INTO document_relations (id, source_doc_id, target_doc_id, relation_type, description)
    VALUES (uuid_generate_v4(), root_id, doc5_id, 'IMPLEMENTS', 'Triển khai thi hành');
END $$;

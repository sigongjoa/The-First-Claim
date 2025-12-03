#!/usr/bin/env python3
import pdfplumber
import json
import os

pdf_path = "/mnt/d/progress/The-First-Claim/assets/1994037951_6WETqkrB_501827919862976725634521800816b5a957c592.pdf"

def analyze_pdf(pdf_file):
    """PDF 파일을 분석하고 결과를 반환합니다."""
    results = {
        "file_name": os.path.basename(pdf_file),
        "total_pages": 0,
        "text_content": [],
        "tables": [],
        "metadata": {},
        "summary": {}
    }

    try:
        with pdfplumber.open(pdf_file) as pdf:
            results["total_pages"] = len(pdf.pages)
            results["metadata"] = pdf.metadata

            print(f"📄 PDF 분석 시작: {os.path.basename(pdf_file)}")
            print(f"📊 총 페이지 수: {results['total_pages']}")
            print(f"📋 메타데이터: {json.dumps(results['metadata'], indent=2, ensure_ascii=False)}")
            print("\n" + "="*80 + "\n")

            # 각 페이지 처리
            for page_num, page in enumerate(pdf.pages, 1):
                print(f"📄 페이지 {page_num}/{results['total_pages']} 분석 중...")

                # 텍스트 추출
                text = page.extract_text()
                if text:
                    results["text_content"].append({
                        "page": page_num,
                        "text": text.strip()
                    })

                # 표 추출
                tables = page.extract_tables()
                if tables:
                    for table_idx, table in enumerate(tables):
                        results["tables"].append({
                            "page": page_num,
                            "table_index": table_idx,
                            "data": table
                        })
                        print(f"   ✓ 페이지 {page_num}에서 표 {table_idx + 1} 찾음")

            # 요약 통계
            results["summary"] = {
                "total_pages": results["total_pages"],
                "total_text_blocks": len(results["text_content"]),
                "total_tables": len(results["tables"]),
                "has_metadata": bool(results["metadata"])
            }

            print("\n" + "="*80)
            print("📊 분석 완료!")
            print(f"✓ 총 페이지: {results['summary']['total_pages']}")
            print(f"✓ 텍스트 블록: {results['summary']['total_text_blocks']}")
            print(f"✓ 표 개수: {results['summary']['total_tables']}")
            print("="*80 + "\n")

    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        results["error"] = str(e)

    return results

def print_text_preview(results, max_length=500):
    """텍스트 내용 미리보기"""
    if results["text_content"]:
        print("\n📝 텍스트 내용 미리보기:")
        print("="*80)
        for item in results["text_content"][:5]:  # 처음 5개 페이지만
            text = item["text"][:max_length]
            print(f"\n[페이지 {item['page']}]")
            print(text)
            if len(item["text"]) > max_length:
                print(f"... (더 많은 내용 있음, 총 {len(item['text'])} 자)")

def print_tables_preview(results):
    """표 내용 미리보기"""
    if results["tables"]:
        print("\n\n📋 표 내용 미리보기:")
        print("="*80)
        for item in results["tables"][:3]:  # 처음 3개 표만
            print(f"\n[페이지 {item['page']}, 표 {item['table_index'] + 1}]")
            table = item["data"]
            for row_idx, row in enumerate(table[:5]):  # 처음 5개 행만
                print(f"  행 {row_idx + 1}: {row}")
            if len(table) > 5:
                print(f"  ... (더 많은 행 있음, 총 {len(table)} 행)")

if __name__ == "__main__":
    results = analyze_pdf(pdf_path)
    print_text_preview(results)
    print_tables_preview(results)

    # 전체 결과를 JSON으로 저장
    output_file = "/mnt/d/progress/The-First-Claim/pdf_analysis_result.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        # JSON 직렬화를 위해 결과 정리
        json_results = {
            "file_name": results["file_name"],
            "total_pages": results["total_pages"],
            "metadata": results["metadata"],
            "summary": results["summary"],
            "text_content_summary": [
                {
                    "page": item["page"],
                    "text_length": len(item["text"]),
                    "preview": item["text"][:200] + "..." if len(item["text"]) > 200 else item["text"]
                }
                for item in results["text_content"]
            ],
            "tables_summary": [
                {
                    "page": item["page"],
                    "table_index": item["table_index"],
                    "rows": len(item["data"]),
                    "columns": len(item["data"][0]) if item["data"] else 0
                }
                for item in results["tables"]
            ]
        }
        json.dump(json_results, f, indent=2, ensure_ascii=False)

    print(f"\n💾 분석 결과가 저장되었습니다: {output_file}")

import json
import sys

def convert_json_to_md(json_file_path, output_file_path):
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    reviewer_id = data.get('reviewer_id', 'unknown_reviewer')
    md_content = f"# 摘要評審報告 - {reviewer_id}\n\n"
    
    md_content += "## 第一階段：語感與寫作絕對淘汰\n\n"
    
    items = data.get('items', [])
    for item in items:
        item_id = item.get('item_id', 'unknown')
        md_content += f"### {item_id}\n"
        
        findings = item.get('findings', [])
        if findings:
            md_content += "**最差語感證據：**\n"
            for i, finding in enumerate(findings, 1):
                condition = finding.get('condition', '')
                notes = finding.get('notes', '')
                md_content += f"{i}. [{condition}] {notes}\n"
            md_content += "\n**判定：** 淘汰\n\n"
        else:
            md_content += "**判定：** 通過\n\n"
            
    global_eval = data.get('global_evaluation', {})
    if global_eval:
        md_content += "## 最終語感比較\n\n"
        top_3 = global_eval.get('top_3_ids', [])
        md_content += f"**Top 3：** {', '.join(top_3)}\n\n"
        comparison = global_eval.get('language_flow_comparison', '')
        md_content += f"**語感差距分析：**\n{comparison}\n\n"
        
        best_id = global_eval.get('best_summary_id', '')
        md_content += f"**最佳摘要：** {best_id}\n\n"
        
    md_content += "## 第二階段：內容比對與改進\n\n"
    
    for item in items:
        stage2 = item.get('stage2_evaluation')
        if stage2:
            item_id = item.get('item_id', 'unknown')
            passed = stage2.get('passed', False)
            suggestions = stage2.get('improvement_suggestions', '')
            
            # 只有當有建議或明確判定時才印出
            if suggestions or not passed:
                md_content += f"### {item_id}\n"
                md_content += f"**第二階段通過：** {'是' if passed else '否'}\n"
                if suggestions:
                    md_content += f"**改進建議：**\n{suggestions}\n\n"
                else:
                    md_content += "\n"
                    
    with open(output_file_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
        
    print(f"Generated Markdown successfully at {output_file_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python json_to_md.py <input.json> <output.md>")
        sys.exit(1)
        
    convert_json_to_md(sys.argv[1], sys.argv[2])

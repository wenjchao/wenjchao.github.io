import json
import sys
import os

HTML_TEMPLATE = """<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<title>Paper Summary</title>
<style>
  :root {{ --ink: #202124; --muted: #5f6368; --rule: #d8dee4; --soft: #f6f8fa; --accent: #355c7d; --accent-strong: #243f5a; --accent-soft: #eaf1f8; }}
  * {{ box-sizing: border-box; }} html {{ scroll-behavior: smooth; }}
  body {{ margin: 0; background: #fff; color: var(--ink); font-family: sans-serif; line-height: 1.8; }}
  main {{ width: min(1120px, calc(100% - 32px)); margin: 0 auto; padding: 48px 0; }}
  .trace-node {{ padding: 14px; border: 1px solid var(--rule); background: #fbfcfe; transition: all 140ms; }}
  .trace-node:hover, .trace-node.is-active {{ border-color: var(--accent); box-shadow: 0 4px 12px rgba(0,0,0,0.1); transform: translateY(-1px); }}
  .trace-node.is-source {{ border-color: var(--accent); background: #eef6ff; outline: 2px solid var(--accent-soft); }}
  .node-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 12px; margin-top: 16px; }}
  .node-id {{ padding: 2px 8px; background: var(--accent-strong); color: #fff; font-size: 0.76rem; border-radius: 999px; }}
  .tag {{ padding: 2px 8px; border: 1px solid var(--rule); font-size: 0.76rem; border-radius: 999px; margin-left: 8px;}}
  .step-section {{ margin-top: 22px; padding: 18px; border: 1px solid var(--rule); }}
  .source-link, .final-source {{ font-size: 0.78rem; border: 1px solid #c7d4df; padding: 2px 8px; border-radius: 999px; text-decoration: none; color: var(--accent-strong); margin-right: 4px;}}
  .final-para {{ display: grid; grid-template-columns: 120px 1fr; gap: 16px; margin-top: 24px; }}
  .question-text {{ font-weight: bold; color: var(--accent-strong); margin-bottom: 4px; display: block; }}
  .answer-text {{ margin-top: 0; }}
</style>
</head>
<body>
<main>

<thinking_process>
{thinking_process_html}
</thinking_process>

<section class="final-output">
{final_output_html}
</section>

</main>
<script>
  const traceNodes = document.querySelectorAll(".trace-node[data-source]");
  const clearSources = () => document.querySelectorAll(".is-source, .is-active").forEach(el => el.classList.remove("is-source", "is-active"));
  const highlightSources = (node) => {{
    clearSources(); node.classList.add("is-active");
    (node.dataset.source || "").split(/\s+/).filter(Boolean).forEach(id => {{
      const el = document.getElementById(id); if(el) el.classList.add("is-source");
    }});
  }};
  traceNodes.forEach(node => {{
    node.addEventListener("mouseenter", () => highlightSources(node));
    node.addEventListener("focusin", () => highlightSources(node));
  }});
  const tp = document.querySelector("thinking_process");
  if(tp) tp.addEventListener("mouseleave", clearSources);
</script>
</body>
</html>
"""

def generate_step_html(step_num, nodes):
    if not nodes:
        return ""
    
    html = f'  <section class="step-section" id="step-{step_num}">\n'
    html += '    <h2>Step ' + str(step_num) + '</h2>\n'
    html += '    <div class="node-grid">\n'
    
    for node in nodes:
        node_id = node.get('id', '')
        tag = node.get('tag', '')
        source = node.get('source', '')
        
        source_attr = f' data-source="{source}"' if source else ''
        
        html += f'      <article class="trace-node" id="{node_id}"{source_attr}>\n'
        html += f'        <div class="node-top"><span class="node-id">{node_id.upper()}</span><span class="tag">{tag}</span></div>\n'
        
        if step_num in [1, 4] or str(step_num) in ['1', '4']:
            content = node.get('content', '')
            html += f'        <p class="node-body">{content}</p>\n'
        else:
            question = node.get('question', '')
            ans_orig = node.get('answer_original', '')
            ans_ref = node.get('answer_refined', '')
            html += '        <div class="node-body">\n'
            html += f'          <span class="question-text">問：{question}</span>\n'
            html += f'          <p class="answer-text">答（原始）：{ans_orig}</p>\n'
            html += f'          <p class="answer-text">答（精修）：{ans_ref}</p>\n'
            html += '        </div>\n'
            if source:
                html += '        <div class="source-links"><span class="source-label">承接</span>'
                for src in source.split():
                    html += f'<a class="source-link" href="#{src}">{src.upper()}</a>'
                html += '</div>\n'
                
        html += '      </article>\n'
        
    html += '    </div>\n'
    html += '  </section>\n'
    return html

def generate_final_output_html(final_output):
    html = ""
    for idx, para in enumerate(final_output):
        sources = para.get('sources', [])
        content = para.get('content', '')
        
        html += '  <div class="final-para">\n'
        if sources:
            html += '    <aside class="final-map">\n'
            for src in sources:
                html += f'      <a class="final-source" href="#{src}">{src.upper()}</a>\n'
            html += '    </aside>\n'
        html += f'    <p>{content}</p>\n'
        html += '  </div>\n'
    return html

def convert_json_to_html(json_file_path, output_file_path):
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    if not data.get('items'):
        print("No items found in JSON.")
        return
        
    item = data['items'][0]  # Take the first item
    
    thinking_process = item.get('thinking_process', [])
    # 優先使用 refined_final_output，若無則使用 final_output
    final_output = item.get('refined_final_output', item.get('final_output', []))
    
    # Group nodes by step
    steps = {}
    for node in thinking_process:
        step = str(node.get('step', ''))
        if step not in steps:
            steps[step] = []
        steps[step].append(node)
        
    thinking_process_html = ""
    for step in ['1', '2', '3', '4']:
        if step in steps:
            thinking_process_html += generate_step_html(step, steps[step])
            
    final_output_html = generate_final_output_html(final_output)
    
    final_html = HTML_TEMPLATE.format(
        thinking_process_html=thinking_process_html,
        final_output_html=final_output_html
    )
    
    with open(output_file_path, 'w', encoding='utf-8') as f:
        f.write(final_html)
        
    print(f"Generated HTML successfully at {output_file_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python json_to_html.py <input.json> <output.html>")
        sys.exit(1)
        
    convert_json_to_html(sys.argv[1], sys.argv[2])

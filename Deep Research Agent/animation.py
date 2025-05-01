import streamlit.components.v1 as components
import base64
import os


def show_research_pipeline():
    # st.set_page_config(layout="wide")

    def image_html(img):
        with open(os.path.join(os.getcwd(), "icons", f"{img}"), "rb") as f:
            data = f.read()
            encoded_img = base64.b64encode(data).decode()
        return f'data:image/png;base64,{encoded_img}'

    components.html(f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {{
        margin: 0;
        background: #0E1117;
        font-family: sans-serif;
        }}
        .container {{
        position: relative;
        width: 100%;
        height: 450px;
        }}
        .icon-box {{
        position: absolute;
        text-align: center;
        }}
        .icon-img {{
    width: 60px;
    height: 60px;
    border-radius: 0;
    border: none;
}}

        .label {{
        font-weight: bold;
        font-size: 12px; /* or 10px, depending on your preference */
        color: white;
        }}
        .agent-box {{
        top: 20px;
        left: 45%;
        }}
        .agent-box .label {{
        margin-bottom: 8px;
        display: block;
        }}
        .tool1-box {{ bottom: 50px; left: 5%; display: none; }}
        .tool2-box {{ bottom: 50px; left: 28%; display: none; }}
        .tool3-box {{ bottom: 50px; left: 52%; display: none; }}
        .tool4-box {{ bottom: 50px; left: 76%; display: none; }}

        .msg {{
        position: absolute;
        background: rgba(255, 255, 255, 0.5);
        padding: 6px 12px;
        border-radius: 8px;
        border: 1px solid #ccc;
        font-size: 10px;
        opacity: 0;
        transition: opacity 0.5s ease-in-out;
        }}
        .msg.show {{ opacity: 1; }}

        svg {{
        position: absolute;
        width: 100%;
        height: 100%;
        pointer-events: none;
        }}
        .arrow {{
        fill: none;
        stroke-width: 2;
        marker-end: url(#arrowhead);
        stroke-dasharray: 5 10;
        stroke-dashoffset: 1000;
        animation: drawLine 85s linear forwards;
        }}
        .arrow.request {{ stroke: #007bff; }}
        .arrow.response {{ stroke: #28a745; }}

        @keyframes drawLine {{
        to {{ stroke-dashoffset: 0; }}
        }}
    </style>
    </head>
    <body>
    <div class="container">
    <!-- Research Team Lead -->
    <div class="icon-box agent-box" id="agent">
        <div class="label">Research Team Lead</div>
        <img src="{image_html('bot.png')}" class="icon-img" />
    </div>

    <!-- Tools -->
    <div class="icon-box tool1-box" id="tool1">
        <img src="{image_html('ai.png')}" class="icon-img" />
        <div class="label">Research Planner</div>
    </div>

    <div class="icon-box tool2-box" id="tool2">
        <img src="{image_html('ai.png')}" class="icon-img" />
        <div class="label">Research Agent</div>
    </div>

    <div class="icon-box tool3-box" id="tool3">
        <img src="{image_html('ai.png')}" class="icon-img" />
        <div class="label">Analysis Agent</div>
    </div>

    <div class="icon-box tool4-box" id="tool4">
        <img src="{image_html('ai.png')}" class="icon-img" />
        <div class="label">Writer Agent</div>
    </div>

    <svg id="svgCanvas">
        <defs>
        <marker id="arrowhead" markerWidth="8" markerHeight="8" refX="8" refY="4" orient="auto" markerUnits="strokeWidth">
  <path d="M0,0 L8,4 L0,8" fill="none" stroke="white" stroke-width="0.8"/>
</marker>




        </defs>
    </svg>

    <div id="msg" class="msg"></div>
    <div id="msgBack" class="msg"></div>
    <div id="finalMsg" class="msg" style="font-size:16px; color:#222;"></div>
    </div>

    <script>
    const agent = document.getElementById('agent');
    const svg = document.getElementById('svgCanvas');
    const msg = document.getElementById('msg');
    const msgBack = document.getElementById('msgBack');
    const topMsg = document.getElementById('finalMsg');

    const toolSequence = [
        {{ id: 'tool1', request: 'Start the  Research Plan', response: 'Plan Created' }},
        {{ id: 'tool2', request: 'Assigning Research Task', response: 'Research Notes Ready' }},
        {{ id: 'tool3', request: 'Assigning Data Analysis', response: 'Insights Extracted' }},
        {{ id: 'tool4', request: 'Generate Report Draft', response: 'Draft Submitted' }},
    ];

    let currentIndex = 0;
    const maxInteractions = toolSequence.length;

    function getCoords(fromElem, toElem) {{
        const fromRect = fromElem.getBoundingClientRect();
        const toRect = toElem.getBoundingClientRect();
        const fromX = fromRect.left + fromRect.width / 2 + window.scrollX;
        const fromY = fromRect.top + fromRect.height / 2 + window.scrollY;
        const toX = toRect.left + toRect.width / 2 + window.scrollX;
        const toY = toRect.top + toRect.height / 2 + window.scrollY;
        return {{ from: {{x: fromX, y: fromY + 40}}, to: {{x: toX, y: toY - 40}} }};
    }}

    function drawPath(from, to, id, cls) {{
        const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
        const midX = (from.x + to.x) / 2;
        const midY = (from.y + to.y) / 2;
        const ctrlX = midX;
        const ctrlY = cls === 'request' ? midY - 80 : midY + 80;
        path.setAttribute("d", `M${{from.x}},${{from.y}} Q${{ctrlX}},${{ctrlY}} ${{to.x}},${{to.y}}`);
        path.setAttribute("class", "arrow " + cls);
        svg.appendChild(path);
    }}

    function interact() {{
        if (currentIndex >= maxInteractions) return;

        const tool = toolSequence[currentIndex];
        const toolElem = document.getElementById(tool.id);
        toolElem.style.display = 'block';

        const {{from, to}} = getCoords(agent, toolElem);
        drawPath(from, to, 'req'+tool.id, 'request');

        msg.innerText = tool.request;
        msg.style.left = (from.x + to.x) / 2 - 80 + 'px';
        msg.style.top = (from.y + to.y) / 2 - 60 + 'px';
        msg.classList.add('show');

        setTimeout(() => {{
        drawPath(to, from, 'res'+tool.id, 'response');
        msgBack.innerText = tool.response;
        msgBack.style.left = (from.x + to.x) / 2 - 80 + 'px';
        msgBack.style.top = (from.y + to.y) / 2 + 30 + 'px';
        msgBack.classList.add('show');

        // Final message after all interactions
        if (currentIndex === maxInteractions - 1) {{
            const agentRect = agent.getBoundingClientRect();
            const agentPos = {{
            x: agentRect.left + agentRect.width / 2 + window.scrollX,
            y: agentRect.top + window.scrollY
            }};
            setTimeout(() => {{
            topMsg.innerText = "Final Response Generated!";
            topMsg.style.left = (agentPos.x - 70) + 'px';
            topMsg.style.top = (agentPos.y - 120) + 'px';
            topMsg.classList.add('show');
            }}, 1800);
        }}
        }}, 5000);  // Delay agent response by 5 seconds

        currentIndex++;
    }}

    setInterval(interact, 10000);
    </script>
    </body>
    </html>
    """, height=480)




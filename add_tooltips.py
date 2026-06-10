import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add position: relative to overlay-btn
content = content.replace('box-shadow: 0 4px 12px rgba(0,0,0,0.2); \n              color: var(--text-main);\n              transition: all 0.2s; \n          }', 'box-shadow: 0 4px 12px rgba(0,0,0,0.2); \n              color: var(--text-main);\n              transition: all 0.2s; \n              position: relative;\n          }')

# 2. Add ::after pseudo-element CSS
tooltip_css = '''
          .overlay-btn::after {
              content: attr(data-tooltip);
              position: absolute;
              right: 120%;
              top: 50%;
              transform: translateY(-50%);
              background: var(--bg-card);
              color: var(--text-main);
              padding: 6px 12px;
              border-radius: 6px;
              font-size: 12px;
              font-weight: 600;
              white-space: nowrap;
              opacity: 0;
              visibility: hidden;
              transition: opacity 0.2s, right 0.2s;
              border: 1px solid var(--border-glass);
              box-shadow: 0 4px 12px rgba(0,0,0,0.2);
              pointer-events: none;
              z-index: 1001;
          }
          .overlay-btn:hover::after {
              opacity: 1;
              visibility: visible;
              right: 115%;
          }
          .overlay-btn.active { background: var(--text-main); color: var(--bg-body); }'''

content = content.replace('.overlay-btn.active { background: var(--text-main); color: var(--bg-body); }', tooltip_css)

# 3. Replace all title="..." with data-tooltip="..." in the map-overlay div
# Wait, I'll just replace 'title=' with 'data-tooltip=' everywhere for the buttons.
content = content.replace('title="Toggle Theme"', 'data-tooltip="Toggle Theme"')
content = content.replace('title="Measure Distance"', 'data-tooltip="Measure Distance"')
content = content.replace('title="Measure Azimuth"', 'data-tooltip="Measure Azimuth"')
content = content.replace('title="Reset View"', 'data-tooltip="Reset View"')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("Added instant tooltips")

import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

css_old = '''.overlay-btn { 
              background: var(--bg-panel); 
              backdrop-filter: var(--panel-blur);
              padding: 10px 14px; 
              border-radius: 12px; 
              cursor: pointer; 
              display: flex; 
              align-items: center; 
              justify-content: flex-start;
              gap: 10px;
              border: 1px solid var(--border-glass); 
              box-shadow: 0 4px 12px rgba(0,0,0,0.2); 
              color: var(--text-main);
              transition: all 0.2s; 
          }
          .overlay-btn span { font-size: 13px; font-weight: 600; white-space: nowrap; }'''

css_new = '''.overlay-btn { 
              background: var(--bg-panel); 
              backdrop-filter: var(--panel-blur);
              padding: 10px; 
              border-radius: 12px; 
              cursor: pointer; 
              display: flex; 
              align-items: center; 
              justify-content: center; 
              width: 44px; 
              height: 44px; 
              border: 1px solid var(--border-glass); 
              box-shadow: 0 4px 12px rgba(0,0,0,0.2); 
              color: var(--text-main);
              transition: all 0.2s; 
          }'''

def normalize(s): return re.sub(r'\s+', r'\\s+', re.escape(s))
content = re.sub(normalize(css_old), css_new, content)

content = re.sub(r'\s*<span>Toggle Theme</span>', '', content)
content = re.sub(r'\s*<span>Distance</span>', '', content)
content = re.sub(r'\s*<span>Azimuth</span>', '', content)
content = re.sub(r'\s*<span>Reset View</span>', '', content)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("Reversed changes")

# ui_components.py - Flask-independent UI components
import os

class BasicPage:
    def __init__(self, title="Page", container_width="650px", container_height="700px"):
        self.title = title
        self.container_width = container_width
        self.container_height = container_height
        self.elements = []
        self.scripts = []
    
    def element_header(self, logo_url="../logo.jpg", logo_width="320px", logo_height="100px", 
                      title="KIND 행사내역 조회 프로그램", subtitle="타임폴리오 대체투자본부"):
        return f'''
        <div class="header">
            <div class="logo">
                <img src="{logo_url}" alt="Logo" style="width:{logo_width};height:{logo_height};object-fit:contain;border-radius:10px;">
            </div>
            <h1 class="title">{title}</h1>
            <p class="subtitle">{subtitle}</p>
        </div>
        '''
    
    def element_form_group(self, label_text, input_type="text", input_id="", input_name="", 
                          input_placeholder="", input_value="", required=False, input_class="form-input"):
        required_attr = "required" if required else ""
        return f'''
        <div class="form-group">
            <label class="form-label" for="{input_id}">{label_text}</label>
            <input type="{input_type}" id="{input_id}" name="{input_name}" 
                   class="{input_class}" placeholder="{input_placeholder}" 
                   value="{input_value}" {required_attr}>
        </div>
        '''
    
    def element_date(self, from_date_label="검색 시작일", to_date_label="검색 종료일", 
                    from_date_id="fromDate", to_date_id="toDate", 
                    from_date_value="2024-09-20", to_date_value="2025-09-30"):
        return f'''
        <div class="form-group">
            <div class="date-row">
                <div>
                    <label class="form-label" for="{from_date_id}">{from_date_label}</label>
                    <input type="date" id="{from_date_id}" name="{from_date_id}" class="form-input" 
                           value="{from_date_value}" required>
                </div>
                <div>
                    <label class="form-label" for="{to_date_id}">{to_date_label}</label>
                    <input type="date" id="{to_date_id}" name="{to_date_id}" class="form-input" 
                           value="{to_date_value}" required>
                </div>
            </div>
        </div>
        '''
    
    def element_checkbox(self, checkbox_id="headless", checkbox_name="headless", 
                        label_text="Chrome 팝업 없이 실행하기", checked=False):
        checked_attr = "checked" if checked else ""
        return f'''
        <div class="checkbox-group">
            <input type="checkbox" id="{checkbox_id}" name="{checkbox_name}" class="checkbox" {checked_attr}>
            <label for="{checkbox_id}" class="checkbox-label">{label_text}</label>
        </div>
        '''
    
    def element_button(self, button_id, button_text, button_type="button", 
                      button_class="btn btn-primary", onclick="", style="", hidden=False):
        hidden_style = "display:none" if hidden else ""
        combined_style = f"{hidden_style};{style}" if style else hidden_style
        style_attr = f'style="{combined_style}"' if combined_style else ""
        onclick_attr = f'onclick="{onclick}"' if onclick else ""
        return f'''
        <button id="{button_id}" type="{button_type}" class="{button_class}" 
                {onclick_attr} {style_attr}>{button_text}</button>
        '''
    
    def element_button_group(self, buttons):
        button_html = ""
        for button in buttons:
            button_html += self.element_button(**button)
        return f'''
        <div class="button-group">
            {button_html}
        </div>
        '''
    
    def element_info_panel(self, panel_id="companyInfo", hidden=True):
        display_style = "display: none;" if hidden else ""
        return f'''
        <div id="{panel_id}" class="info-panel" style="{display_style}"></div>
        '''
    
    def add_element(self, element_html):
        self.elements.append(element_html)
    
    def add_script(self, script_content):
        self.scripts.append(script_content)
    
    def generate_html(self, form_id="configForm"):
        elements_html = "\n".join(self.elements)
        scripts_html = "\n".join(self.scripts)
        
        return f'''
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', 'Microsoft YaHei', 'Malgun Gothic', Arial, sans-serif;
            background: linear-gradient(135deg, #1D79B0 0%, #1D5D8C 50%, #344B79 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}
        
        .button-group {{ 
            display: flex; 
            gap: 12px; 
            justify-content: center; 
            flex-wrap: wrap; 
        }}
        .btn {{ 
            white-space: nowrap; 
            min-width: 110px; 
        }}
        
        .container {{
            background: white;
            border-radius: 20px;
            padding: 40px;
            width: 100%;
            max-width: {self.container_width};
            min-height: {self.container_height};
            animation: slideUp 0.5s ease-out;
        }}
        
        @keyframes slideUp {{
            from {{
                opacity: 0;
                transform: translateY(30px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        
        .logo {{
            width: 320px;
            height: 100px;
            border-radius: 15px;
            margin: 0 auto 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: white;
        }}
        
        .title {{
            font-size: 28px;
            font-weight: 700;
            color: #2c3e50;
            margin-bottom: 8px;
        }}
        
        .subtitle {{
            color: #6c757d;
            font-size: 16px;
        }}
        
        .form-group {{
            margin-bottom: 25px;
        }}
        
        .form-label {{
            display: block;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 8px;
            font-size: 14px;
        }}
        
        .form-input {{
            width: 100%;
            padding: 15px;
            border: 2px solid #e9ecef;
            border-radius: 12px;
            font-size: 16px;
            font-family: 'Segoe UI', 'Microsoft YaHei', 'Malgun Gothic', Arial, sans-serif;
            transition: all 0.3s ease;
            background: #f8f9fa;
        }}
        
        .form-input:focus {{
            outline: none;
            border-color: #007bff;
            background: white;
            box-shadow: 0 0 0 3px rgba(0,123,255,0.1);
        }}
        
        .date-row {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }}
        
        .checkbox-group {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 30px;
        }}
        
        .checkbox {{
            width: 20px;
            height: 20px;
            accent-color: #007bff;
        }}
        
        .checkbox-label {{
            color: #2c3e50;
            font-size: 14px;
        }}
        
        .button-group {{
            display: flex;
            gap: 15px;
            justify-content: flex-end;
        }}
        
        .btn {{
            padding: 15px 30px;
            border: none;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            min-width: 120px;
        }}
        
        .btn-primary {{
            background: linear-gradient(135deg, #007bff, #0056b3);
            color: white;
        }}
        
        .btn-primary:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0,123,255,0.3);
        }}
        
        .btn-secondary {{
            background: #6c757d;
            color: white;
        }}
        
        .btn-secondary:hover {{
            background: #5a6268;
            transform: translateY(-2px);
        }}
        
        .info-panel {{
            margin: 20px 0;
            padding: 15px;
            border-radius: 12px;
            background: #eef7ff;
            border: 1px solid #cfe6ff;
            color: #0c4a6e;
            display: none;
            font-size: 14px;
        }}
        
        .dev-mode-container {{
            margin-top: 20px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 12px;
            border: 1px solid #e9ecef;
            display: none;
            margin: 20px 0;
        }}
        
        .dev-settings {{
            display: grid;
            gap: 15px;
        }}
        
        .dev-setting-group {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #e9ecef;
        }}
        
        .dev-setting-group h4 {{
            margin: 0 0 10px 0;
            color: #2c3e50;
            font-size: 16px;
            font-weight: 600;
        }}
        
        .dev-setting-item {{
            display: grid;
            grid-template-columns: 1fr 2fr;
            gap: 10px;
            align-items: center;
            margin-bottom: 10px;
        }}
        
        .dev-setting-label {{
            font-size: 12px;
            color: #6c757d;
            font-weight: 500;
        }}
        
        .dev-setting-input {{
            padding: 8px;
            border: 1px solid #e9ecef;
            border-radius: 6px;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <form id="{form_id}">
            {elements_html}
        </form>
    </div>
    
    <script>
        {scripts_html}
    </script>
</body>
</html>
        '''

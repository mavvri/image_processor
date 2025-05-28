import os

class FormulaRenderer:
    """
    Renders mathematical formulas with beautiful HTML/CSS styling
    """
    
    @staticmethod
    def render_formula(formula, description="", inline=False):
        """
        Render a mathematical formula with proper styling
        
        Args:
            formula (str): LaTeX-like formula string
            description (str): Description of the formula
            inline (bool): Whether to render inline or as block
        """
        css_class = "formula-inline" if inline else "formula-block"
        
        return f"""
        <div class="{css_class}">
            <div class="formula-container">
                <span class="formula-math">{formula}</span>
            </div>
            {f'<div class="formula-description">{description}</div>' if description else ''}
        </div>
        """
    
    @staticmethod
    def get_formula_css():
        """Get CSS styles for formula rendering"""
        return """
        <style>
        .formula-block {
            margin: 12px 0;
            padding: 16px;
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            border: 1px solid #cbd5e1;
            border-radius: 12px;
            border-left: 4px solid #1d4ed8;
        }
        
        .formula-inline {
            display: inline-block;
            margin: 4px 8px;
            padding: 6px 12px;
            background: rgba(29, 78, 216, 0.05);
            border: 1px solid rgba(29, 78, 216, 0.15);
            border-radius: 8px;
        }
        
        .formula-container {
            text-align: center;
            margin: 8px 0;
        }
        
        .formula-math {
            font-family: 'Computer Modern', 'Latin Modern Math', 'Times New Roman', serif;
            font-size: 16px;
            font-weight: 500;
            color: #1e293b;
            letter-spacing: 0.5px;
            display: inline-block;
            padding: 8px 16px;
            background: white;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
        }
        
        .formula-description {
            margin-top: 8px;
            font-size: 13px;
            color: #64748b;
            font-style: italic;
            line-height: 1.5;
        }
        
        /* Mathematical symbols styling */
        .sigma { font-size: 1.2em; }
        .integral { font-size: 1.4em; }
        .sqrt { 
            border-top: 1px solid #1e293b;
            padding-top: 2px;
        }
        .fraction {
            display: inline-block;
            text-align: center;
            vertical-align: middle;
        }
        .numerator {
            display: block;
            border-bottom: 1px solid #1e293b;
            padding-bottom: 2px;
        }
        .denominator {
            display: block;
            padding-top: 2px;
        }
        .subscript {
            font-size: 0.8em;
            vertical-align: sub;
        }
        .superscript {
            font-size: 0.8em;
            vertical-align: super;
        }
        </style>
        """
    
    @staticmethod
    def convert_latex_to_html(latex_formula):
        """
        Convert LaTeX-like formulas to HTML with proper styling
        """
        # Replace common LaTeX symbols with HTML equivalents
        conversions = {
            r'\sigma': '<span class="sigma">σ</span>',
            r'\Sigma': '<span class="sigma">Σ</span>',
            r'\pi': 'π',
            r'\alpha': 'α',
            r'\beta': 'β',
            r'\gamma': 'γ',
            r'\delta': 'δ',
            r'\epsilon': 'ε',
            r'\theta': 'θ',
            r'\lambda': 'λ',
            r'\mu': 'μ',
            r'\nabla': '∇',
            r'\partial': '∂',
            r'\infty': '∞',
            r'\int': '<span class="integral">∫</span>',
            r'\sqrt': '<span class="sqrt">√</span>',
            r'\leq': '≤',
            r'\geq': '≥',
            r'\neq': '≠',
            r'\approx': '≈',
            r'\pm': '±',
            r'\times': '×',
            r'\cdot': '·',
        }
        
        html_formula = latex_formula
        for latex, html in conversions.items():
            html_formula = html_formula.replace(latex, html)
        
        # Handle subscripts and superscripts
        import re
        html_formula = re.sub(r'_\{([^}]+)\}', r'<sub>\1</sub>', html_formula)
        html_formula = re.sub(r'\^\{([^}]+)\}', r'<sup>\1</sup>', html_formula)
        html_formula = re.sub(r'_([a-zA-Z0-9])', r'<sub>\1</sub>', html_formula)
        html_formula = re.sub(r'\^([a-zA-Z0-9])', r'<sup>\1</sup>', html_formula)
        
        return html_formula

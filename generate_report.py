import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# -----------------------------------------------------------------------------
# 1. Data Loading & Preprocessing
# -----------------------------------------------------------------------------
FILE_PATH = '국민연금공단_시군구별 청년계층 가입자 현황_20241231.csv'

if not os.path.exists(FILE_PATH):
    print(f"Error: File not found at {FILE_PATH}")
    # Create dummy data for testing if file missing (optional, but good for robustness)
    # For now, we assume file exists as per user context.
    exit(1)

df = pd.read_csv(FILE_PATH, encoding='cp949')
df['시도'] = df['시군구명'].apply(lambda x: x.split()[0])

# -----------------------------------------------------------------------------
# 2. Visualizations
# -----------------------------------------------------------------------------

# Fig 1: Sunburst Chart (Age Groups)
df_melted = df.melt(id_vars=['연령(구분)', '시도'], 
                    value_vars=['사업장가입자', '지역가입자', '임의가입자', '임의계속가입자'],
                    var_name='가입유형', value_name='가입자수')

fig_age = px.sunburst(df_melted, path=['연령(구분)', '가입유형'], values='가입자수',
                    title='연령대별 국민연금 가입 구조',
                    color='가입유형', color_discrete_sequence=px.colors.qualitative.Pastel)
fig_age.update_layout(margin=dict(t=40, l=0, r=0, b=0))

# Fig 2: Treemap (Regional)
fig_region = px.treemap(df, path=[px.Constant("전국"), '시도', '시군구명'], 
                       values='사업장가입자',
                       color='사업장가입자',
                       color_continuous_scale='Blues',
                       title='전국 청년 일자리(사업장 가입자) 지도')
fig_region.update_layout(margin=dict(t=40, l=0, r=0, b=0))

# Fig 3: Bubble Chart (Comparison)
city_sum = df.groupby('시도').agg({
    '사업장가입자': 'sum',
    '지역가입자': 'sum',
    '임의가입자': 'sum'
}).reset_index()

fig_compare = px.scatter(city_sum, x="지역가입자", y="사업장가입자",
                 size="사업장가입자", color="시도",
                 hover_name="시도", log_x=True, size_max=60,
                 title="지역별 고용 안정성 vs 자영업 비율",
                 labels={"사업장가입자": "직장인 가입자 수", "지역가입자": "자영업/프리랜서 가입자 수"})
fig_compare.update_layout(margin=dict(t=40, l=0, r=0, b=0))


# -----------------------------------------------------------------------------
# 3. HTML Generation (Quarto Styling)
# -----------------------------------------------------------------------------

# Convert figures to HTML divs (excluding full html, just the div)
div_age = fig_age.to_html(full_html=False, include_plotlyjs='cdn')
div_region = fig_region.to_html(full_html=False, include_plotlyjs=False) # JS already included in first call
div_compare = fig_compare.to_html(full_html=False, include_plotlyjs=False)

# Quarto-like CSS & Layout Template
html_template = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>국민연금 청년계층 데이터 분석 보고서</title>
    <style>
        :root {{
            --sidebar-width: 300px;
            --main-max-width: 900px;
            --font-main: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            --color-text: #333;
            --color-bg: #fff;
            --color-link: #007bff;
            --color-border: #e9ecef;
            --color-sidebar-bg: #f8f9fa;
        }}

        body {{
            font-family: var(--font-main);
            color: var(--color-text);
            margin: 0;
            display: flex;
            min-height: 100vh;
        }}

        /* Sidebar Styling */
        .sidebar {{
            width: var(--sidebar-width);
            background-color: var(--color-sidebar-bg);
            border-right: 1px solid var(--color-border);
            padding: 2rem;
            position: fixed;
            height: 100vh;
            overflow-y: auto;
            flex-shrink: 0;
        }}

        .sidebar-title {{
            font-size: 1.2rem;
            font-weight: 700;
            margin-bottom: 1rem;
            color: #2c3e50;
        }}

        .sidebar-nav ul {{
            list-style: none;
            padding: 0;
        }}

        .sidebar-nav li {{
            margin-bottom: 0.5rem;
        }}

        .sidebar-nav a {{
            text-decoration: none;
            color: #555;
            font-size: 0.95rem;
            transition: color 0.2s;
        }}

        .sidebar-nav a:hover {{
            color: var(--color-link);
        }}
        
        .sidebar-footer {{
            margin-top: 2rem;
            font-size: 0.8rem;
            color: #888;
        }}

        /* Main Content Styling */
        .main-content {{
            flex-grow: 1;
            margin-left: var(--sidebar-width);
            padding: 2rem 4rem;
            max-width: 100%;
        }}

        .container {{
            max-width: var(--main-max-width);
            margin: 0 auto;
        }}

        h1 {{ 
            font-size: 2.2rem; 
            margin-bottom: 0.5rem; 
            font-weight: 700;
            border-bottom: 1px solid #eee;
            padding-bottom: 0.5rem;
        }}
        
        h2 {{ 
            font-size: 1.5rem; 
            margin-top: 3rem; 
            margin-bottom: 1rem; 
            color: #2c3e50;
            border-bottom: 1px solid #eee;
            padding-bottom: 0.3rem; 
        }}

        h3 {{
            font-size: 1.2rem;
            margin-top: 2rem;
            color: #495057;
        }}

        p {{
            line-height: 1.7;
            margin-bottom: 1.5rem;
            color: #444;
        }}

        .chart-container {{
            margin: 2rem 0;
            border: 1px solid #eee;
            border-radius: 8px;
            padding: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.03);
            background: white;
        }}
        
        .callout {{
            background-color: #f0f7ff;
            border-left: 5px solid #007bff;
            padding: 1rem;
            margin-bottom: 1.5rem;
            border-radius: 4px;
        }}

        /* Responsive Design */
        @media (max-width: 768px) {{
            body {{ flex-direction: column; }}
            .sidebar {{ 
                width: 100%; 
                height: auto; 
                position: relative; 
                border-right: none;
                border-bottom: 1px solid var(--color-border);
            }}
            .main-content {{ 
                margin-left: 0; 
                padding: 1.5rem; 
            }}
        }}
    </style>
</head>
<body>

    <!-- Sidebar -->
    <nav class="sidebar">
        <div class="sidebar-title">청년계층 국민연금 분석</div>
        <div class="sidebar-nav">
            <ul>
                <li><a href="#overview">1. 개요</a></li>
                <li><a href="#age-analysis">2. 연령별 가입 구조</a></li>
                <li><a href="#region-analysis">3. 지역별 일자리 분포</a></li>
                <li><a href="#comparison">4. 고용 안정성 비교</a></li>
            </ul>
        </div>
        <div class="sidebar-footer">
            <p>Data Source: 국민연금공단 (2024.12.31)</p>
            <p>Generated by: Python & Plotly</p>
        </div>
    </nav>

    <!-- Main Content -->
    <main class="main-content">
        <div class="container">
            
            <header>
                <h1 class="title">국민연금 시군구별 청년계층 가입자 현황 분석</h1>
                <p class="subtitle" style="color: #666; font-size: 1.1rem;">2024년 12월 말 기준 데이터 분석 보고서</p>
            </header>

            <section id="overview">
                <h2>1. 개요</h2>
                <div class="callout">
                    <strong>분석 목적:</strong> 본 보고서는 국민연금공단의 시군구별 청년계층 가입자 현황 데이터를 바탕으로, 연령별 가입 유형, 지역별 사업장 가입자 분포, 그리고 고용 형태별(직장인 vs 프리랜서/자영업) 상관관계를 시각화하여 분석합니다.
                </div>
                <p>
                    이 보고서는 <strong>Quarto</strong> 스타일을 지향하는 자동 생성된 HTML 문서입니다.
                    주요 분석 내용은 다음과 같습니다:
                </p>
                <ul>
                    <li>연령대에 따른 가입 유형(사업장, 지역, 임의 등)의 비중 변화</li>
                    <li>전국 시군구별 청년 일자리(사업장 가입자)의 수도권 집중도</li>
                    <li>시도별 직장 가입자와 지역 가입자 간의 규모 비교</li>
                </ul>
            </section>

            <section id="age-analysis">
                <h2>2. 연령별 가입 구조 (Sunburst Chart)</h2>
                <p>
                    연령대별로 국민연금 가입 유형이 어떻게 다른지 계층적으로 시각화하였습니다. 
                    중앙에서 바깥쪽으로 나갈수록 세부적인 분류를 보여줍니다.
                </p>
                <div class="chart-container">
                    {div_age}
                </div>
                <p>
                    * 차트의 섹션을 클릭하면 해당 카테고리를 확대해서 볼 수 있습니다.
                </p>
            </section>

            <section id="region-analysis">
                <h2>3. 지역별 일자리 분포 (Treemap)</h2>
                <p>
                    사업장 가입자 수(직장인)의 규모를 사각형의 크기로 표현했습니다. 
                    서울 및 수도권 지역의 사각형 크기를 통해 일자리 집중 현상을 직관적으로 확인할 수 있습니다.
                </p>
                <div class="chart-container">
                    {div_region}
                </div>
            </section>

            <section id="comparison">
                <h2>4. 고용 안정성 및 규모 비교 (Bubble Chart)</h2>
                <p>
                    각 시도의 <strong>지역가입자(X축)</strong>와 <strong>사업장가입자(Y축)</strong> 수를 비교합니다.
                    원의 크기는 사업장 가입자(직장인)의 규모를 나타냅니다.
                </p>
                <div class="chart-container">
                    {div_compare}
                </div>
                <p>
                    대각선 위쪽에 위치할수록 자영업/프리랜서 대비 직장 가입자 비율이 높은 지역으로, 상대적으로 고용 안정성이 높다고 해석할 수 있습니다.
                </p>
            </section>

            <footer style="margin-top: 4rem; border-top: 1px solid #eee; padding-top: 1rem; color: #888; text-align: center;">
                &copy; 2024 Analysis Report. Generated automatically.
            </footer>
        </div>
    </main>

</body>
</html>
"""

OUTPUT_FILE = 'national_pension_analysis_report.html'
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write(html_template)

print(f"Successfully generated report: {OUTPUT_FILE}")

✨ AdSpark



AdSpark is an agentic AI ad studio that turns a structured product brief into downloadable, platform-ready campaign banners.



It uses a Copywriter, Critic, and Composer workflow to generate taglines, validate copy against quality and safety rules, and create category-aware ad visuals such as food packaging and fitness-watch creatives.



What it does



\- Collects structured campaign inputs including product, category, USP, audience, tone, format, and CTA

\- Generates multiple tagline candidates through a Copywriter agent

\- Scores taglines using a Critic agent for length, USP relevance, requested-theme fit, brand safety, and readability

\- Uses a conditional rewrite loop when copy fails quality checks

\- Uses a banner-safe fallback when generated copy still fails hard validation gates

\- Creates category-aware visuals with Pillow

\- Produces downloadable campaign banner variants

\- Shows an agent trace panel for transparent workflow debugging



Workflow



Structured Brief



Copywriter Agent



Critic Agent and Quality Gates



Rewrite Loop or Safe Fallback



Composer Agent



Downloadable Campaign Variants



Tech Stack



\- Python

\- Streamlit

\- Pydantic

\- Pillow

\- Multi-agent workflow

\- Rule-based quality scoring

\- Category-aware banner composition



How to run locally



Clone the repository



git clone https://github.com/YOUR\_USERNAME/adspark-agentic-ad-studio.git



cd adspark-agentic-ad-studio



Create a virtual environment



python -m venv .venv



Activate the environment on Windows


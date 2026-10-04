from pathlib import Path
import sys

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from agents.composer import compose_banner_variants
from agents.workflow import run_copywriter_critic_loop
from schemas import (
    AdBrief,
    AdFormat,
    CTA,
    Category,
    ColorMood,
    TaglineLength,
    TextPosition,
    Tone,
    VisualStyle,
)


st.set_page_config(
    page_title="AdSpark",
    page_icon="✨",
    layout="wide",
)


st.markdown(
    """
    <style>
        .stApp {
            background:
                radial-gradient(
                    circle at 10% 0%,
                    rgba(255, 111, 32, 0.13),
                    transparent 28%
                ),
                radial-gradient(
                    circle at 90% 15%,
                    rgba(255, 180, 110, 0.08),
                    transparent 25%
                ),
                #0C0F16;
        }

        .block-container {
            max-width: 1220px;
            padding-top: 2.5rem;
            padding-bottom: 3rem;
        }

        .adspark-hero {
            border: 1px solid rgba(255, 156, 82, 0.20);
            border-radius: 22px;
            padding: 28px 30px;
            margin-bottom: 24px;
            background: linear-gradient(
                135deg,
                rgba(255, 107, 31, 0.18),
                rgba(29, 17, 10, 0.45)
            );
        }

        .adspark-kicker,
        .section-label {
            color: #FFB26B;
            font-weight: 700;
            letter-spacing: 0.11em;
            font-size: 0.76rem;
            text-transform: uppercase;
        }

        .section-label {
            margin-bottom: 0.25rem;
        }

        .adspark-hero h1 {
            font-size: 2.55rem;
            margin: 0.25rem 0 0.45rem 0;
            line-height: 1.05;
        }

        .adspark-hero p {
            color: #C7CBD6;
            font-size: 1rem;
            margin-bottom: 0;
        }

        .success-copy {
            color: #A5F3C4;
            background: rgba(20, 83, 45, 0.30);
            border: 1px solid rgba(74, 222, 128, 0.22);
            border-radius: 12px;
            padding: 13px;
            font-size: 1.05rem;
            font-weight: 700;
        }

        div[data-testid="stForm"] {
            background: rgba(255, 255, 255, 0.025);
            border: 1px solid rgba(255, 255, 255, 0.09);
            border-radius: 18px;
            padding: 20px 22px 8px 22px;
        }

        div[data-testid="stDownloadButton"] button,
        div[data-testid="stFormSubmitButton"] button {
            border-radius: 10px;
            font-weight: 700;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def split_csv(value: str) -> list[str]:
    return [
        item.strip()
        for item in value.split(",")
        if item.strip()
    ]


def load_fitfuel_example() -> None:
    """
    Fill Streamlit session state with a stable demo campaign brief.
    """

    example_values = {
        "product_name": "FitFuel Protein Bar",
        "category": "Food",
        "product_description": "High-protein snack with no added sugar",
        "usp": "20g protein, zero sugar",
        "audience": "Gym-goers and busy professionals aged 18–25",
        "objective": "Product launch",
        "cta": "Buy now",
        "tone": "Witty",
        "visual_style": "Photorealistic",
        "color_mood": "Warm",
        "brand_hex": "#F97316",
        "tagline_length": "Short (3–5 words)",
        "text_position": "Top",
        "num_variants": 3,
        "include_words_text": "fuel, protein",
        "avoid_words_text": "guilt, cheat",
    }

    for key, value in example_values.items():
        st.session_state[key] = value


def initialize_state() -> None:
    """
    Create persistent state keys once per Streamlit browser session.
    """

    if "result" not in st.session_state:
        st.session_state.result = None

    if "submitted_brief" not in st.session_state:
        st.session_state.submitted_brief = None


def show_validation_error(error: Exception) -> None:
    """
    Convert Pydantic's detailed error string into a user-friendly message.
    """

    error_text = str(error)

    if "product_name" in error_text and "usp" in error_text:
        st.error(
            "Please enter a product name and a key selling point "
            "(USP) before generating your banner."
        )
    elif "product_name" in error_text:
        st.error(
            "Please enter a product or brand name "
            "(at least 2 characters)."
        )
    elif "usp" in error_text:
        st.error(
            "Please enter a key selling point / USP "
            "(at least 4 characters)."
        )
    else:
        st.error(f"Please fix the brief: {error}")


initialize_state()


st.markdown(
    """
    <div class="adspark-hero">
        <div class="adspark-kicker">Agentic creative studio</div>
        <h1>✨ AdSpark</h1>
        <p>
            Turn a structured product brief into a campaign-ready banner.
            Copywriter, Critic, and Composer agents collaborate so your
            copy is concise, brand-safe, and ready for visual QA.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


top_left, top_right = st.columns([3, 1])

with top_left:
    st.markdown(
        "Create a brief, generate brand-safe copy, then export "
        "platform-ready visual variants."
    )

with top_right:
    st.button(
        "Auto-fill demo",
        on_click=load_fitfuel_example,
        use_container_width=True,
    )


with st.form("adspark_brief_form"):
    st.subheader("Product")

    product_col, category_col = st.columns(2)

    with product_col:
        product_name = st.text_input(
            "Product / brand name *",
            placeholder="FitFuel Protein Bar",
            key="product_name",
        )

    with category_col:
        category = st.selectbox(
            "Industry / category *",
            options=[item.value for item in Category],
            key="category",
        )

    product_description = st.text_area(
        "Product description",
        max_chars=200,
        placeholder="High-protein snack with no added sugar",
        key="product_description",
    )

    usp = st.text_input(
        "Key selling point (USP) *",
        placeholder="20g protein, zero sugar",
        key="usp",
    )

    st.subheader("Audience and campaign")

    audience_col, objective_col, cta_col = st.columns(3)

    with audience_col:
        audience = st.text_input(
            "Target audience",
            placeholder="Gym-goers and busy professionals aged 18–25",
            key="audience",
        )

    with objective_col:
        objective = st.selectbox(
            "Campaign objective",
            options=[
                "Brand awareness",
                "Product launch",
                "Sales / discount",
                "Event promotion",
                "App download",
            ],
            key="objective",
        )

    with cta_col:
        cta = st.selectbox(
            "Call to action",
            options=[item.value for item in CTA],
            key="cta",
        )

    st.subheader("Tone and visual direction")

    tone_col, style_col, color_col = st.columns(3)

    with tone_col:
        tone = st.selectbox(
            "Tone of tagline *",
            options=[item.value for item in Tone],
            key="tone",
        )

    with style_col:
        visual_style = st.selectbox(
            "Visual style",
            options=[item.value for item in VisualStyle],
            key="visual_style",
        )

    with color_col:
        color_mood = st.selectbox(
            "Color mood",
            options=[item.value for item in ColorMood],
            key="color_mood",
        )

    brand_hex = st.color_picker(
        "Brand accent color",
        value="#F97316",
        key="brand_hex",
    )

    st.subheader("Format and output")

    format_col, length_col, position_col, variants_col = st.columns(4)

    with format_col:
        ad_format = st.selectbox(
            "Ad format *",
            options=[item.value for item in AdFormat],
            key="ad_format",
        )

    with length_col:
        tagline_length = st.selectbox(
            "Tagline length",
            options=[item.value for item in TaglineLength],
            key="tagline_length",
        )

    with position_col:
        text_position = st.selectbox(
            "Text position",
            options=[item.value for item in TextPosition],
            key="text_position",
        )

    with variants_col:
        num_variants = st.selectbox(
            "Number of variants",
            options=[1, 3, 5],
            key="num_variants",
        )

    with st.expander("Advanced options"):
        advanced_left, advanced_right = st.columns(2)

        with advanced_left:
            include_words_text = st.text_input(
                "Words or themes to include",
                placeholder="fuel, protein",
                key="include_words_text",
            )

        with advanced_right:
            avoid_words_text = st.text_input(
                "Words or themes to avoid",
                placeholder="guilt, cheat",
                key="avoid_words_text",
            )

    submitted = st.form_submit_button(
        "Generate campaign variants",
        type="primary",
        use_container_width=True,
    )


if submitted:
    try:
        brief = AdBrief(
            product_name=product_name,
            category=category,
            usp=usp,
            tone=tone,
            ad_format=ad_format,
            product_description=product_description,
            audience=audience or "General audience",
            objective=objective,
            cta=cta,
            visual_style=visual_style,
            color_mood=color_mood,
            brand_hex=brand_hex,
            tagline_length=tagline_length,
            text_position=text_position,
            num_variants=num_variants,
            include_words=split_csv(include_words_text),
            avoid_words=split_csv(avoid_words_text),
        )

        with st.spinner(
            "Copywriter, Critic, and Composer agents are working..."
        ):
            workflow_result = run_copywriter_critic_loop(brief)

            banner_variants = compose_banner_variants(
                brief=brief,
                tagline=workflow_result["final_tagline"],
            )

        st.session_state.result = {
            "workflow": workflow_result,
            "banners": banner_variants,
        }

        st.session_state.submitted_brief = brief

    except Exception as error:
        show_validation_error(error)


if st.session_state.result:
    result = st.session_state.result

    # Remove results created by the older one-banner implementation.
    if "banners" not in result:
        st.session_state.result = None
        st.rerun()

    workflow = result["workflow"]
    banners = result["banners"]

    st.divider()

    st.markdown(
        '<div class="section-label">Generated campaign</div>',
        unsafe_allow_html=True,
    )

    st.subheader("Your Critic-approved creative variants")

    st.markdown(
        f'<div class="success-copy">“{workflow["final_tagline"]}”</div>',
        unsafe_allow_html=True,
    )

    st.write("")

    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

    with metric_col1:
        st.metric(
            "Critic score",
            f'{workflow["final_score"]}/100',
        )

    with metric_col2:
        st.metric(
            "Rewrite attempts",
            workflow["rewrite_attempts"],
        )

    with metric_col3:
        st.metric(
            "Fallback used",
            "Yes" if workflow["used_fallback"] else "No",
        )

    with metric_col4:
        st.metric(
            "Variants",
            len(banners),
        )

    st.write("")
    st.markdown("### Campaign previews")
    st.caption(
        "Visual mockups are optimized for food and fitness demos. "
        "Category-specific product rendering is being expanded."
    )

    gallery_columns = st.columns(min(3, len(banners)))

    for index, banner in enumerate(banners):
        column = gallery_columns[index % len(gallery_columns)]

        with column:
            st.image(
                banner["output_path"],
                caption=(
                    f"Variant {banner['variant_number']} · "
                    f"{banner['variant_color_mood']} · "
                    f"{banner['variant_position']}"
                ),
                use_container_width=True,
            )

            with open(banner["output_path"], "rb") as image_file:
                image_bytes = image_file.read()

            st.download_button(
                label=f"Download variant {banner['variant_number']}",
                data=image_bytes,
                file_name=Path(banner["output_path"]).name,
                mime="image/png",
                key=f"download_variant_{banner['variant_number']}",
                use_container_width=True,
            )

    st.write("")

    with st.expander("Agent trace"):
        for index, step in enumerate(workflow["trace"], start=1):
            st.markdown(
                f"**{index}. {step['agent']} → {step['action']}**"
            )
            st.json(step["details"])

    with st.expander("Structured brief"):
        st.json(
            st.session_state.submitted_brief.model_dump(
                mode="json"
            )
        )
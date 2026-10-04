from enum import Enum
from typing import List, Optional, Tuple

from pydantic import BaseModel, Field, field_validator


class Category(str, Enum):
    FOOD = "Food"
    FITNESS = "Fitness"
    FINTECH = "Fintech"
    FASHION = "Fashion"
    TRAVEL = "Travel"
    TECH = "Tech"
    EDUCATION = "Education"
    REAL_ESTATE = "Real estate"
    HEALTH = "Health"
    AUTOMOTIVE = "Automotive"
    OTHER = "Other"


class Tone(str, Enum):
    WITTY = "Witty"
    LUXURY = "Luxury"
    URGENT = "Urgent"
    EMOTIONAL = "Emotional"
    PLAYFUL = "Playful"
    MINIMAL = "Minimal"
    BOLD = "Bold"
    INSPIRATIONAL = "Inspirational"


class VisualStyle(str, Enum):
    PHOTOREALISTIC = "Photorealistic"
    FLAT_ILLUSTRATION = "Flat illustration"
    RENDER_3D = "3D render"
    MINIMALIST = "Minimalist"
    VINTAGE = "Vintage"
    NEON_CYBERPUNK = "Neon / cyberpunk"
    WATERCOLOR = "Watercolor"


class ColorMood(str, Enum):
    WARM = "Warm"
    COOL = "Cool"
    PASTEL = "Pastel"
    DARK = "Dark"
    BRAND_COLOR = "Brand color"


class AdFormat(str, Enum):
    INSTAGRAM_POST = "Instagram post (1080×1080)"
    INSTAGRAM_STORY = "Story (1080×1920)"
    WEB_BANNER = "Web banner (1200×628)"
    POSTER_A3 = "Poster (A3 portrait)"
    BILLBOARD = "Billboard (wide)"


FORMAT_CONFIG = {
    AdFormat.INSTAGRAM_POST: {
        "key": "instagram_square",
        "width": 1080,
        "height": 1080,
    },
    AdFormat.INSTAGRAM_STORY: {
        "key": "instagram_story",
        "width": 1080,
        "height": 1920,
    },
    AdFormat.WEB_BANNER: {
        "key": "web_banner",
        "width": 1200,
        "height": 628,
    },
    AdFormat.POSTER_A3: {
        "key": "poster_a3_portrait",
        "width": 2480,
        "height": 3508,
    },
    AdFormat.BILLBOARD: {
        "key": "billboard_wide",
        "width": 1920,
        "height": 640,
    },
}


class TaglineLength(str, Enum):
    SHORT = "Short (3–5 words)"
    MEDIUM = "Medium (6–8 words)"
    LONG = "Long (7–10 words)"


TAGLINE_WORD_LIMITS = {
    TaglineLength.SHORT: (3, 5),
    TaglineLength.MEDIUM: (6, 8),
    TaglineLength.LONG: (7, 10),
}


class TextPosition(str, Enum):
    AUTO = "Auto"
    TOP = "Top"
    CENTER = "Center"
    BOTTOM = "Bottom"


class CTA(str, Enum):
    BUY_NOW = "Buy now"
    LEARN_MORE = "Learn more"
    SIGN_UP = "Sign up"
    VISIT_US = "Visit us"
    DOWNLOAD = "Download"
    NONE = "None"


class AdBrief(BaseModel):
    product_name: str = Field(..., min_length=2, max_length=80)
    category: Category
    usp: str = Field(..., min_length=4, max_length=150)
    tone: Tone
    ad_format: AdFormat

    product_description: str = Field(default="", max_length=200)
    audience: str = Field(default="General audience", max_length=150)
    objective: str = Field(default="Brand awareness", max_length=80)
    cta: CTA = CTA.NONE

    visual_style: VisualStyle = VisualStyle.PHOTOREALISTIC
    color_mood: ColorMood = ColorMood.BRAND_COLOR
    brand_hex: Optional[str] = Field(
        default=None,
        pattern=r"^#[0-9A-Fa-f]{6}$",
    )

    tagline_length: TaglineLength = TaglineLength.SHORT
    text_position: TextPosition = TextPosition.AUTO
    num_variants: int = Field(default=3, ge=1, le=5)
    language: str = Field(default="English", min_length=2, max_length=30)

    include_words: List[str] = Field(default_factory=list)
    avoid_words: List[str] = Field(default_factory=list)

    @field_validator(
        "product_name",
        "usp",
        "product_description",
        "audience",
        "objective",
        mode="before",
    )
    @classmethod
    def clean_text(cls, value):
        if value is None:
            return ""
        return " ".join(value.strip().split())

    @field_validator("include_words", "avoid_words")
    @classmethod
    def clean_lists(cls, values):
        cleaned = []

        for item in values:
            item = item.strip()

            if item and item.lower() not in {
                existing.lower() for existing in cleaned
            }:
                cleaned.append(item)

        return cleaned

    @property
    def dimensions(self) -> Tuple[int, int]:
        config = FORMAT_CONFIG[self.ad_format]
        return config["width"], config["height"]

    @property
    def format_key(self) -> str:
        return FORMAT_CONFIG[self.ad_format]["key"]

    @property
    def tagline_word_range(self) -> Tuple[int, int]:
        return TAGLINE_WORD_LIMITS[self.tagline_length]
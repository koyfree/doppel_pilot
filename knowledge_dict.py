import pandas as pd
from summarize_personality import summarize_personality

# 각 facet별 문항번호 (R: reverse)
facet_items = {
    "Extraversion": ["Big5_1R", "Big5_6", "Big5_11", "Big5_16", "Big5_21R", "Big5_26R"],
    "Sociability": ["Big5_1R", "Big5_16"],
    "Assertiveness": ["Big5_6", "Big5_21R"],
    "Energy Level": ["Big5_11", "Big5_26R"],
    "Agreeableness": ["Big5_2", "Big5_7R", "Big5_12", "Big5_17R", "Big5_22", "Big5_27R"],
    "Compassion": ["Big5_2", "Big5_17R"],
    "Respectfulness": ["Big5_7R", "Big5_22"],
    "Trust": ["Big5_12", "Big5_27R"],
    "Conscientiousness": ["Big5_3R", "Big5_8R", "Big5_13", "Big5_18", "Big5_23", "Big5_28R"],
    "Organization": ["Big5_3R", "Big5_18"],
    "Productiveness": ["Big5_8R", "Big5_23"],
    "Responsibility": ["Big5_13", "Big5_28R"],
    "Negative Emotionality": ["Big5_4", "Big5_9", "Big5_14R", "Big5_19R", "Big5_24R", "Big5_29"],
    "Anxiety": ["Big5_4", "Big5_19R"],
    "Depression": ["Big5_9", "Big5_24R"],
    "Emotional Volatility": ["Big5_14R", "Big5_29"],
    "Open-Mindedness": ["Big5_5", "Big5_10R", "Big5_15", "Big5_20R", "Big5_25", "Big5_30R"],
    "Aesthetic Sensitivity": ["Big5_5", "Big5_20R"],
    "Intellectual Curiosity": ["Big5_10R", "Big5_25"],
    "Creative Imagination": ["Big5_15", "Big5_30R"]
}

# facet → 긍정/부정 label
facet_labels = {
    "Extraversion": ("extroverted", "introverted"),
    "Sociability": ("sociable", "unsociable"),
    "Assertiveness": ("assertive", "passive"),
    "Energy Level": ("energetic", "low-energy"),
    "Agreeableness": ("agreeable", "uncooperative"),
    "Compassion": ("compassionate", "indifferent"),
    "Respectfulness": ("respectful", "disrespectful"),
    "Trust": ("trusting", "suspicious"),
    "Conscientiousness": ("conscientious", "careless"),
    "Organization": ("organized", "disorganized"),
    "Productiveness": ("productive", "unproductive"),
    "Responsibility": ("responsible", "irresponsible"),
    "Negative Emotionality": ("emotionally unstable", "emotionally stable"),
    "Anxiety": ("anxious", "calm"),
    "Depression": ("downcast", "upbeat"),
    "Emotional Volatility": ("emotionally reactive", "emotionally steady"),
    "Open-Mindedness": ("open-minded", "closed-minded"),
    "Aesthetic Sensitivity": ("aesthetically aware", "indifferent to beauty"),
    "Intellectual Curiosity": ("intellectually curious", "uninterested in ideas"),
    "Creative Imagination": ("imaginative", "unimaginative")
}

response_map = {
    "Strongly disagree": 1,
    "Disagree": 2,
    "Somewhat disagree": 3,
    "Neutral": 4,
    "Somewhat agree": 5,
    "Agree": 6,
    "Strongly agree": 7
}

def is_reverse(item):
    return item.endswith("R")

def reverse(score):
    return 8 - score  # 7점 척도 기준 (1↔7)

def verbalize(score, pos_label, neg_label):
    if score >= 6.5:
        return f"extremely {pos_label}"
    elif score >= 6.0:
        return f"very {pos_label}"
    elif score >= 5.5:
        return f"moderately {pos_label}"
    elif score >= 4.5:
        return f"slightly {pos_label}"
    elif score >= 3.5:
        return "neutral"
    elif score >= 2.5:
        return f"slightly un{pos_label}" if " " not in pos_label else f"slightly {neg_label}"
    elif score >= 2.0:
        return f"moderately un{pos_label}" if " " not in pos_label else f"moderately {neg_label}"
    elif score >= 1.5:
        return f"very un{pos_label}" if " " not in pos_label else f"very {neg_label}"
    else:
        return f"extremely un{pos_label}" if " " not in pos_label else f"extremely {neg_label}"

def build_knowledge_dict(sheet_url: str, openai_api_key: str) -> dict:
    if "edit" in sheet_url:
        sheet_url = sheet_url.replace("/edit?", "/export?format=csv&")

    df = pd.read_csv(sheet_url)
    knowledge = {}

    for _, row in df.iterrows():
        name = row['NAME']

        # personality 문장 모으기
        personality_lines = []
        for facet, items in facet_items.items():
            scores = []
            for item in items:
                col = item.replace("R", "")
                response = str(row[col]).strip()
                val = response_map.get(response, 4)
                if is_reverse(item):
                    val = reverse(val)
                scores.append(val)
            avg = sum(scores) / len(scores)
            pos_label, neg_label = facet_labels[facet]
            label = verbalize(avg, pos_label, neg_label)
            personality_lines.append(f"For {facet} facet, {label}.")

        personality_text = "\n".join(personality_lines)

        # GPT 요약 추가
        from summarize_personality import summarize_personality
        summary_text = summarize_personality(personality_text, openai_api_key)

        # 전체 profile 구성
        knowledge[name] = f"""
Profile:
[Demographics]
\t•\tAge: {row['AGE']}
\t•\tSex: {row['SEX']}
\t•\tOccupation: {row['JOB']}
\t•\tLiving Style: {row['LIVING']}

[Personality]
{summary_text}

[Top 5 Things this character loves and hates]
\t•\tWhat this character love: {row['top5_love']}
\t•\tWhat this character hate: {row['top5_hate']}

[Weekly Activities Overview]
\t•\t{row['weekly_activities']}
""".strip()
    st.write("📌 전체 열 이름:", df.columns.tolist())
    return knowledge

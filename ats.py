import re
from typing import Dict, Any, List

CONTACT_EMAIL_REGEX = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
CONTACT_PHONE_REGEX = re.compile(r'(\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}')
CONTACT_LINKEDIN_REGEX = re.compile(r'linkedin\.com/in/[\w-]+|linkedin\.com/[\w-]+|linkedin', re.IGNORECASE)

STANDARD_SECTIONS = {
    "Summary": [r'\b(summary|professional summary|executive summary|objective|about me|profile)\b'],
    "Skills": [r'\b(skills|technical skills|core competencies|technologies|proficiencies)\b'],
    "Experience": [r'\b(experience|work experience|employment history|work history|professional experience)\b'],
    "Education": [r'\b(education|academic background|qualifications|academic history)\b'],
    "Projects": [r'\b(projects|key projects|personal projects|technical projects)\b']
}

COMMON_TECH_KEYWORDS = [
    "python", "javascript", "typescript", "java", "c++", "c#", "html", "css", "react", "vue",
    "angular", "node", "nodejs", "fastapi", "django", "flask", "sql", "postgresql", "mysql",
    "mongodb", "nosql", "redis", "docker", "kubernetes", "aws", "azure", "gcp", "git", "github",
    "ci/cd", "rest", "api", "graphql", "linux", "agile", "scrum", "machine learning", "deep learning",
    "nlp", "data analysis", "pandas", "numpy", "tensorflow", "pytorch", "microservices", "devops",
    "system design", "testing", "pytest", "unit test", "cybersecurity", "cloud", "ui/ux", "figma"
]

ACTION_VERBS = {
    "developed", "built", "designed", "implemented", "created", "managed", "led", "architected",
    "optimized", "spearheaded", "automated", "reduced", "increased", "delivered", "coordinated",
    "launched", "established", "engineered", "executed", "collaborated", "formulated", "revamped",
    "orchestrated", "streamlined", "deployed", "scaled", "improved", "transformed", "pioneered"
}

def calculate_ats_score(text: str) -> Dict[str, Any]:
    text_clean = text.strip()
    words = re.findall(r'\b[A-Za-z0-9+#.-]+\b', text_clean)
    word_count = len(words)
    lines = [line.strip() for line in text_clean.splitlines() if line.strip()]

    breakdown = {}
    weak_points: List[str] = []
    strong_points: List[str] = []

    # 1. Contact info present (15 points: email 5, phone 5, LinkedIn 5)
    contact_pts = 0
    has_email = bool(CONTACT_EMAIL_REGEX.search(text_clean))
    has_phone = bool(CONTACT_PHONE_REGEX.search(text_clean))
    has_linkedin = bool(CONTACT_LINKEDIN_REGEX.search(text_clean))

    if has_email:
        contact_pts += 5
    else:
        weak_points.append("Missing email address")

    if has_phone:
        contact_pts += 5
    else:
        weak_points.append("Missing telephone / mobile number")

    if has_linkedin:
        contact_pts += 5
    else:
        weak_points.append("Missing LinkedIn profile link")

    if contact_pts == 15:
        strong_points.append("Comprehensive contact information (Email, Phone, LinkedIn)")
    breakdown["contact_info"] = contact_pts

    # 2. Standard sections found (Summary, Skills, Experience, Education, Projects: 25 points, 5 each)
    section_pts = 0
    found_sections = []
    missing_sections = []

    lower_text = text_clean.lower()
    for sec_name, patterns in STANDARD_SECTIONS.items():
        found = any(re.search(pat, lower_text) for pat in patterns)
        if found:
            section_pts += 5
            found_sections.append(sec_name)
        else:
            missing_sections.append(sec_name)

    if missing_sections:
        weak_points.append(f"Missing essential resume sections: {', '.join(missing_sections)}")
    if section_pts >= 20:
        strong_points.append("Standard, recruiter-friendly section structure")
    breakdown["standard_sections"] = section_pts

    # 3. Skills/keyword density (20 points)
    found_keywords = set()
    for kw in COMMON_TECH_KEYWORDS:
        if re.search(r'\b' + re.escape(kw) + r'\b', lower_text):
            found_keywords.add(kw)

    kw_count = len(found_keywords)
    if kw_count >= 10:
        skills_pts = 20
        strong_points.append(f"High technical keyword density ({kw_count}+ keywords matched)")
    elif kw_count >= 7:
        skills_pts = 15
        strong_points.append(f"Good keyword density ({kw_count} keywords matched)")
    elif kw_count >= 4:
        skills_pts = 10
        weak_points.append("Moderate skill keyword density; consider adding more role-relevant tools")
    elif kw_count >= 1:
        skills_pts = 5
        weak_points.append("Low keyword density; very few industry technologies identified")
    else:
        skills_pts = 0
        weak_points.append("Critical lack of recognizable technical or industry keywords")
    breakdown["skills_density"] = skills_pts

    # 4. Quantified achievements (15 points: metrics, %, numbers in bullets)
    metric_matches = re.findall(
        r'(\b\d+%|\$\d+[\d,]*|\b\d+[kKmMbB]\b|\b\d+\+\b|\b(?:increased|decreased|reduced|saved|improved|boosted|grew|cut)\b[^.\n]*\b\d+|\b\d+\s*(?:users|clients|customers|requests|downloads|engineers|hours|days|x|percent)\b)',
        text_clean,
        re.IGNORECASE
    )
    metric_count = len(metric_matches)
    if metric_count >= 4:
        quant_pts = 15
        strong_points.append("High volume of quantified metrics and measurable achievements")
    elif metric_count >= 2:
        quant_pts = 10
        strong_points.append("Includes measurable impact and numerical results")
    elif metric_count >= 1:
        quant_pts = 5
        weak_points.append("Only minimal quantified metrics found; quantify more bullet points with numbers and percentages")
    else:
        quant_pts = 0
        weak_points.append("No quantified impact found (missing percentages, metrics, or dollar values)")
    breakdown["quantified_achievements"] = quant_pts

    # 5. Action verbs at bullet starts (10 points)
    action_verb_count = 0
    for line in lines:
        cleaned_line = re.sub(r'^[•\-\*▪–—\d\.\)\s]+', '', line).strip()
        first_word = cleaned_line.split()[0].lower() if cleaned_line.split() else ""
        if first_word in ACTION_VERBS:
            action_verb_count += 1

    if action_verb_count >= 5:
        verb_pts = 10
        strong_points.append("Strong usage of active power verbs to lead bullet points")
    elif action_verb_count >= 3:
        verb_pts = 7
    elif action_verb_count >= 1:
        verb_pts = 4
        weak_points.append("Few bullet points begin with strong active verbs")
    else:
        verb_pts = 0
        weak_points.append("No action verbs detected at start of accomplishment bullets")
    breakdown["action_verbs"] = verb_pts

    # 6. Length sanity (300-900 words) and bullet formatting (10 points)
    length_pts = 0
    if 300 <= word_count <= 900:
        length_pts += 6
        strong_points.append(f"Ideal concise resume length ({word_count} words)")
    elif 200 <= word_count < 300 or 901 <= word_count <= 1300:
        length_pts += 3
        weak_points.append(f"Resume length ({word_count} words) is slightly outside the recommended 300-900 word range")
    else:
        weak_points.append(f"Suboptimal word count ({word_count} words); aim for 300-900 words")

    bullet_count = sum(1 for line in lines if re.match(r'^[•\-\*▪–—]|\d+\.\s', line.strip()))
    if bullet_count >= 5:
        length_pts += 4
        strong_points.append("Well-formatted bullet points for readability")
    elif bullet_count >= 2:
        length_pts += 2
    else:
        weak_points.append("Insufficient bullet points; avoid large blocks of unformatted text")
    breakdown["length_and_formatting"] = length_pts

    # 7. No obvious problems (tables-only, huge paragraphs, empty text: 5 points)
    problem_pts = 5
    if word_count < 80:
        problem_pts = 0
        weak_points.append("Extremely sparse text content")
    else:
        # Check for very long single paragraph (>250 words)
        paragraphs = text_clean.split("\n\n")
        has_monolith = any(len(p.split()) > 250 for p in paragraphs)
        if has_monolith:
            problem_pts = 2
            weak_points.append("Contains monolithic paragraph blocks exceeding 250 words")
    breakdown["structure_integrity"] = problem_pts

    total_score = sum(breakdown.values())
    total_score = max(0, min(100, total_score))

    return {
        "score": total_score,
        "breakdown": breakdown,
        "weak_points": weak_points,
        "strong_points": strong_points,
        "word_count": word_count
    }

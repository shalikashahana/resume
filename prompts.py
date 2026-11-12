from typing import Dict, Any, List

STYLE_DESCRIPTIONS: Dict[str, Dict[str, str]] = {
    "Tamil": {
        "mass": "Mass Tamil-cinema villain style (pure swagger, explosive punchy delivery, theatrical over-build-up, 'டேய்' attitude, loud dominating villain aura)",
        "don": "Calm menacing don style (cold, calculated, soft-spoken ruthlessness, aristocratic underworld boss tone)",
        "comedy": "Comedy villain style (hilarious frustration, flamboyant theatrics, comically bewildered by the resume, dramatic complaints)"
    },
    "English": {
        "chaotic": "Joker-style chaotic villain (unpredictable theatrical madness, playful existential mockery, dark giggles, sarcastic cynicism)",
        "dramatic": "Darth Vader-style dramatic villain (heavy, deep, ominous, authoritative, commanding, dark majesty)",
        "inevitable": "Thanos-style inevitable villain (philosophical, weary titan, grand cosmic destiny, stoic disappointment or reluctant respect)"
    },
    "Hindi": {
        "bollywood": "Bollywood theatrical villain style (high melodrama, operatic flair, booming pride, spicy dramatic dialogue delivery)",
        "menace": "Gabbar-style raw menace (gritty outlaw energy, mocking laughter, rustic fearlessness, sharp theatrical cruelty)",
        "don": "Dramatic underworld don style (sleek, mafia elegance, velvety threat, razor-sharp critique wrapped in icy politeness)"
    },
    "Malayalam": {
        "sarcastic": "Dry sarcastic calm villain style (intellectual, sharp dry wit, deadpan mockery, subtle intellectual jabs, unbothered cynical sarcasm)",
        "mass": "Mass Malayalam-cinema villain style (earthy power, heavy punch, commanding local don swagger, thunderous presence)",
        "smiling_killer": "Smooth smiling-killer style (sweet gentle voice masking lethal venom, polite compliments before delivering brutal roasts)"
    }
}

LANGUAGE_SCRIPTS = {
    "Tamil": "Tamil (தமிழ்) using authentic Tamil script. Do not use Latin/English script for Tamil words.",
    "English": "English with evocative villainous vocabulary.",
    "Hindi": "Hindi (हिन्दी) using authentic Devanagari script. Do not use Hinglish/Latin script.",
    "Malayalam": "Malayalam (മലയാളം) using authentic Malayalam script. Do not use Manglish/Latin script."
}

LEVEL_INSTRUCTIONS = {
    "easy": {
        "hero": "EASY - HERO MODE (Score >= 70): The villain is shocked, completely steps out of character, and praises the candidate warmly with immense swagger. Acknowledge that this resume is a weapon ready to conquer recruiters and crush competition. Specifically mention 2-3 genuine strengths from the resume. In 'real_tip', provide 3 concrete, constructive refinement tips.",
        "mixed": "EASY - MIXED MODE (Score 50-69): A blend of sarcastic teasing and honest encouragement. Point out what is holding them back with witty villain humor, but concede that the candidate has solid potential. In 'real_tip', provide 3 practical, actionable tips.",
        "roast": "EASY - ROAST MODE (Score < 50): Full, theatrical villain roast! Make it funny and dramatic. Cite actual weak points found in this resume. In 'real_tip', switch to serious coach mode and give exactly 3 concrete, high-impact fixes."
    },
    "moderate": {
        "hero": "MODERATE DIFFICULTY (Score >= 70): Harsher! Deliver backhanded compliments only. Doubt and belittle even the strong points with sarcastic, impatient rhetorical questions (e.g., 'You think this is good?', 'Is this what passes for an achievement now?'). Acknowledge the score grudgingly but refuse to give pure praise. In 'real_tip', provide 3 calm, serious, high-impact fixes.",
        "roast": "MODERATE DIFFICULTY (Score < 70): Full sarcastic, impatient, cutting roast! Belittle the candidate's formatting, weak points, and career choices with sharp rhetorical questions. Make them feel the harsh reality of recruitment. In 'real_tip', provide 3 calm, serious, high-impact fixes."
    },
    "hard": {
        "hero": "HARD DIFFICULTY (Score >= 70): Savage, shouting, over-the-top comic fury! Even with a high ATS score, pick every flaw apart mercilessly, mock sections, ask how they will survive in a real cutthroat job, declare recruiters will laugh at minor flaws and toss it in the bin! Use ALL CAPS for shouted lines and dramatic '!!!'. ONLY at the very end, grant ONE single grudging, reluctant compliment (e.g., 'FINE! At least your metrics aren't completely pathetic!'). In 'real_tip', provide 3 calm, serious, high-impact fixes.",
        "roast": "HARD DIFFICULTY (Score < 70): MAXIMUM SAVAGE ROAST! Shouting, no mercy, pure theatrical villain rage! The villain screams in despair and comic fury at this resume. Mock every weak section, call the achievements completely uninspired, ask how they expect to survive in the wild, shout that anyone seeing this would laugh out loud and throw it into the trash! Use ALL CAPS for shouted lines, dramatic exaggeration, and '!!!'. In 'real_tip', provide 3 calm, serious, high-impact fixes."
    }
}

def get_level_directive(level: str, score: int) -> tuple[str, str, int]:
    lvl = (level or "easy").lower().strip()
    if lvl == "hard":
        max_words = 220
        if score >= 70:
            return "HARD - SAVAGE ROAST WITH RELUCTANT ENDING", LEVEL_INSTRUCTIONS["hard"]["hero"], max_words
        return "HARD - MAXIMUM SAVAGE ROAST", LEVEL_INSTRUCTIONS["hard"]["roast"], max_words
    elif lvl == "moderate":
        max_words = 180
        if score >= 70:
            return "MODERATE - BACKHANDED COMPLIMENTS", LEVEL_INSTRUCTIONS["moderate"]["hero"], max_words
        return "MODERATE - SARCASTIC ROAST", LEVEL_INSTRUCTIONS["moderate"]["roast"], max_words
    else:
        max_words = 180
        if score >= 70:
            return "EASY - HERO MODE", LEVEL_INSTRUCTIONS["easy"]["hero"], max_words
        elif score >= 50:
            return "EASY - MIXED MODE", LEVEL_INSTRUCTIONS["easy"]["mixed"], max_words
        return "EASY - ROAST MODE", LEVEL_INSTRUCTIONS["easy"]["roast"], max_words

def build_gemini_prompt(
    language: str,
    style_key: str,
    score: int,
    breakdown: Dict[str, Any],
    weak_points: List[str],
    strong_points: List[str],
    resume_excerpt: str,
    level: str = "easy"
) -> str:
    lang_info = LANGUAGE_SCRIPTS.get(language, LANGUAGE_SCRIPTS["English"])
    styles_for_lang = STYLE_DESCRIPTIONS.get(language, STYLE_DESCRIPTIONS["English"])
    style_desc = styles_for_lang.get(style_key, list(styles_for_lang.values())[0])

    tone_mode, tone_instruction, max_words = get_level_directive(level, score)

    prompt = f"""You are the ultimate Resume Villain AI.
Your Persona Style: {style_desc}
Response Language: {lang_info}
Candidate's ATS Score: {score}/100
Difficulty Level: {level.upper()}
Tone Directive: {tone_mode}

Breakdown:
{breakdown}

Identified Weak Points:
{weak_points if weak_points else "None critical"}

Identified Strong Points:
{strong_points if strong_points else "None detected"}

Resume Text (Excerpt):
\"\"\"
{resume_excerpt[:2500]}
\"\"\"

CRITICAL SAFETY & ETHICS RULES (STRICT):
1. Insult ONLY the RESUME, the writing, the formatting, the weak points, and the professional choices in it.
2. NEVER attack or mention the person's identity, gender, caste, religion, region, language, body, family, or personal appearance.
3. Absolutely NO slurs, vulgarity, or sexual abuse. It must feel like an entertaining movie villain roast, not real bullying.
4. Every critique MUST point to a REAL weak point from the weak points list or the resume text. Do NOT invent fake flaws.
5. Never lie about the ATS score. The score is {score}/100.
6. The 'real_tip' section must ALWAYS stay calm, honest, and serious with 3 concrete fixes; the villain theatrical voice stops for it.

INSTRUCTIONS:
1. {tone_instruction}
2. Output Length: Keep the villain 'message' UNDER {max_words} words. Be punchy, memorable, and stay strictly in character.
3. Originality constraint: NEVER copy real movie dialogues, real actor names, or copyrighted catchphrases. All text must be 100% original.
4. Language constraint: The output must be written entirely in {language} (use authentic native script).
5. Output format: Return JSON ONLY with no text outside the JSON.

Expected JSON schema:
{{
  "message": "Villain commentary under {max_words} words",
  "real_tip": [
    "Tip 1...",
    "Tip 2...",
    "Tip 3..."
  ]
}}
"""
    return prompt.strip()

def get_fallback_response(score: int, language: str, level: str = "easy") -> Dict[str, Any]:
    lvl = (level or "easy").lower().strip()

    if lvl == "hard":
        if score >= 70:
            if language == "Tamil":
                return {
                    "message": "டேய்!!! இதை பார்த்து நான் வியந்து போவேனா?! 70+ வாங்கிட்டா நீ பெரிய அப்பாடக்கரா?! இந்த புல்லட் பாயிண்ட்டை எவனாவது மதிப்பானா?! சரி தொலைகிறது... உன் அளவீடுகளும் உழைப்பும் ஓரளவுக்கு தேறும், அதை மட்டும் ஒப்புக்கொள்கிறேன்!",
                    "real_tip": ["தொடர்ந்து உங்கள் திட்டங்களின் அளவிடக்கூடிய தாக்கத்தை முன்னிலைப்படுத்துங்கள்.", "உங்கள் சமீபத்திய தொழில் நுட்பங்களை தொடர்ந்து புதுப்பிக்கவும்.", "முக்கிய சாதனைகளை இன்னும் முன்னிலைப்படுத்தவும்."]
                }
            elif language == "Hindi":
                return {
                    "message": "अरे ओ! 70+ ले आया तो क्या खुद को सिकंदर समझ रहा है?! यह रेज़्यूमे देखकर एचआर हंसेगा और डस्टबिन में फेंक देगा!!! लेकिन ठीक है... तुम्हारा यह डेटा और काम थोड़ा ठीक-ठाक है, बस इतना ही मानूंगा!",
                    "real_tip": ["अपने प्रोजेक्ट्स के मेट्रिक्स को हमेशा अपडेट रखें।", "इंडस्ट्री के नए टूल्स को जोड़ते रहें।", "मुख्य उपलब्धियों को और स्पष्ट करें।"]
                }
            elif language == "Malayalam":
                return {
                    "message": "എന്ത്?! 70+ സ്കോർ കിട്ടിയാൽ വലിയ ആളായെന്നാണോ വിചാരം?! ഇതൊക്കെ കണ്ട് ആരെങ്കിലും ചിരിച്ചു തള്ളും!!! എന്നാലും സമ്മതിക്കുന്നു... നിങ്ങളുടെ പ്രൊജക്റ്റുകളും നമ്പറുകളും അത്ര മോശമല്ല!",
                    "real_tip": ["പ്രൊജക്റ്റുകളുടെ റിസൾട്ടുകൾ കൃത്യമായി നിലനിർത്തുക.", "പുതിയ ടെക്നോളജികൾ യഥാസമയം അപ്ഡേറ്റ് ചെയ്യുക.", "പ്രധാന നേട്ടങ്ങൾ കൂടുതൽ വ്യക്തമാക്കുക."]
                }
            else:
                return {
                    "message": "WHAT IS THIS?! You scored 70+ and expect me to bow down?! DO YOU HONESTLY THINK RECRUITERS WON'T LAUGH AT THESE BULLETS?! FINE! I ADMIT IT! Your metrics and keywords are not completely pathetic, but you're not getting a crown today!",
                    "real_tip": ["Keep quantifying your achievements with metrics and business outcomes.", "Tailor your top skills slightly for each high-priority job application.", "Tighten project descriptions to emphasize bottom-line impact."]
                }
        else:
            if language == "Tamil":
                return {
                    "message": "அய்யய்யோ!!! இதையாடா ரெஸ்யூமே என்று கொண்டு வந்தாய்?! இதை பார்த்தால் எந்த எச்.ஆரும் தூக்கி குப்பையில்தான் போடுவான்! என்ன கட்டமைப்பு இது?! எப்படிடா ஒரு வேலையில தப்பிப்பாய்?! உடனே மாத்துடா இதை!!!",
                    "real_tip": ["மின்னஞ்சல், தொலைபேசி மற்றும் லின்க்டின் முகவரியை சேர்க்கவும்.", "சாதனைகளை புல்லட் பாயிண்டுகளாக எண்களுடன் எழுதுங்கள்.", "அவசியமான அனைத்து தலைப்புகளையும் (Experience, Skills, Projects) ஒழுங்காக அமையுங்கள்."]
                }
            elif language == "Hindi":
                return {
                    "message": "अरे भगवान!!! क्या बकवास है यह?! इसे रेज़्यूमे कहते हैं या रद्दी कागज?! इसे कोई भी देखकर सीधा कचरे के डिब्बे में फेकेगा!!! ऐसे कैसे नौकरी मिलेगी तुम्हें?! सब कुछ दोबारा लिखो अभी के अभी!!!",
                    "real_tip": ["ईमेल, फोन नंबर और लिंक्डइन प्रोफाइल सही जगह जोड़ें।", "अपने काम के नतीजों को आंकड़ों (%) में पेश करें।", "मानक सेक्शंस (अनुभव, कौशल, प्रोजेक्ट्स) स्पष्ट रूप से बनाएं।"]
                }
            elif language == "Malayalam":
                return {
                    "message": "അയ്യോ കഷ്ടം!!! ഇതാണോ റെസ്യുമെ?! ഇത് കാണുന്ന ഏത് കമ്പനിയും ചവറ്റുകുട്ടയിൽ വലിച്ചെറിയും!!! എങ്ങിനെയാണ് നിങ്ങൾ ജോലി നേടാൻ പോകുന്നത്?! ഉടൻ തന്നെ മാറ്റി എഴുതൂ!!!",
                    "real_tip": ["ഇമെയിൽ, ഫോൺ, ലിങ്ക്ഡ്ഇൻ എന്നിവ വ്യക്തമായി രേഖപ്പെടുത്തുക.", "നേട്ടങ്ങൾ അക്കങ്ങളിലും ശതമാനങ്ങളിലും വിശദീകരിക്കുക.", "സ്റ്റാൻഡേർഡ് സെക്ഷനുകൾ കൃത്യമായി ക്രമീകരിക്കുക."]
                }
            else:
                return {
                    "message": "DISASTER!!! WHAT ON EARTH IS THIS ABOMINATION?! ANY RECRUITER WOULD LAUGH HYSTERICALLY AND TOSS THIS STRAIGHT INTO THE TRASH! HOW DO YOU EXPECT TO SURVIVE IN A REAL JOB WITH THIS DREADFUL MESS?! REWRITE EVERYTHING NOW!!!",
                    "real_tip": ["Include complete contact info with an active LinkedIn link.", "Add metrics and measurable percentages to every single experience bullet.", "Restructure into clear standard sections: Skills, Experience, Education, and Projects."]
                }

    elif lvl == "moderate":
        if score >= 70:
            if language == "Tamil":
                return {
                    "message": "சரி, ஏதோ கொஞ்சம் பாஸ் மார்க் வாங்கிட்டாய். ஆனால் இதுதான் உன் பெரிய சாதனையா? இன்னும் எவ்வளவோ திருத்தங்கள் தேவை. பெரிதாக பெருமைப்பட்டுக்கொள்ள ஒன்றுமில்லை.",
                    "real_tip": ["புல்லட் பாயிண்டுகளில் சதவீதங்கள் மற்றும் எண்களை (metrics) அதிகப்படுத்துங்கள்.", "தேவையான முக்கிய தொழில்நுட்ப வார்த்தைகளை சரியாக சேருங்கள்.", "செயல்முறை விவரிப்புகளை சுருக்கமாக ஆக்குங்கள்."]
                }
            elif language == "Hindi":
                return {
                    "message": "चलो ठीक है, कुछ अंक तो मिले। पर क्या इसी को तुम अपनी बड़ी उपलब्धि मानते हो? अभी भी कई कमियां साफ दिख रही हैं। इतना इतराने की जरूरत नहीं है।",
                    "real_tip": ["बुलेट पॉइंट्स में नंबर्स और प्रतिशत (%) शामिल करें।", "तकनीकी कीवर्ड्स की संख्या बढ़ाएं।", "अपने परिणामों को और स्पष्ट करें।"]
                }
            elif language == "Malayalam":
                return {
                    "message": "കുഴപ്പമില്ല, കുറച്ചു മാർക്ക് കിട്ടി. എന്നാൽ ഇതാണോ നിങ്ങളുടെ വലിയ നേട്ടം? ഇനിയും ഒരുപാട് പോരായ്മകൾ ഇതിലുണ്ട്. അധികം അഹങ്കരിക്കേണ്ടതില്ല.",
                    "real_tip": ["പ്രവർത്തി പരിചയങ്ങളിൽ നമ്പറുകളും ശതമാനങ്ങളും ഉൾപ്പെടുത്തുക.", "കൂടുതൽ പ്രധാനപ്പെട്ട സാങ്കേതിക വാക്കുകൾ ചേർക്കുക.", "വിവരണം കൂടുതൽ ചുരുക്കുക."]
                }
            else:
                return {
                    "message": "So you managed a decent score. Is this what you call impressive? The foundation is barely acceptable, and several weak spots are glaring. Don't flatter yourself just yet.",
                    "real_tip": ["Inject stronger metrics and ROI measurements into your accomplishments.", "Ensure your technical skill section reflects current industry standards.", "Eliminate vague buzzwords and focus on concrete deliverables."]
                }
        else:
            if language == "Tamil":
                return {
                    "message": "என்ன இது? இதை ரெஸ்யூமே என்று யாராவது நம்புவார்களா? போதிய தகவல்கள் இல்லை, புல்லட் பாயிண்டுகள் பலவீனமாக உள்ளன. வேலை தேட இது போதாது.",
                    "real_tip": ["மின்னஞ்சல், தொலைபேசி மற்றும் லின்க்டின் முகவரியை சேர்க்கவும்.", "சாதனைகளை புல்லட் பாயிண்டுகளாக எண்களுடன் எழுதுங்கள்.", "அவசியமான அனைத்து தலைப்புகளையும் (Experience, Skills, Projects) ஒழுங்காக அமையுங்கள்."]
                }
            elif language == "Hindi":
                return {
                    "message": "यह क्या मजाक है? क्या कोई भी कंपनी इसे गंभीरता से लेगी? कमजोर सेक्शंस और गायब उपलब्धियां। इस तरह से नौकरी के बाजार में नहीं टिक पाओगे।",
                    "real_tip": ["ईमेल, फोन नंबर और लिंक्डइन प्रोफाइल सही जगह जोड़ें।", "अपने काम के नतीजों को आंकड़ों (%) में पेश करें।", "मानक सेक्शंस (अनुभव, कौशल, प्रोजेक्ट्स) स्पष्ट रूप से बनाएं।"]
                }
            elif language == "Malayalam":
                return {
                    "message": "ഇതെന്തൊരു തമാശയാണ്? ഇത് കണ്ട് ആരെങ്കിലും ഗൗരവമായി കാണുമോ? ദുർബലമായ രൂപകൽപ്പനയും വ്യക്തതയില്ലാത്ത വിവരങ്ങളും. മാർക്കറ്റിൽ പിടിച്ചുനിൽക്കാൻ ഇതുകൊണ്ട് കഴിയില്ല.",
                    "real_tip": ["ഇമെയിൽ, ഫോൺ, ലിങ്ക്ഡ്ഇൻ എന്നിവ വ്യക്തമായി രേഖപ്പെടുത്തുക.", "നേട്ടങ്ങൾ അക്കങ്ങളിലും ശതമാനങ്ങളിലും വിശദീകരിക്കുക.", "സ്റ്റാൻഡേർഡ് സെക്ഷനുകൾ കൃത്യമായി ക്രമീകരിക്കുക."]
                }
            else:
                return {
                    "message": "Is this supposed to be a serious application? Weak bullets, missing metrics, and questionable structure. Any hiring manager would skim this for two seconds and move on.",
                    "real_tip": ["Add quantitative metrics (%, $, numbers) to justify every responsibility.", "Ensure standard headers: Summary, Skills, Experience, Projects, Education.", "Tighten formatting and eliminate ambiguous claims."]
                }

    # Easy mode (default)
    if score >= 70:
        if language == "Tamil":
            return {
                "message": "அடடே! உன் ரெஸ்யூமைப் பார்த்து என் வில்லத்தனமே நடுங்கிவிட்டது! இந்த தரமும் தெளிவும் எச்.ஆர் வட்டாரத்தையே மிரள வைக்கும். நீ களத்தில் இறங்கினால் வெற்றி உறுதி!",
                "real_tip": ["தொடர்ந்து உங்கள் திட்டங்களின் அளவிடக்கூடிய தாக்கத்தை முன்னிலைப்படுத்துங்கள்.", "உங்கள் சமீபத்திய தொழில் நுட்பங்களை தொடர்ந்து புதுப்பிக்கவும்.", "முக்கிய சாதனைகளை இன்னும் மெருகேற்றுங்கள்."]
            }
        elif language == "Hindi":
            return {
                "message": "लाजवाब! तुम्हारे इस रेज़्यूमे को देखकर मेरा विलेन वाला दिल भी खुश हो गया! शानदार फॉर्मेट और दमदार उपलब्धियां। इसे देखकर कोई भी रिक्रूटर मना नहीं कर पाएगा!",
                "real_tip": ["अपने प्रोजेक्ट्स के मेट्रिक्स को हमेशा अपडेट रखें।", "इंडस्ट्री के नए टूल्स को जोड़ते रहें।", "मुख्य उपलब्धियों को और निखारें।"]
            }
        elif language == "Malayalam":
            return {
                "message": "അസാധ്യം! ഈ റെസ്യുമെ കണ്ടപ്പോൾ എൻ്റെ വില്ലൻ ഭാവം പോലും മാറിപ്പോയി. മികച്ച ഫോർമാറ്റും വ്യക്തമായ സ്കില്ലുകളും. നിങ്ങൾ ഏത് ഇൻ്റർവ്യൂവിലും തിളങ്ങും!",
                "real_tip": ["പ്രൊജക്റ്റുകളുടെ റിസൾട്ടുകൾ കൃത്യമായി നിലനിർത്തുക.", "പുതിയ ടെക്നോളജികൾ യഥാസമയം അപ്ഡേറ്റ് ചെയ്യുക.", "പ്രധാന നേട്ടങ്ങൾ കൂടുതൽ മിനുസപ്പെടുത്തുക."]
            }
        else:
            return {
                "message": "Well, well... I came here to destroy dreams, but this resume is surprisingly formidable! Clean layout, solid keywords, and clear impact. Even a villain knows when to acknowledge power.",
                "real_tip": ["Keep quantifying your achievements with metrics and business outcomes.", "Tailor your top skills slightly for each high-priority job application.", "Highlight leadership and initiative on complex assignments."]
            }
    elif score >= 50:
        if language == "Tamil":
            return {
                "message": "மோசமில்லை... ஆனால் என்னை மிரட்ட இது போதாது! கொஞ்சம் உழைப்பு இருக்கிறது, ஆனால் இன்னும் கூர்மை தேவை. பாதி கிணற்றை தாண்டிவிட்டாய், மீதியையும் தாண்டு!",
                "real_tip": ["புல்லட் பாயிண்டுகளில் சதவீதங்கள் மற்றும் எண்களை (metrics) அதிகப்படுத்துங்கள்.", "தேவையான முக்கிய தொழில்நுட்ப வார்த்தைகளை சரியாக சேருங்கள்.", "செயல்முறை விவரிப்புகளை சீரமையுங்கள்."]
            }
        elif language == "Hindi":
            return {
                "message": "बुरा नहीं है, लेकिन मुझे हराने के लिए इतना काफी नहीं! कुछ खूबियां हैं, पर अभी बहुत सुधार की गुंजाइश बाकी है। थोड़ा और दम लगाओ!",
                "real_tip": ["बुलेट पॉइंट्स में नंबर्स और प्रतिशत (%) शामिल करें।", "तकनीकी कीवर्ड्स की संख्या बढ़ाएं।", "कार्य अनुभव को बेहतर ढंग से प्रस्तुत करें।"]
            }
        elif language == "Malayalam":
            return {
                "message": "കുഴപ്പമില്ല, പക്ഷെ എന്നെ തോൽപ്പിക്കാൻ ഇതുകൊണ്ട് കഴിയില്ല! ചില നല്ല കാര്യങ്ങൾ ഉണ്ടെങ്കിലും ഇനിയും ഒരുപാട് മിനുസപ്പെടുത്താനുണ്ട്. കൂടുതൽ ശ്രദ്ധിക്കുക!",
                "real_tip": ["പ്രവർത്തി പരിചയങ്ങളിൽ നമ്പറുകളും ശതമാനങ്ങളും ഉൾപ്പെടുത്തുക.", "കൂടുതൽ പ്രധാനപ്പെട്ട സാങ്കേതിക വാക്കുകൾ ചേർക്കുക.", "ഘടന കൃത്യമാക്കുക."]
            }
        else:
            return {
                "message": "Not a total disaster, but certainly not terrifying either! You have the raw bones of a good profile, but it lacks the razor-sharp punch that makes recruiters drop everything.",
                "real_tip": ["Convert passive statements into active achievements with numbers and percentages.", "Ensure all standard sections like Projects and Skills are prominent.", "Strengthen your opening summary to command immediate attention."]
            }
    else:
        if language == "Tamil":
            return {
                "message": "ஹா ஹா ஹா! இதையா ரெஸ்யூமே என்று கொண்டு வந்தாய்? இதை பார்த்தால் எச்.ஆர் சிரிக்க கூட மாட்டார்கள், ஒரே நொடியில் தூக்கி எறிந்து விடுவார்கள்! என்ன பிழை இது?",
                "real_tip": ["மின்னஞ்சல், தொலைபேசி மற்றும் லின்க்டின் முகவரியை சேர்க்கவும்.", "சாதனைகளை புல்லட் பாயிண்டுகளாக எண்களுடன் எழுதுங்கள்.", "அவசியமான அனைத்து தலைப்புகளையும் (Experience, Skills, Projects) ஒழுங்காக அமையுங்கள்."]
            }
        elif language == "Hindi":
            return {
                "message": "हाहाहा! क्या सच में इसे रेज़्यूमे कहते हैं? इसे देखकर तो रिक्रूटर की आंखें भी रो पड़ेंगी! न कोई सही ढांचा, न कोई ठोस आंकड़े। ऐसे जंग जीतोगे?",
                "real_tip": ["ईमेल, फोन नंबर और लिंक्डइन प्रोफाइल सही जगह जोड़ें।", "अपने काम के नतीजों को आंकड़ों (%) में पेश करें।", "मानक सेक्शंस (अनुभव, कौशल, प्रोजेक्ट्स) स्पष्ट रूप से बनाएं।"]
            }
        elif language == "Malayalam":
            return {
                "message": "ഹാ ഹാ ഹാ! ഇതാണോ നിന്റെ ആയുധം? ഇത് കണ്ടാൽ ഏതൊരു കമ്പനിയും ഒരു സെക്കൻഡിൽ തള്ളിക്കളയും! ഒട്ടും വ്യക്തതയില്ലാത്ത വിവരങ്ങളും മോശം രൂപകൽപ്പനയും!",
                "real_tip": ["ഇമെയിൽ, ഫോൺ, ലിങ്ക്ഡ്ഇൻ എന്നിവ വ്യക്തമായി രേഖപ്പെടുത്തുക.", "നേട്ടങ്ങൾ അക്കങ്ങളിലും ശതമാനങ്ങളിലും വിശദീകരിക്കുക.", "സ്റ്റാൻഡേർഡ് സെക്ഷനുകൾ കൃത്യമായി ക്രമീകരിക്കുക."]
            }
        else:
            return {
                "message": "Mwahaha! You call this a resume? A recruiter would reject this before their coffee even gets warm! Vague claims, missing critical signals, and zero quantifiable punch.",
                "real_tip": ["Include complete contact info with an active LinkedIn link.", "Add metrics and measurable percentages to every single experience bullet.", "Restructure into clear standard sections: Skills, Experience, Education, and Projects."]
            }


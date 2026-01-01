"""
Matching Engine v3 - Rich Biographical Matching
Generates detailed explanations based on actual scientist biographies
"""

import json
import google.generativeai as genai
from config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)

# Trait descriptions for generating meaningful explanations
TRAIT_DESCRIPTIONS = {
    "approach": {
        "theoretical": "approaches problems through mathematical reasoning and abstract thinking",
        "experimental": "prefers hands-on experimentation and empirical validation",
        "applied": "focuses on practical applications and real-world impact",
        "observational": "excels at pattern recognition and careful observation"
    },
    "collaboration": {
        "solo": "thrives working independently with deep focus",
        "small_team": "works best with a few trusted collaborators",
        "large_team": "excels at orchestrating large collaborative efforts",
        "mentor": "finds fulfillment in teaching while researching"
    },
    "risk": {
        "conservative": "prefers proven paths with strong evidence",
        "calculated": "carefully weighs risks before committing",
        "bold": "embraces unconventional ideas and breakthrough thinking",
        "hedged": "explores risky ideas while maintaining safer alternatives"
    },
    "motivation": {
        "curiosity": "driven purely by the joy of understanding",
        "impact": "motivated by making a tangible difference in lives",
        "recognition": "seeks acknowledgment and validation of excellence",
        "duty": "driven by responsibility to country and community"
    },
    "adversity": {
        "persist": "responds to obstacles with redoubled determination",
        "pivot": "adapts fluidly when facing barriers",
        "fight": "directly challenges unfair systems and rejection",
        "accept": "philosophically accepts setbacks while staying focused"
    },
    "breadth": {
        "specialist": "goes extremely deep in one focused area",
        "generalist": "learns broadly across many fields",
        "interdisciplinary": "works at the intersection of multiple fields",
        "expanding": "starts deep then gradually expands scope"
    },
    "authority": {
        "independent": "works best outside traditional structures",
        "institutional": "builds and strengthens institutions",
        "reformer": "challenges norms while working within systems",
        "revolutionary": "creates entirely new frameworks"
    },
    "communication": {
        "reserved": "lets work speak for itself",
        "charismatic": "enjoys explaining ideas to broad audiences",
        "written": "communicates through detailed documentation",
        "demonstrative": "shows rather than tells through building"
    },
    "time_horizon": {
        "immediate": "focuses on urgent problems needing solutions now",
        "medium": "thinks in terms of achievable multi-year goals",
        "long_term": "maintains decades-spanning vision",
        "eternal": "pursues timeless questions transcending eras"
    },
    "resources": {
        "frugal": "achieves great things with minimal resources",
        "adequate": "needs reasonable resources, avoids excess",
        "abundant": "secures big resources for big problems",
        "ideas_first": "focuses on ideas, lets resources follow"
    },
    "legacy": {
        "knowledge": "wants discoveries that outlast them",
        "people": "values the students and people influenced",
        "institutions": "builds systems that continue their work",
        "movement": "seeks to change how society thinks"
    },
    "failure": {
        "analytical": "treats failures as data points for analysis",
        "persistent": "tries again with modifications until success",
        "serendipitous": "looks for unexpected discoveries in failures",
        "pragmatic": "moves on quickly to more promising directions"
    }
}


class MatchingEngineV3:
    """
    Rich biographical matching engine
    """

    def __init__(self, database_path='scientist_db_rich.json'):
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.load_database(database_path)

    def load_database(self, path):
        """Load the scientist database"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                self.scientists = json.load(f)
            print(f"Loaded {len(self.scientists)} scientists with rich profiles")
        except FileNotFoundError:
            print(f"Database not found at {path}")
            self.scientists = []

    def calculate_match_score(self, user_profile: dict, scientist: dict) -> tuple:
        """Calculate match score with detailed trait analysis"""
        matching_traits = []
        differing_traits = []

        scientist_traits = scientist.get('traits', {})

        for dimension, user_value in user_profile.items():
            scientist_value = scientist_traits.get(dimension)

            if scientist_value == user_value:
                matching_traits.append({
                    "dimension": dimension,
                    "value": user_value,
                    "match_type": "exact",
                    "description": TRAIT_DESCRIPTIONS.get(dimension, {}).get(user_value, "")
                })
            elif self._are_related(dimension, user_value, scientist_value):
                matching_traits.append({
                    "dimension": dimension,
                    "user_value": user_value,
                    "scientist_value": scientist_value,
                    "match_type": "related",
                    "user_desc": TRAIT_DESCRIPTIONS.get(dimension, {}).get(user_value, ""),
                    "scientist_desc": TRAIT_DESCRIPTIONS.get(dimension, {}).get(scientist_value, "")
                })
            else:
                if scientist_value:
                    differing_traits.append({
                        "dimension": dimension,
                        "user_value": user_value,
                        "scientist_value": scientist_value,
                        "user_desc": TRAIT_DESCRIPTIONS.get(dimension, {}).get(user_value, ""),
                        "scientist_desc": TRAIT_DESCRIPTIONS.get(dimension, {}).get(scientist_value, "")
                    })

        exact = sum(1 for t in matching_traits if t.get('match_type') == 'exact')
        related = sum(1 for t in matching_traits if t.get('match_type') == 'related')
        score = (exact * 1.0 + related * 0.5) / len(user_profile) if user_profile else 0

        return score, matching_traits, differing_traits

    def _are_related(self, dimension: str, val1: str, val2: str) -> bool:
        """Check if trait values are related"""
        if not val1 or not val2:
            return False

        related_pairs = {
            "approach": [("theoretical", "observational"), ("experimental", "applied")],
            "collaboration": [("solo", "small_team"), ("large_team", "mentor")],
            "risk": [("calculated", "hedged"), ("bold", "calculated")],
            "motivation": [("curiosity", "recognition"), ("impact", "duty")],
            "adversity": [("persist", "fight"), ("pivot", "accept")],
            "breadth": [("generalist", "interdisciplinary"), ("specialist", "expanding")],
            "authority": [("independent", "reformer"), ("institutional", "reformer")],
            "communication": [("written", "reserved"), ("charismatic", "demonstrative")],
            "time_horizon": [("medium", "long_term"), ("long_term", "eternal")],
            "resources": [("frugal", "adequate"), ("adequate", "abundant")],
            "legacy": [("knowledge", "people"), ("institutions", "movement")],
            "failure": [("analytical", "pragmatic"), ("persistent", "serendipitous")]
        }

        pairs = related_pairs.get(dimension, [])
        return (val1, val2) in pairs or (val2, val1) in pairs

    def find_matches(self, user_profile: dict, domain_filter: str = None, top_n: int = 3) -> list:
        """Find top matching scientists"""
        candidates = self.scientists

        if domain_filter:
            domain_map = {
                "cosmos": ["Physics", "Space Science", "Astrophysics", "Astronomy", "Aerospace"],
                "quantum": ["Physics", "Mathematics", "Computer Science"],
                "life": ["Biology", "Medicine", "Biochemistry", "Neuroscience", "Chemistry"],
                "earth": ["Environmental Science", "Agriculture", "Ecology", "Earth Science"],
                "engineering": ["Engineering", "Technology", "Computer Science", "Aerospace"]
            }
            allowed = domain_map.get(domain_filter, [])
            if allowed:
                candidates = [s for s in candidates if s.get('field') in allowed]

        scored = []
        for scientist in candidates:
            score, matching, differing = self.calculate_match_score(user_profile, scientist)
            scored.append({
                "scientist": scientist,
                "score": score,
                "matching_traits": matching,
                "differing_traits": differing
            })

        scored.sort(key=lambda x: x['score'], reverse=True)
        return scored[:top_n]

    def build_rich_resonance(self, name: str, trait: dict, summary: str, achievements: str, moments: list, user_profile: dict = None) -> dict:
        """Build a rich resonance explanation using actual biographical data and user's specific answers"""
        dim = trait['dimension']
        dim_title = dim.replace('_', ' ').title()

        # Get user's actual answer for this dimension
        user_answer = user_profile.get(dim, '') if user_profile else ''
        user_desc = TRAIT_DESCRIPTIONS.get(dim, {}).get(user_answer, '')

        # Extract specific details from biography
        summary_lower = summary.lower() if summary else ""
        achievements_lower = achievements.lower() if achievements else ""

        # Clear used sentences cache for this scientist at start
        self._used_sentences[name] = set()

        # Build CONCISE explanations - 1-2 sentences max
        explanations = {
            "approach": {
                "theoretical": f"Like you, {name} approached problems through abstract reasoning. {self._find_evidence(summary, achievements, ['theory', 'mathematical', 'equation', 'formula'], name)}",
                "experimental": f"You both believe in testing ideas hands-on. {self._find_evidence(summary, achievements, ['experiment', 'laboratory', 'discovered', 'tested'], name)}",
                "applied": f"Like you, {name} focused on making science useful. {self._find_evidence(summary, achievements, ['practical', 'application', 'developed', 'implemented'], name)}",
                "observational": f"You share {name}'s gift for observation and pattern recognition. {self._find_evidence(summary, achievements, ['observed', 'pattern', 'data', 'survey'], name)}"
            },
            "collaboration": {
                "solo": f"Like you, {name} thrived working independently. {self._find_evidence(summary, achievements, ['alone', 'solitary', 'independent', 'independently'], name)}",
                "small_team": f"You both work best with trusted collaborators. {self._find_evidence(summary, achievements, ['collaborat', 'worked with', 'partner', 'together'], name)}",
                "large_team": f"Like you, {name} excelled at leading large teams. {self._find_evidence(summary, achievements, ['led', 'directed', 'team', 'organization', 'founded'], name)}",
                "mentor": f"You share {name}'s dedication to mentoring. {self._find_evidence(summary, achievements, ['taught', 'mentor', 'students', 'trained', 'professor'], name)}"
            },
            "risk": {
                "conservative": f"Like you, {name} preferred methodical, proven approaches. {self._find_evidence(summary, achievements, ['meticulous', 'careful', 'systematic', 'rigorous'], name)}",
                "calculated": f"You both carefully weigh risks before committing. {self._find_evidence(summary, achievements, ['strategic', 'planned', 'considered', 'calculated'], name)}",
                "bold": f"You share {name}'s appetite for breakthrough thinking. {self._find_evidence(summary, achievements, ['revolutionary', 'pioneer', 'breakthrough', 'first', 'unconventional'], name)}",
                "hedged": f"Like you, {name} balanced bold ideas with pragmatic backup plans. {self._find_evidence(summary, achievements, ['diverse', 'multiple', 'varied', 'balanced'], name)}"
            },
            "motivation": {
                "curiosity": f"Pure curiosity drives you both. {self._find_evidence(summary, achievements, ['curious', 'passion', 'fascinated', 'love of'], name)}",
                "impact": f"You share {name}'s drive to make a tangible difference. {self._find_evidence(summary, achievements, ['help', 'improve', 'benefit', 'society', 'humanity'], name)}",
                "recognition": f"Like you, {name} pursued excellence and acknowledgment. {self._find_evidence(summary, achievements, ['award', 'prize', 'honor', 'recognition', 'medal'], name)}",
                "duty": f"You share {name}'s sense of duty to nation. {self._find_evidence(summary, achievements, ['nation', 'India', 'country', 'service'], name)}"
            },
            "adversity": {
                "persist": f"Like you, {name} redoubled efforts when facing obstacles. {self._find_evidence(summary, achievements, ['persever', 'persist', 'despite', 'overcame'], name)}",
                "pivot": f"You both adapt fluidly when facing barriers. {self._find_evidence(summary, achievements, ['changed', 'shifted', 'adapted', 'new direction'], name)}",
                "fight": f"Like you, {name} directly challenged unfair systems. {self._find_evidence(summary, achievements, ['fought', 'challenged', 'opposed', 'battle'], name)}",
                "accept": f"You share {name}'s philosophical acceptance while staying focused. {self._find_evidence(summary, achievements, ['philosophical', 'accepted', 'graceful'], name)}"
            },
            "legacy": {
                "knowledge": f"Like you, {name} wanted discoveries that outlast them. {self._find_evidence(summary, achievements, ['discovery', 'theorem', 'theory', 'understanding'], name)}",
                "people": f"You share {name}'s focus on influencing the next generation. {self._find_evidence(summary, achievements, ['students', 'trained', 'mentored', 'influenced'], name)}",
                "institutions": f"Like you, {name} built lasting institutions. {self._find_evidence(summary, achievements, ['founded', 'established', 'built', 'institution'], name)}",
                "movement": f"You share {name}'s desire to transform how society thinks. {self._find_evidence(summary, achievements, ['movement', 'revolution', 'transformed', 'changed'], name)}"
            },
            "breadth": {
                "specialist": f"Like you, {name} went deep in one focused area. {self._find_evidence(summary, achievements, ['specialist', 'expert', 'focused', 'dedicated'], name)}",
                "generalist": f"You share {name}'s broad intellectual curiosity. {self._find_evidence(summary, achievements, ['broad', 'diverse', 'various', 'multiple fields'], name)}",
                "interdisciplinary": f"Like you, {name} worked across multiple fields. {self._find_evidence(summary, achievements, ['interdisciplinary', 'combined', 'bridged', 'intersection'], name)}",
                "expanding": f"You both started deep then expanded scope. {self._find_evidence(summary, achievements, ['expanded', 'grew', 'evolved', 'broadened'], name)}"
            },
            "authority": {
                "independent": f"Like you, {name} worked best outside traditional structures. {self._find_evidence(summary, achievements, ['independent', 'own path', 'unconventional'], name)}",
                "institutional": f"You share {name}'s dedication to building institutions. {self._find_evidence(summary, achievements, ['institution', 'organization', 'established', 'founded'], name)}",
                "reformer": f"Like you, {name} challenged norms while working within systems. {self._find_evidence(summary, achievements, ['reform', 'changed', 'improved', 'modernized'], name)}",
                "revolutionary": f"You share {name}'s revolutionary approach. {self._find_evidence(summary, achievements, ['revolutionary', 'breakthrough', 'pioneered', 'first'], name)}"
            },
            "communication": {
                "reserved": f"Like you, {name} let work speak for itself. {self._find_evidence(summary, achievements, ['quietly', 'modest', 'humble', 'reserved'], name)}",
                "charismatic": f"You share {name}'s gift for explaining ideas. {self._find_evidence(summary, achievements, ['spoke', 'lectured', 'communicated', 'explained'], name)}",
                "written": f"Like you, {name} communicated through detailed writing. {self._find_evidence(summary, achievements, ['wrote', 'published', 'authored', 'books', 'papers'], name)}",
                "demonstrative": f"You both believe in showing rather than telling. {self._find_evidence(summary, achievements, ['built', 'created', 'demonstrated', 'showed'], name)}"
            },
            "time_horizon": {
                "immediate": f"Like you, {name} focused on urgent problems. {self._find_evidence(summary, achievements, ['urgent', 'immediate', 'pressing', 'crisis'], name)}",
                "medium": f"You share {name}'s strategic multi-year thinking. {self._find_evidence(summary, achievements, ['planned', 'strategic', 'project', 'developed'], name)}",
                "long_term": f"Like you, {name} maintained decades-spanning vision. {self._find_evidence(summary, achievements, ['vision', 'long-term', 'decades', 'future'], name)}",
                "eternal": f"You both pursue timeless questions. {self._find_evidence(summary, achievements, ['fundamental', 'eternal', 'timeless', 'universal'], name)}"
            },
            "resources": {
                "frugal": f"Like you, {name} achieved great things with minimal resources. {self._find_evidence(summary, achievements, ['limited', 'modest', 'frugal', 'simple'], name)}",
                "adequate": f"You share {name}'s balanced approach to resources. {self._find_evidence(summary, achievements, ['efficient', 'practical', 'reasonable'], name)}",
                "abundant": f"Like you, {name} mobilized major resources for big problems. {self._find_evidence(summary, achievements, ['major', 'large-scale', 'significant', 'funded'], name)}",
                "ideas_first": f"You both focus on ideas first. {self._find_evidence(summary, achievements, ['idea', 'concept', 'theory', 'vision'], name)}"
            },
            "failure": {
                "analytical": f"Like you, {name} treated failures as data points. {self._find_evidence(summary, achievements, ['analyzed', 'studied', 'systematic', 'methodical'], name)}",
                "persistent": f"You share {name}'s relentless persistence. {self._find_evidence(summary, achievements, ['persistent', 'persevered', 'continued', 'despite'], name)}",
                "serendipitous": f"Like you, {name} found discoveries in failures. {self._find_evidence(summary, achievements, ['discovered', 'unexpected', 'accident', 'serendipity'], name)}",
                "pragmatic": f"You share {name}'s practical approach to moving on. {self._find_evidence(summary, achievements, ['practical', 'pragmatic', 'focused', 'moved'], name)}"
            }
        }

        # Get the trait value
        trait_value = trait.get('value') if trait.get('match_type') == 'exact' else trait.get('scientist_value', trait.get('user_value'))

        # Get explanation or build default
        if dim in explanations and trait_value in explanations[dim]:
            explanation = explanations[dim][trait_value]
        else:
            desc = trait.get('description', trait.get('scientist_desc', ''))
            explanation = f"You share {name}'s approach: {desc}. {self._extract_relevant_fact(summary, achievements, moments)}"

        return {
            "trait": dim_title,
            "explanation": explanation
        }

    # Class-level cache to track used sentences per scientist
    _used_sentences = {}

    def _find_evidence(self, summary: str, achievements: str, keywords: list, scientist_name: str = "") -> str:
        """Find evidence from biography matching keywords - returns DIFFERENT sentences each time"""
        text = f"{summary} {achievements}"
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 20]

        # Track which sentences have been used for this scientist
        if scientist_name not in self._used_sentences:
            self._used_sentences[scientist_name] = set()
        used = self._used_sentences[scientist_name]

        # Pure skip patterns - expanded to catch Wikipedia intros
        pure_bio_patterns = ['was born', 'died on', 'married', 'children', 'spouse', 'moved to']

        def is_wikipedia_intro(s):
            """Detect Wikipedia-style intro sentences"""
            s_lower = s.lower()
            # Pattern: dates in parentheses like "(19 July 1938 – 20 May 2025)"
            if '(' in s and ')' in s and any(month in s for month in ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']):
                return True
            # Pattern: "Name was a/an Indian/American/British..."
            if ') was a' in s_lower or ') is a' in s_lower:
                return True
            if 'was an indian' in s_lower or 'is an indian' in s_lower:
                return True
            if 'was a indian' in s_lower or 'was an american' in s_lower or 'was a british' in s_lower:
                return True
            # Pattern: starts with name and immediately has nationality
            nationality_patterns = ['indian physicist', 'indian scientist', 'indian mathematician', 'indian engineer',
                                   'indian chemist', 'indian biologist', 'indian astronomer', 'indian astrophysicist']
            if any(p in s_lower[:100] for p in nationality_patterns):
                return True
            return False

        def is_complete_sentence(s):
            """Check if sentence is complete and not a fragment"""
            if not s or len(s) < 30:
                return False
            # Must start with capital letter (proper sentence start)
            if not s[0].isupper():
                return False
            # Skip sentences that start with words that indicate fragments or incomplete thoughts
            first_word = s.split()[0].lower() if s.split() else ""
            fragment_starters = ['first', 'also', 'and', 'but', 'or', 'which', 'where', 'when', 'that', 'who',
                                'awarded', 'served', 'known', 'in', 'career', 'early', 'later', 'after',
                                'before', 'during', 'following', 'padma', 'born', 'died', 'received', 'joined',
                                'performed', 'made', 'was', 'is', 'has', 'had', 'worked', 'studied',
                                'nobel', 'upon', 'the', 'his', 'her', 'their', 'a', 'an', 'for', 'with', 'on', 'at',
                                'he', 'she', 'they', 'it', 'this', 'these', 'from', 'since', 'as', 'being']
            if first_word in fragment_starters:
                return False
            return True

        # First pass: find sentences with specific keywords that haven't been used
        for sentence in sentences:
            if sentence in used:
                continue
            sentence_lower = sentence.lower()

            if any(p in sentence_lower for p in pure_bio_patterns):
                continue

            # Skip Wikipedia intro sentences
            if is_wikipedia_intro(sentence):
                continue

            if any(kw in sentence_lower for kw in keywords):
                # Extract work part from intro sentences
                if 'who ' in sentence_lower and len(sentence) > 50:
                    who_index = sentence_lower.find('who ')
                    work_part = sentence[who_index + 4:].strip()
                    if len(work_part) > 20 and is_complete_sentence(work_part[0].upper() + work_part[1:]):
                        used.add(sentence)
                        return work_part[0].upper() + work_part[1:] + "."
                if len(sentence) < 300 and is_complete_sentence(sentence):
                    used.add(sentence)
                    return sentence + "."

        # Second pass: find ANY unused work-related sentence
        work_indicators = ['research', 'discovered', 'developed', 'invented', 'pioneered', 'founded',
                          'contributed', 'published', 'award', 'prize', 'known for', 'breakthrough',
                          'theory', 'equation', 'method', 'technique', 'professor', 'director',
                          'institute', 'led', 'established', 'study', 'work']

        for sentence in sentences:
            if sentence in used:
                continue
            sentence_lower = sentence.lower()

            if any(p in sentence_lower for p in pure_bio_patterns):
                continue

            # Skip Wikipedia intro sentences
            if is_wikipedia_intro(sentence):
                continue

            if any(kw in sentence_lower for kw in work_indicators):
                if 'who ' in sentence_lower and len(sentence) > 50:
                    who_index = sentence_lower.find('who ')
                    work_part = sentence[who_index + 4:].strip()
                    if len(work_part) > 20 and is_complete_sentence(work_part[0].upper() + work_part[1:]):
                        used.add(sentence)
                        return work_part[0].upper() + work_part[1:] + "."
                if len(sentence) < 300 and is_complete_sentence(sentence):
                    used.add(sentence)
                    return sentence + "."

        # Return empty if nothing good found - DON'T return fragments
        return ""

    def _extract_relevant_fact(self, summary: str, achievements: str, moments: list, keywords: list = None) -> str:
        """Extract a relevant fact from the biography, optionally matching keywords"""

        # If keywords provided, try to find matching content first
        if keywords:
            text = f"{summary} {achievements}"
            sentences = text.split('.')
            for sentence in sentences:
                sentence_lower = sentence.lower()
                if any(kw in sentence_lower for kw in keywords):
                    clean = sentence.strip()
                    if len(clean) > 20 and len(clean) < 300:
                        return clean + "."

        # Look for significant moments (prefer achievements over migration/personal events)
        if moments and len(moments) > 0:
            for m in moments:
                m_lower = m.lower()
                # Skip mundane facts, prefer scientific/career achievements
                if any(word in m_lower for word in ['award', 'prize', 'discovered', 'invented', 'founded', 'breakthrough', 'published', 'developed']):
                    return m
            # Return first moment if no significant one found
            return moments[0]

        if achievements:
            sentences = achievements.split('.')
            for s in sentences:
                if len(s.strip()) > 20:
                    return s.strip() + "."

        if summary:
            sentences = summary.split('.')
            for s in sentences[1:3]:  # Skip first sentence (usually intro)
                if len(s.strip()) > 30:
                    return s.strip() + "."

        return ""

    def generate_rich_narrative(self, user_profile: dict, match: dict) -> dict:
        """Generate detailed narrative based on actual biography"""
        scientist = match['scientist']
        matching = match['matching_traits']
        differing = match['differing_traits']

        # Build context from scientist's actual data
        name = scientist['name']
        field = scientist['field']
        subfield = scientist.get('subfield', '')
        archetype = scientist.get('archetype', 'Distinguished Researcher')
        achievements = scientist.get('achievements', '')
        summary = scientist.get('summary', '')
        moments = scientist.get('moments', [])
        working_style = scientist.get('working_style', '')

        # Build matching traits explanation
        trait_explanations = []
        for t in matching[:4]:
            dim = t['dimension']
            if t['match_type'] == 'exact':
                desc = t.get('description', '')
                trait_explanations.append(f"- {dim}: Both you and {name} {desc}")
            else:
                user_desc = t.get('user_desc', '')
                sci_desc = t.get('scientist_desc', '')
                trait_explanations.append(f"- {dim}: You {user_desc}, while {name} {sci_desc} - related approaches")

        trait_text = "\n".join(trait_explanations)

        prompt = f"""Match a quiz-taker with {name}, an Indian scientist.

BIO DATA:
Name: {name} | Field: {field} - {subfield} | Archetype: "{archetype}"
Achievements: {achievements[:500]}
Summary: {summary[:400]}
Moments: {json.dumps(moments[:3])}
Working Style: {working_style[:200]}

SHARED TRAITS: {trait_text}
DIFFERENCES: {json.dumps(differing[:1])}

Return JSON with SHORT, PUNCHY content. Each explanation should be 1-2 sentences MAX. Be specific - use real facts, awards, discoveries.

{{
    "match_quality": "Deep Resonance" or "Kindred Spirit" or "Parallel Paths",
    "resonances": [
        {{"trait": "TraitName", "explanation": "1-2 sentences. Connect user's trait to ONE specific fact about {name}."}},
        {{"trait": "TraitName", "explanation": "1-2 sentences with specific connection."}}
    ],
    "contrasts": [
        {{"trait": "TraitName", "explanation": "1 sentence on productive difference."}}
    ],
    "working_style": "2 sentences on {name}'s work habits. Be specific.",
    "character_moment": "1-2 sentences. ONE specific event from their life."
}}

Return ONLY valid JSON. Keep it concise."""

        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()

            if text.startswith('```'):
                text = text.split('```')[1]
                if text.startswith('json'):
                    text = text[4:]
            text = text.strip()

            result = json.loads(text)
            print(f"[AI] GEMINI GENERATED for {name}")
            return result

        except Exception as e:
            print(f"[FALLBACK] Using template for {name}: {e}")
            # RICH FALLBACK using actual biographical data and user's specific answers
            resonances = []
            for t in matching[:3]:
                resonances.append(self.build_rich_resonance(name, t, summary, achievements, moments, user_profile))

            # Dimension-specific keywords for finding relevant contrast evidence
            dimension_keywords = {
                "risk": ["bold", "daring", "cautious", "careful", "risk", "unconventional", "pioneering", "revolutionary"],
                "approach": ["theoretical", "experimental", "practical", "applied", "mathematical", "observation"],
                "collaboration": ["team", "solo", "alone", "collaborated", "partner", "independent", "mentored"],
                "motivation": ["curiosity", "impact", "society", "recognition", "award", "duty", "service"],
                "adversity": ["struggle", "obstacle", "challenge", "overcame", "persisted", "adapted"],
                "breadth": ["specialized", "broad", "interdisciplinary", "focused", "diverse"],
                "authority": ["institution", "independent", "established", "founded", "challenged"],
                "communication": ["published", "lecture", "wrote", "presented", "taught"],
                "time_horizon": ["long-term", "immediate", "vision", "future", "decades"],
                "resources": ["minimal", "frugal", "funded", "resources", "budget"],
                "legacy": ["students", "institution", "discovery", "movement", "influence"],
                "failure": ["failed", "setback", "learned", "adapted", "retry"]
            }

            # Build contrast explanation with relevant evidence
            contrasts = []
            for d in differing[:1]:
                dim = d['dimension']
                dim_title = dim.replace('_', ' ').title()
                user_desc = d.get('user_desc', 'take one approach')
                sci_desc = d.get('scientist_desc', 'took another path')
                keywords = dimension_keywords.get(dim, [])
                contrast_evidence = self._find_evidence(summary, achievements, keywords) if keywords else ""
                if not contrast_evidence:
                    contrast_evidence = ""
                contrasts.append({
                    "trait": dim_title,
                    "explanation": f"You {user_desc.replace('thrives', 'thrive').replace('excels', 'excel').replace('finds', 'find').replace('goes', 'go').replace('learns', 'learn').replace('works', 'work').replace('builds', 'build').replace('challenges', 'challenge').replace('creates', 'create').replace('lets', 'let').replace('enjoys', 'enjoy').replace('focuses', 'focus').replace('thinks', 'think').replace('needs', 'need').replace('secures', 'secure').replace('achieves', 'achieve').replace('treats', 'treat').replace('tries', 'try').replace('looks', 'look').replace('moves', 'move').replace('prefers', 'prefer').replace('embraces', 'embrace').replace('adapts', 'adapt').replace('responds', 'respond').replace('maintains', 'maintain').replace('pursues', 'pursue').replace('communicates', 'communicate').replace('demonstrates', 'demonstrate').replace('takes', 'take').replace('uses', 'use')}, while {name} {sci_desc}. This difference can expand your perspective."
                })

            # Build working style from actual data - NEVER show generic placeholder
            if working_style and len(working_style) > 50 and "Made significant contributions" not in working_style and "significant contributions" not in working_style.lower():
                style_text = working_style
            else:
                # Build from archetype and field - make it specific
                archetype_styles = {
                    "Experimental Pioneer": f"Known for rigorous hands-on experimentation and meticulous lab work in {field}.",
                    "Theoretical Visionary": f"Approached {field} through deep mathematical reasoning and theoretical frameworks.",
                    "Institution Builder": f"Combined research excellence with building lasting institutions in {field}.",
                    "Distinguished Researcher": f"Maintained high standards of research excellence throughout their career in {field}.",
                    "Intuitive Visionary": f"Known for bold, intuitive leaps in {field} that others later proved correct.",
                    "Contemporary Leader": f"Leads by example in {field}, balancing research with mentorship."
                }
                style_text = archetype_styles.get(archetype, f"A dedicated researcher who advanced the field of {field}.")

            # Find best defining moment (prefer significant achievements over mundane facts)
            # Skip truncated sentences (ending with abbreviations like "M.", "Ph.", "Dr.", etc.)
            def is_complete_sentence(s):
                if not s or len(s) < 30:
                    return False
                # Check if sentence is truncated (ends with common abbreviations)
                truncated_endings = [' M.', ' B.', ' Ph.', ' Dr.', ' Prof.', ' Mr.', ' Mrs.', ' Ms.', ' Jr.', ' Sr.', ' St.', ' vs.', ' etc.', ' i.e.', ' e.g.']
                for ending in truncated_endings:
                    if s.rstrip().endswith(ending):
                        return False
                return True

            moment_text = None
            # Skip patterns that indicate Wikipedia intro, not a defining moment
            intro_patterns = ['is an indian', 'was an indian', 'is a indian', 'was a indian',
                             'born on', 'born in', '(born', 'is an american', 'was an american',
                             'is a scientist', 'was a scientist', 'who headed', 'who served']

            if moments:
                # First try to find a significant complete moment
                for m in moments:
                    if not is_complete_sentence(m):
                        continue
                    m_lower = m.lower()
                    # Skip intro-style sentences
                    if any(p in m_lower for p in intro_patterns):
                        continue
                    if any(word in m_lower for word in ['award', 'prize', 'discovered', 'invented', 'founded', 'breakthrough', 'published', 'first', 'developed', 'pioneered', 'became', 'led', 'launched']):
                        moment_text = m
                        break
                # Fall back to first complete non-intro moment
                if not moment_text:
                    for m in moments:
                        if is_complete_sentence(m):
                            m_lower = m.lower()
                            if not any(p in m_lower for p in intro_patterns):
                                moment_text = m
                                break

            # If still no moment, try to find from summary (skip first sentence which is usually intro)
            if not moment_text and summary:
                sentences = summary.split('.')
                for s in sentences[1:4]:  # Skip first sentence, check next 3
                    s = s.strip()
                    if len(s) > 40 and len(s) < 200:
                        s_lower = s.lower()
                        if not any(p in s_lower for p in intro_patterns):
                            if any(word in s_lower for word in ['first', 'founded', 'led', 'became', 'award', 'pioneered', 'discovered', 'developed']):
                                moment_text = s + "."
                                break

            if not moment_text:
                # Use archetype-based moment as last resort
                archetype_moments = {
                    "Experimental Pioneer": f"Pioneered groundbreaking experimental techniques in {field}.",
                    "Theoretical Visionary": f"Developed influential theoretical frameworks in {field}.",
                    "Institution Builder": f"Founded key research institutions advancing {field} in India.",
                    "Distinguished Researcher": f"Received major recognition for contributions to {field}.",
                    "Contemporary Leader": f"Currently leading transformative initiatives in {field}."
                }
                moment_text = archetype_moments.get(archetype, f"Made lasting contributions to {field}.")

            return {
                "match_quality": "Deep Resonance" if match['score'] > 0.7 else ("Kindred Spirit" if match['score'] > 0.5 else "Parallel Paths"),
                "resonances": resonances,
                "contrasts": contrasts if contrasts else [],
                "working_style": style_text,
                "character_moment": moment_text
            }

    def get_full_matches(self, user_profile: dict, domain: str = None) -> list:
        """Get full match results with rich narratives"""
        matches = self.find_matches(user_profile, domain)

        results = []
        for match in matches:
            scientist = match['scientist']
            narrative = self.generate_rich_narrative(user_profile, match)

            # Build Wikipedia URL from wiki_title
            wiki_title = scientist.get('wiki_title', scientist['name'].replace(' ', '_'))
            wiki_url = f"https://en.wikipedia.org/wiki/{wiki_title.replace(' ', '_')}"

            results.append({
                "name": scientist['name'],
                "field": scientist['field'],
                "subfield": scientist.get('subfield', ''),
                "archetype": scientist.get('archetype', ''),
                "era": scientist.get('era', ''),
                "achievements": scientist.get('achievements', ''),
                "score": match['score'],
                "match_quality": narrative.get('match_quality', 'Kindred Spirit'),
                "resonances": narrative.get('resonances', []),
                "contrasts": narrative.get('contrasts', []),
                "working_style": narrative.get('working_style', ''),
                "character_moment": narrative.get('character_moment', ''),
                "summary": scientist.get('summary', ''),
                "moments": scientist.get('moments', []),
                "wiki_url": wiki_url
            })

        return results


if __name__ == "__main__":
    engine = MatchingEngineV3()

    test_profile = {
        "approach": "theoretical",
        "collaboration": "solo",
        "risk": "bold",
        "motivation": "curiosity",
        "adversity": "persist",
        "breadth": "specialist",
        "authority": "independent",
        "communication": "reserved",
        "time_horizon": "eternal",
        "resources": "frugal",
        "legacy": "knowledge",
        "failure": "persistent"
    }

    print("Testing theoretical solo researcher...")
    matches = engine.get_full_matches(test_profile, domain="cosmos")

    for m in matches:
        print(f"\n=== {m['name']} ===")
        print(f"Match Quality: {m['match_quality']}")
        print(f"Archetype: {m['archetype']}")
        print(f"\nWhy You Match:")
        for r in m['resonances']:
            print(f"  • {r['trait']}: {r['explanation'][:100]}...")

# Scientist Twin Matching Algorithm Documentation

## Overview

The Scientist Twin quiz uses a sophisticated 12-dimension personality matching system to pair users with Indian scientists who share similar traits, working styles, and approaches to discovery.

## 12 Trait Dimensions

Each quiz question maps to one of 12 carefully chosen dimensions that differentiate scientists:

### 1. **Approach** (Problem-Solving Style)
- **theoretical**: Mathematical reasoning, abstract thinking
- **experimental**: Hands-on experimentation, empirical validation
- **applied**: Practical applications, real-world impact
- **observational**: Pattern recognition, careful observation

### 2. **Collaboration** (Working Style)
- **solo**: Thrives working independently
- **small_team**: Works best with few trusted collaborators
- **large_team**: Excels at orchestrating large efforts
- **mentor**: Finds fulfillment in teaching while researching

### 3. **Risk** (Risk Tolerance)
- **conservative**: Prefers proven paths with strong evidence
- **calculated**: Carefully weighs risks before committing
- **bold**: Embraces unconventional ideas and breakthrough thinking
- **hedged**: Explores risky ideas while maintaining safer alternatives

### 4. **Motivation** (Primary Driver)
- **curiosity**: Driven by joy of understanding
- **impact**: Motivated by making tangible difference
- **recognition**: Seeks acknowledgment and validation
- **duty**: Driven by responsibility to country/community

### 5. **Adversity** (Response to Setbacks)
- **persist**: Responds with redoubled determination
- **pivot**: Adapts fluidly when facing barriers
- **fight**: Directly challenges unfair systems
- **accept**: Philosophically accepts setbacks while staying focused

### 6. **Breadth** (Knowledge Style)
- **specialist**: Goes extremely deep in one focused area
- **generalist**: Learns broadly across many fields
- **interdisciplinary**: Works at intersection of multiple fields
- **expanding**: Starts deep then gradually expands scope

### 7. **Authority** (Relationship with Institutions)
- **independent**: Works best outside traditional structures
- **institutional**: Builds and strengthens institutions
- **reformer**: Challenges norms while working within systems
- **revolutionary**: Creates entirely new frameworks

### 8. **Communication** (Style of Sharing Ideas)
- **reserved**: Lets work speak for itself
- **charismatic**: Enjoys explaining ideas to broad audiences
- **written**: Communicates through detailed documentation
- **demonstrative**: Shows rather than tells through building

### 9. **Time Horizon** (Temporal Perspective)
- **immediate**: Focuses on urgent problems needing solutions now
- **medium**: Thinks in terms of achievable multi-year goals
- **long_term**: Maintains decades-spanning vision
- **eternal**: Pursues timeless questions transcending eras

### 10. **Resources** (Resource Philosophy)
- **frugal**: Achieves great things with minimal resources
- **adequate**: Needs reasonable resources, avoids excess
- **abundant**: Secures big resources for big problems
- **ideas_first**: Focuses on ideas, lets resources follow

### 11. **Legacy** (What They Want to Leave Behind)
- **knowledge**: Wants discoveries that outlast them
- **people**: Values students and people influenced
- **institutions**: Builds systems that continue their work
- **movement**: Seeks to change how society thinks

### 12. **Failure** (Relationship with Failure)
- **analytical**: Treats failures as data points for analysis
- **persistent**: Tries again with modifications until success
- **serendipitous**: Looks for unexpected discoveries in failures
- **pragmatic**: Moves on quickly to more promising directions

## Scoring Algorithm

### Match Score Calculation

For each scientist in the database, we calculate a match score using this formula:

```
score = (exact_matches × 1.0 + related_matches × 0.5) / total_dimensions
```

Where:
- **exact_matches**: Number of dimensions where user and scientist have identical trait values
- **related_matches**: Number of dimensions where traits are related (see Related Pairs below)
- **total_dimensions**: Always 12

**Example:**
- 8 exact matches + 2 related matches = (8 × 1.0 + 2 × 0.5) / 12 = 9/12 = **0.75 (75% match)**

### Related Trait Pairs

Certain trait values within the same dimension are considered "related" and receive partial credit (0.5):

| Dimension | Related Pairs |
|-----------|--------------|
| approach | (theoretical, observational), (experimental, applied) |
| collaboration | (solo, small_team), (large_team, mentor) |
| risk | (calculated, hedged), (bold, calculated) |
| motivation | (curiosity, recognition), (impact, duty) |
| adversity | (persist, fight), (pivot, accept) |
| breadth | (generalist, interdisciplinary), (specialist, expanding) |
| authority | (independent, reformer), (institutional, reformer) |
| communication | (written, reserved), (charismatic, demonstrative) |
| time_horizon | (medium, long_term), (long_term, eternal) |
| resources | (frugal, adequate), (adequate, abundant) |
| legacy | (knowledge, people), (institutions, movement) |
| failure | (analytical, pragmatic), (persistent, serendipitous) |

## Domain Filtering

The quiz allows users to choose a scientific domain, which filters the candidate pool:

| Domain | Included Fields |
|--------|----------------|
| **Cosmos** | Physics, Space Science, Astrophysics, Astronomy, Aerospace |
| **Quantum & Math** | Physics, Mathematics, Computer Science |
| **Chemistry** | Chemistry, Material Science, Biochemistry |
| **Life Sciences** | Biology, Medicine, Neuroscience, Genetics |
| **Earth & Environment** | Environmental Science, Agriculture, Ecology, Earth Science |
| **Engineering & Tech** | Engineering, Technology, Computer Science, Aerospace |

## Match Quality Labels

Based on the final score, matches are labeled:

- **Deep Resonance**: score > 0.70 (70%+)
- **Kindred Spirit**: 0.50 < score ≤ 0.70 (50-70%)
- **Parallel Paths**: score ≤ 0.50 (<50%)

## Anti-Repetition System

To ensure variety across multiple quiz attempts, even with identical answers:

### How It Works

1. **Session Tracking**: Store the last 9 shown scientist names in Flask session
   - Covers approximately 3 quiz attempts (3 matches × 3 attempts = 9)

2. **Top-Tier Pool**: Define "top tier" as scientists within 15% of the best score
   - If best score is 0.80, top tier includes all scientists with score ≥ 0.68

3. **Prioritization Logic**:
   ```
   IF fresh scientists ≥ 3 in top tier:
       Randomize among fresh scientists, return top 3
   ELSE IF fresh scientists > 0:
       Mix fresh + recently shown, randomize, return top 3
   ELSE:
       All top tier were recently shown → randomize to vary order
   ```

4. **Result**: Users with identical answers will see different scientists as their #1 match across attempts, while maintaining matching quality

### Benefits

- **Prevents Skewing**: Ensures all 500+ scientists get distributed fairly
- **Maintains Quality**: Only randomizes among high-quality matches (top 15%)
- **Variety**: Even power users taking quiz multiple times see fresh results
- **No Gaming**: Can't "farm" for a specific scientist by retaking

## Technical Implementation

### File: `matching_engine_v3.py`

**Key Methods:**

1. **`calculate_match_score(user_profile, scientist)`**
   - Returns: (score, matching_traits, differing_traits)
   - Iterates through 12 dimensions
   - Checks for exact and related matches

2. **`find_matches(user_profile, domain_filter, top_n, recently_shown)`**
   - Filters by domain
   - Calculates scores for all candidates
   - Applies anti-repetition logic
   - Returns top N matches

3. **`get_full_matches(user_profile, domain, recently_shown)`**
   - Calls find_matches()
   - Generates rich narratives using Gemini AI
   - Returns complete match results with explanations

### File: `web_app_v3.py`

**Route: `/api/get-matches`**
- Retrieves `recently_shown_scientists` from session
- Calls `matching_engine.get_full_matches()` with anti-repetition
- Updates session with newly shown scientists
- Maintains last 9 entries in session

## Database Structure

Each scientist in `scientist_db_rich.json` contains:

```json
{
  "name": "Scientist Name",
  "field": "Physics",
  "subfield": "Astrophysics",
  "era": "1910-1995",
  "archetype": "Theoretical Visionary",
  "traits": {
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
    "failure": "analytical"
  },
  "summary": "Biography text...",
  "achievements": "Key accomplishments...",
  "working_style": "How they worked...",
  "moments": ["Defining moment 1", "Defining moment 2"],
  "image_url": "https://...",
  "wiki_title": "Wikipedia_Article_Title"
}
```

## Performance Characteristics

- **Database Size**: 500+ scientists with rich biographical data
- **Average Matching Time**: <100ms per quiz completion
- **Match Quality**: Typical top match score ranges from 0.65-0.85
- **Coverage**: Anti-repetition ensures all scientists appear over time

## Quality Assurance

### Match Validation

The system ensures quality through:

1. **Multi-dimensional matching** prevents one-dimensional stereotyping
2. **Related pairs** acknowledge spectrum of traits rather than binary choices
3. **Domain filtering** maintains relevance to user's interests
4. **Score thresholds** prevent poor matches from being labeled "Deep Resonance"

### Narrative Generation

Match explanations are generated using:
- **Gemini AI** for rich, contextual narratives (primary)
- **Template fallback** using actual biographical data (backup)
- **Sentence filtering** removes Wikipedia-style intro boilerplate
- **Evidence extraction** pulls specific facts to support trait matches

## Future Enhancements

Potential improvements to consider:

1. **Weighted Dimensions**: Allow certain traits to carry more weight
2. **Cultural Context**: Add region/language preferences
3. **Historical Era Preferences**: Let users filter by time period
4. **Dynamic Thresholds**: Adjust top-tier percentage based on domain size
5. **Machine Learning**: Train on user feedback to improve matching

---

**Last Updated**: January 2026
**Version**: 3.0
**Maintained by**: SciRio Team

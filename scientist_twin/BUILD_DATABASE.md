# Building the 500 Scientist Database

This guide explains how to generate the comprehensive database of 500+ Indian scientists with rich vector profiles.

## Quick Start

```bash
# Generate database with 50 scientists (for testing)
python database_builder.py 50

# Generate full database with 500 scientists
python database_builder.py 500
```

## What the Builder Does

The `database_builder.py` script:

1. **Fetches Wikipedia Data**: Uses Wikipedia API to get full biographies
2. **Extracts Comprehensive Profiles**: Uses Gemini AI to analyze each biography across 10 dimensions:
   - Early life & background
   - Educational path
   - Working style
   - Response to adversity
   - Career choices
   - Social impact orientation
   - Values & philosophy
   - Career trajectory
   - Work-life integration
   - Legacy focus

3. **Creates Rich Vectors**: For each scientist, generates:
   - 50+ quantifiable data points
   - Specific evidence from their biography
   - Concrete examples of traits
   - Personality summary
   - Key life moments
   - Archetype classification

4. **Saves to JSON**: Outputs `scientist_db_comprehensive.json`

## Database Schema

Each scientist entry contains:

```json
{
  "name": "Scientist Name",
  "domain": "quantum|cosmos|life|earth|engineering",
  "wikipedia_title": "Wikipedia_Page_Title",
  "wikipedia_url": "https://...",
  "biography_length": 5000,

  "comprehensive_profile": {
    "early_life": {
      "socioeconomic_background": {
        "rating": "underprivileged",
        "evidence": ["Grew up in poverty...", "Father was laborer..."]
      },
      "family_support": {...},
      "access_to_resources": {...},
      "geographic_context": {...}
    },
    "educational_path": {...},
    "working_style": {...},
    "adversity_response": {...},
    "career_choices": {...},
    "social_impact": {...},
    "values_philosophy": {...},
    "career_trajectory": {...},
    "work_life": {...},
    "legacy": {...}
  },

  "personality_summary": "3-4 sentence narrative",
  "key_life_moments": ["moment 1", "moment 2", ...],
  "archetype": "One phrase descriptor"
}
```

## Time & Cost Estimates

### For 50 Scientists:
- **Time**: 60-90 minutes
- **API Calls**: ~100 Gemini requests
- **Cost**: ~$2-5 (depending on Gemini API pricing)

### For 500 Scientists:
- **Time**: 10-15 hours (can run overnight)
- **API Calls**: ~1000 Gemini requests
- **Cost**: ~$20-50

## Monitoring Progress

The builder shows real-time progress:

```
Building database of 500 scientists...

[cyan]Processing: C. V. Raman[/cyan]
[green]✓ C. V. Raman[/green]

[cyan]Processing: Srinivasa Ramanujan[/cyan]
[green]✓ Srinivasa Ramanujan[/green]

[cyan]Processing: Unknown Scientist[/cyan]
[yellow]✗ Unknown Scientist - insufficient data[/yellow]

[====================] 45% 225/500 [00:45:00 remaining]
```

## Handling Failures

Some Wikipedia articles may be:
- Too short (< 500 words)
- Missing or deleted
- Protected/restricted

The builder will:
- Skip scientists with insufficient data
- Log failures
- Continue processing others
- Report final stats

## Quality Control

After generation, review the database:

```python
import json

with open('scientist_db_comprehensive.json') as f:
    db = json.load(f)

# Check counts by domain
from collections import Counter
domains = Counter(s['domain'] for s in db)
print(domains)

# Check profile completeness
incomplete = [s for s in db if len(s.get('comprehensive_profile', {})) < 5]
print(f"Incomplete profiles: {len(incomplete)}")

# Check biography length distribution
lengths = [s['biography_length'] for s in db]
print(f"Avg biography length: {sum(lengths)/len(lengths):.0f} words")
```

## Expanding the Database

To add more scientists:

1. **Edit `database_builder.py`**:
   - Add names to `get_indian_scientist_names()` function
   - Organize by domain/field

2. **Run incremental build**:
   ```python
   # In database_builder.py, modify to append mode
   # Then run with new scientist names only
   ```

3. **Verify quality**:
   - Check generated profiles
   - Ensure sufficient biographical detail

## Using the Database

Once generated, use it with the enhanced matcher:

```python
from enhanced_matching import EnhancedMatcher

matcher = EnhancedMatcher('scientist_db_comprehensive.json')
matches = matcher.find_deep_matches(user_profile, num_matches=3)
```

## Troubleshooting

**"API Error"**: Check Gemini API key in `config.py`

**"Wikipedia 403"**: Wikipedia is rate-limiting - add delays between requests

**"Insufficient data"**: Scientist has stub article - skip or find better sources

**"JSON parse error"**: Gemini output malformed - implement retry logic

## Performance Optimization

For faster builds:

1. **Batch processing**: Process in chunks of 50
2. **Parallel requests**: Use asyncio for concurrent Wikipedia fetches
3. **Caching**: Save intermediate results
4. **Resume capability**: Track progress and resume from failures

## Next Steps

After building the database:

1. Test with `main_enhanced.py`
2. Verify match quality
3. Refine extraction prompts if needed
4. Expand to 500+ scientists
5. Deploy for India Science Fest!

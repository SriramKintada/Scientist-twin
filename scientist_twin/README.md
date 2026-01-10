# 🔬 Scientist Twin 2.0

*A Psychological Sorting Hat for the India Science Fest*

Match yourself with legendary Indian scientists through AI-powered personality analysis and biographical interpretation.

## ✨ Features

- **Tailored Psychological Quiz**: Questions adapted to your scientific domain
- **8-Trait Personality Profiling**: Persistence, Risk-Taking, Intuition, Logic, Collaboration, Social Impact, Resilience, Creativity
- **Interpretive AI Matching**: Uses Google Gemini to find biographical parallels
- **12+ Curated Scientists**: From Ramanujan to Tessy Thomas
- **Beautiful CLI Output**: Rich markdown formatting with resonance analysis

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### Run the App

```bash
cd scientist_twin
python main.py
```

## 🎯 How It Works

1. **Choose Your Domain**: Cosmos, Life & Biology, Quantum Logic, Earth & Environment, or Engineering
2. **Select Impact Style**: Theoretical Discovery, Societal Change, Engineering Feats, or Education
3. **Take the Quiz**: 6 scenario-based questions tailored to your interests
4. **Get Matched**: AI analyzes 12+ scientists to find your closest match
5. **Discover**: Learn about resonances, contrasts, and shared working styles

## 🧬 The Science Behind It

This app uses **interpretive matching**, not algorithmic scoring:

- Each scientist's biography is pre-analyzed for personality indicators
- Your quiz responses generate an 8-dimensional trait profile
- Google Gemini AI interprets biographical narratives to find meaningful parallels
- Wikipedia provides rich biographical context for each match

**Important**: This is a creative exploration tool, not a clinical assessment.

## 📊 Database

Currently includes:
- **C.V. Raman** - Nobel laureate physicist
- **Srinivasa Ramanujan** - Mathematical genius
- **A.P.J. Abdul Kalam** - Aerospace engineer & President
- **Homi J. Bhabha** - Nuclear physicist & institution builder
- **Vikram Sarabhai** - Space research visionary
- **Subrahmanyan Chandrasekhar** - Astrophysicist
- **Salim Ali** - Ornithologist
- **Har Gobind Khorana** - Molecular biologist
- **Tessy Thomas** - Missile scientist
- **Yellapragada Subbarow** - Biochemist
- **M.S. Swaminathan** - Agricultural scientist
- **Jagadish Chandra Bose** - Physicist & biologist

## 🔧 Configuration

API key is configured in `config.py`. To use your own Gemini API key:

```python
GEMINI_API_KEY = "your-api-key-here"
```

## 📝 Output Format

### Primary Match
- **Match Strength**: Deep Resonance / Parallel Paths / Kindred Spirits
- **Resonances**: 2-3 personality traits you share
- **Contrasts**: Where you differ
- **Working Style Summary**: How you'd approach problems similarly
- **Character Moment**: A specific biographical anecdote that mirrors your traits

### Alternative Matches
- 2 additional scientist matches
- Brief resonance explanations
- Wikipedia links for further reading

### Technical Transparency
- Your full 8-trait score breakdown
- Visual bar chart
- Domain and impact style selection

## 🎨 Design Philosophy

**Option A: Lean Into Interpretation**

We embrace that this is AI-powered creative matching, not hard science:
- Transparent messaging about interpretive nature
- Qualitative match descriptions instead of false-precision percentages
- Focus on storytelling and discovery over algorithmic accuracy

The goal: Help users discover Indian scientists they've never heard of through a personalized, engaging narrative.

## 🛠️ Technical Stack

- **Python 3.8+**
- **Google Generative AI (Gemini Pro)**: For question generation and matching
- **Wikipedia API**: For biographical data
- **Rich**: For beautiful CLI output

## 📈 Future Enhancements

- Expand to 100+ scientists
- Multi-language support (Hindi, Tamil, etc.)
- Web interface
- Export match results as shareable cards
- Batch pre-processing for faster matches

## 🤝 Contributing

Built for the India Science Fest. To expand the scientist database:

1. Add entries to `scientist_db.json`
2. Follow the existing schema
3. Include: name, domain, trait_summary, personality_summary, key_moments
4. Add Wikipedia title for automatic enrichment

## 📄 License

MIT License - Built for educational and cultural purposes

## 🙏 Acknowledgments

- Wikipedia for biographical data
- Google Generative AI for interpretive matching
- All the incredible Indian scientists who inspire us

---

*"Science is a way of thinking much more than it is a body of knowledge." - Carl Sagan*

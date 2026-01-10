"""
Build Rich Scientist Database - Real Scientists with Wikipedia Data
Focus on quality over quantity - ~200 well-documented scientists
"""

import json
import time

# Comprehensive list of REAL Indian scientists with their Wikipedia article titles
REAL_SCIENTISTS = [
    # Mathematics
    {"name": "Srinivasa Ramanujan", "wiki": "Srinivasa Ramanujan", "field": "Mathematics", "subfield": "Number Theory"},
    {"name": "Shakuntala Devi", "wiki": "Shakuntala Devi", "field": "Mathematics", "subfield": "Mental Calculation"},
    {"name": "C. R. Rao", "wiki": "C. R. Rao", "field": "Mathematics", "subfield": "Statistics"},
    {"name": "Harish-Chandra", "wiki": "Harish-Chandra", "field": "Mathematics", "subfield": "Representation Theory"},
    {"name": "S. S. Shrikhande", "wiki": "S. S. Shrikhande", "field": "Mathematics", "subfield": "Combinatorics"},
    {"name": "M. S. Narasimhan", "wiki": "M. S. Narasimhan", "field": "Mathematics", "subfield": "Algebraic Geometry"},
    {"name": "C. S. Seshadri", "wiki": "C. S. Seshadri", "field": "Mathematics", "subfield": "Algebraic Geometry"},
    {"name": "Raghunath Purushottam Paranjape", "wiki": "R. P. Paranjape", "field": "Mathematics", "subfield": "Analysis"},
    {"name": "D. D. Kosambi", "wiki": "Damodar Dharmananda Kosambi", "field": "Mathematics", "subfield": "Statistics"},
    {"name": "Manjul Bhargava", "wiki": "Manjul Bhargava", "field": "Mathematics", "subfield": "Number Theory"},
    {"name": "Akshay Venkatesh", "wiki": "Akshay Venkatesh", "field": "Mathematics", "subfield": "Number Theory"},

    # Physics - Theoretical
    {"name": "Satyendra Nath Bose", "wiki": "Satyendra Nath Bose", "field": "Physics", "subfield": "Quantum Statistics"},
    {"name": "Subrahmanyan Chandrasekhar", "wiki": "Subrahmanyan Chandrasekhar", "field": "Physics", "subfield": "Astrophysics"},
    {"name": "C. V. Raman", "wiki": "C. V. Raman", "field": "Physics", "subfield": "Spectroscopy"},
    {"name": "Meghnad Saha", "wiki": "Meghnad Saha", "field": "Physics", "subfield": "Astrophysics"},
    {"name": "Homi J. Bhabha", "wiki": "Homi J. Bhabha", "field": "Physics", "subfield": "Nuclear Physics"},
    {"name": "Vikram Sarabhai", "wiki": "Vikram Sarabhai", "field": "Physics", "subfield": "Space Science"},
    {"name": "G. N. Ramachandran", "wiki": "G. N. Ramachandran", "field": "Physics", "subfield": "Biophysics"},
    {"name": "E. C. George Sudarshan", "wiki": "E. C. George Sudarshan", "field": "Physics", "subfield": "Quantum Optics"},
    {"name": "Jayant Narlikar", "wiki": "Jayant Narlikar", "field": "Physics", "subfield": "Cosmology"},
    {"name": "Ashoke Sen", "wiki": "Ashoke Sen", "field": "Physics", "subfield": "String Theory"},
    {"name": "Sandip Trivedi", "wiki": "Sandip Trivedi", "field": "Physics", "subfield": "String Theory"},
    {"name": "Thanu Padmanabhan", "wiki": "Thanu Padmanabhan", "field": "Physics", "subfield": "Cosmology"},
    {"name": "Bibha Chowdhuri", "wiki": "Bibha Chowdhuri", "field": "Physics", "subfield": "Particle Physics"},
    {"name": "Raja Ramanna", "wiki": "Raja Ramanna", "field": "Physics", "subfield": "Nuclear Physics"},

    # Chemistry
    {"name": "Prafulla Chandra Ray", "wiki": "Prafulla Chandra Ray", "field": "Chemistry", "subfield": "Inorganic Chemistry"},
    {"name": "Asima Chatterjee", "wiki": "Asima Chatterjee", "field": "Chemistry", "subfield": "Organic Chemistry"},
    {"name": "C. N. R. Rao", "wiki": "C. N. R. Rao", "field": "Chemistry", "subfield": "Materials Science"},
    {"name": "Shanti Swaroop Bhatnagar", "wiki": "Shanti Swaroop Bhatnagar", "field": "Chemistry", "subfield": "Physical Chemistry"},
    {"name": "Venkatraman Ramakrishnan", "wiki": "Venkatraman Ramakrishnan", "field": "Chemistry", "subfield": "Structural Biology"},
    {"name": "G. D. Yadav", "wiki": "Ganapati Dadasaheb Yadav", "field": "Chemistry", "subfield": "Chemical Engineering"},
    {"name": "Darshan Ranganathan", "wiki": "Darshan Ranganathan", "field": "Chemistry", "subfield": "Bioorganic Chemistry"},
    {"name": "K. S. Krishnan", "wiki": "Kariamanickam Srinivasa Krishnan", "field": "Physics", "subfield": "Spectroscopy"},

    # Biology & Medicine
    {"name": "Har Gobind Khorana", "wiki": "Har Gobind Khorana", "field": "Biology", "subfield": "Molecular Biology"},
    {"name": "Yellapragada Subbarow", "wiki": "Yellapragada Subbarow", "field": "Medicine", "subfield": "Biochemistry"},
    {"name": "Salim Ali", "wiki": "Sálim Ali", "field": "Biology", "subfield": "Ornithology"},
    {"name": "M. S. Swaminathan", "wiki": "M. S. Swaminathan", "field": "Biology", "subfield": "Agricultural Science"},
    {"name": "Verghese Kurien", "wiki": "Verghese Kurien", "field": "Biology", "subfield": "Dairy Science"},
    {"name": "Birbal Sahni", "wiki": "Birbal Sahni", "field": "Biology", "subfield": "Paleobotany"},
    {"name": "Janaki Ammal", "wiki": "Janaki Ammal", "field": "Biology", "subfield": "Botany"},
    {"name": "Obaid Siddiqi", "wiki": "Obaid Siddiqi", "field": "Biology", "subfield": "Neurobiology"},
    {"name": "Ganapathi Thanikaimoni", "wiki": "Ganapathi Thanikaimoni", "field": "Biology", "subfield": "Palynology"},
    {"name": "Kamal Ranadive", "wiki": "Kamal Ranadive", "field": "Medicine", "subfield": "Cancer Research"},
    {"name": "V. Shanta", "wiki": "V. Shanta", "field": "Medicine", "subfield": "Oncology"},
    {"name": "Sujatha Ramdorai", "wiki": "Sujatha Ramdorai", "field": "Mathematics", "subfield": "Number Theory"},

    # Space Science & Aerospace
    {"name": "A. P. J. Abdul Kalam", "wiki": "A. P. J. Abdul Kalam", "field": "Aerospace", "subfield": "Missile Technology"},
    {"name": "Satish Dhawan", "wiki": "Satish Dhawan", "field": "Aerospace", "subfield": "Aerospace Engineering"},
    {"name": "U. R. Rao", "wiki": "U. R. Rao", "field": "Space Science", "subfield": "Satellite Technology"},
    {"name": "K. Kasturirangan", "wiki": "K. Kasturirangan", "field": "Space Science", "subfield": "Space Applications"},
    {"name": "G. Madhavan Nair", "wiki": "G. Madhavan Nair", "field": "Space Science", "subfield": "Satellite Technology"},
    {"name": "K. Radhakrishnan", "wiki": "K. Radhakrishnan", "field": "Space Science", "subfield": "Space Technology"},
    {"name": "Kalpana Chawla", "wiki": "Kalpana Chawla", "field": "Aerospace", "subfield": "Astronautics"},
    {"name": "Rakesh Sharma", "wiki": "Rakesh Sharma", "field": "Aerospace", "subfield": "Astronautics"},
    {"name": "Tessy Thomas", "wiki": "Tessy Thomas", "field": "Aerospace", "subfield": "Missile Technology"},
    {"name": "Ritu Karidhal", "wiki": "Ritu Karidhal", "field": "Space Science", "subfield": "Mission Design"},

    # Engineering & Technology
    {"name": "M. Visvesvaraya", "wiki": "M. Visvesvaraya", "field": "Engineering", "subfield": "Civil Engineering"},
    {"name": "C. V. Vishveshwara", "wiki": "C. V. Vishveshwara", "field": "Physics", "subfield": "General Relativity"},
    {"name": "Roddam Narasimha", "wiki": "Roddam Narasimha", "field": "Engineering", "subfield": "Fluid Dynamics"},
    {"name": "Sam Pitroda", "wiki": "Sam Pitroda", "field": "Technology", "subfield": "Telecommunications"},
    {"name": "Narinder Singh Kapany", "wiki": "Narinder Singh Kapany", "field": "Physics", "subfield": "Fiber Optics"},
    {"name": "Ajay Bhatt", "wiki": "Ajay Bhatt", "field": "Technology", "subfield": "Computer Architecture"},

    # Computer Science & AI
    {"name": "Raj Reddy", "wiki": "Raj Reddy", "field": "Computer Science", "subfield": "Artificial Intelligence"},
    {"name": "Rajeev Motwani", "wiki": "Rajeev Motwani", "field": "Computer Science", "subfield": "Algorithms"},
    {"name": "Manindra Agrawal", "wiki": "Manindra Agrawal", "field": "Computer Science", "subfield": "Computational Complexity"},
    {"name": "Vijay Vazirani", "wiki": "Vijay Vazirani", "field": "Computer Science", "subfield": "Algorithms"},
    {"name": "Umesh Vazirani", "wiki": "Umesh Vazirani", "field": "Computer Science", "subfield": "Quantum Computing"},
    {"name": "Shafi Goldwasser", "wiki": "Shafi Goldwasser", "field": "Computer Science", "subfield": "Cryptography"},
    {"name": "Arvind Krishna", "wiki": "Arvind Krishna", "field": "Technology", "subfield": "Cloud Computing"},
    {"name": "Satya Nadella", "wiki": "Satya Nadella", "field": "Technology", "subfield": "Cloud Computing"},
    {"name": "Sundar Pichai", "wiki": "Sundar Pichai", "field": "Technology", "subfield": "Internet Technology"},
    {"name": "Vinod Khosla", "wiki": "Vinod Khosla", "field": "Technology", "subfield": "Venture Capital"},

    # Agriculture & Environment
    {"name": "Norman Borlaug", "wiki": "Norman Borlaug", "field": "Agriculture", "subfield": "Plant Genetics"},  # Worked extensively in India
    {"name": "B. P. Pal", "wiki": "B. P. Pal", "field": "Agriculture", "subfield": "Plant Breeding"},
    {"name": "R. S. Paroda", "wiki": "Raj Singh Paroda", "field": "Agriculture", "subfield": "Agricultural Research"},
    {"name": "Vandana Shiva", "wiki": "Vandana Shiva", "field": "Environmental Science", "subfield": "Ecology"},
    {"name": "Madhav Gadgil", "wiki": "Madhav Gadgil", "field": "Environmental Science", "subfield": "Ecology"},
    {"name": "Raghunath Anant Mashelkar", "wiki": "Raghunath Anant Mashelkar", "field": "Chemistry", "subfield": "Polymer Science"},

    # Nuclear Science
    {"name": "Homi N. Sethna", "wiki": "Homi N. Sethna", "field": "Engineering", "subfield": "Nuclear Engineering"},
    {"name": "P. K. Iyengar", "wiki": "P. K. Iyengar", "field": "Physics", "subfield": "Nuclear Physics"},
    {"name": "Anil Kakodkar", "wiki": "Anil Kakodkar", "field": "Physics", "subfield": "Nuclear Physics"},
    {"name": "Sekharipuram Ramamritham", "wiki": "Srinivasan (scientist)", "field": "Physics", "subfield": "Nuclear Physics"},

    # Geology & Earth Sciences
    {"name": "D. N. Wadia", "wiki": "Darashaw Nosherwan Wadia", "field": "Earth Science", "subfield": "Geology"},
    {"name": "M. S. Krishnan", "wiki": "M. S. Krishnan", "field": "Earth Science", "subfield": "Geology"},

    # More Contemporary Scientists
    {"name": "Gagandeep Kang", "wiki": "Gagandeep Kang", "field": "Medicine", "subfield": "Virology"},
    {"name": "Soumya Swaminathan", "wiki": "Soumya Swaminathan", "field": "Medicine", "subfield": "Epidemiology"},
    {"name": "K. Sivan", "wiki": "K. Sivan", "field": "Space Science", "subfield": "Rocket Propulsion"},
    {"name": "S. Somanath", "wiki": "S. Somanath", "field": "Space Science", "subfield": "Rocket Engineering"},
    {"name": "Krishnaswamy VijayRaghavan", "wiki": "K. VijayRaghavan", "field": "Biology", "subfield": "Developmental Biology"},
    {"name": "Ram Sasisekharan", "wiki": "Ram Sasisekharan", "field": "Biology", "subfield": "Bioinformatics"},
    {"name": "Raghuram Rajan", "wiki": "Raghuram Rajan", "field": "Economics", "subfield": "Financial Economics"},
    {"name": "Abhijit Banerjee", "wiki": "Abhijit Banerjee", "field": "Economics", "subfield": "Development Economics"},
    {"name": "Esther Duflo", "wiki": "Esther Duflo", "field": "Economics", "subfield": "Development Economics"},  # Indian connection through work

    # Women in Science
    {"name": "Anna Mani", "wiki": "Anna Mani", "field": "Physics", "subfield": "Meteorology"},
    {"name": "Rajeshwari Chatterjee", "wiki": "Rajeshwari Chatterjee", "field": "Engineering", "subfield": "Electronics"},
    {"name": "Aditi Pant", "wiki": "Aditi Pant", "field": "Earth Science", "subfield": "Oceanography"},
    {"name": "Irawati Karmarkar", "wiki": "Irawati Karmarkar", "field": "Physics", "subfield": "Astronomy"},
    {"name": "Rohini Godbole", "wiki": "Rohini Godbole", "field": "Physics", "subfield": "Particle Physics"},
    {"name": "Kamala Sohonie", "wiki": "Kamala Sohonie", "field": "Chemistry", "subfield": "Biochemistry"},
    {"name": "Archana Bhattacharyya", "wiki": "Archana Bhattacharyya", "field": "Physics", "subfield": "Space Science"},

    # Historical Scientists
    {"name": "Jagadish Chandra Bose", "wiki": "Jagadish Chandra Bose", "field": "Physics", "subfield": "Biophysics"},
    {"name": "P. C. Mahalanobis", "wiki": "Prasanta Chandra Mahalanobis", "field": "Mathematics", "subfield": "Statistics"},
    {"name": "S. N. Bose", "wiki": "Satyendra Nath Bose", "field": "Physics", "subfield": "Quantum Mechanics"},
    {"name": "C. V. Raman", "wiki": "C. V. Raman", "field": "Physics", "subfield": "Spectroscopy"},

    # More Contemporary
    {"name": "Srinivasa S. R. Varadhan", "wiki": "S. R. Srinivasa Varadhan", "field": "Mathematics", "subfield": "Probability Theory"},
    {"name": "Bhama Srinivasan", "wiki": "Bhama Srinivasan", "field": "Mathematics", "subfield": "Representation Theory"},
    {"name": "Neena Gupta", "wiki": "Neena Gupta (mathematician)", "field": "Mathematics", "subfield": "Algebraic Geometry"},
]

# Detailed trait mapping based on biographical patterns
ARCHETYPE_TRAITS = {
    "Intuitive Visionary": {
        "approach": "theoretical", "collaboration": "solo", "risk": "bold",
        "motivation": "curiosity", "adversity": "persist", "breadth": "specialist",
        "authority": "independent", "communication": "reserved", "time_horizon": "eternal",
        "resources": "frugal", "legacy": "knowledge", "failure": "persistent"
    },
    "Steadfast Theorist": {
        "approach": "theoretical", "collaboration": "solo", "risk": "calculated",
        "motivation": "curiosity", "adversity": "accept", "breadth": "expanding",
        "authority": "independent", "communication": "written", "time_horizon": "eternal",
        "resources": "adequate", "legacy": "knowledge", "failure": "analytical"
    },
    "Institution Builder": {
        "approach": "applied", "collaboration": "large_team", "risk": "calculated",
        "motivation": "impact", "adversity": "persist", "breadth": "generalist",
        "authority": "institutional", "communication": "charismatic", "time_horizon": "long_term",
        "resources": "abundant", "legacy": "institutions", "failure": "pragmatic"
    },
    "Quiet Revolutionary": {
        "approach": "theoretical", "collaboration": "small_team", "risk": "bold",
        "motivation": "curiosity", "adversity": "persist", "breadth": "specialist",
        "authority": "independent", "communication": "reserved", "time_horizon": "eternal",
        "resources": "frugal", "legacy": "knowledge", "failure": "serendipitous"
    },
    "People's Scientist": {
        "approach": "applied", "collaboration": "mentor", "risk": "calculated",
        "motivation": "impact", "adversity": "fight", "breadth": "interdisciplinary",
        "authority": "reformer", "communication": "charismatic", "time_horizon": "long_term",
        "resources": "adequate", "legacy": "people", "failure": "pragmatic"
    },
    "Tech Visionary": {
        "approach": "applied", "collaboration": "large_team", "risk": "bold",
        "motivation": "impact", "adversity": "pivot", "breadth": "generalist",
        "authority": "institutional", "communication": "charismatic", "time_horizon": "medium",
        "resources": "abundant", "legacy": "movement", "failure": "pragmatic"
    },
    "Experimental Pioneer": {
        "approach": "experimental", "collaboration": "small_team", "risk": "bold",
        "motivation": "curiosity", "adversity": "persist", "breadth": "specialist",
        "authority": "independent", "communication": "demonstrative", "time_horizon": "long_term",
        "resources": "frugal", "legacy": "knowledge", "failure": "serendipitous"
    },
    "Bridge Builder": {
        "approach": "theoretical", "collaboration": "small_team", "risk": "calculated",
        "motivation": "impact", "adversity": "persist", "breadth": "interdisciplinary",
        "authority": "reformer", "communication": "written", "time_horizon": "long_term",
        "resources": "adequate", "legacy": "institutions", "failure": "analytical"
    },
    "National Champion": {
        "approach": "applied", "collaboration": "large_team", "risk": "bold",
        "motivation": "duty", "adversity": "fight", "breadth": "generalist",
        "authority": "institutional", "communication": "charismatic", "time_horizon": "long_term",
        "resources": "abundant", "legacy": "movement", "failure": "persistent"
    },
    "Deep Specialist": {
        "approach": "theoretical", "collaboration": "solo", "risk": "calculated",
        "motivation": "curiosity", "adversity": "persist", "breadth": "specialist",
        "authority": "independent", "communication": "written", "time_horizon": "eternal",
        "resources": "adequate", "legacy": "knowledge", "failure": "analytical"
    },
    "Compassionate Healer": {
        "approach": "applied", "collaboration": "mentor", "risk": "calculated",
        "motivation": "impact", "adversity": "persist", "breadth": "specialist",
        "authority": "institutional", "communication": "charismatic", "time_horizon": "long_term",
        "resources": "adequate", "legacy": "people", "failure": "pragmatic"
    },
    "Trailblazing Woman": {
        "approach": "experimental", "collaboration": "solo", "risk": "bold",
        "motivation": "recognition", "adversity": "fight", "breadth": "specialist",
        "authority": "reformer", "communication": "reserved", "time_horizon": "long_term",
        "resources": "frugal", "legacy": "movement", "failure": "persistent"
    }
}

# Pre-defined rich profiles for key scientists (will be enriched with Wikipedia)
RICH_PROFILES = {
    "G. N. Ramachandran": {
        "archetype": "Experimental Pioneer",
        "summary": "The father of molecular biophysics who discovered the triple helix structure of collagen. His Ramachandran plot revolutionized protein structure analysis and remains a fundamental tool in structural biology. Working from Madras with limited resources, he competed with the best Western labs and won.",
        "achievements": "Discovered collagen triple helix structure, invented the Ramachandran plot for protein structure analysis, founded molecular biophysics in India. Nominated for Nobel Prize multiple times.",
        "moments": [
            "Proved the triple helix structure of collagen when Western scientists doubted him",
            "Created the Ramachandran plot which became essential for validating protein structures",
            "Built world-class biophysics research in Madras despite limited resources",
            "His methods are now built into every protein structure validation software"
        ],
        "working_style": "Rigorous mathematical physicist who brought precision to biology. Combined theoretical insight with experimental validation. Mentored generations of Indian biophysicists while demanding excellence."
    },
    "E. C. George Sudarshan": {
        "archetype": "Quiet Revolutionary",
        "summary": "The physicist who should have won the Nobel Prize for quantum optics. He developed the quantum theory of optical coherence before Glauber (who won the Nobel), and co-developed V-A theory of weak interactions. Despite being overlooked for major prizes, he remained productive and gracious.",
        "achievements": "Sudarshan-Glauber representation in quantum optics, V-A theory of weak interactions (with Marshak), quantum Zeno effect, tachyon theory. Padma Vibhushan recipient.",
        "moments": [
            "Developed optical coherence theory in 1963, six months before Glauber's similar work",
            "Co-developed V-A theory which explained weak nuclear forces",
            "When Glauber won the 2005 Nobel for 'his' work, Sudarshan remained dignified",
            "Continued groundbreaking research into his 80s, publishing on quantum foundations"
        ],
        "working_style": "Theoretical physicist of exceptional breadth who worked on problems from particle physics to quantum optics. Known for generosity in collaboration and graciousness despite being overlooked for recognition."
    },
    "Jayant Narlikar": {
        "archetype": "Steadfast Theorist",
        "summary": "Cosmologist who challenged the Big Bang theory with the Steady State model alongside Fred Hoyle. Founder of IUCAA in Pune, he made cosmology accessible through popular science writing in multiple languages. Combines deep theoretical work with public engagement.",
        "achievements": "Hoyle-Narlikar theory of gravitation, Steady State cosmology contributions, founded IUCAA, popular science books in English and Marathi. Padma Vibhushan recipient.",
        "moments": [
            "Collaborated with Fred Hoyle at Cambridge to develop alternatives to Big Bang cosmology",
            "Founded IUCAA in Pune, creating a world-class astronomy center in India",
            "Wrote science fiction novels in Marathi to make science accessible",
            "Continued defending Steady State cosmology with new evidence when others abandoned it"
        ],
        "working_style": "Combines theoretical rigor with clear communication. Believes scientists should engage the public and write in regional languages. Patient defender of unpopular scientific positions when evidence warrants."
    },
    "Ashoke Sen": {
        "archetype": "Deep Specialist",
        "summary": "String theorist who proved S-duality and discovered Sen's conjecture on tachyon condensation. Working from Allahabad (now ICTS Bangalore), he produces world-leading theoretical physics while mentoring the next generation. Known for intense focus and mathematical precision.",
        "achievements": "Proved S-duality conjecture, Sen's conjecture on tachyon condensation, Breakthrough Prize in Fundamental Physics, Dirac Medal. One of the world's leading string theorists.",
        "moments": [
            "Proved S-duality in string theory, confirming a deep connection between different theories",
            "Developed understanding of black hole entropy in string theory",
            "Won the first Breakthrough Prize in Fundamental Physics (shared with others)",
            "Chose to remain in India rather than take offers from top Western universities"
        ],
        "working_style": "Intensely focused theorist who works on deep mathematical problems for years. Known for precision and rigor. Mentors students while maintaining prodigious research output."
    },
    "Jagadish Chandra Bose": {
        "archetype": "Experimental Pioneer",
        "summary": "Polymath who invented wireless communication before Marconi and proved that plants have feelings. Built his own equipment in colonial India, faced racism from British journals, yet made discoveries that were decades ahead. True Renaissance scientist.",
        "achievements": "Invented wireless millimeter wave communication (before Marconi), demonstrated plant sensitivity to stimuli, invented crescograph, pioneered semiconductor detectors. Knighted in 1917.",
        "moments": [
            "Demonstrated wireless transmission in 1895, a year before Marconi's patent",
            "Proved plants respond to stimuli like animals using his crescograph invention",
            "Refused to patent his inventions, believing knowledge should be free",
            "Built precision instruments in India that rivaled European laboratories"
        ],
        "working_style": "Polymath who moved freely between physics and biology. Built his own instruments when none existed. Believed in science for humanity, not profit - refused patents on principle."
    },
    "P. C. Mahalanobis": {
        "archetype": "Bridge Builder",
        "summary": "Statistician who created the Mahalanobis distance and designed India's economic planning. Founded the Indian Statistical Institute, invented large-scale sample surveys, and advised Nehru on the Second Five Year Plan. Bridged pure mathematics and national development.",
        "achievements": "Mahalanobis distance, founded ISI Kolkata, designed India's Second Five Year Plan, pioneered sample survey methodology. Member of Planning Commission.",
        "moments": [
            "Invented the Mahalanobis distance during anthropological skull measurements",
            "Designed sampling methodology that made national surveys feasible",
            "Created ISI Kolkata which became a world center for statistics",
            "His economic models shaped India's industrial development for decades"
        ],
        "working_style": "Bridged theoretical statistics with practical application. Built institutions and trained statisticians while advising on national policy. Believed statistics should serve development, not just academia."
    },
    "Satish Dhawan": {
        "archetype": "Institution Builder",
        "summary": "The father of experimental fluid dynamics in India who transformed ISRO into a world-class space agency. When the SLV-3 rocket failed in 1979, he took personal blame at the press conference. When it succeeded in 1980, he pushed Kalam forward to take the credit. This defined his selfless leadership.",
        "achievements": "Built ISRO into leading space agency, developed India's satellite launch capability, founded National Aerospace Laboratories, pioneered boundary layer research. Padma Vibhushan recipient.",
        "moments": [
            "After SLV-3 failure in 1979, faced the press alone and took full responsibility",
            "After SLV-3 success in 1980, pushed APJ Abdul Kalam to address the press instead",
            "Built IISc aerospace engineering into a world-recognized department",
            "Transformed ISRO from a small agency into a space power during his chairmanship"
        ],
        "working_style": "Selfless leader who deflected credit and absorbed blame. Combined academic rigor with practical engineering. Built teams by trusting people completely while demanding excellence. Believed institutions outlast individuals."
    },
    "Tessy Thomas": {
        "archetype": "Trailblazing Woman",
        "summary": "The 'Missile Woman of India' who led the Agni-IV and Agni-V missile programs. First woman to head a missile project in India, she broke barriers in a male-dominated field through sheer technical excellence. Rose from project engineer to project director through decades of dedication.",
        "achievements": "Project Director for Agni-IV and Agni-V missiles, first woman scientist to head an Indian missile project. Currently Director General of Aeronautical Systems. Multiple national awards.",
        "moments": [
            "Joined DRDO as a young engineer and worked her way up over three decades",
            "Led the successful test of Agni-IV in 2011, proving India's long-range capability",
            "Directed Agni-V development, India's first intercontinental ballistic missile",
            "Faced skepticism as a woman in missile technology but let results speak"
        ],
        "working_style": "Technically rigorous leader who earns respect through competence, not authority. Known for hands-on involvement in every aspect of missile development. Mentors young women engineers while maintaining demanding standards."
    },
    "M. Visvesvaraya": {
        "archetype": "Institution Builder",
        "summary": "The engineering genius who built modern Mysore and pioneered Indian engineering. Designed the Krishna Raja Sagar dam with innovative automatic flood gates. As Diwan of Mysore, he transformed a princely state into an industrial powerhouse. His birthday is celebrated as Engineer's Day in India.",
        "achievements": "Built Krishna Raja Sagar dam, automatic flood gates invention, modernized Mysore state, founded multiple engineering institutions. Bharat Ratna 1955, knighted in 1915.",
        "moments": [
            "Invented automatic flood gates that are still used in dams worldwide",
            "Designed water supply systems for Aden that are still functional today",
            "Transformed Mysore from an agricultural state to industrial leader as Diwan",
            "Lived to 101, working productively until his final years"
        ],
        "working_style": "Meticulous planner who believed 'an ounce of practice is worth tons of theory.' Combined engineering precision with administrative vision. Famously punctual and disciplined, expecting the same from others."
    },
    "Sundar Pichai": {
        "archetype": "Tech Visionary",
        "summary": "The CEO of Alphabet who rose from a middle-class Chennai family to lead the world's most influential technology company. Known for calm demeanor, consensus-building, and product intuition. Led the development of Chrome browser before rising to CEO, demonstrating how technical excellence meets business leadership.",
        "achievements": "CEO of Alphabet/Google, led Chrome development (now 65% browser market share), oversaw Android, Drive, and AI initiatives. Led Google's transformation into an AI-first company.",
        "moments": [
            "Grew up in Chennai sharing a two-room apartment with his family",
            "Proposed Chrome browser when many at Google were skeptical of entering the browser market",
            "Chrome became the world's dominant browser within years of launch",
            "Chosen as CEO over other candidates for his ability to build consensus across Google's divisions"
        ],
        "working_style": "Calm, analytical leader who builds consensus rather than dictating. Known for deep product intuition and letting teams own their work. Avoids the spotlight but makes decisive calls when needed."
    },
    "Srinivasa Ramanujan": {
        "archetype": "Intuitive Visionary",
        "summary": "A self-taught mathematical genius who, without formal training, produced nearly 3,900 results and formulas. Born in poverty in Erode, he saw mathematics as divine revelation, claiming theorems came to him in dreams from the goddess Namagiri. Despite chronic illness and isolation in Cambridge, he revolutionized number theory, infinite series, and continued fractions.",
        "achievements": "3,900+ mathematical results, Ramanujan Prime, Ramanujan theta function, mock theta functions, partition theory, highly composite numbers. Elected Fellow of Royal Society at age 30.",
        "moments": [
            "At age 15, obtained a copy of Carr's Synopsis and taught himself advanced mathematics in isolation",
            "Sent letters to three Cambridge mathematicians; only G.H. Hardy recognized his genius",
            "Despite dying at 32, filled notebooks that mathematicians are still mining for insights today",
            "His 'Lost Notebook' discovered in 1976 contained groundbreaking work on mock theta functions"
        ],
        "working_style": "Worked in complete isolation with minimal resources, often going without food to afford paper. Intuited results without formal proofs, 'seeing' mathematical truths that took others decades to verify."
    },
    "C. V. Raman": {
        "archetype": "Experimental Pioneer",
        "summary": "The first Asian to win the Nobel Prize in Science (1930). Using homemade equipment in a dusty Calcutta laboratory, he discovered the Raman Effect - that light changes wavelength when scattered by molecules. His fierce independence and experimental brilliance proved that world-class science could be done in India.",
        "achievements": "Nobel Prize 1930 for Raman Effect, founded Indian Journal of Physics, built Indian Institute of Science, Bharat Ratna recipient. Discovered why the sea is blue.",
        "moments": [
            "On a ship voyage, wondered why the Mediterranean was so blue - leading to his Nobel work",
            "Discovered the Raman Effect with equipment costing less than 200 rupees",
            "Announced in advance that he would win the Nobel Prize and booked his passage to Stockholm",
            "Built the Raman Research Institute entirely through personal savings after retiring"
        ],
        "working_style": "Fiercely independent experimentalist who built his own equipment. Believed great discoveries required observation and intuition, not expensive apparatus. Demanded excellence and was known for his sharp tongue."
    },
    "Homi J. Bhabha": {
        "archetype": "Institution Builder",
        "summary": "The visionary father of India's nuclear program who dreamed of atomic energy for development, not destruction. Trained at Cambridge in cosmic rays, he returned to build TIFR and BARC from scratch, creating institutions that would outlast him. Died tragically in a 1966 plane crash, but his vision continues.",
        "achievements": "Founded TIFR (1945) and BARC, architect of India's three-stage nuclear program, developed indigenous thorium-based nuclear technology. Cosmic ray cascade theory.",
        "moments": [
            "Convinced J.R.D. Tata to fund a fundamental research institute with a napkin sketch",
            "Built TIFR on Bombay's seafront against all bureaucratic odds",
            "Designed India's unique three-stage thorium cycle nuclear program",
            "His mysterious death in 1966 remains a subject of conspiracy theories"
        ],
        "working_style": "Aristocratic visionary who combined scientific brilliance with political acumen. Attracted the best minds, secured funding from industrialists and government alike. Believed in doing 'first-class science in first-class style.'"
    },
    "A. P. J. Abdul Kalam": {
        "archetype": "People's Scientist",
        "summary": "The 'Missile Man' who became India's most beloved President. Born in a boat-building family in Rameswaram, he led India's missile and satellite programs. Unlike typical scientists, he was equally comfortable inspiring school children and leading nuclear tests. His humility and vision made him a national icon.",
        "achievements": "SLV-III rocket, Agni and Prithvi missiles, Pokhran-II nuclear tests, served as President of India (2002-2007), authored 'Wings of Fire' and 'Ignited Minds'. India's highest civilian awards.",
        "moments": [
            "Walked to school selling newspapers, couldn't afford a proper bicycle",
            "Led the team that launched India's first satellite launch vehicle despite failures",
            "During Pokhran-II, personally supervised tests while avoiding satellite detection",
            "As President, would stop his motorcade to talk to children and refused VIP treatment"
        ],
        "working_style": "Collaborative leader who empowered young engineers and scientists. Known for taking responsibility for failures and giving credit for successes. Combined technical rigor with spiritual depth and poetic sensibility."
    },
    "Vikram Sarabhai": {
        "archetype": "Institution Builder",
        "summary": "The father of India's space program who dreamed of satellites serving rural development. Born into a wealthy industrialist family, he chose science over business. Founded ISRO, PRL, IIM Ahmedabad, and more institutions than any other Indian. Proved that space technology could be India's tool for social change.",
        "achievements": "Founded ISRO, Physical Research Laboratory, IIM Ahmedabad, ATIRA, Darpana Academy. Launched India's first sounding rocket from a church in Thumba. Pioneered space applications for telecommunications, meteorology, education.",
        "moments": [
            "Started India's space program by transporting rocket parts on bicycles to a fishing village",
            "Convinced the local bishop to let ISRO use a church as their first workshop",
            "After the moon landing, declared India should use space technology for development, not prestige",
            "Died suddenly in 1971 at age 52, but every ISRO achievement carries his vision"
        ],
        "working_style": "Aristocratic democrat who combined family wealth with socialist ideals. Built institutions by attracting diverse talents and connecting science to society. Believed technology should serve the poorest citizen."
    },
    "Satyendra Nath Bose": {
        "archetype": "Quiet Revolutionary",
        "summary": "The physicist whose quantum statistics gave rise to 'bosons.' Without a PhD or foreign training, he derived quantum statistics by treating photons as indistinguishable particles - a radical idea that Einstein immediately recognized and championed. Despite naming an entire class of particles, he never received the Nobel Prize.",
        "achievements": "Bose-Einstein statistics, bosons named after him, Bose-Einstein condensate prediction, key contributions to quantum mechanics. Multiple Padma awards.",
        "moments": [
            "His paper on quantum statistics was rejected; he sent it directly to Einstein who translated and published it",
            "Einstein immediately extended the work, leading to prediction of Bose-Einstein condensate",
            "Never received the Nobel Prize, yet an entire class of particles bears his name",
            "Returned from Europe to teach in Dhaka and Calcutta, preferring to build Indian physics"
        ],
        "working_style": "Polymath who read literature and played esraj as intensely as he did physics. Taught in Bengali and championed science in Indian languages. Sought truth rather than recognition."
    },
    "Har Gobind Khorana": {
        "archetype": "Deep Specialist",
        "summary": "Nobel laureate who cracked the genetic code and synthesized the first artificial gene. Born in a village with no electricity in undivided Punjab, he rose to become one of molecular biology's founding fathers. His work on nucleotides laid the foundation for the biotech revolution.",
        "achievements": "Nobel Prize in Physiology/Medicine 1968, synthesized first artificial gene (1970), cracked genetic code showing how nucleotides determine amino acids. Created first synthetic oligonucleotides.",
        "moments": [
            "Born in a village of 100 people with no literate family member before his father",
            "Only student from his village to receive a university education",
            "Synthesized a complete gene from scratch for the first time in human history",
            "His work directly enabled PCR, gene therapy, and the entire biotechnology industry"
        ],
        "working_style": "Methodical, patient experimentalist who spent years perfecting techniques. Extremely private, focusing entirely on laboratory work. Built teams of loyal students who became leaders themselves."
    },
    "M. S. Swaminathan": {
        "archetype": "Compassionate Healer",
        "summary": "The 'Father of the Green Revolution in India' who saved millions from famine. Partnered with Norman Borlaug to introduce high-yielding wheat varieties, transforming India from a food-importing nation to self-sufficiency. Later advocated for sustainable agriculture and farmers' rights.",
        "achievements": "Green Revolution architect, introduced Mexican dwarf wheat varieties, founded M.S. Swaminathan Research Foundation, World Food Prize 1987. Advocated for 'evergreen revolution' combining productivity with sustainability.",
        "moments": [
            "In 1966, bet India's food security on untested Mexican wheat varieties during a drought",
            "Convinced reluctant farmers to adopt new seeds by demonstrating results in their own fields",
            "Later acknowledged Green Revolution's environmental costs and advocated sustainable alternatives",
            "At 98, continued fighting for farmers' minimum support prices"
        ],
        "working_style": "Field scientist who spent as much time with farmers as in laboratories. Combined scientific rigor with deep empathy for rural poverty. Believed science must serve social justice."
    },
    "Subrahmanyan Chandrasekhar": {
        "archetype": "Steadfast Theorist",
        "summary": "Nobel laureate who discovered that massive stars must collapse into what we now call black holes. At just 19, on a ship to Cambridge, he calculated the 'Chandrasekhar limit.' When Eddington publicly mocked his theory, he quietly waited 50 years for vindication. His patience and depth became legendary.",
        "achievements": "Nobel Prize 1983, Chandrasekhar limit for white dwarfs, foundational work on black holes. Authored 10 books, each in a different field. National Medal of Science.",
        "moments": [
            "Derived the Chandrasekhar limit at age 19 during a sea voyage from India to England",
            "At age 24, the great Eddington publicly ridiculed his theory at the Royal Astronomical Society",
            "Instead of fighting, he quietly moved on and mastered six different fields over 50 years",
            "Finally received the Nobel Prize in 1983, validating work he did as a teenager"
        ],
        "working_style": "Systematic perfectionist who would master a field completely, write a definitive book, then move to an entirely new area. Taught courses with just one student with the same rigor as packed auditoriums."
    },
    "Satya Nadella": {
        "archetype": "Tech Visionary",
        "summary": "The CEO who transformed Microsoft from a stagnant Windows company into a cloud computing leader. Born in Hyderabad, his empathetic leadership style - shaped by raising a son with cerebral palsy - revolutionized Microsoft's cutthroat culture. Increased Microsoft's value from $300B to over $2T.",
        "achievements": "Microsoft CEO since 2014, led pivot to cloud computing (Azure), acquired LinkedIn and GitHub, transformed company culture. Author of 'Hit Refresh.'",
        "moments": [
            "His son's cerebral palsy taught him empathy that transformed his leadership approach",
            "Killed the 'stack ranking' system that made Microsoft employees compete against each other",
            "Made Microsoft embrace Linux and open source - once called 'cancer' by previous CEO",
            "During COVID, accelerated digital transformation: 'Two years of transformation in two months'"
        ],
        "working_style": "Empathetic listener who asks 'What did you learn?' rather than 'What did you accomplish?' Reads poetry and philosophy for leadership insights. Believes in growth mindset over fixed capabilities."
    },
    "Raj Reddy": {
        "archetype": "Bridge Builder",
        "summary": "Pioneer of artificial intelligence and speech recognition. The first person of Asian origin to win the Turing Award. At Carnegie Mellon, he built robots, speech recognition systems, and trained generations of AI researchers who now lead the field worldwide.",
        "achievements": "Turing Award 1994, pioneered speech understanding and robotics, founded Robotics Institute at CMU, co-founder of Raj Reddy Institute of Technology. Legion of Honor recipient.",
        "moments": [
            "Built one of the first speech recognition systems in the 1970s - 40 years before Siri",
            "Received Turing Award alongside Ed Feigenbaum for expert systems work",
            "Founded CMU's Robotics Institute, now the world's largest university robotics program",
            "Continues working on technology for the developing world in his 80s"
        ],
        "working_style": "Long-term visionary who invests in ideas decades before they become practical. Known for supporting unconventional students and ideas. Believes AI should help the poorest people, not just the richest markets."
    },
    "Kalpana Chawla": {
        "archetype": "Trailblazing Woman",
        "summary": "The first Indian-born woman in space, who dreamed of flying since childhood in Karnal, Haryana. She flew two Space Shuttle missions, logging 30 days in space before dying tragically in the Columbia disaster. Her memory inspires millions of Indian girls to reach for the stars.",
        "achievements": "First Indian-born woman in space (STS-87, 1997), second mission STS-107 (2003), logged over 30 days in space. Multiple NASA posthumous awards.",
        "moments": [
            "As a child in Karnal, would lie on the roof watching planes and dreaming of flying",
            "Moved to US alone in her 20s with $1,000 to pursue aerospace engineering",
            "On her first mission, became a hero for millions of Indian women and girls",
            "Died with six crewmates when Columbia disintegrated on re-entry, February 1, 2003"
        ],
        "working_style": "Methodical and calm under pressure. Brought a Bhagavad Gita to space along with her engineering manuals. Believed in meticulous preparation while maintaining wonder at the universe."
    },
    "Venkatraman Ramakrishnan": {
        "archetype": "Deep Specialist",
        "summary": "Nobel laureate who revealed the atomic structure of the ribosome - the cell's protein-making machinery. His journey from physics to biology to the Nobel Prize exemplifies persistent reinvention. Known for his blunt opinions about Indian science and award culture.",
        "achievements": "Nobel Prize in Chemistry 2009 for ribosome structure, President of Royal Society 2015-2020, pioneered cryo-electron microscopy techniques.",
        "moments": [
            "Changed fields from physics to biology in his 30s, starting over as a graduate student",
            "Worked on ribosome structure for over two decades before Nobel recognition",
            "After winning Nobel, criticized Indian award culture: 'In the US, I was respected. In India, I became a celebrity.'",
            "Declined the Padma award, questioning whether awards help science"
        ],
        "working_style": "Obsessive focus on one big problem for decades. Willing to learn entirely new fields when necessary. Believes recognition should be for ongoing work, not past achievements."
    },
    "C. N. R. Rao": {
        "archetype": "Institution Builder",
        "summary": "India's most prolific chemist with over 1,700 research papers. For six decades, he has dominated Indian materials science while building institutions and mentoring thousands. His energy and longevity in active research are unmatched.",
        "achievements": "Over 1,700 papers, 60+ books. Founded JNCASR, Bharat Ratna 2014. Pioneer in solid-state chemistry and nanomaterials. Dan David Prize, Padma Vibhushan.",
        "moments": [
            "Published first paper at age 20, continues publishing at 90+",
            "Founded Jawaharlal Nehru Centre for Advanced Scientific Research from scratch",
            "Has trained over 100 PhD students who now lead chemistry departments across India",
            "At 90, still goes to lab daily: 'Science is too exciting to retire from'"
        ],
        "working_style": "Workaholic who starts at 5 AM and expects similar dedication. Combines broad knowledge with deep expertise. Known for sharp criticism of mediocrity and fierce protection of his students."
    },
    "Meghnad Saha": {
        "archetype": "Bridge Builder",
        "summary": "The astrophysicist whose ionization equation unlocked the secrets of stellar spectra. Self-made from poverty in rural Bengal, he combined theoretical physics with practical nation-building - championing river valley projects and calendar reform while revolutionizing astrophysics.",
        "achievements": "Saha Ionization Equation, founded Indian Physical Society, planned Damodar Valley project, elected to Parliament. Built Saha Institute of Nuclear Physics.",
        "moments": [
            "Walked miles to school barefoot, taught himself German to read physics papers",
            "Derived the ionization equation that explains stellar spectra, enabling stellar classification",
            "Was nominated for Nobel Prize multiple times but never won",
            "Died of a heart attack while rushing to a meeting about river valley planning"
        ],
        "working_style": "Combined abstract theory with practical applications. Believed scientists must engage with society's problems. Known for blunt criticism of colonial science policy and persistent advocacy for Indian science."
    }
}

def infer_traits_from_profile(name, field, wiki_data=None):
    """Infer personality traits based on scientist's profile"""

    # Check if we have a pre-defined profile
    if name in RICH_PROFILES:
        archetype = RICH_PROFILES[name]["archetype"]
        return ARCHETYPE_TRAITS.get(archetype, ARCHETYPE_TRAITS["Deep Specialist"])

    # Infer based on field and other indicators
    if field in ["Mathematics", "Physics"]:
        if "theoretical" in str(wiki_data).lower():
            return ARCHETYPE_TRAITS["Steadfast Theorist"]
        return ARCHETYPE_TRAITS["Deep Specialist"]
    elif field in ["Technology", "Computer Science"]:
        return ARCHETYPE_TRAITS["Tech Visionary"]
    elif field in ["Space Science", "Aerospace"]:
        return ARCHETYPE_TRAITS["National Champion"]
    elif field in ["Medicine", "Biology"]:
        return ARCHETYPE_TRAITS["Compassionate Healer"]
    elif field in ["Engineering"]:
        return ARCHETYPE_TRAITS["Institution Builder"]
    elif field in ["Environmental Science", "Agriculture"]:
        return ARCHETYPE_TRAITS["Bridge Builder"]
    else:
        return ARCHETYPE_TRAITS["Deep Specialist"]

def get_archetype_for_traits(traits):
    """Find closest archetype for a trait set"""
    for archetype, arch_traits in ARCHETYPE_TRAITS.items():
        match_count = sum(1 for k, v in traits.items() if arch_traits.get(k) == v)
        if match_count >= 8:
            return archetype
    return "Deep Specialist"

def build_database():
    """Build the rich scientist database"""
    scientists = []

    for idx, scientist in enumerate(REAL_SCIENTISTS, 1):
        name = scientist["name"]
        field = scientist["field"]
        subfield = scientist["subfield"]

        # Check for rich profile
        if name in RICH_PROFILES:
            profile = RICH_PROFILES[name]
            traits = infer_traits_from_profile(name, field)

            entry = {
                "id": idx,
                "name": name,
                "field": field,
                "subfield": subfield,
                "archetype": profile["archetype"],
                "achievements": profile["achievements"],
                "summary": profile["summary"],
                "moments": profile["moments"],
                "working_style": profile.get("working_style", profile["summary"]),
                "traits": traits,
                "era": "Historical" if idx < 50 else "Contemporary"
            }
        else:
            # Create basic profile - will be enriched
            traits = infer_traits_from_profile(name, field)
            archetype = get_archetype_for_traits(traits)

            entry = {
                "id": idx,
                "name": name,
                "field": field,
                "subfield": subfield,
                "archetype": archetype,
                "achievements": f"Significant contributions to {subfield}",
                "summary": f"Distinguished {field} researcher specializing in {subfield}.",
                "moments": [f"Major breakthrough in {subfield}"],
                "working_style": f"Known for expertise in {subfield}.",
                "traits": traits,
                "era": "Contemporary"
            }

        scientists.append(entry)
        print(f"Added: {name} ({field})")

    return scientists

if __name__ == "__main__":
    print("Building rich scientist database...")
    scientists = build_database()

    with open("scientist_db_rich.json", "w", encoding="utf-8") as f:
        json.dump(scientists, f, indent=2, ensure_ascii=False)

    print(f"\nCreated database with {len(scientists)} scientists")
    print("Rich profiles: ", len(RICH_PROFILES))

"""
Build Rich Database of 400+ Indian Scientists
Fetches real data from Wikipedia for quality profiles
"""

import json
import time
import re

# Comprehensive list of Indian scientists with Wikipedia article titles
# Organized by field for better coverage

SCIENTISTS_MASTER_LIST = [
    # ===========================================
    # MATHEMATICS (Target: 50+)
    # ===========================================
    {"name": "Srinivasa Ramanujan", "wiki": "Srinivasa Ramanujan", "field": "Mathematics", "subfield": "Number Theory"},
    {"name": "Harish-Chandra", "wiki": "Harish-Chandra", "field": "Mathematics", "subfield": "Representation Theory"},
    {"name": "S. R. Srinivasa Varadhan", "wiki": "S. R. Srinivasa Varadhan", "field": "Mathematics", "subfield": "Probability Theory"},
    {"name": "Manjul Bhargava", "wiki": "Manjul Bhargava", "field": "Mathematics", "subfield": "Number Theory"},
    {"name": "Akshay Venkatesh", "wiki": "Akshay Venkatesh", "field": "Mathematics", "subfield": "Number Theory"},
    {"name": "C. R. Rao", "wiki": "C. R. Rao", "field": "Mathematics", "subfield": "Statistics"},
    {"name": "P. C. Mahalanobis", "wiki": "Prasanta Chandra Mahalanobis", "field": "Mathematics", "subfield": "Statistics"},
    {"name": "D. D. Kosambi", "wiki": "Damodar Dharmananda Kosambi", "field": "Mathematics", "subfield": "Statistics"},
    {"name": "C. S. Seshadri", "wiki": "C. S. Seshadri", "field": "Mathematics", "subfield": "Algebraic Geometry"},
    {"name": "M. S. Narasimhan", "wiki": "M. S. Narasimhan", "field": "Mathematics", "subfield": "Algebraic Geometry"},
    {"name": "S. S. Shrikhande", "wiki": "S. S. Shrikhande", "field": "Mathematics", "subfield": "Combinatorics"},
    {"name": "R. C. Bose", "wiki": "Raj Chandra Bose", "field": "Mathematics", "subfield": "Combinatorics"},
    {"name": "Shakuntala Devi", "wiki": "Shakuntala Devi", "field": "Mathematics", "subfield": "Mental Calculation"},
    {"name": "Bhama Srinivasan", "wiki": "Bhama Srinivasan", "field": "Mathematics", "subfield": "Representation Theory"},
    {"name": "Sujatha Ramdorai", "wiki": "Sujatha Ramdorai", "field": "Mathematics", "subfield": "Number Theory"},
    {"name": "Neena Gupta", "wiki": "Neena Gupta (mathematician)", "field": "Mathematics", "subfield": "Algebraic Geometry"},
    {"name": "K. R. Parthasarathy", "wiki": "Kalyanapuram Rangachari Parthasarathy", "field": "Mathematics", "subfield": "Probability"},
    {"name": "M. S. Raghunathan", "wiki": "M. S. Raghunathan", "field": "Mathematics", "subfield": "Lie Groups"},
    {"name": "S. Ramanan", "wiki": "S. Ramanan", "field": "Mathematics", "subfield": "Algebraic Geometry"},
    {"name": "T. N. Shorey", "wiki": "T. N. Shorey", "field": "Mathematics", "subfield": "Number Theory"},
    {"name": "Raman Parimala", "wiki": "Raman Parimala", "field": "Mathematics", "subfield": "Algebra"},
    {"name": "Dipendra Prasad", "wiki": "Dipendra Prasad", "field": "Mathematics", "subfield": "Number Theory"},
    {"name": "Rahul Pandharipande", "wiki": "Rahul Pandharipande", "field": "Mathematics", "subfield": "Algebraic Geometry"},
    {"name": "Kannan Soundararajan", "wiki": "Kannan Soundararajan", "field": "Mathematics", "subfield": "Number Theory"},
    {"name": "Madhu Sudan", "wiki": "Madhu Sudan", "field": "Mathematics", "subfield": "Theoretical CS"},
    {"name": "Nikhil Srivastava", "wiki": "Nikhil Srivastava", "field": "Mathematics", "subfield": "Spectral Graph Theory"},

    # ===========================================
    # PHYSICS (Target: 80+)
    # ===========================================
    {"name": "C. V. Raman", "wiki": "C. V. Raman", "field": "Physics", "subfield": "Spectroscopy"},
    {"name": "Satyendra Nath Bose", "wiki": "Satyendra Nath Bose", "field": "Physics", "subfield": "Quantum Mechanics"},
    {"name": "Subrahmanyan Chandrasekhar", "wiki": "Subrahmanyan Chandrasekhar", "field": "Physics", "subfield": "Astrophysics"},
    {"name": "Meghnad Saha", "wiki": "Meghnad Saha", "field": "Physics", "subfield": "Astrophysics"},
    {"name": "Homi J. Bhabha", "wiki": "Homi J. Bhabha", "field": "Physics", "subfield": "Nuclear Physics"},
    {"name": "Vikram Sarabhai", "wiki": "Vikram Sarabhai", "field": "Physics", "subfield": "Space Science"},
    {"name": "J. C. Bose", "wiki": "Jagadish Chandra Bose", "field": "Physics", "subfield": "Biophysics"},
    {"name": "K. S. Krishnan", "wiki": "Kariamanickam Srinivasa Krishnan", "field": "Physics", "subfield": "Spectroscopy"},
    {"name": "G. N. Ramachandran", "wiki": "G. N. Ramachandran", "field": "Physics", "subfield": "Biophysics"},
    {"name": "E. C. G. Sudarshan", "wiki": "E. C. George Sudarshan", "field": "Physics", "subfield": "Quantum Optics"},
    {"name": "Ashoke Sen", "wiki": "Ashoke Sen", "field": "Physics", "subfield": "String Theory"},
    {"name": "Jayant Narlikar", "wiki": "Jayant Narlikar", "field": "Physics", "subfield": "Cosmology"},
    {"name": "Raja Ramanna", "wiki": "Raja Ramanna", "field": "Physics", "subfield": "Nuclear Physics"},
    {"name": "P. K. Iyengar", "wiki": "P. K. Iyengar", "field": "Physics", "subfield": "Nuclear Physics"},
    {"name": "Anil Kakodkar", "wiki": "Anil Kakodkar", "field": "Physics", "subfield": "Nuclear Physics"},
    {"name": "Bikash Sinha", "wiki": "Bikash Sinha", "field": "Physics", "subfield": "Nuclear Physics"},
    {"name": "R. Chidambaram", "wiki": "Rajagopala Chidambaram", "field": "Physics", "subfield": "Nuclear Physics"},
    {"name": "Thanu Padmanabhan", "wiki": "Thanu Padmanabhan", "field": "Physics", "subfield": "Cosmology"},
    {"name": "Sandip Trivedi", "wiki": "Sandip Trivedi", "field": "Physics", "subfield": "String Theory"},
    {"name": "Spenta Wadia", "wiki": "Spenta R. Wadia", "field": "Physics", "subfield": "String Theory"},
    {"name": "Atish Dabholkar", "wiki": "Atish Dabholkar", "field": "Physics", "subfield": "String Theory"},
    {"name": "Sunil Mukhi", "wiki": "Sunil Mukhi", "field": "Physics", "subfield": "String Theory"},
    {"name": "Probir Roy", "wiki": "Probir Roy", "field": "Physics", "subfield": "Particle Physics"},
    {"name": "Rohini Godbole", "wiki": "Rohini Godbole", "field": "Physics", "subfield": "Particle Physics"},
    {"name": "C. V. Vishveshwara", "wiki": "C. V. Vishveshwara", "field": "Physics", "subfield": "General Relativity"},
    {"name": "Bibha Chowdhuri", "wiki": "Bibha Chowdhuri", "field": "Physics", "subfield": "Particle Physics"},
    {"name": "Anna Mani", "wiki": "Anna Mani", "field": "Physics", "subfield": "Meteorology"},
    {"name": "Bimla Buti", "wiki": "Bimla Buti", "field": "Physics", "subfield": "Plasma Physics"},
    {"name": "Narinder Singh Kapany", "wiki": "Narinder Singh Kapany", "field": "Physics", "subfield": "Fiber Optics"},
    {"name": "Vainu Bappu", "wiki": "M. K. Vainu Bappu", "field": "Physics", "subfield": "Astronomy"},
    {"name": "Govind Swarup", "wiki": "Govind Swarup", "field": "Physics", "subfield": "Radio Astronomy"},
    {"name": "Yash Pal", "wiki": "Yash Pal", "field": "Physics", "subfield": "Cosmic Rays"},
    {"name": "Devendra Lal", "wiki": "Devendra Lal", "field": "Physics", "subfield": "Nuclear Geophysics"},
    {"name": "A. P. Mitra", "wiki": "Ashesh Prosad Mitra", "field": "Physics", "subfield": "Ionospheric Physics"},
    {"name": "D. S. Kothari", "wiki": "D. S. Kothari", "field": "Physics", "subfield": "Theoretical Physics"},
    {"name": "Brebis Bleaney", "wiki": "Brebis Bleaney", "field": "Physics", "subfield": "Spectroscopy"},
    {"name": "Sisir Kumar Mitra", "wiki": "Sisir Kumar Mitra", "field": "Physics", "subfield": "Radio Physics"},
    {"name": "D. M. Bose", "wiki": "Debendra Mohan Bose", "field": "Physics", "subfield": "Cosmic Rays"},
    {"name": "Piara Singh Gill", "wiki": "Piara Singh Gill", "field": "Physics", "subfield": "Cosmic Rays"},

    # ===========================================
    # CHEMISTRY (Target: 50+)
    # ===========================================
    {"name": "C. N. R. Rao", "wiki": "C. N. R. Rao", "field": "Chemistry", "subfield": "Materials Science"},
    {"name": "Venkatraman Ramakrishnan", "wiki": "Venkatraman Ramakrishnan", "field": "Chemistry", "subfield": "Structural Biology"},
    {"name": "Prafulla Chandra Ray", "wiki": "Prafulla Chandra Ray", "field": "Chemistry", "subfield": "Inorganic Chemistry"},
    {"name": "Shanti Swaroop Bhatnagar", "wiki": "Shanti Swaroop Bhatnagar", "field": "Chemistry", "subfield": "Physical Chemistry"},
    {"name": "Asima Chatterjee", "wiki": "Asima Chatterjee", "field": "Chemistry", "subfield": "Organic Chemistry"},
    {"name": "Darshan Ranganathan", "wiki": "Darshan Ranganathan", "field": "Chemistry", "subfield": "Bioorganic Chemistry"},
    {"name": "G. N. Ramachandran", "wiki": "G. N. Ramachandran", "field": "Chemistry", "subfield": "Structural Biology"},
    {"name": "Raghunath Anant Mashelkar", "wiki": "Raghunath Anant Mashelkar", "field": "Chemistry", "subfield": "Polymer Science"},
    {"name": "Kamala Sohonie", "wiki": "Kamala Sohonie", "field": "Chemistry", "subfield": "Biochemistry"},
    {"name": "T. R. Seshadri", "wiki": "Tiruvenkatacharya Rajendra Seshadri", "field": "Chemistry", "subfield": "Natural Products"},
    {"name": "K. Venkataraman", "wiki": "K. Venkataraman", "field": "Chemistry", "subfield": "Synthetic Chemistry"},
    {"name": "Har Gobind Khorana", "wiki": "Har Gobind Khorana", "field": "Chemistry", "subfield": "Molecular Biology"},
    {"name": "Yellapragada Subbarow", "wiki": "Yellapragada Subbarow", "field": "Chemistry", "subfield": "Biochemistry"},
    {"name": "R. Raghavan", "wiki": "R. S. Raghavan", "field": "Chemistry", "subfield": "Neutrino Physics"},
    {"name": "Goverdhan Mehta", "wiki": "Goverdhan Mehta", "field": "Chemistry", "subfield": "Organic Chemistry"},
    {"name": "K. N. Ganesh", "wiki": "K. N. Ganesh", "field": "Chemistry", "subfield": "Bioorganic Chemistry"},
    {"name": "M. M. Sharma", "wiki": "Man Mohan Sharma", "field": "Chemistry", "subfield": "Chemical Engineering"},

    # ===========================================
    # BIOLOGY & MEDICINE (Target: 60+)
    # ===========================================
    {"name": "M. S. Swaminathan", "wiki": "M. S. Swaminathan", "field": "Biology", "subfield": "Agricultural Science"},
    {"name": "Verghese Kurien", "wiki": "Verghese Kurien", "field": "Biology", "subfield": "Dairy Science"},
    {"name": "Salim Ali", "wiki": "Sálim Ali", "field": "Biology", "subfield": "Ornithology"},
    {"name": "Birbal Sahni", "wiki": "Birbal Sahni", "field": "Biology", "subfield": "Paleobotany"},
    {"name": "Janaki Ammal", "wiki": "Janaki Ammal", "field": "Biology", "subfield": "Botany"},
    {"name": "Obaid Siddiqi", "wiki": "Obaid Siddiqi", "field": "Biology", "subfield": "Neurobiology"},
    {"name": "Kamal Ranadive", "wiki": "Kamal Ranadive", "field": "Medicine", "subfield": "Cancer Research"},
    {"name": "V. Shanta", "wiki": "V. Shanta", "field": "Medicine", "subfield": "Oncology"},
    {"name": "Gagandeep Kang", "wiki": "Gagandeep Kang", "field": "Medicine", "subfield": "Virology"},
    {"name": "Soumya Swaminathan", "wiki": "Soumya Swaminathan", "field": "Medicine", "subfield": "Epidemiology"},
    {"name": "K. VijayRaghavan", "wiki": "K. VijayRaghavan", "field": "Biology", "subfield": "Developmental Biology"},
    {"name": "Lalji Singh", "wiki": "Lalji Singh", "field": "Biology", "subfield": "DNA Fingerprinting"},
    {"name": "Pushpa Bhargava", "wiki": "Pushpa Mittra Bhargava", "field": "Biology", "subfield": "Molecular Biology"},
    {"name": "M. G. K. Menon", "wiki": "Mambillikalathil Govind Kumar Menon", "field": "Physics", "subfield": "Cosmic Rays"},
    {"name": "S. S. Vasan", "wiki": "S. S. Vasan", "field": "Medicine", "subfield": "Epidemiology"},
    {"name": "B. P. Pal", "wiki": "Benjamin Peary Pal", "field": "Biology", "subfield": "Botany"},
    {"name": "E. K. Janaki Ammal", "wiki": "Janaki Ammal", "field": "Biology", "subfield": "Cytogenetics"},
    {"name": "Archana Sharma", "wiki": "Archana Sharma (scientist)", "field": "Biology", "subfield": "Cytogenetics"},
    {"name": "Manju Sharma", "wiki": "Manju Sharma", "field": "Biology", "subfield": "Biotechnology"},
    {"name": "S. K. Joshi", "wiki": "S. K. Joshi", "field": "Biology", "subfield": "Condensed Matter"},
    {"name": "Nitya Anand", "wiki": "Nitya Anand", "field": "Medicine", "subfield": "Pharmacology"},

    # ===========================================
    # SPACE & AEROSPACE (Target: 40+)
    # ===========================================
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
    {"name": "K. Sivan", "wiki": "K. Sivan", "field": "Space Science", "subfield": "Rocket Propulsion"},
    {"name": "S. Somanath", "wiki": "S. Somanath", "field": "Space Science", "subfield": "Rocket Engineering"},
    {"name": "Roddam Narasimha", "wiki": "Roddam Narasimha", "field": "Aerospace", "subfield": "Fluid Dynamics"},
    {"name": "A. S. Kiran Kumar", "wiki": "Alur Seelin Kiran Kumar", "field": "Space Science", "subfield": "Remote Sensing"},
    {"name": "M. Annadurai", "wiki": "Mylswamy Annadurai", "field": "Space Science", "subfield": "Satellite Systems"},
    {"name": "Nambi Narayanan", "wiki": "Nambi Narayanan", "field": "Space Science", "subfield": "Cryogenic Technology"},
    {"name": "S. C. Gupta", "wiki": "Satish Chandra Gupta", "field": "Aerospace", "subfield": "Rocket Technology"},
    {"name": "V. K. Saraswat", "wiki": "V. K. Saraswat", "field": "Aerospace", "subfield": "Missile Defense"},
    {"name": "Avinash Chander", "wiki": "Avinash Chander", "field": "Aerospace", "subfield": "Missile Technology"},
    {"name": "Sivathanu Pillai", "wiki": "A. Sivathanu Pillai", "field": "Aerospace", "subfield": "BrahMos Missile"},

    # ===========================================
    # ENGINEERING & TECHNOLOGY (Target: 50+)
    # ===========================================
    {"name": "M. Visvesvaraya", "wiki": "M. Visvesvaraya", "field": "Engineering", "subfield": "Civil Engineering"},
    {"name": "Sam Pitroda", "wiki": "Sam Pitroda", "field": "Technology", "subfield": "Telecommunications"},
    {"name": "Ajay Bhatt", "wiki": "Ajay Bhatt", "field": "Technology", "subfield": "Computer Architecture"},
    {"name": "Raj Reddy", "wiki": "Raj Reddy", "field": "Computer Science", "subfield": "Artificial Intelligence"},
    {"name": "Rajeev Motwani", "wiki": "Rajeev Motwani", "field": "Computer Science", "subfield": "Algorithms"},
    {"name": "Manindra Agrawal", "wiki": "Manindra Agrawal", "field": "Computer Science", "subfield": "Computational Complexity"},
    {"name": "Vijay Vazirani", "wiki": "Vijay Vazirani", "field": "Computer Science", "subfield": "Algorithms"},
    {"name": "Umesh Vazirani", "wiki": "Umesh Vazirani", "field": "Computer Science", "subfield": "Quantum Computing"},
    {"name": "Satya Nadella", "wiki": "Satya Nadella", "field": "Technology", "subfield": "Cloud Computing"},
    {"name": "Sundar Pichai", "wiki": "Sundar Pichai", "field": "Technology", "subfield": "Internet Technology"},
    {"name": "Vinod Khosla", "wiki": "Vinod Khosla", "field": "Technology", "subfield": "Venture Capital"},
    {"name": "Arvind Krishna", "wiki": "Arvind Krishna", "field": "Technology", "subfield": "Cloud Computing"},
    {"name": "Shantanu Narayen", "wiki": "Shantanu Narayen", "field": "Technology", "subfield": "Software"},
    {"name": "Romesh Wadhwani", "wiki": "Romesh Wadhwani", "field": "Technology", "subfield": "Software"},
    {"name": "Sabeer Bhatia", "wiki": "Sabeer Bhatia", "field": "Technology", "subfield": "Internet"},
    {"name": "Rajiv Mody", "wiki": "Rajiv Mody", "field": "Technology", "subfield": "Semiconductors"},
    {"name": "Padmasree Warrior", "wiki": "Padmasree Warrior", "field": "Technology", "subfield": "Engineering"},
    {"name": "Jayshree Ullal", "wiki": "Jayshree Ullal", "field": "Technology", "subfield": "Networking"},
    {"name": "Rajeshwari Chatterjee", "wiki": "Rajeshwari Chatterjee", "field": "Engineering", "subfield": "Electronics"},
    {"name": "Homi N. Sethna", "wiki": "Homi N. Sethna", "field": "Engineering", "subfield": "Nuclear Engineering"},
    {"name": "F. C. Kohli", "wiki": "Faqir Chand Kohli", "field": "Technology", "subfield": "IT Industry"},
    {"name": "Nandan Nilekani", "wiki": "Nandan Nilekani", "field": "Technology", "subfield": "Software"},
    {"name": "N. R. Narayana Murthy", "wiki": "N. R. Narayana Murthy", "field": "Technology", "subfield": "Software"},
    {"name": "Azim Premji", "wiki": "Azim Premji", "field": "Technology", "subfield": "IT Industry"},

    # ===========================================
    # EARTH & ENVIRONMENTAL SCIENCES (Target: 30+)
    # ===========================================
    {"name": "Vandana Shiva", "wiki": "Vandana Shiva", "field": "Environmental Science", "subfield": "Ecology"},
    {"name": "Madhav Gadgil", "wiki": "Madhav Gadgil", "field": "Environmental Science", "subfield": "Ecology"},
    {"name": "D. N. Wadia", "wiki": "Darashaw Nosherwan Wadia", "field": "Earth Science", "subfield": "Geology"},
    {"name": "M. S. Krishnan", "wiki": "M. S. Krishnan", "field": "Earth Science", "subfield": "Geology"},
    {"name": "Aditi Pant", "wiki": "Aditi Pant", "field": "Earth Science", "subfield": "Oceanography"},
    {"name": "Harsh K. Gupta", "wiki": "Harsh K. Gupta", "field": "Earth Science", "subfield": "Seismology"},
    {"name": "R. Ramesh", "wiki": "R. Ramesh (scientist)", "field": "Earth Science", "subfield": "Climate Science"},
    {"name": "Shyam Saran", "wiki": "Shyam Saran", "field": "Environmental Science", "subfield": "Climate Policy"},

    # ===========================================
    # ECONOMICS & SOCIAL SCIENCES (Target: 20+)
    # ===========================================
    {"name": "Amartya Sen", "wiki": "Amartya Sen", "field": "Economics", "subfield": "Welfare Economics"},
    {"name": "Abhijit Banerjee", "wiki": "Abhijit Banerjee", "field": "Economics", "subfield": "Development Economics"},
    {"name": "Raghuram Rajan", "wiki": "Raghuram Rajan", "field": "Economics", "subfield": "Financial Economics"},
    {"name": "Jagdish Bhagwati", "wiki": "Jagdish Bhagwati", "field": "Economics", "subfield": "International Trade"},
    {"name": "C. Rangarajan", "wiki": "C. Rangarajan", "field": "Economics", "subfield": "Monetary Policy"},
    {"name": "Manmohan Singh", "wiki": "Manmohan Singh", "field": "Economics", "subfield": "Economic Policy"},
    {"name": "Bimal Jalan", "wiki": "Bimal Jalan", "field": "Economics", "subfield": "Banking"},
    {"name": "Arvind Panagariya", "wiki": "Arvind Panagariya", "field": "Economics", "subfield": "International Economics"},
    {"name": "Arvind Subramanian", "wiki": "Arvind Subramanian", "field": "Economics", "subfield": "International Finance"},
    {"name": "Kaushik Basu", "wiki": "Kaushik Basu", "field": "Economics", "subfield": "Development Economics"},

    # ===========================================
    # AGRICULTURE (Target: 20+)
    # ===========================================
    {"name": "Norman Borlaug", "wiki": "Norman Borlaug", "field": "Agriculture", "subfield": "Plant Genetics"},
    {"name": "B. P. Pal", "wiki": "Benjamin Peary Pal", "field": "Agriculture", "subfield": "Plant Breeding"},
    {"name": "R. S. Paroda", "wiki": "Raj Singh Paroda", "field": "Agriculture", "subfield": "Agricultural Research"},
    {"name": "S. K. Sinha", "wiki": "S. K. Sinha", "field": "Agriculture", "subfield": "Plant Physiology"},
    {"name": "Swaminathan Award", "wiki": "M. S. Swaminathan", "field": "Agriculture", "subfield": "Green Revolution"},

    # ===========================================
    # ADDITIONAL NOTABLE SCIENTISTS
    # ===========================================
    {"name": "Ruchi Ram Sahni", "wiki": "Ruchi Ram Sahni", "field": "Chemistry", "subfield": "Physical Chemistry"},
    {"name": "Shambhu Nath De", "wiki": "Shambhu Nath De", "field": "Medicine", "subfield": "Cholera Research"},
    {"name": "Upendranath Brahmachari", "wiki": "Upendranath Brahmachari", "field": "Medicine", "subfield": "Kala-azar Treatment"},
    {"name": "Subhas Mukhopadhyay", "wiki": "Subhas Mukhopadhyay", "field": "Medicine", "subfield": "IVF"},

    # ===========================================
    # EXPANDED LIST - MORE SCIENTISTS (Target: 400+)
    # ===========================================

    # More Mathematicians
    {"name": "K. Chandrasekharan", "wiki": "K. S. Chandrasekharan", "field": "Mathematics", "subfield": "Number Theory"},
    {"name": "Shreeram Abhyankar", "wiki": "Shreeram Shankar Abhyankar", "field": "Mathematics", "subfield": "Algebraic Geometry"},
    {"name": "R. Parimala", "wiki": "R. Parimala", "field": "Mathematics", "subfield": "Algebra"},
    {"name": "T. A. Sarasvati Amma", "wiki": "T. A. Sarasvati Amma", "field": "Mathematics", "subfield": "History of Mathematics"},
    {"name": "Subbayya Sivasankaranarayana Pillai", "wiki": "S. S. Pillai", "field": "Mathematics", "subfield": "Number Theory"},
    {"name": "K. Mahler", "wiki": "Kurt Mahler", "field": "Mathematics", "subfield": "Number Theory"},
    {"name": "V. S. Varadarajan", "wiki": "Veeravalli S. Varadarajan", "field": "Mathematics", "subfield": "Lie Groups"},
    {"name": "R. Balasubramanian", "wiki": "R. Balasubramanian", "field": "Mathematics", "subfield": "Number Theory"},

    # More Physicists
    {"name": "B. V. Sreekantan", "wiki": "B. V. Sreekantan", "field": "Physics", "subfield": "Cosmic Rays"},
    {"name": "B. M. Udgaonkar", "wiki": "B. M. Udgaonkar", "field": "Physics", "subfield": "Particle Physics"},
    {"name": "S. Chandrasekhar", "wiki": "S. Chandrasekhar", "field": "Physics", "subfield": "Liquid Crystals"},
    {"name": "T. V. Ramakrishnan", "wiki": "T. V. Ramakrishnan", "field": "Physics", "subfield": "Condensed Matter"},
    {"name": "N. Mukunda", "wiki": "N. Mukunda", "field": "Physics", "subfield": "Theoretical Physics"},
    {"name": "Ramamurti Rajaraman", "wiki": "R. Rajaraman", "field": "Physics", "subfield": "Theoretical Physics"},
    {"name": "M. G. K. Menon", "wiki": "M. G. K. Menon", "field": "Physics", "subfield": "Particle Physics"},
    {"name": "S. S. Kapoor", "wiki": "S. S. Kapoor", "field": "Physics", "subfield": "Nuclear Physics"},
    {"name": "T. Padmanabhan", "wiki": "Thanu Padmanabhan", "field": "Physics", "subfield": "Cosmology"},
    {"name": "Cumrun Vafa", "wiki": "Cumrun Vafa", "field": "Physics", "subfield": "String Theory"},

    # More Chemists & Biochemists
    {"name": "G. Padmanaban", "wiki": "Govindarajan Padmanaban", "field": "Chemistry", "subfield": "Biochemistry"},
    {"name": "P. T. Narasimhan", "wiki": "P. T. Narasimhan", "field": "Chemistry", "subfield": "Physical Chemistry"},
    {"name": "T. Ramasami", "wiki": "T. Ramasami", "field": "Chemistry", "subfield": "Leather Chemistry"},
    {"name": "D. Balasubramanian", "wiki": "D. Balasubramanian", "field": "Chemistry", "subfield": "Biochemistry"},
    {"name": "V. Prelog", "wiki": "Vladimir Prelog", "field": "Chemistry", "subfield": "Stereochemistry"},
    {"name": "T. S. S. R. Murty", "wiki": "T. S. S. R. Murty", "field": "Chemistry", "subfield": "Organic Chemistry"},
    {"name": "Darshan Ranganathan", "wiki": "Darshan Ranganathan", "field": "Chemistry", "subfield": "Bioorganic"},

    # More Biologists & Medical Scientists
    {"name": "S. Varadarajan", "wiki": "S. Varadarajan", "field": "Biology", "subfield": "Microbiology"},
    {"name": "P. Balaram", "wiki": "P. Balaram", "field": "Biology", "subfield": "Molecular Biophysics"},
    {"name": "K. S. Krishnan", "wiki": "K. S. Krishnan (neuroscientist)", "field": "Biology", "subfield": "Neuroscience"},
    {"name": "R. V. Swamy", "wiki": "R. V. Swamy", "field": "Medicine", "subfield": "Toxicology"},
    {"name": "Venugopal Dhoot", "wiki": "Venugopal Dhoot", "field": "Medicine", "subfield": "Ophthalmology"},
    {"name": "M. S. Valiathan", "wiki": "M. S. Valiathan", "field": "Medicine", "subfield": "Cardiac Surgery"},
    {"name": "Yusuf Hamied", "wiki": "Yusuf Hamied", "field": "Chemistry", "subfield": "Pharmaceutical Chemistry"},
    {"name": "Kiran Mazumdar-Shaw", "wiki": "Kiran Mazumdar-Shaw", "field": "Biology", "subfield": "Biotechnology"},
    {"name": "Shubha Tole", "wiki": "Shubha Tole", "field": "Biology", "subfield": "Neurobiology"},
    {"name": "Shahid Jameel", "wiki": "Shahid Jameel", "field": "Biology", "subfield": "Virology"},
    {"name": "V. P. Sharma", "wiki": "V. P. Sharma", "field": "Medicine", "subfield": "Malaria Research"},
    {"name": "Indira Nath", "wiki": "Indira Nath", "field": "Medicine", "subfield": "Immunology"},
    {"name": "T. Jacob John", "wiki": "T. Jacob John", "field": "Medicine", "subfield": "Virology"},
    {"name": "Maharaj Kishan Bhan", "wiki": "Maharaj Kishan Bhan", "field": "Medicine", "subfield": "Pediatrics"},

    # More Space Scientists
    {"name": "Vainu Bappu", "wiki": "Vainu Bappu", "field": "Space Science", "subfield": "Astronomy"},
    {"name": "P. Sreekumar", "wiki": "P. Sreekumar", "field": "Space Science", "subfield": "X-ray Astronomy"},
    {"name": "V. Narayanan", "wiki": "V. Narayanan (scientist)", "field": "Space Science", "subfield": "Propulsion"},
    {"name": "N. Valarmathi", "wiki": "N. Valarmathi", "field": "Space Science", "subfield": "Communication Systems"},
    {"name": "M. Y. S. Prasad", "wiki": "M. Y. S. Prasad", "field": "Space Science", "subfield": "Rocket Engineering"},
    {"name": "P. Kunhikrishnan", "wiki": "P. Kunhikrishnan", "field": "Space Science", "subfield": "Satellite Technology"},
    {"name": "G. Narayanan", "wiki": "G. Narayanamma", "field": "Space Science", "subfield": "Mission Design"},

    # More Engineers & Tech Leaders
    {"name": "Verghese Kurien", "wiki": "Verghese Kurien", "field": "Engineering", "subfield": "Dairy Engineering"},
    {"name": "J. R. D. Tata", "wiki": "J. R. D. Tata", "field": "Engineering", "subfield": "Aviation"},
    {"name": "A. P. J. Abdul Kalam", "wiki": "A. P. J. Abdul Kalam", "field": "Engineering", "subfield": "Aerospace"},
    {"name": "E. Sreedharan", "wiki": "E. Sreedharan", "field": "Engineering", "subfield": "Civil Engineering"},
    {"name": "R. A. Mashelkar", "wiki": "Raghunath Anant Mashelkar", "field": "Engineering", "subfield": "Chemical Engineering"},
    {"name": "Ashok Jhunjhunwala", "wiki": "Ashok Jhunjhunwala", "field": "Technology", "subfield": "Telecommunications"},
    {"name": "V. S. Ramamurthy", "wiki": "V. S. Ramamurthy", "field": "Physics", "subfield": "Nuclear Physics"},
    {"name": "Pradeep Sindhu", "wiki": "Pradeep Sindhu", "field": "Technology", "subfield": "Networking"},
    {"name": "Desh Deshpande", "wiki": "Desh Deshpande", "field": "Technology", "subfield": "Networking"},
    {"name": "Gururaj Deshpande", "wiki": "Gururaj Deshpande", "field": "Technology", "subfield": "Entrepreneurship"},
    {"name": "Kanwal Rekhi", "wiki": "Kanwal Rekhi", "field": "Technology", "subfield": "Software"},
    {"name": "K. R. Srinivasan", "wiki": "K. R. Srinivasan", "field": "Technology", "subfield": "IT Services"},
    {"name": "Anand Mahindra", "wiki": "Anand Mahindra", "field": "Engineering", "subfield": "Automotive"},
    {"name": "Ratan Tata", "wiki": "Ratan Tata", "field": "Engineering", "subfield": "Industrial"},

    # More Computer Scientists
    {"name": "Aravind Joshi", "wiki": "Aravind Joshi", "field": "Computer Science", "subfield": "NLP"},
    {"name": "Rajeev Alur", "wiki": "Rajeev Alur", "field": "Computer Science", "subfield": "Theory"},
    {"name": "Sanjeev Arora", "wiki": "Sanjeev Arora", "field": "Computer Science", "subfield": "Algorithms"},
    {"name": "Shafi Goldwasser", "wiki": "Shafi Goldwasser", "field": "Computer Science", "subfield": "Cryptography"},
    {"name": "Prabhakar Raghavan", "wiki": "Prabhakar Raghavan", "field": "Computer Science", "subfield": "Algorithms"},
    {"name": "Sanjay Ghemawat", "wiki": "Sanjay Ghemawat", "field": "Computer Science", "subfield": "Distributed Systems"},
    {"name": "C. Mohan", "wiki": "C. Mohan (computer scientist)", "field": "Computer Science", "subfield": "Databases"},
    {"name": "Rakesh Agrawal", "wiki": "Rakesh Agrawal (computer scientist)", "field": "Computer Science", "subfield": "Data Mining"},
    {"name": "Jitendra Malik", "wiki": "Jitendra Malik", "field": "Computer Science", "subfield": "Computer Vision"},
    {"name": "Fei-Fei Li", "wiki": "Fei-Fei Li", "field": "Computer Science", "subfield": "AI"},
    {"name": "Demis Hassabis", "wiki": "Demis Hassabis", "field": "Computer Science", "subfield": "AI"},
    {"name": "Daphne Koller", "wiki": "Daphne Koller", "field": "Computer Science", "subfield": "Machine Learning"},

    # More Earth & Environmental Scientists
    {"name": "R. Ramesh", "wiki": "R. Ramesh (scientist)", "field": "Earth Science", "subfield": "Climate"},
    {"name": "Anil K. Gupta", "wiki": "Anil K. Gupta", "field": "Environmental Science", "subfield": "Innovation"},
    {"name": "Sunita Narain", "wiki": "Sunita Narain", "field": "Environmental Science", "subfield": "Environmental Policy"},
    {"name": "J. Srinivasan", "wiki": "J. Srinivasan", "field": "Earth Science", "subfield": "Atmospheric Science"},
    {"name": "M. Rajeevan", "wiki": "M. Rajeevan", "field": "Earth Science", "subfield": "Meteorology"},

    # Nobel Laureates & Global Figures
    {"name": "S. Chandrashekhar", "wiki": "Subrahmanyan Chandrasekhar", "field": "Physics", "subfield": "Astrophysics"},
    {"name": "Venki Ramakrishnan", "wiki": "Venkatraman Ramakrishnan", "field": "Chemistry", "subfield": "Structural Biology"},
    {"name": "Har Gobind Khorana", "wiki": "Har Gobind Khorana", "field": "Chemistry", "subfield": "Molecular Biology"},

    # Women Scientists in India
    {"name": "Aditi Pant", "wiki": "Aditi Pant", "field": "Earth Science", "subfield": "Oceanography"},
    {"name": "Anandibai Joshi", "wiki": "Anandibai Joshi", "field": "Medicine", "subfield": "Physician"},
    {"name": "Kadambini Ganguly", "wiki": "Kadambini Ganguly", "field": "Medicine", "subfield": "Physician"},
    {"name": "Kamla Sohonie", "wiki": "Kamala Sohonie", "field": "Chemistry", "subfield": "Biochemistry"},
    {"name": "Mangala Narlikar", "wiki": "Mangala Narlikar", "field": "Mathematics", "subfield": "Mathematics"},
    {"name": "Charusita Chakravarty", "wiki": "Charusita Chakravarty", "field": "Chemistry", "subfield": "Physical Chemistry"},
    {"name": "Vidita Vaidya", "wiki": "Vidita Vaidya", "field": "Biology", "subfield": "Neuroscience"},
    {"name": "Yamuna Krishnan", "wiki": "Yamuna Krishnan", "field": "Chemistry", "subfield": "Chemical Biology"},
    {"name": "Shubha Tole", "wiki": "Shubha Tole", "field": "Biology", "subfield": "Neurobiology"},
    {"name": "Manju Sharma", "wiki": "Manju Sharma", "field": "Biology", "subfield": "Biotechnology"},
    {"name": "Tessy Thomas", "wiki": "Tessy Thomas", "field": "Aerospace", "subfield": "Missile Technology"},
    {"name": "Ritu Karidhal", "wiki": "Ritu Karidhal", "field": "Space Science", "subfield": "Mission Design"},
    {"name": "M. Vanitha", "wiki": "M. Vanitha", "field": "Space Science", "subfield": "Project Management"},
    {"name": "Nandini Harinath", "wiki": "Nandini Harinath", "field": "Space Science", "subfield": "Mission Operations"},

    # Historical Scientists
    {"name": "Aryabhata", "wiki": "Aryabhata", "field": "Mathematics", "subfield": "Astronomy"},
    {"name": "Brahmagupta", "wiki": "Brahmagupta", "field": "Mathematics", "subfield": "Algebra"},
    {"name": "Bhaskara II", "wiki": "Bhāskara II", "field": "Mathematics", "subfield": "Mathematics"},
    {"name": "Varahamihira", "wiki": "Varahamihira", "field": "Mathematics", "subfield": "Astronomy"},
    {"name": "Madhava", "wiki": "Madhava of Sangamagrama", "field": "Mathematics", "subfield": "Calculus"},
    {"name": "Sushruta", "wiki": "Sushruta", "field": "Medicine", "subfield": "Surgery"},
    {"name": "Charaka", "wiki": "Charaka", "field": "Medicine", "subfield": "Ayurveda"},
    {"name": "Nagarjuna", "wiki": "Nāgārjuna (metallurgist)", "field": "Chemistry", "subfield": "Metallurgy"},
]

# Remove duplicates
seen = set()
UNIQUE_SCIENTISTS = []
for s in SCIENTISTS_MASTER_LIST:
    if s['name'] not in seen:
        seen.add(s['name'])
        UNIQUE_SCIENTISTS.append(s)

print(f"Total unique scientists in master list: {len(UNIQUE_SCIENTISTS)}")

# Trait inference patterns based on keywords in biography
TRAIT_PATTERNS = {
    "approach": {
        "theoretical": ["theory", "theoretical", "mathematical", "equation", "formula", "abstract", "conceptual"],
        "experimental": ["experiment", "laboratory", "lab", "discovered", "observed", "tested", "measurement"],
        "applied": ["practical", "application", "industry", "implemented", "developed", "built", "designed"],
        "observational": ["observed", "survey", "field work", "data collection", "pattern", "catalogued"]
    },
    "collaboration": {
        "solo": ["alone", "solitary", "independent", "single-handedly", "by himself", "by herself"],
        "small_team": ["collaborat", "partner", "worked with", "co-author", "together with"],
        "large_team": ["led", "directed", "team", "organization", "institution", "project director"],
        "mentor": ["taught", "mentor", "students", "trained", "guided", "professor", "teacher"]
    },
    "risk": {
        "conservative": ["careful", "meticulous", "systematic", "methodical", "rigorous"],
        "calculated": ["strategic", "planned", "considered", "balanced"],
        "bold": ["revolutionary", "radical", "unconventional", "breakthrough", "pioneer", "daring", "first"],
        "hedged": ["diverse", "multiple", "varied", "parallel"]
    },
    "motivation": {
        "curiosity": ["curious", "passion", "fascinated", "love of", "interest in", "wondered"],
        "impact": ["help", "improve", "benefit", "society", "humanity", "people", "practical"],
        "recognition": ["award", "prize", "honor", "recognition", "fame", "acknowledged"],
        "duty": ["nation", "country", "India", "patriot", "service", "responsibility", "duty"]
    },
    "adversity": {
        "persist": ["persever", "persist", "despite", "overcame", "struggle", "continued"],
        "pivot": ["changed", "shifted", "adapted", "new direction", "turned to"],
        "fight": ["fought", "challenged", "opposed", "resisted", "battle"],
        "accept": ["philosophical", "accepted", "graceful", "stoic"]
    },
    "breadth": {
        "specialist": ["specialist", "focused", "dedicated", "expert in", "devoted to"],
        "generalist": ["polymath", "diverse", "many fields", "wide-ranging", "versatile"],
        "interdisciplinary": ["interdisciplinary", "bridged", "combined", "intersection"],
        "expanding": ["later", "expanded", "broadened", "moved to"]
    },
    "authority": {
        "independent": ["independent", "outside", "own path", "self-taught", "unconventional"],
        "institutional": ["founded", "established", "built", "institution", "director", "chairman"],
        "reformer": ["reformed", "changed", "modernized", "transformed"],
        "revolutionary": ["revolutionary", "radical", "overthrew", "new paradigm"]
    },
    "communication": {
        "reserved": ["quiet", "modest", "humble", "shy", "private", "reserved"],
        "charismatic": ["speaker", "communicator", "popular", "public", "eloquent", "charismatic"],
        "written": ["author", "wrote", "published", "papers", "books"],
        "demonstrative": ["demonstrated", "showed", "displayed", "exhibited"]
    },
    "time_horizon": {
        "immediate": ["urgent", "immediate", "pressing", "current"],
        "medium": ["years", "project", "goal"],
        "long_term": ["decades", "vision", "long-term", "future"],
        "eternal": ["fundamental", "timeless", "eternal", "universal", "basic"]
    },
    "resources": {
        "frugal": ["limited", "scarce", "minimal", "meager", "simple equipment", "modest"],
        "adequate": ["sufficient", "adequate", "reasonable"],
        "abundant": ["well-funded", "resources", "large budget", "significant funding"],
        "ideas_first": ["ideas", "concept", "theory first"]
    },
    "legacy": {
        "knowledge": ["discovery", "theorem", "theory", "understanding", "knowledge"],
        "people": ["students", "trained", "mentored", "influenced", "next generation"],
        "institutions": ["founded", "established", "built", "institution", "organization"],
        "movement": ["movement", "changed", "revolution", "inspired", "transformed society"]
    },
    "failure": {
        "analytical": ["analyzed", "learned", "studied", "understood why"],
        "persistent": ["tried again", "persisted", "continued", "never gave up"],
        "serendipitous": ["accident", "unexpected", "serendip", "chance"],
        "pragmatic": ["moved on", "practical", "pragmatic", "next project"]
    }
}

def infer_traits_from_text(text: str) -> dict:
    """Infer personality traits from biographical text"""
    text_lower = text.lower()
    traits = {}

    for dimension, values in TRAIT_PATTERNS.items():
        best_match = None
        best_score = 0

        for trait_value, keywords in values.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > best_score:
                best_score = score
                best_match = trait_value

        # Default if no match
        if best_match is None:
            defaults = {
                "approach": "theoretical",
                "collaboration": "small_team",
                "risk": "calculated",
                "motivation": "curiosity",
                "adversity": "persist",
                "breadth": "specialist",
                "authority": "institutional",
                "communication": "written",
                "time_horizon": "long_term",
                "resources": "adequate",
                "legacy": "knowledge",
                "failure": "analytical"
            }
            best_match = defaults[dimension]

        traits[dimension] = best_match

    return traits

def extract_achievements(text: str) -> str:
    """Extract key achievements from text"""
    # Look for awards, discoveries, inventions
    achievements = []

    # Common achievement patterns
    patterns = [
        r"Nobel Prize[^.]*\.",
        r"awarded[^.]*\.",
        r"discovered[^.]*\.",
        r"invented[^.]*\.",
        r"developed[^.]*\.",
        r"founded[^.]*\.",
        r"Padma[^.]*\.",
        r"Bharat Ratna[^.]*\.",
        r"Fellow of[^.]*\.",
        r"first [^.]*\."
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        achievements.extend(matches[:2])  # Limit per pattern

    if achievements:
        return " ".join(achievements[:5])  # Top 5 achievements
    return ""

def extract_key_moments(text: str) -> list:
    """Extract key moments/stories from biography"""
    moments = []

    # Look for year-based events
    year_pattern = r"In \d{4}[^.]*\."
    year_matches = re.findall(year_pattern, text)
    moments.extend(year_matches[:3])

    # Look for turning points
    turning_patterns = [
        r"[^.]*breakthrough[^.]*\.",
        r"[^.]*turning point[^.]*\.",
        r"[^.]*famous[^.]*\.",
        r"[^.]*landmark[^.]*\."
    ]

    for pattern in turning_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        moments.extend(matches[:1])

    return moments[:4] if moments else ["Made significant contributions to their field"]

def extract_summary(text: str, max_sentences: int = 4) -> str:
    """Extract first few meaningful sentences as summary"""
    sentences = text.split('.')
    summary_sentences = []

    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) > 50 and len(sentence) < 400:
            summary_sentences.append(sentence)
            if len(summary_sentences) >= max_sentences:
                break

    return '. '.join(summary_sentences) + '.' if summary_sentences else text[:500]

def determine_archetype(traits: dict, field: str) -> str:
    """Determine archetype from traits"""
    # Map common trait combinations to archetypes
    if traits.get('approach') == 'theoretical' and traits.get('collaboration') == 'solo':
        if traits.get('risk') == 'bold':
            return "Intuitive Visionary"
        return "Deep Specialist"

    if traits.get('authority') == 'institutional' and traits.get('legacy') == 'institutions':
        return "Institution Builder"

    if traits.get('motivation') == 'impact' and traits.get('communication') == 'charismatic':
        return "People's Scientist"

    if traits.get('approach') == 'experimental' and traits.get('risk') == 'bold':
        return "Experimental Pioneer"

    if traits.get('adversity') == 'fight' and traits.get('authority') == 'reformer':
        return "Trailblazing Pioneer"

    if traits.get('collaboration') == 'large_team' and field in ['Aerospace', 'Space Science']:
        return "National Champion"

    if traits.get('approach') == 'applied' and field == 'Technology':
        return "Tech Visionary"

    if traits.get('breadth') == 'interdisciplinary':
        return "Bridge Builder"

    return "Distinguished Researcher"

def determine_era(text: str) -> str:
    """Determine scientist's era from text"""
    import re
    # Look for birth year
    birth_match = re.search(r'born[^0-9]*(\d{4})', text.lower())
    if birth_match:
        year = int(birth_match.group(1))
        if year < 1900:
            return "Pre-Independence Pioneer"
        elif year < 1950:
            return "Nation Builder"
        elif year < 1970:
            return "Modernization Era"
        else:
            return "Contemporary Leader"

    # Look for death year or any year
    year_match = re.search(r'\b(18\d{2}|19\d{2}|20\d{2})\b', text)
    if year_match:
        year = int(year_match.group(1))
        if year < 1950:
            return "Pre-Independence Pioneer"
        elif year < 1980:
            return "Nation Builder"
        else:
            return "Contemporary Leader"

    return "Contemporary"

def extract_working_style(text: str, name: str) -> str:
    """Extract working style description"""
    text_lower = text.lower()

    styles = []

    if "alone" in text_lower or "solitary" in text_lower or "isolation" in text_lower:
        styles.append(f"{name} preferred working in focused solitude")
    elif "team" in text_lower or "collaborat" in text_lower:
        styles.append(f"{name} thrived in collaborative environments")

    if "meticulous" in text_lower or "careful" in text_lower:
        styles.append("with meticulous attention to detail")
    elif "intuiti" in text_lower or "instinct" in text_lower:
        styles.append("guided by powerful intuition")

    if "experiment" in text_lower or "laboratory" in text_lower:
        styles.append("spending long hours in the laboratory")
    elif "theoret" in text_lower or "mathematical" in text_lower:
        styles.append("pursuing elegant mathematical formulations")

    if "taught" in text_lower or "mentor" in text_lower or "students" in text_lower:
        styles.append("while nurturing the next generation of scientists")

    if styles:
        return " ".join(styles) + "."
    return f"{name} was known for dedicated and rigorous scientific work."


# Test the count
if __name__ == "__main__":
    print(f"\nReady to fetch data for {len(UNIQUE_SCIENTISTS)} scientists")

"""
Enhanced Database Builder using Wikipedia MCP + Firecrawl MCP
Generates comprehensive scientist profiles with rich biographical data
"""

import json
import time
import google.generativeai as genai
from config import GEMINI_API_KEY
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn

console = Console()
genai.configure(api_key=GEMINI_API_KEY)

class MCPScientistProfiler:
    """
    Enhanced profiler using Wikipedia MCP and Firecrawl MCP
    for comprehensive biographical data extraction
    """

    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        console.print("[cyan]Enhanced Database Builder with MCP Integration[/cyan]")
        console.print("[dim]Using Wikipedia MCP + Firecrawl MCP for rich data[/dim]\n")

    def get_comprehensive_indian_scientists_list(self) -> list:
        """
        Comprehensive list of 200+ Indian scientists across all domains
        Organized by field for systematic database building
        """
        return [
            # Physics - Quantum & Classical (40)
            "C. V. Raman", "Satyendra Nath Bose", "Homi J. Bhabha",
            "Meghnad Saha", "Subrahmanyan Chandrasekhar", "Jagadish Chandra Bose",
            "E. C. George Sudarshan", "Ashoke Sen", "Narinder Singh Kapany",
            "G. N. Ramachandran", "Yash Pal", "Thanu Padmanabhan",
            "Rohini Godbole", "Jayant Narlikar", "Anil Kakodkar",
            "Raja Ramanna", "Homi Sethna", "M. G. K. Menon",
            "Vainu Bappu", "Govind Swarup", "Ramanath Cowsik",
            "Bibhas De", "Debendra Mohan Bose", "Sisir Kumar Mitra",
            "Amal Kumar Raychaudhuri", "Venkatraman Radhakrishnan",
            "Abhay Ashtekar", "Ajay Sood", "Rajesh Gopakumar",
            "Siddharth Parameswaran", "Senthil Todadri", "Nergis Mavalvala",
            "Sandip Trivedi", "Shiraz Minwalla", "Spenta Wadia",
            "Thanu Padmanabhan", "Abhijit Majumder", "Amol Dighe",
            "Deepak Dhar", "Mustansir Barma",

            # Mathematics & Computer Science (30)
            "Srinivasa Ramanujan", "Harish-Chandra", "C. R. Rao",
            "Manjul Bhargava", "Akshay Venkatesh", "Rajeev Motwani",
            "Narendra Karmarkar", "Shreeram Shankar Abhyankar",
            "Vijay Kumar Patodi", "M. S. Narasimhan", "C. S. Seshadri",
            "Shakuntala Devi", "Raj Reddy", "Dabbala Rajagopal Reddy",
            "Manindra Agrawal", "Rohit Parikh", "Ravi Kannan",
            "Umesh Vazirani", "Vijay Vazirani", "Satish Dhawan",
            "Ramarathnam Vaidyanathan", "Sanjoy Mitter", "Rajeev Alur",
            "Paritosh Pandya", "K. Gopinath", "Prabhakar Raghavan",
            "Rajeev Sangal", "Sunita Sarawagi", "Krithi Ramamritham",
            "S. Ramakrishnan",

            # Space & Aerospace (20)
            "Vikram Sarabhai", "A. P. J. Abdul Kalam", "Satish Dhawan",
            "U. R. Rao", "K. Kasturirangan", "G. Madhavan Nair",
            "K. Radhakrishnan", "A. S. Kiran Kumar", "K. Sivan",
            "Tessy Thomas", "Nambi Narayanan", "Mylswamy Annadurai",
            "Ritu Karidhal", "Muthayya Vanitha", "Nigar Shaji",
            "V. R. Lalithambika", "S. Somanath", "P. Kunhikrishnan",
            "Tapan Misra", "M. Annadurai",

            # Biology, Medicine & Life Sciences (50)
            "Har Gobind Khorana", "Yellapragada Subbarow", "Salim Ali",
            "M. S. Swaminathan", "Venkatraman Ramakrishnan", "Birbal Sahni",
            "T. N. Khoshoo", "Obaid Siddiqi", "Pushpa Mittra Bhargava",
            "Govindjee Govindjee", "Anil Kumar Sharma", "Raman Sukumar",
            "E. K. Janaki Ammal", "Rajeshwari Chatterjee", "Kamala Sohonie",
            "Asima Chatterjee", "V. Ramalingaswami", "P. N. Tandon",
            "V. S. Ramachandran", "Ranjit Roy Chaudhury", "B. K. Anand",
            "Nitya Anand", "Prem Nath Chhuttani", "Vulimiri Ramalingaswami",
            "Lalji Singh", "Samir Brahmachari", "K. Vijay Raghavan",
            "Gagandeep Kang", "Indira Nath", "N. K. Jerne",
            "Upendra Kaul", "Balram Bhargava", "Srinath Reddy",
            "D. Balasubramanian", "M. Ramaswamy", "P. Balaram",
            "Rohini Godbole", "Vidita Vaidya", "Shubha Tole",
            "Mitradas Panicker", "K. VijayRaghavan", "Shekhar Mande",
            "Soumya Swaminathan", "Randeep Guleria", "Vineeta Bal",
            "Satyajit Rath", "Bhabatosh Das", "Tapas Majumdar",
            "Krishnaswamy VijayRaghavan", "Ramesh Mahadevan",

            # Chemistry & Biochemistry (25)
            "C. N. R. Rao", "Prafulla Chandra Ray", "Asima Chatterjee",
            "Darshan Ranganathan", "Biman Bagchi", "Shanti Swarup Bhatnagar",
            "Usha Varanasi", "R. Chidambaram", "G. N. Ramachandran",
            "Goverdhan Mehta", "Ashutosh Sharma", "S. Varadarajan",
            "M. Vidyasagar", "Roddam Narasimha", "T. V. Ramakrishnan",
            "E. S. Raja Gopal", "S. Ramaseshan", "G. S. Ranganath",
            "N. Mukunda", "Rajaram Nityananda", "Dilip Kondepudi",
            "Ganapathi Thanikaimoni", "K. R. Rajaraman", "M. S. Raghunathan",
            "C. S. Raman",

            # Agriculture & Environmental Science (20)
            "M. S. Swaminathan", "B. P. Pal", "R. H. Richharia",
            "Verghese Kurien", "Rajendra Singh", "Anil Agarwal",
            "Sunita Narain", "Vandana Shiva", "M. K. Ranjitsinh",
            "Madhav Gadgil", "Sulochana Gadgil", "K. Kasturirangan",
            "R. K. Pachauri", "Suman Sahai", "Sanjay Gupta",
            "B. Venkateswarlu", "P. C. Kesavan", "R. S. Paroda",
            "S. K. Datta", "G. S. Khush",

            # Engineering & Technology (25)
            "E. Sreedharan", "Sam Pitroda", "Raghunath Anant Mashelkar",
            "G. D. Yadav", "Roddam Narasimha", "N. R. Narayana Murthy",
            "Azim Premji", "Nandan Nilekani", "Kris Gopalakrishnan",
            "Rajeev Chandrasekhar", "Suhas Patil", "Vinod Dham",
            "Sabeer Bhatia", "Gururaj Deshpande", "Kanwal Rekhi",
            "Sanjay Mehrotra", "Arvind Krishna", "Sundar Pichai",
            "Satya Nadella", "Shantanu Narayen", "Jayshree Ullal",
            "Nikesh Arora", "Punit Renjen", "Leena Nair",
            "Raghu Raghuram",

            # Social Sciences & Economics (15)
            "Amartya Sen", "Jagdish Bhagwati", "Raghuram Rajan",
            "Kaushik Basu", "Abhijit Banerjee", "Arvind Panagariya",
            "Partha Dasgupta", "T. N. Srinivasan", "Pranab Bardhan",
            "Dilip Mookherjee", "Rohini Pande", "Esther Duflo",
            "Sendhil Mullainathan", "Raj Chetty", "Parag Pathak",
        ]

    def create_scientist_profile_with_mcp(self, name: str) -> dict:
        """
        Create comprehensive profile using MCP tools

        Workflow:
        1. Search Wikipedia MCP for scientist
        2. Get full article via Wikipedia MCP
        3. Use Firecrawl MCP for additional sources if needed
        4. Extract comprehensive profile with Gemini AI
        5. Return rich biographical vector
        """

        console.print(f"[cyan]Processing: {name}[/cyan]")

        # For now, this is a placeholder that will use MCP tools after restart
        # The actual implementation will be:
        # 1. mcp__wikipedia__search_wikipedia(name)
        # 2. mcp__wikipedia__get_article(title)
        # 3. mcp__wikipedia__get_sections(title)
        # 4. mcp__firecrawl__scrape() for additional sources
        # 5. Extract comprehensive profile

        # Return placeholder structure
        return {
            "name": name,
            "status": "pending_mcp_activation",
            "note": "Will be generated after MCP restart"
        }

    def generate_database_batch(self, batch_size: int = 50):
        """Generate a batch of scientist profiles"""

        scientists = self.get_comprehensive_indian_scientists_list()[:batch_size]
        database = []

        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=console
        ) as progress:

            task = progress.add_task(
                f"[cyan]Building database of {batch_size} scientists...",
                total=batch_size
            )

            for name in scientists:
                profile = self.create_scientist_profile_with_mcp(name)
                database.append(profile)
                progress.advance(task)
                time.sleep(0.1)

        # Save
        output_file = f'scientist_db_mcp_{batch_size}.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(database, f, indent=2, ensure_ascii=False)

        console.print(f"\n[green]Database batch created: {output_file}[/green]")
        console.print(f"[cyan]Scientists ready for MCP processing: {len(database)}[/cyan]")

        return database


if __name__ == "__main__":
    import sys

    # Get batch size from command line
    batch_size = int(sys.argv[1]) if len(sys.argv) > 1 else 50

    console.print(f"[bold]Preparing to build database of {batch_size} scientists[/bold]\n")
    console.print("[yellow]Note: Full MCP integration will be available after restart[/yellow]")
    console.print("[yellow]Current version creates scientist list for processing[/yellow]\n")

    profiler = MCPScientistProfiler()
    database = profiler.generate_database_batch(batch_size)

    console.print("\n[bold green]Next Steps:[/bold green]")
    console.print("1. Restart to activate Wikipedia MCP + Firecrawl MCP")
    console.print("2. Re-run this script to fetch comprehensive data")
    console.print("3. Generated profiles will include:")
    console.print("   - Wikipedia biographical data")
    console.print("   - Additional sources via Firecrawl")
    console.print("   - AI-extracted 50+ trait dimensions")
    console.print("   - Rich personality vectors")

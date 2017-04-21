# healthgrades_scraper
grabbing some of healthgrades useful data programmatically

# Usage

Clone the repo

Make a virtual environment

Install the requirements

    pip install requirements.txt
    
Run

   python healthgrades_v2.py

This will put a directory for each specialty into your working directory. Inside each directory will be `.csv` files for every 100 docs pulled from healthgrades. If the specialty finishes, it will combine all the `.csv` files into one, this will have `combined` in the title. There will also be the combined patient experience surveys into the specialty directory as well. 

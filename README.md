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


If your connection dies at some point while running, your console will tell you the last file that was created successfully, and it will be in the specialty directory as well. Then you can go into `healthgrades_v2.py` and uncomment the lines 543 to 545 and update the search page to the last completed csv number. Then you can kick it off again and it will continue where it left off.

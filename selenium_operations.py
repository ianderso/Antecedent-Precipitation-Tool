#  This software was developed by United States Army Corps of Engineers (USACE)
#  employees in the course of their official duties.  USACE used copyrighted,
#  open source code to develop this software, as such this software
#  (per 17 USC 101) is considered "joint work."  Pursuant to 17 USC 105,
#  portions of the software developed by USACE employees in the course of their
#  official duties are not subject to copyright protection and are in the public
#  domain.
#
#  USACE assumes no responsibility whatsoever for the use of this software by
#  other parties, and makes no guarantees, expressed or implied, about its
#  quality, reliability, or any other characteristic.
#
#  The software is provided "as is," without warranty of any kind, express or
#  implied, including but not limited to the warranties of merchantability,
#  fitness for a particular purpose, and noninfringement.  In no event shall the
#  authors or U.S. Government be liable for any claim, damages or other
#  liability, whether in an action of contract, tort or otherwise, arising from,
#  out of or in connection with the software or the use or other dealings in the
#  software.
#
#  Public domain portions of this software can be redistributed and/or modified
#  freely, provided that any derivative works bear some notice that they are
#  derived from it, and any modified versions bear some notice that they have
#  been modified.
#
#  Copyrighted portions of the software are annotated within the source code.
#  Open Source Licenses, included in the source code, apply to the applicable
#  copyrighted portions.  Copyrighted portions of the software are not in the
#  public domain.

######################################
##  ------------------------------- ##
##      selenium_operations.py      ##
##  ------------------------------- ##
##      Writen by: Jason Deters     ##
##  ------------------------------- ##
##    Last Edited on:  2020-05-27   ##
##  ------------------------------- ##
######################################

# Import Standard Libraries
import os
import json
import time
import traceback
import requests

# Import PIP Libraries
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

import JLog


class getJSON(object):
    def __init__(self, url):
        self.url = url
        self.driver = None
        self.jsonResult = None
        # Create PrintLog
        self.L = JLog.PrintLog(Indent=2)
        # Find root folder
        self.module_path = os.path.dirname(os.path.realpath(__file__))
    def __call__(self):
        self.L.Wrap('Request URL: {}'.format(self.url))
        self.browserList = [self.useRequests,
                            self.Chrome]
        for browser in self.browserList:
            try:
                browser()
                return self.jsonResult
            except Exception:
                self.L.Wrap(traceback.format_exc())
                time.sleep(1)
        if self.jsonResult is None:
            self.L.Wrap("All methods failed for automated elevation query!")
            return None

    def useRequests(self):
        self.content = requests.get(self.url)
        time.sleep(4)
        self.jsonResult = self.content.json()
        return

    def Chrome(self):
        self.L.Wrap('Attempting to open Google Chrome in headless mode...')
        # Create Selenium Chrome Options class
        self.chrome_options = webdriver.ChromeOptions()
        # Populate class with Chrome Options (supposedly increase stability)
        self.chrome_options.add_argument('--disable-extensions')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--headless')
        # Instantiate webdriver
        self.driver = webdriver.Chrome(chrome_options=self.chrome_options)
        # Get open the URL with Selenium Instance
        self.driver.get(self.url)
        # Grab body and convert to JSON format
        self.jsonResult = json.loads(self.driver.find_element_by_tag_name('body').text)
        # Close the browser window and the driver executable
        self.driver.close()
        self.driver.quit()
        return


def global_elev_query(lat, lon, units='Feet'):
    """
    Queries worldwide elevation service by using Selenium to operate
    the JavaScript form at "https://www.freemaptools.com/elevation-finder.htm"
    """
    log = JLog.PrintLog()
    url = "https://www.freemaptools.com/elevation-finder.htm"

    # Create Options object and set automation options
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')
##    chrome_options.add_argument('--ignore-certificate-errors')
##    chrome_options.add_argument('--ignore-certificate-errors-spki-list')
##    chrome_options.add_argument('--ignore-ssl-errors')
    # Create driver object
    driver = webdriver.Chrome( chrome_options=chrome_options)
    tries = 1
    while tries < 10:
        try:
            tries += 1
            # Open Page
            driver.get(url)
            # Time buffer (Occasionally helps fewer warning messages post, but not mandatory)
            time.sleep(.1)
            # Get input element
            input_element = driver.find_element_by_id('locationSearchTextBox')
            # Enter Lat/Lon Query
            input_element.send_keys('{}, {}'.format(lat, lon))
            # Submit Query
            input_element.send_keys(Keys.RETURN)
            # Collect All Divs (NO SELECTABLE IDs on PAGE)
            divs = driver.find_elements(By.XPATH, "//div")
            # Search for text string ending with " feet" FORMAT: "1044.0 m / 3425.2 feet"
            for item in divs:
                if item.text.endswith(" feet"):
                    try:
                        # Parse string for elevation FORMAT: "1044.0 m / 3425.2 feet"
                        middle_string = " m / "
                        middle_location = item.text.find(middle_string)
                        elevation_meters = float(item.text[:middle_location])
                        elevation_feet = float(item.text[(middle_location + len(middle_string)):-5])
                        # Close the browser window and the driver executable
                        driver.stop_client()
                        driver.quit()
                        if units == 'Feet':
                            return elevation_feet
                        else:
                            return elevation_meters
                    except:
                        log.Write(traceback.format_exc())
                        raise
        except Exception:
            print('Attempt {} failed'.format(tries-1))
            # Time buffer (Occasionally helps fewer warning messages post, but not mandatory)
            time.sleep(.1)

def test_get_json():
    """Tests get_json function"""
    print('Testing get_json with USGS elevation query:')
    # Set URL
    url = "http://nationalmap.gov/epqs/pqs.php?x=-95.164569&y=29.446176&output=json&units=Feet"
    # Get JSON format text from url Body
    instance = getJSON(url)
    json_result = instance()
    # Parse JSON to get Elevation
    service = json_result['USGS_Elevation_Point_Query_Service']
    query = service['Elevation_Query']
    elevation = query['Elevation']
    print('Elevation = {}'.format(elevation))

def test_global_elev_query():
    """Tests global_elev_query function"""
    print('')
    print('Testing global_elev_query:')
    elevation = global_elev_query(55.2, 80.5)
    print('  Elevation = {}'.format(elevation))

if __name__ == '__main__':
    test_get_json()
    test_global_elev_query()

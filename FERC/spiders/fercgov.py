# -*- coding: utf-8 -*-
import uuid

import scrapy
from scrapy.http import FormRequest
from scrapy.utils.response import open_in_browser


from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.selector import Selector
from scrapy.http import HtmlResponse


from FERC.items import FercItem
from scrapy.loader import ItemLoader

import re
import json
import os

from datetime import datetime

# The path to the current project
base_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# The path to the folder where files are downloaded and log file is stored
download_folder = os.path.join(base_folder, 'download_folder')
# If directory doesn't exist - create it
if os.path.exists(download_folder):
    pass
else:
    os.mkdir(download_folder)

class FercgovSpider(scrapy.Spider):
    """
    Variables___________________

    GENERAL WARNING ABOUT docstart, docslimit, doccounter:
            empirically it was discovered that the server can produce
            more than 200 in search results. 200 is very stable though
            and this scraper has a replicated (reverse-engineered) way
            that the server increments its counters for "next pages".

    FORMATTING OF VARIABLES THAT NEED TO BE CHANGED:
            If you're not familiar with Python syntax, all options are provided
            below. If you need to use a list for dockets - there is an example
            of how to pass a list. If you want no dockets specified, uncomment
            the line that has an empty list (delete the "#" symbol at the line start).
            Please use those particular formats. Make sure that both "dockets"
            and "search" variables are declared (at least one of the provided
            formatting options is uncommented and filled with the search data
            that you want).



    +++ Variables that can't be changed:
            - name: scraper name that is called by [scrapy crawl] command.
                    cd into this project directory (FERC) and TYPE
                    "scrapy crawl fercgov" to start the scrapers

            - allowed_domains: only pages that have their url contain this
                    domain are considered as appropriate [response]. Generated
                    automatically by scrapy. If changed, none of the returned
                    pages will be processed

            - start_urls: url that requests are sent to. FERC has a very unique
                    way of displaying pages. In order to see any new page this
                    scraper sends HTTP POST requests to the FERC server.

            - docstart: first document to be contained in output in the search
                    results

            - doccounter: increment the "next page" requests and get this many
                    of next documents

            - docslimit: last document to be contained in output in the search
                    results

    +++ Variables that need to be changed according to your needs:
            - dockets: list of dockets to be searched. Has to be a list regardless
                    of the number of dockets (whether it's many dockets written
                    as a list of strings or no specific docket written as an
                    empty list).

                    Acceptable formats:
                    ["########", "########"] - search for many dockets in separate
                            queries
                    ["########"] - search one docket
                    [] - docket not specified (search by text instead)

            - search: string containing the word/phrase to search by.

                    Acceptable formats:
                    "########" - search for a string pattern either alongside
                            specific dockets or by itself
                    "" - don't include a string in the query. Requires having one
                            or more dockets
    """

    name = "fercgov"
    allowed_domains = ["elibrary.ferc.gov"]
    start_urls = ['https://elibrary.ferc.gov/idmws/search/fercgensearch.asp']
    # docket = docket
    docstart = 0
    doccounter = 200
    docslimit = 200
    # dockets = ["CP16-17", "CP15-500"]
    dockets = ["CP16-17"]
    # dockets = []
    # search = "pipeline"
    search = ""

    # Path to the JSON output file
    json_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'download_folder/log.json')

    def parse(self, response):

        # If the docket list isn't empty
        if len(self.dockets) > 0:

            # For each docket generate a new search request
            for docket in self.dockets:

                # Query request declared with all the search data
                # formdata includes the data that FERC server accepts
                query = FormRequest.from_response(response,
                    formdata = {
                                "FROMdt" : "",
                                "TOdt" : "",
                                "firstDt" : "1/1/1904",
                                "LastDt" : "12/31/2037",
                                "DocsStart" : str(self.docstart),
                                "DocsLimit" : str(self.docslimit),
                                "SortSpec" : "filed_date desc accession_num asc",
                                "datefield" : "filed_date",
                                "dFROM" : "10/08/2017",
                                "dTO" : "11/08/2017",
                                "dYEAR" : "1",
                                "dMONTH" : "1",
                                "dDAY" : "1",
                                "date" : "All",
                                "category" : "submittal,issuance",
                                "libraryall" : "electric, hydro, gas, rulemaking, oil, general",
                                "docket" : str(docket),
                                "subdock_radio" : "all_subdockets",
                                "class" : "999",
                                "type" : "999",
                                "textsearch" : str(self.search),
                                "description" : "description",
                                "fulltext" : "fulltext",
                                "DocsCount" : str(self.doccounter)},
                callback=self.parse_query, dont_filter = True)
                # pass the relevant form data to the query for parsing next pages
                # and generating new queries
                query.meta["DocsStart"] = str(self.docstart)
                query.meta["docket"] = str(docket)
                query.meta["textsearch"] = str(self.search)
                query.meta["DocsCount"] = str(self.doccounter)
                query.meta["DocsLimit"] = str(self.docslimit)
                # query posted to the server
                yield query
        # If the docket list is empty
        else:
            # Query request declared with all the search data
            # formdata includes the data that FERC server accepts
            # since the docket is not passed, text search field is used
            query = FormRequest.from_response(response,
                    formdata = {
                                "FROMdt" : "",
                                "TOdt" : "",
                                "firstDt" : "1/1/1904",
                                "LastDt" : "12/31/2037",
                                "DocsStart" : str(self.docstart),
                                "DocsLimit" : str(self.docslimit),
                                "SortSpec" : "filed_date desc accession_num asc",
                                "datefield" : "filed_date",
                                "dFROM" : "10/08/2017",
                                "dTO" : "11/08/2017",
                                "dYEAR" : "1",
                                "dMONTH" : "1",
                                "dDAY" : "1",
                                "date" : "All",
                                "category" : "submittal,issuance",
                                "libraryall" : "electric, hydro, gas, rulemaking, oil, general",
                                "docket" : "",
                                "subdock_radio" : "all_subdockets",
                                "class" : "999",
                                "type" : "999",
                                "textsearch" : str(self.search),
                                "description" : "description",
                                "fulltext" : "fulltext",
                                "DocsCount" : str(self.doccounter)},
                    callback=self.parse_query, dont_filter = True)
            # pass the relevant form data to the query for parsing next pages
            # and generating new queries
            query.meta["DocsStart"] = str(self.docstart)
            query.meta["docket"] = ""
            query.meta["textsearch"] = str(self.search)
            query.meta["DocsCount"] = str(self.doccounter)
            query.meta["DocsLimit"] = str(self.docslimit)
            # query posted to the server
            yield query

    def parse_query(self, response):
        # Extract all the rows that the search results return
        # output rows are not styled and it's the easiest way to identfy them
        page_rows = response.xpath('//tr[@bgcolor and not(@bgcolor="navy")]').extract()
        # Each row contains both meta data and urls for new requests
        for row in page_rows:
            # Each observation is an item. Item data is populated in a dictionary
            itemdata = {}
            # New selector is declared to select columns for each row
            sel = Selector(text = row)
            # Use the selector to extract columns (<td>)
            columns = sel.xpath('body/tr/td').extract()

            ## SUBMITTAL/ISSUANCE + #
            sel2 = Selector(text = columns[0])
            # Select the text of any descendant except the link tags
            column1 = sel2.xpath("//*[not(name()='a')]/text()").extract()
            # Replace the new lines and other white space
            column1 = [element.replace("\r", "") for element in column1 if element.replace("\r", "") != ""]
            column1 = [element.replace("\n", "") for element in column1 if element.replace("\n", "") != ""]
            # itemdata["action_category"] = column1[0]
            # itemdata["action_accession"] = column1[1]


            ## DOC DATE / PUBLISH DATE
            sel2 = Selector(text = columns[1])
            # Select all text descendants
            column2 = sel2.xpath("//text()").extract()
            # Replace the new lines and other white space
            column2 = [element.replace("\r", "") for element in column2 if element.replace("\r", "") != ""]
            column2 = [element.replace("\n", "") for element in column2 if element.replace("\n", "") != ""]
            column2 = [element.replace("\t", "") for element in column2 if element.replace("\t", "") != ""]
            # itemdata["date_doc"] = column2[0]
            # itemdata["date_publish"] = column2[1]
            #
            ## DOCKET NUMBER / NUMBERS
            sel2 = Selector(text = columns[2])
            # Select the text of any descendant except the link tags
            column3 = sel2.xpath("//*[not(name()='a')]/text()").extract()
            # Replace the new lines and other white space
            column3 = [element.replace("\r", "") for element in column3 if element.replace("\r", "") != ""]
            column3 = [element.replace("\n", "") for element in column3 if element.replace("\n", "") != ""]
            column3 = [element.replace("\t", "") for element in column3 if element.replace("\t", "") != ""]
            # if len(column3) == 1:
            #     itemdata["docket_numbers"] = column3[0]
            # else:
            #     itemdata["docket_numbers"] = column3

            ## DESCRIPTION
            sel2 = Selector(text = columns[3])
            # Select all text descendants
            column4 = sel2.xpath("//text()").extract()
            # Replace the new lines and other white space
            column4 = [element.replace("\r", "") for element in column4 if element.replace("\r", "") != ""]
            column4 = [element.replace("\n", "") for element in column4 if element.replace("\n", "") != ""]
            column4 = [element.replace("\t", "") for element in column4 if element.replace("\t", "") != ""]
            itemdata["description"] = column4[0]
            # itemdata["availability"] = column4[1].split("Availability:")[-1].strip()

            #
            ## CLASS
            sel2 = Selector(text = columns[4])
            # Select all text descendants
            column5 = sel2.xpath("//text()").extract()
            # Replace the new lines and other white space
            column5 = [element.replace("\r", "") for element in column5 if element.replace("\r", "") != ""]
            column5 = [element.replace("\n", "") for element in column5 if element.replace("\n", "") != ""]
            column5 = [element.replace("\t", "") for element in column5 if element.replace("\t", "") != ""]
            # itemdata["class"] = column5[0]
            # itemdata["type"] = column5[1]

            ## FILE AND INFO TEXT
            sel2 = Selector(text = columns[6])
            column6_text = sel2.xpath("//a/text()").extract()
            # Replace the new lines and other white space
            column6_text = [element.replace("\r", "") for element in column6_text if element.replace("\r", "") != ""]
            column6_text = [element.replace("\n", "") for element in column6_text if element.replace("\n", "") != ""]
            column6_text = [element.replace("\t", "") for element in column6_text if element.replace("\t", "") != ""]

            # #
            ## FILE AND INFO LINKS
            column6_link = sel2.xpath("//a/@href").extract()
            # Replace the new lines and other white space
            column6_link = [element.replace("\r", "") for element in column6_link if element.replace("\r", "") != ""]
            column6_link = [element.replace("\n", "") for element in column6_link if element.replace("\n", "") != ""]
            column6_link = [element.replace("\t", "") for element in column6_link if element.replace("\t", "") != ""]
            column6_link = ["https://elibrary.ferc.gov/idmws/search/" + str(element) for element in column6_link]

            links_and_text = list(zip(column6_text, column6_link))
            for element in links_and_text:
                itemdata[str(element[0]).lower() + "_link"] = element[1]

            itemdata["query_docstart"] = response.meta["DocsStart"]
            itemdata["query_docscount"] = response.meta["DocsCount"]
            itemdata["query_docslimit"] = response.meta["DocsLimit"]
            itemdata["query_docket"] = response.meta["docket"]
            itemdata["query_textsearch"] = response.meta["textsearch"]


            # Generate a request to the server for the document info page
            # server accepts the doclist code in the form field
            info_query = FormRequest(url = "https://elibrary.ferc.gov/idmws/doc_info.asp",
                formdata = {"doclist" : itemdata["info_link"].split("doclist=")[-1]},
                callback=self.parse_info, dont_filter = True, meta = itemdata)
            yield info_query


        # Look for link to the "Next page" - the link itself isn't callable,
        # however the new request will be generated to the search query server
        # to replicate the following of such link in a browser
        next_pages = response.xpath('//a[text()="NextPage"]').extract()

        # Inherit the meta data from the previous request for new request.
        # Extract the numbers for what results to display and the query terms
        # such as dockets and search string
        docstart = int(response.meta["DocsStart"])
        docket = response.meta["docket"]
        search = response.meta["textsearch"]
        doccounter = int(response.meta["DocsCount"])
        docslimit = int(response.meta["DocsLimit"])

        # If the "Next page" link is found
        if len(next_pages) > 0:
            # Increment the nubmers for document counts so that unseen results
            # are displayed.
            docstart += doccounter
            docslimit += doccounter

            # Create a new request based on incremented and inhereted query
            # parameters
            new_query = FormRequest(url="https://elibrary.ferc.gov/idmws/search/results.asp",
                    formdata = {
                                "FROMdt" : "",
                                "TOdt" : "",
                                "firstDt" : "1/1/1904",
                                "LastDt" : "12/31/2037",
                                "DocsStart" : str(docstart),
                                "DocsLimit" : str(docslimit),
                                "date" : "All",
                                "SortSpec" : "filed_date desc accession_num asc",
                                "datefield" : "filed_date",
                                "dFROM" : "10/08/2017",
                                "dTO" : "11/08/2017",
                                "dYEAR" : "1",
                                "dMONTH" : "1",
                                "dDAY" : "1",
                                "date" : "All",
                                "category" : "submittal,issuance",
                                "libraryall" : "electric, hydro, gas, rulemaking, oil, general",
                                "docket" : str(docket),
                                "subdock_radio" : "all_subdockets",
                                "class" : "999",
                                "type" : "999",
                                "textsearch" : str(search),
                                "description" : "description",
                                "fulltext" : "fulltext",
                                "DocsCount" : str(doccounter)},
                    callback=self.parse_query, dont_filter = True)
            # pass the relevant meta data for another loop of "Next page"
            new_query.meta["DocsStart"] = str(docstart)
            new_query.meta["docket"] = str(docket)
            new_query.meta["textsearch"] = str(search)
            new_query.meta["DocsCount"] = str(doccounter)
            new_query.meta["DocsLimit"] = str(docslimit)
            # Issue the POST request to the server
            yield new_query

    def parse_info(self, response):

        # yield response.meta
        #### Bottom tables in the Info page such as dockets, correspondents etc.
        bottom_tables_xpath = '//table[not(.//table) and .//td and .//font and count(.//td)>1 and .//td[@bgcolor = "silver"]]'

        #### Bottom tables in the Info page such as dockets, correspondents etc.
        # Includes the table name so that tables are not parsed blindly (create
        # a new field for each row) but a special formatting is applied to each
        # kind of table by name
        bottom_tables_full_xpath = '//td[not(.//table//table) and .//td and .//font and count(.//td)>1 and .//td[@bgcolor = "silver"]]'

        ### Basic meta info however more detailed than the general query
        basic_info_table_xpath = '//tbody//tr[.//font and not(.//table) and .//td[@bgcolor = "silver"] and ./td[not(.//b)]]'

        ### Borderless tables in the info page that contain library data and
        # category data
        borderless_tables_xpath = '//td[.//table[.//td and .//font and not(.//td[@bgcolor = "silver"])] and count(.//table)<10]'

        # Start parsing the page with the most information-intensive tables
        # Extract all the tables with their names
        bottom_tables = response.xpath(bottom_tables_full_xpath).extract()

        # Declare lists to store data found in the tables
        document_class_type = []
        document_child_list = []
        document_parent_list = []
        associated_numbers = []
        docket_numbers = []
        output_row = {}

        # Iterate over each extracted table
        for bottom_table in bottom_tables:
            # New selector is declared to select rows in each table
            sel = Selector(text = bottom_table)
            # Extract the rows and table name separately
            extracted_rows = sel.xpath('//tr[not(.//tr)]').extract()
            bottom_table_name = sel.xpath('//td//b//text()').extract()
            # Replace the new lines and other white space
            bottom_table_name = [element.replace("\r", "") for element in bottom_table_name if element.replace("\r", "") != ""]
            bottom_table_name = [element.replace("\n", "") for element in bottom_table_name if element.replace("\n", "") != ""]
            bottom_table_name = [element.replace("\t", "") for element in bottom_table_name if element.replace("\t", "") != ""]
            # Select the first occurance of bold text after irrelevant
            # data was dropped or replaced
            bottom_table_name = bottom_table_name[0]
            # Drop the punctuation
            bottom_table_name = bottom_table_name.replace(":", "").strip()
            # Format to filter the tables in further steps
            bottom_table_name = bottom_table_name.replace(" ", "_").upper()
            # create an empty list to store column labels
            table_column_labels = []

            # Iterate over extracted rows
            for position, row in enumerate(extracted_rows):
                # Declare a selector to parse columns
                sel2 = Selector(text = row)
                # Extract the text from each column in a row
                extracted_text = sel2.xpath('//td//text()').extract()
                # Replace the new lines and other white space
                extracted_text = [element.replace("\r", "") for element in extracted_text]
                extracted_text = [element.replace("\n", "") for element in extracted_text]
                extracted_text = [element.replace("\t", "") for element in extracted_text]

                # The first row contains
                if position == 0:
                    # Pass the column labels to list declared above
                    table_column_labels = extracted_text
                # Parse every row after the column label row
                else:
                    # Parse the table with name CORRESPONDENT
                    if bottom_table_name == "CORRESPONDENT":
                        # Most consistent version of table formatting (on the
                        # FERC side). Usually empty name fields are marked with
                        # "x" or "*", this portion of code deals with such formatting
                        if len(extracted_text) == 5:
                            # Select name fields according to their correct
                            # absolute position (index)
                            first_name = extracted_text[2]
                            middle_name = extracted_text[3]
                            last_name = extracted_text[1]
                            # Declare list with name components First, Middle, Last
                            name_component_list = [first_name, middle_name, last_name]
                            # The most common formatting for empty name field is
                            # "*", default to this method
                            for component_position, name_component in enumerate(name_component_list):
                                if name_component == "x":
                                    name_component_list[component_position] = "*"
                            # Join the name to one string since first or middle
                            # name are not essential to analysis
                            full_name = ' '.join(map(str, name_component_list))
                            # Replace "*"
                            full_name = full_name.replace("* ", "").replace("*", "").strip()

                            # Create a column label according to the type of
                            # correspondent
                            name_column_label = bottom_table_name + "_" + extracted_text[0]  + "_NAME"
                            name_column_label = str(name_column_label).lower()

                            # Create a column label according to the name of
                            # correspondent's organization name
                            org_column_label = bottom_table_name + "_" + extracted_text[0]  + "_ORGANIZATION"
                            org_column_label = str(org_column_label).lower()

                            # Default name formatting is set to uppercase (there
                            # are some inconsistencies on FERC side using either
                            # uppercase or capitalized or lowercase)
                            output_row[name_column_label] = full_name.upper()
                            output_row[org_column_label] = extracted_text[4]
                        # Less consistent version of name formatting uses empty
                        # string rather then "x" or "*", therefore no text is
                        # extracted and relative indexing has to be used
                        else:
                            output_row["correspondent_type"] = bottom_table_name + "_" + extracted_text[0]
                            # Get the name using relative indexing
                            name_component_list = extracted_text[1:-1]
                            # The most common formatting for empty name field is
                            # "*", default to this method
                            for component_position, name_component in enumerate(name_component_list):
                                if name_component == "x":
                                    name_component_list[component_position] = "*"
                            # Join the name to one string since first or middle
                            # name are not essential to analysis
                            full_name = ' '.join(map(str, name_component_list))
                            # Replace "*"
                            full_name = full_name.replace("* ", "").replace("*", "").strip()

                            # Create a column label according to the type of
                            # correspondent
                            name_column_label = bottom_table_name + "_" + extracted_text[0]  + "_NAME"
                            name_column_label = str(name_column_label).lower()

                            # Create a column label according to the name of
                            # correspondent's organization name
                            org_column_label = bottom_table_name + "_" + extracted_text[0]  + "_ORGANIZATION"
                            org_column_label = str(org_column_label).lower()

                            # Default name formatting is set to uppercase (there
                            # are some inconsistencies on FERC side using either
                            # uppercase or capitalized or lowercase)
                            output_row[name_column_label] = full_name.upper()
                            output_row[org_column_label] = extracted_text[-1]

                    # Parse the table with name DOCUMENT_TYPE
                    if bottom_table_name == "DOCUMENT_TYPE":
                        # Separate the class and type with " - "
                        class_type_row = extracted_text[0] + " - " + extracted_text[1]
                        # Store multiple document types in a list
                        # Many document submissions/issuances have more than
                        # one type/class
                        document_class_type.append(class_type_row)

                    # Parse the table with names PARENT_DOCUMENTS and CHILD_DOCUMENTS
                    # Few submissions/issuances have these hieararchical tables
                    if bottom_table_name in ["PARENT_DOCUMENTS", "CHILD_DOCUMENTS"]:
                        # Drop empty text fields
                        extracted_text = [element for element in extracted_text if element != ""]

                        # Append the lists of parent/child documents according
                        # to the listed hierarchy type
                        if bottom_table_name.split("_")[0].lower() == "parent":
                            document_parent_list.append(" - ".join(extracted_text))
                        elif bottom_table_name.split("_")[0].lower() == "child":
                            document_child_list.append(" - ".join(extracted_text))

                    # Parse the table with name ASSOCIATED_NUMBERS
                    if bottom_table_name == "ASSOCIATED_NUMBERS":
                        # Drop empty text fields
                        extracted_text = [element for element in extracted_text if element != ""]
                        associated_numbers_row = " - ".join(extracted_text)
                        associated_numbers.append(associated_numbers_row)

                    # Parse the table with name DOCKET_NUMBERS
                    if bottom_table_name == "DOCKET_NUMBERS":
                        # Drop empty text fields
                        extracted_text = [element for element in extracted_text if element != ""]
                        # Join the docket and subdocket in one string
                        docket_numbers_row = "-".join(extracted_text[0:-1])
                        # Join the full docket string with the docket type
                        docket_numbers_row = " : ".join([docket_numbers_row, extracted_text[-1]])
                        # Append the list of dockets with all subdockets
                        # It is not very common but there are issuances with a
                        # substantially large list of dockets
                        docket_numbers.append(docket_numbers_row)
                    # if bottom_table_name not in ["DOCKET_NUMBERS", "ASSOCIATED_NUMBERS",
                    #         "PARENT_DOCUMENTS", "CHILD_DOCUMENTS", "DOCUMENT_TYPE", "CORRESPONDENT"]:
                        # yield {"pew" : [response.meta["info_link"], bottom_table_name]}



            # yield {"pew" : [response.meta["info_link"], bottom_table_name]}

        # Join each list of strings into one large string
        # This is done to avoid having too many columns. For example in a case
        # when a few dozen dockets are listed in one issuance, having a column
        # for each with result in a sparse matrix with low interpretabiltiy
        document_class_type = ", ".join(document_class_type)
        document_parent_list = ", ".join(document_parent_list)
        document_child_list = ", ".join(document_child_list)
        associated_numbers = ", ".join(associated_numbers)
        docket_numbers = ", ".join(docket_numbers)

        output_row["document_class_type"] = document_class_type
        output_row["document_child_list"] = document_child_list
        output_row["document_parent_list"] = document_parent_list
        output_row["associated_numbers"] = associated_numbers
        output_row["docket_numbers"] = docket_numbers

        # Extract information from the middle table
        # Table with no borders contains minor information and isn't clearly
        # displayed as a table
        borderless_tables = response.xpath(borderless_tables_xpath).extract()

        for borderless_table in borderless_tables:
            sel = Selector(text = borderless_table)
            # Extract the labels
            borderless_table_name = sel.xpath('//b//text()').extract()
            # Extract the text
            borderless_table_content = sel.xpath('//tr//text()').extract()
            # Replace the new lines and other white space
            borderless_table_name = [element.replace("\r", "") for element in borderless_table_name if element.replace("\r", "").strip() != ""]
            borderless_table_name = [element.replace("\n", "") for element in borderless_table_name if element.replace("\n", "").strip() != ""]
            borderless_table_name = [element.replace("\t", "") for element in borderless_table_name if element.replace("\t", "").strip() != ""]
            # Replace the new lines and other white space
            borderless_table_content = [element.replace("\r", "") for element in borderless_table_content if element.replace("\r", "").strip() != ""]
            borderless_table_content = [element.replace("\n", "") for element in borderless_table_content if element.replace("\n", "").strip() != ""]
            borderless_table_content = [element.replace("\t", "") for element in borderless_table_content if element.replace("\t", "").strip() != ""]
            # Format entries and append to item data dictionary
            for content_element in borderless_table_content:
                borderless_table_name = "".join(borderless_table_name)
                borderless_table_name = borderless_table_name.replace(":", "")
                borderless_table_name = borderless_table_name.strip()
                borderless_table_name = borderless_table_name.lower()
                # Mark the categories with binary labeling
                output_row[borderless_table_name + "_" + content_element.lower()] = "X"

        # Extract the table with basic info contained at the top of the page
        # Information usually mirrors the general query results page
        # with some extra information
        basic_info_rows = response.xpath(basic_info_table_xpath).extract()


        for basic_info_row in basic_info_rows:
            sel = Selector(text = basic_info_row)
            # Extract all column text
            basic_info_entry = sel.xpath('//td//text()').extract()
            # Replace all white space  and discard &nbsp
            basic_info_entry = [element.replace("\r", "") for element in basic_info_entry if element.replace("\r", "").strip() != ""]
            basic_info_entry = [element.replace("\n", "") for element in basic_info_entry if element.replace("\n", "").strip() != ""]
            basic_info_entry = [element.replace("\t", "") for element in basic_info_entry if element.replace("\t", "").strip() != ""]
            basic_info_entry = [element.replace("\t", "") for element in basic_info_entry if element.replace("\t", "").strip() != "&nbsp"]
            basic_info_entry = [element.strip() for element in basic_info_entry]
            # Split full row list into lists of 2 (column label + value)
            basic_info_entry = [basic_info_entry[i:i+2] for i in range(0,len(basic_info_entry),2)]
            # Iterate over each column label + value pair
            for entry in basic_info_entry:
                # Some instances of First Received Date being blank were observed.
                # Index out of range error is produced every time it occurs since
                # the column + value pair list that is yielded is of length = 1
                # i.e. only label is returned
                try:
                    # Set column label to lowercase, replace punctuation and
                    # white space. Do not do the same to values since white space
                    # is used to separate dates and time, PM and other important
                    # components
                    entry_label = entry[0].lower()
                    entry_label = entry_label.replace("-", "_")
                    entry_label = entry_label.replace(" ", "_")
                    entry_label = entry_label.replace(":", "")
                    output_row[entry_label] = entry[1]
                    # yield {"pew" : [response.meta["info_link"], entry_label, output_row[entry_label]]}
                except IndexError:
                    pass

        # Populate the output row with query data
        # Preserves search query data for future queries
        output_row["query_docstart"] = response.meta["query_docstart"]
        output_row["query_docscount"] = response.meta["query_docscount"]
        output_row["query_docslimit"] = response.meta["query_docslimit"]
        output_row["query_docket"] = response.meta["query_docket"]
        output_row["query_textsearch"] = response.meta["query_textsearch"]
        # Links to the info and file links of the submission/issuance
        output_row["info_link"] = response.meta["info_link"]
        output_row["file_link"] = response.meta["file_link"]
        # Accession description
        output_row["description"] = response.meta["description"]

        # Generate the request to the file page
        file_query = FormRequest(url = "https://elibrary.ferc.gov/idmws/file_list.asp",
            formdata = {"doclist" : output_row["info_link"].split("doclist=")[-1]},
            callback=self.parse_files, dont_filter = True, meta = output_row)

        # Yield the request
        yield file_query


    def parse_files(self, response):

        # Declare the xpath for the row extraction
        file_rows_xpath = "//table[.//a and .//input]//tr[.//text()[contains(.,'Type')]]/following-sibling::*[not(.//input[@type = 'button']) and not(.//img)]"

        # Data returned by the final crawl node is inherited from the
        # output row passed as meta
        item_data = response.meta

        sel = Selector(text = response.body)

        # Extract file rows from the returned page
        file_rows = sel.xpath(file_rows_xpath).extract()

        # File page consists of sections dedicated to each file format
        # Declare an empty list to populate with each section
        download_sections = []
        # Individual section that is populated, passed to the list of
        # sections and reinitialized
        download_section = []

        for file_row in file_rows:
            # New selector is declared to select rows in each table
            sel2 = Selector(text = file_row)
            # Extract the columns that have a horizontal rule tag
            # Sections are separated by horizontal lines
            hor_line = sel2.xpath('//td[.//hr]').extract()
            # If no such column is extracted - pass the row to the section
            if len(hor_line) == 0:
                download_section.append(file_row)
            # If there is a column with horizontal rule - break the section and
            # pass it to the sections list, declare an empty section
            else:
                download_sections.append(download_section)
                download_section = []

        # Declare three lists of title sections, file names and links to files
        all_section_down_titles = []
        all_section_down_text = []
        all_section_down_links = []


        for section in download_sections:
            # Populate individual section lists
            download_title = ""
            download_text = []
            download_links = []
            # Iterate over all the rows in each section
            for row_index, row in enumerate(section):
                # Declare a selector to parse each row
                sel3 = Selector(text = row)
                # First extracted row contains title information
                # Titles are separated by format so that files of one format
                # appear under the same section title
                if row_index == 0:
                    section_title = sel3.xpath('//text()').extract()


                    # Replace the new lines and other white space
                    # Also ignore some data that doesn't carry information like
                    # file size
                    section_title = [element.replace("\r", "") for element in section_title if element.replace("\r", "").strip() != ""]
                    section_title = [element.replace("\n", "") for element in section_title if element.replace("\n", "").strip() != ""]
                    section_title = [element.replace("\t", "") for element in section_title if element.replace("\t", "").strip() != ""]
                    section_title = [element.replace("\xa0", "") for element in section_title if element.replace("\t", "").strip() != ""]
                    section_title = [element.strip() for element in section_title if element.strip() != "All"]
                    section_title = [element for element in section_title if re.search("^(\d+)$", element) != True]

                    # Concatenate the section title into one string
                    download_title = "".join(section_title)
                else:
                    # Extract the file link text
                    section_text = sel3.xpath('//a/text()').extract()

                    # Replace the new lines and other white space
                    section_text = [element.replace("\r", "") for element in section_text if element.replace("\r", "").strip() != ""]
                    section_text = [element.replace("\n", "") for element in section_text if element.replace("\n", "").strip() != ""]
                    section_text = [element.replace("\t", "") for element in section_text if element.replace("\t", "").strip() != ""]
                    section_text = [element.replace("\xa0", "") for element in section_text if element.replace("\t", "").strip() != ""]
                    section_text = [element.strip() for element in section_text if element.strip() != ""]
                    section_text = [element.strip() for element in section_text if element.strip() != "No description given"]
                    section_text = [element for element in section_text if not re.search("^(\d+)$", element)]

                    # Extract the file link urls
                    section_link = sel3.xpath('//a/@href').extract()

                    # Replace the new lines and other white space
                    section_link = [element.replace("\r", "") for element in section_link if element.replace("\r", "").strip() != ""]
                    section_link = [element.replace("\n", "") for element in section_link if element.replace("\n", "").strip() != ""]
                    section_link = [element.replace("\t", "") for element in section_link if element.replace("\t", "").strip() != ""]

                    # Populate the list of file titles
                    if len(section_text) > 0:
                        for text_element in section_text:
                            download_text.append(text_element)

                    # Populate the list of file links
                    if len(section_link) > 0:
                        for link_element in section_link:
                            download_links.append(link_element)

            # Repeat the section title N times where N is the size of file list
            down_titles = [download_title] * len(download_links)
            # Populate the full lists of titles, section titles and links
            for position, row in enumerate(down_titles):
                all_section_down_titles.append(down_titles[position])
                all_section_down_text.append(download_text[position])
                all_section_down_links.append("https://elibrary.ferc.gov/idmws/" + download_links[position])

            # Create columns of link titles and link urls for each type of document :
            # i.e. a column for pdf links, a column for pdf file titles etc.
            item_data["file_down_text_" + download_title.lower().replace(" ", "_")] = ", ".join(download_text)
            item_data["file_down_link_" + download_title.lower().replace(" ", "_")] = ", ".join(download_links)

        # Create the top level DOCKET + SEARCH_STRING folder path
        docket_dir = [item_data["query_docket"], item_data["query_textsearch"]]
        docket_dir = [element for element in docket_dir if element != ""]
        docket_dir = "_".join(docket_dir)
        docket_path = os.path.join(download_folder, docket_dir)
        # Convert the document posting date to the right format:
        # Year_Month(month)_date for convenient folder sorting by name
        doc_date = datetime.strptime(item_data["document_date"].replace("/", "_"), "%m_%d_%Y").date()
        # Create item path using date
        item_path = os.path.join(docket_path, doc_date.strftime("%Y_%m(%B)_%d"))
        # Distinguish between publicly available documents and others, use
        # this data in folder naming so that it's apparent that the folder is
        # empty due to document's status
        if item_data["available"] == "Public":
            item_accession_path = os.path.join(item_path, item_data["accession_number"].replace("-", "_"))
        else:
            item_accession_path = os.path.join(item_path, item_data["accession_number"].replace("-", "_") + "_EMPTY_" + item_data["available"])

        # Record the folder location data in item dictionary
        item_data["path"] = str(item_accession_path)
        # Record all the names and links of the files downloaded
        item_data["all_file_names"] = ", ".join(all_section_down_text)
        item_data["all_file_links"] = ", ".join(all_section_down_links)

        # If the file exists - open it and update with the current item data
        try:
            with open(self.json_dir) as f:
                data = json.load(f)
            # If the data isn't in the dictionary already - write it to the file
            if item_data["info_link"].split("doclist=")[-1] not in data.keys():
                # If the document is availavle for download - yield a download
                # request
                if item_data["available"] == "Public":
                    for index, url in enumerate(all_section_down_links):
                        yield scrapy.Request(url, callback=self.parse_down,
                                meta = {"title" : all_section_down_titles[index],
                                        "text" : all_section_down_text[index],
                                        "initial_url" : all_section_down_links[index],
                                        "item_data" : item_data})
                # If not a public document - create an empty folder
                else:
                    if os.path.exists(download_folder):
                        pass
                    else:
                        os.mkdir(download_folder)
                    if os.path.exists(docket_path):
                        pass
                    else:
                        os.mkdir(docket_path)
                    if os.path.exists(item_path):
                        pass
                    else:
                        os.mkdir(item_path)
                    if os.path.exists(item_accession_path):
                        pass
                    else:
                        os.mkdir(item_accession_path)
                    unique_titles = list(set(all_section_down_titles))
                    for unique_title in unique_titles:
                        unique_title_path = os.path.join(item_accession_path, unique_title)
                        if os.path.exists(unique_title_path):
                            pass
                        else:
                            os.mkdir(unique_title_path)
                    try:
                        with open(self.json_dir) as jsr:
                            data = json.load(jsr)

                        data.update({item_data["info_link"].split("doclist=")[-1]: item_data})
                        # Write the file

                    except FileNotFoundError:
                        data = {item_data["info_link"].split("doclist=")[-1]: item_data}

                    with open(self.json_dir, 'w') as jsw:
                        json.dump(data, jsw)

        # If the file doesn't exist (scraper ran for the first time) - create the file
        except FileNotFoundError:
            # data = {item_data2["info_link"].split("doclist=")[-1]: item_data2}
            # with open(self.json_dir, 'w') as f:
            #     json.dump(data, f)
            # If the document is availavle for download - yield a download
            # request
            if item_data["available"] == "Public":
                for index, url in enumerate(all_section_down_links):
                    yield scrapy.Request(url, callback=self.parse_down,
                            meta = {"title" : all_section_down_titles[index],
                                    "text" : all_section_down_text[index],
                                    "initial_url" : all_section_down_links[index],
                                    "download_maxsize" : 0,
                                    "item_data" : item_data})
            # If not a public document - create an empty folder
            else:
                if os.path.exists(download_folder):
                    pass
                else:
                    os.mkdir(download_folder)
                if os.path.exists(docket_path):
                    pass
                else:
                    os.mkdir(docket_path)
                if os.path.exists(item_path):
                    pass
                else:
                    os.mkdir(item_path)
                if os.path.exists(item_accession_path):
                    pass
                else:
                    os.mkdir(item_accession_path)
                unique_titles = list(set(all_section_down_titles))
                for unique_title in unique_titles:
                    unique_title_path = os.path.join(item_accession_path, unique_title)
                    if os.path.exists(unique_title_path):
                        pass
                    else:
                        os.mkdir(unique_title_path)

                try:
                    with open(self.json_dir) as jsr:
                        data = json.load(jsr)

                    data.update({item_data["info_link"].split("doclist=")[-1]: item_data})
                    # Write the file

                except FileNotFoundError:
                    data = {item_data["info_link"].split("doclist=")[-1]: item_data}

                with open(self.json_dir, 'w') as jsw:
                    json.dump(data, jsw)


    def parse_down(self, response):

        # Inherit item data from the request meta (passed to response)
        item_data = response.meta["item_data"]

        # Copy the item data
        item_data2 = item_data.copy()
        # Drop the Scrapy meta data that is automatically passed into
        # meta part of the object
        drop_meta = ["download_latency", "download_slot", "download_timeout",
                        "depth", "retry_times", "download_maxsize"]
        for drop_item in drop_meta:
            if drop_item in item_data2.keys():
                del item_data2[drop_item]

        # Request is bounced via internal FERC server procedure, the end
        # url contains the file format, it's the only way to get the correct
        # file format
        try:
            file_name = str(response.url).split("&")[0].split("downloadfile=")[1]
        except IndexError:
            yield {"=============FILENAME ERROR=============" : response.url}

        try:
            file_format = re.search("[a-z]+$", file_name).group()
        except AttributeError:
            yield {"=============FORMAT ERROR=============" : file_name}

        # # Check whether the file tree exists for all elements of downloaded files
        # # of the item.
        # if os.path.exists(download_folder):
        #     pass
        # else:
        #     os.mkdir(download_folder)

        docket_dir = [item_data["query_docket"], item_data["query_textsearch"]]
        docket_dir = [element for element in docket_dir if element != ""]
        docket_dir = "_".join(docket_dir)

        docket_path = os.path.join(download_folder, docket_dir)

        if os.path.exists(docket_path):
            pass
        else:
            os.mkdir(docket_path)

        doc_date = datetime.strptime(item_data["document_date"].replace("/", "_"), "%m_%d_%Y").date()
        item_path = os.path.join(docket_path, doc_date.strftime("%Y_%m(%B)_%d"))

        if os.path.exists(item_path):
            pass
        else:
            os.mkdir(item_path)

        item_accession_path = os.path.join(item_path, item_data["accession_number"].replace("-", "_"))

        if os.path.exists(item_accession_path):
            pass
        else:
            os.mkdir(item_accession_path)

        unique_title_path = os.path.join(item_accession_path, response.meta["title"])
        if os.path.exists(unique_title_path):
            pass
        else:
            os.mkdir(unique_title_path)

        # Create the path to the final downloaded file
        final_file_path = os.path.join(unique_title_path, response.meta["text"] + "." + file_format)

        # Do nothing if the file was already downloaded
        # Extra safe check since the download request wouldn't be issued if the
        # file has already been downloaded
        if os.path.exists(final_file_path):
            pass
        # Download the file with the proper format if it hasn't been downloaded
        # yet. Uses "write bytes" so that other files rather than text files
        # are saved properly
        else:
            with open(final_file_path, "wb") as f:
                f.write(response.body)
            try:
                with open(self.json_dir) as jsr:
                    data = json.load(jsr)

                data.update({item_data2["info_link"].split("doclist=")[-1]: item_data2})
                # Write the file

            except FileNotFoundError:
                data = {item_data2["info_link"].split("doclist=")[-1]: item_data2}

            with open(self.json_dir, 'w') as jsw:
                json.dump(data, jsw)

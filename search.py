#!/usr/bin/python3

######################
# File System Search #
######################

# START: INFO
# Add script to /usr/local/bin and change name from "search.py" to "search"
# Next, send command in /usr/local/bin "chmod +x search"
# Script to search file system for files and/or directories
# Dependencies: ["os", "argparse", "logging"]
# END: INFO


# IMPORTS
import os
import sys
import logging


# START
print('Searching...')


# SET DATA
DIRECTORY_SEARCH = 0
FILE_SEARCH = 1
SEARCH_BOTH = 2
HOME_DIRECTORY = os.getenv('HOME')


# INITIALIZATION
output_directory = HOME_DIRECTORY + '/Documents/py_sys_search'
output_file = output_directory + '/search_output.txt'
log_file = output_directory + '/py_sys_search.log'
# Check if files and directories exist already
if not os.path.exists(output_directory):
    os.mkdir(output_directory)
# Set up logger
logging.basicConfig(filename=log_file,
                    level=logging.DEBUG,
                    filemode='w',
                    format='%(asctime)s - %(levelname)s: %(message)s',
                    datefmt='%Y%m%d_%H:%M:%S')
logging.debug('Logger for "py_sys_searcher" created...')
# Set defaults
search_root = HOME_DIRECTORY


# PARSE ARGUMENTS
logging.debug('Parsing command line arguments...')
search_exact = False
search_string = ''
num_arguments = len(sys.argv) - 1
logging.debug('Received {} command line arguments'.format(str(num_arguments)))
file_name = sys.argv[0]
if num_arguments == 0:
    logging.error('No argument passed from command line')
    exit(-1)
elif num_arguments == 1:
    search_type = SEARCH_BOTH
    search_string = sys.argv[1]
elif num_arguments > 1:
    real_args = []
    read_arg = 1
    max_read = num_arguments - 1
    while read_arg < max_read:
        real_args.append(sys.argv[read_arg])
    search_string = sys.argv[num_arguments]
    file_search = False
    directory_search = False
    for a in real_args:
        if (a == '-f') or (a == '--file') or (a == '--files'):
            file_search = True
        if (a == '-d') or (a == '--directory') or (a == '--directories'):
            directory_search = True
        if (a == '-e') or (a == '--exact'):
            # TODO: Fix this case
            search_exact = True
    if directory_search and not file_search:
        search_type = DIRECTORY_SEARCH
    elif file_search and not directory_search:
        search_type = FILE_SEARCH
    else:
        search_type = SEARCH_BOTH


logging.warning('Searching for string "{}"'.format(search_string))


# METHODS


# Returns a tuple of lists within "top_dir" => "(all_directories, all_files)"
def recursive_search(top_dir):
    logging.debug('Starting recursive file search...')
    found_items = os.listdir(top_dir)
    all_dirs = [top_dir]
    all_files = []
    search_dirs = []
    # First iteration
    if len(found_items) == 0:
        logging.warning('No files or sub-directories found under directory "{}"'.format(top_dir))
        return None, None
    for item in found_items:
        item_path = top_dir + '/' + item
        if os.path.isdir(item_path):
            search_dirs.append(item_path)
            all_dirs.append(item_path)
        if os.path.isfile(item_path):
            all_files.append(item_path)
    # Continuing iterations
    while len(search_dirs) != 0:
        next_dir = []
        for read_dir in search_dirs:
            try:
                contents = os.listdir(read_dir)
                for item in contents:
                    item_path = read_dir + '/' + item
                    if os.path.isdir(item_path):
                        next_dir.append(item_path)
                        all_dirs.append(item_path)
                    if os.path.isfile(item_path):
                        all_files.append(item_path)
            except IOError:
                logging.warning('Unable to read contents of {}...'.format(read_dir))
        search_dirs.clear()
        search_dirs.extend(next_dir)
    logging.debug('Found {} files and {} sub-directories under {}'.format(len(all_files), len(all_dirs), top_dir))
    # Return results
    return all_dirs, all_files


# Read file and directory names to find search results
def search_system(search_str, search_typ):
    full_results = []
    dirs, files = recursive_search(search_root)
    # Look in directories
    if (search_typ == DIRECTORY_SEARCH) or (search_typ == SEARCH_BOTH):
        dir_results = []
        for d in dirs:
            split_path = d.split('/')
            check_string = split_path[len(split_path) - 1]
            if search_str in check_string:
                dir_results.append(d)
                logging.debug('Potential directory match found "{}"'.format(d))
        full_results.extend(dir_results)
        logging.debug('Adding potential directory matches to results...')
    # Look in files
    if (search_typ == FILE_SEARCH) or (search_typ == SEARCH_BOTH):
        file_res = []
        for f in files:
            split_path = f.split('/')
            check_string = split_path[len(split_path) - 1]
            if search_str in check_string:
                file_res.append(f)
                logging.debug('Potential file match found "{}"'.format(f))
        full_results.extend(file_res)
        logging.debug('Adding potential file matches to results...')
    # Return results
    if search_exact:
        good_matches = []
        for r in full_results:
            split_path = r.split('/')
            check_string = split_path[len(split_path)]
            if search_str == check_string:
                good_matches.append(r)
                logging.debug('Exact match found "{}"'.format(r))
        return good_matches
    else:
        return full_results


# EXECUTION
results = search_system(search_str=search_string, search_typ=search_type)
num_results = len(results)
logging.debug('Search returned {} potential results'.format(str(num_results)))
if num_results <= 0:
    logging.debug('Search for "{}" returned 0 results'.format(search_string))
    print('Search returned no results...')
elif num_results < 25:
    # Print results out on console
    logging.debug('Outputting results to console...')
    for res in results:
        print(str(res))
else:
    # Write results to output file
    logging.debug('25+ results returned. Writing results to output file "{}"'.format(output_file))
    print('25+ results were returned. Writing results to "{}"'.format(output_file))
    file_string = 'RESULTS:\n\n'
    for res in results:
        add_line = res + '\n'
        file_string += add_line
    file = open(output_file, 'w')
    file.write(file_string)
    file.close()
logging.debug('Script completed. Terminating program...')
# END


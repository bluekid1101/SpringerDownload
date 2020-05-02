import csv
import requests
import os
import threading
from concurrent.futures import ThreadPoolExecutor
from timeit import default_timer as timer


def preprocess_url():
    link_list = []
    with open('seb.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            link_list.append(row[0])
    return link_list[1:]


def get_location_link(links):
    result = []
    for l in links:
        r = requests.get(l, allow_redirects=False)
        loc = r.headers.get('Location') if 'Location' in r.headers else None
        if bool(loc) is True:
            result.append(loc)
    return result


def check_dir():
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    folder_name = 'SpringerBooks1'
    chosen_dir = os.path.join(cur_dir, folder_name)
    if os.path.exists(chosen_dir):
        return chosen_dir
    else:
        os.makedirs(folder_name)
        return chosen_dir


thread_local = threading.local()


def get_session():
    if not hasattr(thread_local, "session"):
        thread_local.session = requests.Session()
    return thread_local.session


def download1(url):
    session = get_session()
    dir = check_dir()
    filename = url.replace('https://link.springer.com/book/', '')
    download_url = "".join(['https://link.springer.com/content/pdf/', filename, '.pdf'])
    with session.get(download_url) as page:
        fn = str.replace(page.headers.get('content-disposition'), 'filename=', '', 1)
        path = os.path.join(dir, fn)
        with open(path, 'wb') as output:
            output.write(page.content)
    print("Done", fn)


def download_all(sites):
    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(download1, sites)


def download(url):
    dir = check_dir()
    filename = url.replace('https://link.springer.com/book/', '')
    path = os.path.join(dir, "".join([filename, '.pdf']))
    download_url = "".join(['https://link.springer.com/content/pdf/', filename, '.pdf'])
    page = requests.get(download_url)
    with open(path, 'wb') as output:
        output.write(page.content)


if __name__ == "__main__":
    l = preprocess_url()
    a = get_location_link(l)
    print(a)
    start = timer()
    download_all(a)
    end = timer()
    print("Total time elapsed: {s} s for {n} books".format(s=end - start, n=len(a)))

# start = timer()
# for i in a:
#     download(i)
# end = timer()
# print("Total time elapsed: {s} s".format(s=end - start))
# with ThreadPoolExecutor(max_workers=5) as executor:
#     future_to_url = {executor.submit(download, url, 60): url for url in a}
#     future_to_url

# r = requests.get(l[0], allow_redirects=False)
# print(r.headers.get('Location'))

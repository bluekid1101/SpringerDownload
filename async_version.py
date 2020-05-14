import csv
import requests
import os
import asyncio
from timeit import default_timer as timer
import aiohttp
import aiofiles



def preprocess_url():
    link_list = []
    with open('seb.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            link_list.append(row[0])
    return link_list[1:]


def get_location_links(links):
    sites = []
    for l in links:
        r = requests.get(l, allow_redirects=False)
        loc = r.headers.get('Location') if 'Location' in r.headers else None
        if bool(loc) is True:
            sites.append(loc)
    return sites


def check_dir():
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    folder_name = 'SpringerBooks1'
    chosen_dir = os.path.join(cur_dir, folder_name)
    if os.path.exists(chosen_dir):
        return chosen_dir
    else:
        os.makedirs(folder_name)
        return chosen_dir


async def download_site(session, url):
    direct = check_dir()
    filename = url.replace('https://link.springer.com/book/', '')
    download_url = "".join(['https://link.springer.com/content/pdf/', filename, '.pdf'])
    async with session.get(download_url) as page:
        # print("Read {0} from {1}".format(page.content_length, url))
        fn = str.replace(page.headers.get('content-disposition'), 'filename=', '', 1)
        path = os.path.join(direct, fn)
        print(path)
        async with aiofiles.open(path, 'wb') as output:
            # data = await page.content.read()
            # if bool(data) is True:
            #     output.write(data)
            while True:
                chunk = await page.content.read(1024)
                if not chunk:
                    break
                await output.write(chunk)


async def download_all(sites):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in sites:
            task = asyncio.ensure_future(download_site(session, url))
            tasks.append(task)
        await asyncio.gather(*tasks, return_exceptions=True)


if __name__ == "__main__":
    l = preprocess_url()
    a = get_location_links(l)
    # a = get_location_links(l[:30])
    start = timer()
    asyncio.get_event_loop().run_until_complete(download_all(a))
    end = timer()
    print("Total time elapsed: {s} s for {n} books".format(s=end - start, n=len(a)))
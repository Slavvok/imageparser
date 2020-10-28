import aiohttp
import asyncio
import aiofiles
import pathlib
import re
import shutil
from urllib.parse import urlparse

PATH = pathlib.Path(__file__).parent.absolute()
URLS_FILE = 'urls.txt'
# TODO: Only full size images
IMAGE = re.compile(r'img .*?src="(.*?)"')
MAX_IMAGES = 10


async def fetch_image(session, url, num, directory):
    async with session.request(method="GET", url=url) as resp:
        if resp.status == 200:
            async with aiofiles.open(f'{directory}/image{num}.png', mode='wb') as f:
                await f.write(await resp.read())


async def find_images(session, url):
        resp = await session.request(method="GET", url=url)
        html = await resp.text()
        num = 0
        folder_name = urlparse(url).netloc
        directory = pathlib.Path(PATH, folder_name)

        await make_directory(directory)

        for image_url in IMAGE.findall(html):
            num += 1
            await fetch_image(session, image_url, num, directory)
            if num == MAX_IMAGES:
                break

        await make_archive(directory)
        await remove_directory(directory)


async def make_archive(directory):
    # TODO: Refactor
    shutil.make_archive(directory, 'zip', directory)


async def make_directory(directory):
    # TODO: Refactor
    if not directory.exists():
        directory.mkdir()


async def remove_directory(directory):
    # TODO: Refactor
    shutil.rmtree(directory)


async def pics_download():

    with open(f'{PATH}/{URLS_FILE}') as f:
        urls = set(map(str.strip, f))

    async with aiohttp.client.ClientSession() as session:
        tasks = list()
        for url in urls:
            tasks.append(find_images(session, url))
        await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(pics_download())

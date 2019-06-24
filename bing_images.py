import os
import queue
import threading
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
from logger import Logger
import traceback


class BingImages(object):
    def __init__(self):
        self.base_url = "https://bing.ioliu.cn"
        self.logger = Logger("bing")
        self.first_queue = queue.Queue(maxsize=25)
        self.second_queue = queue.Queue(maxsize=25)
        self.third_queue = queue.Queue(maxsize=25)
        self.forth_queue = queue.Queue(maxsize=25)
        self.queues = [self.first_queue, self.second_queue, self.third_queue, self.forth_queue]
        self.assign_urls()
        self.file_path = "E:\\BingImages\\"

    def assign_urls(self):
        count = 0
        for single_queue in self.queues:
            while count < 100:
                count += 1
                url = urljoin(self.base_url, "/?p={}".format(count))
                single_queue.put(url, True)
                if count % 25 == 0:
                    break
        self.logger.info("finish assigning urls")

    @staticmethod
    def open_html(url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                          ' (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive'
        }
        try:
            req = requests.get(url, headers=headers)
            html_data = req.content.decode("utf-8", "ignore")
            req.close()
            return html_data
        except Exception as e:
            print("open html error: ", e)
            with open("error.log", 'a+') as f:
                f.write("open html\n" + url + "\n" + traceback.format_exc() + "\n\t")

    @staticmethod
    def parser_html(html, collection):
        soup = BeautifulSoup(html, 'html.parser')
        tags = soup.find_all("a", attrs={'class': 'mark'})
        for tag in tags:
            collection.add(tag['href'])

    def download_images(self, parameter):
        self.check_file_path()
        thread_name = threading.current_thread().getName()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                          ' (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

        self.logger.info("{} start download images".format(thread_name))
        images_links = set()

        while True:
            try:
                url = parameter.get(True, 20)
            except queue.Empty:
                self.logger.info("{} has task done".format(thread_name))
                break
            else:
                self.logger.info("{}".format(url))
                html_data = BingImages.open_html(url)
                BingImages.parser_html(html_data, images_links)

                while len(images_links) > 0:
                    partial_link = images_links.pop()
                    image_link = urljoin(self.base_url, partial_link.split("?")[0] + "?force=download")
                    images_name = partial_link.split("?")[0].split("/")[2]
                    try:
                        with requests.get(url=image_link, headers=headers, stream=True) as req:
                            with open(r"{}{}{}".format(self.file_path, images_name, ".jpg"), "wb") as f:
                                for chunk in req.iter_content(1024):
                                    try:
                                        f.write(chunk)
                                    except IOError as e_io:
                                        print("save picture error: ", e_io)
                                        with open("error.log", 'a+') as f_error:
                                            f_error.write("save picture\n" + image_link +
                                                          "\n" + traceback.format_exc() + "\n\t")
                    except Exception as e_http:
                        print("open photo page error: ", e_http)
                        with open("error.log", 'a+') as f:
                            f.write("get download links\n" + image_link + "\n" + traceback.format_exc() + "\n\t")

    def check_file_path(self):
        if os.path.exists(self.file_path):
            pass
        else:
            self.logger.info("directory is not existed, it will be created")
            os.mkdir(self.file_path)

    def start(self):
        for single_queue in self.queues:
            thread = threading.Thread(target=self.download_images, args=(single_queue,))
            thread.start()

    @staticmethod
    def test():
        s = set()
        # self.assign_urls()
        # print("first_queue: ", self.first_queue.qsize())
        # print("second_queue: ", self.second_queue.qsize())
        # print("third_queue: ", self.third_queue.qsize())
        # print("forth_queue: ", self.forth_queue.qsize())
        html = BingImages.open_html("https://bing.ioliu.cn/?p=1")
        BingImages.parser_html(html, s)


if __name__ == '__main__':
    bing_images = BingImages()
    bing_images.test()
    # bing_images.start()








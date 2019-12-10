import threading
from urllib.parse import urljoin
from bing_images import BingImages
import time


class LatestPhotos(BingImages):
    def __init__(self):
        super().__init__()
        self.queues = [self.first_queue, self.second_queue]

    def assign_urls(self):
        self.first_queue.put(urljoin(self.base_url, "/?p=1"))
        self.second_queue.put(urljoin(self.base_url, "/?p=2"))


if __name__ == '__main__':
    latest_photos = LatestPhotos()
    startTime = time.time()
    latest_photos.start()
    while True:
        if threading.active_count() == 1:
            d_time = time.time() - startTime
            print("==============================")
            print("+++DuringTime: %.2fs" % d_time)
            break








import time

from gevent import monkey; monkey.patch_all()
import gevent
from urllib.parse import urljoin
from bing_images import BingImages


class LatestPhotos(BingImages):
    def __init__(self):
        super().__init__()
        self.queues = [self.first_queue, self.second_queue]

    def assign_urls(self):
        self.first_queue.put(urljoin(self.base_url, "/?p=1"))
        self.second_queue.put(urljoin(self.base_url, "/?p=2"))

    def start(self):
        for single_queue in self.queues:
            job = gevent.spawn(self.download_images, single_queue)
            job.join()


if __name__ == '__main__':
    latest_photos = LatestPhotos()
    startTime = time.time()
    latest_photos.start()
    d_time = time.time() - startTime
    print("==============================")
    print("+++DuringTime: %.2fs" % d_time)






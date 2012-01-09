from xbmcswift import Plugin, xbmc, xbmcplugin
import resources.lib.scraper as scraper


class Plugin_adv(Plugin):

    def add_items(self, iterable, view_mode=None, is_update=False,
                  sort_method_ids=[]):
        items = []
        urls = []
        for i, li_info in enumerate(iterable):
            items.append(self._make_listitem(**li_info))
            if self._mode in ['crawl', 'interactive', 'test']:
                print '[%d] %s%s%s (%s)' % (i + 1, '', li_info.get('label'),
                                            '', li_info.get('url'))
                urls.append(li_info.get('url'))
        if self._mode is 'xbmc':
            if view_mode:
                xbmc.executebuiltin('Container.SetViewMode(%s)' % view_mode)
            xbmcplugin.addDirectoryItems(self.handle, items, len(items))
            for id in sort_method_ids:
                xbmcplugin.addSortMethod(self.handle, id)
            xbmcplugin.endOfDirectory(self.handle, updateListing=is_update)
        return urls


plugin = Plugin_adv('Onlinewelten.com Videos', 'plugin.video.onlinewelten',
                    __file__)


@plugin.route('/', default=True)
def show_categories():
    categories = scraper.getCategories()
    items = [{'label': category['name'],
              'url': plugin.url_for('show_videos',
                                    path=category['path'], page='1'),
             } for i, category in enumerate(categories)]
    return plugin.add_items(items)


@plugin.route('/category/<path>/<page>/')
def show_videos(path, page):
    videos, has_next_page = scraper.getVideos(path, page)
    items = [{'label': video['title'],
              'thumbnail': video['image'],
              'info': {'originaltitle': video['title'],
                       'duration': video['length'],
                       'date': video['date'],
                       'plot': video['description'],
                       'votes': str(video['views'])},
              'url': plugin.url_for('watch_video', url=video['url']),
              'is_folder': False,
              'is_playable': True,
             } for video in videos]
    if has_next_page:
        next_page = str(int(page) + 1)
        items.insert(0, {'label': '>> %s %s >>' % (plugin.get_string(30001),
                                                   next_page),
                         'url': plugin.url_for('show_videos',
                                               path=path,
                                               page=next_page)})
    if int(page) > 1:
        prev_page = str(int(page) - 1)
        items.insert(0, {'label': '<< %s %s <<' % (plugin.get_string(30001),
                                                   prev_page),
                         'url': plugin.url_for('show_videos',
                                               path=path,
                                               page=prev_page)})
    is_update = (int(page) != 1)
    sort_method_ids = (21, 3, 29)
    return plugin.add_items(items, is_update=is_update,
                            sort_method_ids=sort_method_ids)


@plugin.route('/watch/<url>/')
def watch_video(url):
    video_url = scraper.getVideoFile(url)
    return plugin.set_resolved_url(video_url)


if __name__ == '__main__':
    plugin.run()

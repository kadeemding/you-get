#!/usr/bin/env python

__all__ = ['yxfshop_download_by_url']

from ..common import *
from lxml import etree


def yxfshop_download_by_url(url, output_dir='.', merge=True, info_only=False, **kwargs):
    html = get_html(url)
    title = re.search(r'<h1 class="goodsname".+?>(.+?)</h1>', html).group(1)
    product = re.search(r'id="pdt-(\d+?)"', html).group(1)
    print('Url    :     ', url)
    print('Site   :     ', site_info)
    print('Title  :     ', unescape_html(tr(title)))
    print('Product:     ', product)

    main_pics = re.findall(r'c_src="(.+?)"', html)
    doc = etree.HTML(html)
    desc_imgs = doc.xpath('//div[@id="goods-intro"]//img')
    desc_pics = []
    for desc_img in desc_imgs:
        desc_pics.append(desc_img.get('src'))

    if not info_only:
        for i, main_pic in enumerate(main_pics):
            mime, ext, size = url_info(main_pic)
            download_urls([main_pic], '主图%04d' % i, ext, size, os.path.join(output_dir, product), merge=merge)
        for i, desc_pic in enumerate(desc_pics):
            mime, ext, size = url_info(desc_pic)
            download_urls([desc_pic], '描述图%04d' % i, ext, size, os.path.join(output_dir, product), merge=merge)


site_info = "yxfshop.com"
download = yxfshop_download_by_url
download_playlist = playlist_not_supported('yxfshop')

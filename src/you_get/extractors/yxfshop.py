#!/usr/bin/env python

__all__ = ['yxfshop_download_by_url', 'yxfshop_download_playlist_by_url']

from ..common import *
from lxml import etree
from functools import reduce
import datetime
import pytz
import json
import codecs


def yxfshop_download_by_url(url, output_dir='.', merge=True, info_only=False, **kwargs):
    html = get_html(url)
    title = re.search(r'<h1 class="goodsname".+?>(.+?)</h1>', html).group(1)
    product = re.search(r'id="pdt-(\d+?)"', html).group(1)
    title = unescape_html(tr(title))
    print('Url    :     ', url)
    print('Site   :     ', site_info)
    print('Title  :     ', title)
    print('Product:     ', product)

    utc_tz = pytz.timezone('UTC')
    product_info = {
        'title': title,
        'date': datetime.datetime.now(tz=utc_tz).isoformat(),
        'tags': [],
        'categories': [],
        'images': [],
        'thumbnailImage': '',
        'actualPrice': '',
        'comparePrice': '',
        'inStock': True,
        'options': {
            'Color': [],
            'Size': []
        },
        'variants': [{
            'optionCombination': [],
            'comparePrice': '',
            'actualPrice': '',
            'inStock': True
        }]
    }

    main_pics = re.findall(r'c_src="(.+?)"', html)
    doc = etree.HTML(html)
    desc_imgs = doc.xpath('//div[@id="goods-intro"]//img')
    desc_pics = []
    for desc_img in desc_imgs:
        desc_pics.append(desc_img.get('src'))

    product_dir = os.path.join(output_dir, product)
    if not info_only:
        for i, main_pic in enumerate(main_pics):
            mime, ext, size = url_info(main_pic)
            if product_info['thumbnailImage'] == '':
                product_info['thumbnailImage'] = 'img/%s/%s_main_%04d.%s' % (product, product, i, ext)
            product_info['images'].append('img/%s/%s_main_%04d.%s' % (product, product, i, ext))
            download_urls([main_pic], '%s_main_%04d' % (product, i), ext, size, product_dir, merge=merge)
        for i, desc_pic in enumerate(desc_pics):
            mime, ext, size = url_info(desc_pic)
            product_info['images'].append('img/%s/%s_desc_%04d.%s' % (product, product, i, ext))
            download_urls([desc_pic], '%s_desc_%04d' % (product, i), ext, size, product_dir, merge=merge)
        rows = doc.xpath('//div[@id="goods_products_list_buy"]//thead/tr')
        info = [url, title]
        for row in rows:
            f1 = row.xpath('./th[1]/text()')
            f2 = row.xpath('./th[2]/text()')
            f3 = row.xpath('./th[3]/text()')
            f4 = row.xpath('./th[6]/text()')
            info.append('%s, %s, %s, %s' % (f1, f2, f3, f4))
        rows = doc.xpath('//div[@id="goods_products_list_buy"]//tbody/tr')
        for row in rows:
            f1 = row.xpath('./td[1]/text()')
            f2 = row.xpath('./td[2]/text()')
            f3 = row.xpath('./td[3]/text()')
            f4 = row.xpath('./td[6]/text()')
            info.append('%s, %s, %s, %s' % (f1, f2, f3, f4))
        info = map(lambda x: x + '\n', info)
        product_info_str = json.dumps(product_info, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ': '))
        fo = codecs.open(os.path.join(product_dir, '%s.md' % product), "w", 'utf-8')
        fo.write(product_info_str)
        fo.write('\n\n')
        fo.writelines(info)
        fo.close()


def yxfshop_download_playlist_by_url(url, output_dir='.', merge=True, info_only=False, **kwargs):
    products = []
    if os.path.exists("products.txt"):
        fo = open("products.txt", "r")
        products = fo.readlines()
        fo.close()
    list_url_template = 'http://www.yxfshop.com/?gallery-_ANY_--0--%d---20-index.html'
    page = 1
    while True:
        list_url = list_url_template % page
        print(list_url)
        html = get_html(list_url)
        doc = etree.HTML(html)
        items_list = doc.xpath('//div[@class="items-list"]//td[@class="goodpic"]/a')
        for item in items_list:
            item_str = etree.tostring(item, encoding='unicode')
            href = re.search(r'href="(.+?)"', item_str).group(1)
            img_src = re.search(r'src="(.+?)"', item_str).group(1)
            alt = re.search(r'alt="(.+?)"', item_str).group(1)
            if '勿拍' in alt:
                continue
            if 'default_thumbnail_pic' in img_src:
                continue
            if len(list(filter(lambda x: x == href, products))) > 0:
                continue
            yxfshop_download_by_url(href)
            products.append(href)
        next_elm = doc.xpath('//span[@class="next" and @title="已经是最后一页"]')
        if next_elm is None or len(next_elm) == 0:
            page = page + 1
        else:
            break
    products = reduce(lambda x, y: x if y in x else x + [y], products, [])
    products = map(lambda x: x + '\n', products)
    fo = open("products.txt", "w")
    fo.writelines(products)
    fo.close()


site_info = "yxfshop.com"
download = yxfshop_download_by_url
download_playlist = yxfshop_download_playlist_by_url

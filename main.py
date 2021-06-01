import time
import requests
import bs4
import pandas as pd
import datetime


# 获取网页
def getHTMLText(url):
    # 关闭现有HTTP连接
    s = requests.session()
    s.keep_alive = False

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0'}
        r = requests.get(url, headers=headers, timeout=30)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except requests.HTTPError as e:
        print(e)
        print("HTTPError")
    except requests.RequestException as e:
        print(e)
    except:
        print("Unknown Error !")


# 解析网页
def parseHtml(html):
    bsObj = bs4.BeautifulSoup(html, "html.parser")
    info = []  # 储存所有信息
    # 获取电影列表
    tblist = bsObj.find_all('table', attrs={'class': 'tbspan'})

    # 对一页里面的每一个电影单独解析处理
    for item in tblist:
        movie = dict()
        link = item.b.find_all('a')[1]

        # 获取电影详情的url
        url = "https://www.dy2018.com" + link["href"]

        try:
            time.sleep(1)

            # 解析电影详情页
            temp = bs4.BeautifulSoup(getHTMLText(url), "html.parser")

            # 查找id为Zoom的tag
            contentFind = temp.find_all(id='Zoom')
            # 查找带有img标签的tag
            picFind = contentFind[0].find_all('img')

            # 影片图片和截图
            pics = []

            for pic in picFind:
                pics.append(pic['src'])

            # 对其他数据进行处理
            tmpInfo = str(contentFind[0]).replace('\u3000', '').split('<br/>')

            movie['图片'] = pics

            for i in range(0, len(tmpInfo)):
                if '◎译名' == tmpInfo[i][:3]:
                    movie['译名'] = tmpInfo[i][3:]
                if '◎片名' == tmpInfo[i][:3]:
                    movie['片名'] = tmpInfo[i][3:]
                if '◎年代' == tmpInfo[i][:3]:
                    movie['年代'] = tmpInfo[i][3:]
                if '◎产地' == tmpInfo[i][:3]:
                    movie['产地'] = tmpInfo[i][3:]
                if '◎类别' == tmpInfo[i][:3]:
                    movie['类别'] = tmpInfo[i][3:].split('/')
                if '◎语言' == tmpInfo[i][:3]:
                    movie['语言'] = tmpInfo[i][3:]
                if '◎字幕' == tmpInfo[i][:3]:
                    movie['字幕'] = tmpInfo[i][3:]
                if '◎上映日期' == tmpInfo[i][:5]:
                    movie['上映日期'] = tmpInfo[i][5:15]
                if '◎片长' == tmpInfo[i][:3]:
                    movie['片长'] = tmpInfo[i][3:]
                if '◎导演' == tmpInfo[i][:3]:
                    movie['导演'] = tmpInfo[i][3:]
                if '◎主演' == tmpInfo[i][:3]:
                    actors = [tmpInfo[i][3:]]
                    for j in range(i + 1, len(tmpInfo)):
                        if '◎' in tmpInfo[j]:
                            break
                        else:
                            actors.append(tmpInfo[j])
                    movie['主演'] = actors
                if '◎简介' == tmpInfo[i][:3]:
                    movie['简介'] = tmpInfo[i + 1]

            tbody = temp.find_all('tbody')

            downloads = []

            # 将电影下载链接放入movie列表
            for i in tbody:
                download = i.a.text

                downloads.append(download)

            movie['下载链接'] = downloads

            print(movie)

            # 将电影信息全部放入电影列表中
            info.append(movie)
        except Exception as e:
            print(e)
    return info


# 储存电影信息
def saveDate(data):
    file_name = 'movies.csv'  # 可用正则表达式，自动选取名字

    dataFrame = pd.DataFrame(data)
    dataFrame.to_csv(file_name, mode='a', index=False)


# 主函数
def main():
    start_url = "https://www.dy2018.com/"
    depth = 10  # 翻页器，可以自定义翻页数
    style = 20  # 不同类型的电影，共20类
    for j in range(style):
        print("正在爬取第" + str(1 + j) + "类电影信息")
        first_url = start_url + str(1 + j) + "/index"
        for i in range(depth):
            print("正在爬取第" + str(1 + i) + "页电影信息")
            if i == 0:
                url = first_url + ".html"  # 处理第一页,可设计处理“1”，实现不同类型的电影爬取
            else:
                url = first_url + "_" + str(i * 2) + ".html"  # 翻页

            html = getHTMLText(url)

            # 等待2秒继续
            time.sleep(2)

            movies = parseHtml(html)
            saveDate(movies)


if __name__ == '__main__':
    print('爬虫开始启动')
    start_time = datetime.datetime.now()
    main()
    end_time = datetime.datetime.now()
    print("程序总共用时：{:}".format(end_time - start_time))
    print('爬取页面结束')

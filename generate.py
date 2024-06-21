import IPython.display
import requests
from bs4 import BeautifulSoup
import random
import threading
import os


class CrawlInterview:
    def __init__(self):
        self.baseUrl = 'https://gw-c.nowcoder.com/api/sparta/pc/search?_=1718804312152'
        self.baseRequestBody = '{"type":"all","query":"java","page":2,"tag":[],"order":"","gioParams":{"searchFrom_var":"顶部导航栏","searchEnter_var":"主站"}}'
        self.headers = {
            "Content-Type": "application/json;charset=UTF-8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; ...)",
        }
        self.data = {
            "type": "all",
            "query": "java",
            "page": 2,
            "tag": [
                {"name": "面经", "id": 818, "count": None}
            ]
        }
        self.detailBaseUrl = 'https://www.nowcoder.com/feed/main/detail/'
        self.selectKeyWords = [f'{i}.' for i in range(1, 30)]
        self.selectKeyWords.extend([f'{i}、' for i in range(1, 30)])
        self.exceptKeyWords = ['反问', '一面', '二面', '三面', '面经']

        self.question_count = 30
        self.question_cache = []
        self.thread = None
        self.shufflePage = [i for i in range(1, 30)]
        random.shuffle(self.shufflePage)
        self.query_count = 0

    def parseHtml(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        # print(detailRes.text)
        divContent = soup.find(
            'div', class_='feed-content-text tw-text-gray-800 tw-mb-4 tw-break-all')
        ans = []
        if divContent:
            for item in divContent.contents:
                flag = False
                for exceptKeyWord in self.exceptKeyWords:  # 排除项
                    if exceptKeyWord in item:
                        flag = True
                        break
                if flag:
                    continue

                for selectKeyWord in self.selectKeyWords:
                    if selectKeyWord[:3] in item:
                        ans.append(item)
        else:
            # print(f"div content is None")
            pass
        return ans

    def generate(self):
        if len(self.question_cache) > 0:
            if self.thread == None or not self.thread.is_alive():
                self.thread = threading.Thread(target=self._generate)
                self.thread.start()
        else:
            self._generate()
            self.thread = threading.Thread(target=self._generate)
            self.thread.start()
        print(f'目前题库数量为：{len(self.question_cache)}')
        return self.getRandomAns(self.question_cache)

    def _generate(self):
        self.data['page'] = self.shufflePage[self.query_count]
        self.query_count += 1

        response = requests.post(
            self.baseUrl, headers=self.headers, json=self.data)
        ans = []
        if response.status_code == 200:
            # print("请求成功！")
            result = response.json()
            # random_records = random.sample(result['data']['records'],10)
            for item in result['data']['records']:
                # for item in random_records:

                # 没有momentData的是没有面经的
                temp = item['data'].get('momentData', None)
                if temp:
                    uuid = temp['uuid']
                    detailRes = requests.get(self.detailBaseUrl + uuid)
                    ans.extend(self.parseHtml(detailRes.text))
            self.question_cache.extend(ans)
            # ans = self.getRandomAns(ans)
            # return ans
        else:
            print(f"请求失败，状态码：{response.status_code}")
            print(response.text)

    def getRandomAns(self, ans):
        if len(self.question_cache) >= self.question_count:
            random_ans = random.sample(ans, self.question_count)
        else:
            random_ans = self.question_cache
        for i in range(len(random_ans)):
            random_ans[i] = random_ans[i].replace('\xa0', '')
            idx = random_ans[i].find('.')
            if idx != -1:
                random_ans[i] = f'{i+1}.' + random_ans[i][idx+1:]
            else:
                idx = random_ans[i].find('、')
                if idx != -1:
                    random_ans[i] = f'{i+1}.' + random_ans[i][idx+1:]
        return random_ans


interview = CrawlInterview()
print('爬取中...')

while True:
    ans = interview.generate()
    for item in ans:
        print(item)

    print('回车重新生成')
    input()
    os.system('cls')

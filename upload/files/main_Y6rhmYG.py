import pandas as pd
from library import *
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor, defer
class EventSpider(scrapy.Spider):
    name = 'event'
   
    def start_requests(self):
        
        urls = [f'https://{self.t_name}.evenue.net/cgi-bin/ncommerce3/SEPyos?linkID={self.t_code}&get=sect&itC=GS:{self.code}:{self.game_code}:{self.gamecode}{"{:02d}".format(i)}:&randomDate=935'  for i in range(self.start, 40)]
        for i, url in enumerate(urls):
            time.sleep(1)
            url1 = url.replace("nan", "")
            yield scrapy.Request(url1, callback=self.parse, cb_kwargs=dict(i=i))
  
    
    def parse(self, response,i):
        print("Second step")
        dataraw = response.text
        datajson = json.loads(dataraw)
        data = datajson['value']
        secdf = pd.DataFrame(data=data)
        secdf = secdf.transpose()
        secdf.rename(columns = { 0: 'so', 1: 'pl' }, inplace=True)
        secdf = secdf.drop(['so'],axis=1)
        # secdf.drop(secdf.filter(regex="Unname"),axis=1, inplace=True)
        # secdf.drop('Unnamed: 0',inplace=True)
        secdf['Sections'] = secdf.index
        secdf.reset_index(inplace=True)
        secdf.drop(['index'],inplace=True,axis=1)
        # print(secdf)
        tempdf = secdf.explode('pl').reset_index(drop=True)
        tempdf = tempdf['pl'].values.tolist()
        temp = pd.DataFrame(tempdf)
        # templist = secdf['pl'].tolist()
        secdf = secdf.merge(temp,left_index=True,right_index=True)
        secdf.drop(['pl'],inplace=True,axis=1)
        secdf.rename({'cd': 'pricel','cn':'count','tc':'capacity'},inplace=True,axis=1)
        # print(secdf)
      
        prize_url1=f"https://{self.t_name}.evenue.net/pac-api/catalog/plpt/price/{self.game_code}/{self.gamecode}{'{:02d}'.format(i+1)}?_={self.prize_id}"
        prize_url1 = prize_url1.replace("nan", "")
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
        'pac-context-data': '{"distributorId":"'f"{self.code}"'","dataAccountId":"'f"{self.data_id}"'","daylightSavingsTime":false}',
        'Host': f'{self.t_name}.evenue.net'}
        print(headers)
            

        time.sleep(1)
        yield scrapy.Request(prize_url1,meta={'secdf':secdf},callback=self.parseprice,headers=headers,cb_kwargs=dict(i=i))
        
    def parseprice(self,response,i):
        
            print("Third step")
            secdf = pd.DataFrame(response.meta['secdf'])
            dataraw = response.text
            datajson = json.loads(dataraw)
            # print(datajson)
            data = datajson['plptRange']
            pldf = pd.DataFrame(data=data)
            finaldf = secdf.merge(pldf[['PL','PLPT_PRICE']],left_on='pricel',right_on='PL',how='left')
            finaldf.drop(['pricel','PL'],axis=1,inplace=True)
            finaldf['PLPT_PRICE'] = finaldf['PLPT_PRICE'].apply(lambda x: x/100)
            # print(finaldf)
         
            #folder for csv files store
            if not os.path.exists(f'{var}\\{self.t_name}'):
                os.makedirs(f'{var}\\{self.t_name}')

            finaldf.to_csv(f"{var}\\{self.t_name}\\{i+1}.csv",index=False)
            print(f'save into :file{i+1}.csv')

df = pd.read_excel('E:\\PYTHON\\SCRAPE PROJECT\\EVENTS\\teams.xlsx')

@defer.inlineCallbacks
def crawl():
    runner = CrawlerRunner(get_project_settings())

    for i in range((1)): #(len(df))
        row = df.iloc[4]
        t_name = row['Team Name']
        code = row['team code/distributorId']
        t_code = row['t_code']
        gamecode = row['game__code']
        countid = row['team count']
        prize_id = row['prize id']
        data_id = row['dataAccountid']
        game_code = row['game_code']
        start=row['start']
        
        yield runner.crawl(EventSpider, t_name=t_name, code=code, t_code=t_code, gamecode=gamecode, countid=countid, prize_id=prize_id,
                        data_id=data_id, game_code=game_code,start=start)

    reactor.stop()

if __name__ == "__main__":
    crawl()
    reactor.run()

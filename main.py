from bs4 import BeautifulSoup
import os
from datetime import datetime
from pandas import DataFrame
from Youtube_data import YoutubeAnalysis as YA
from Youtube_data import UserAnalsis as UA




class MainDataAnalysis:




    def __init__(self,watchhis_path,filepath):


        self.save_dir = filepath
        self.save_dir_logs = filepath + '/LOGS/'
        self.save_dir_analysis = filepath + '/User_analysis/'

        os.makedirs(self.save_dir, exist_ok=True)
        os.makedirs(self.save_dir_logs, exist_ok=True)
        os.makedirs(self.save_dir_analysis, exist_ok=True)


        soup = self.read_file(watchhis_path)
        self.transform_to_xls(soup)


        pass


    def read_file(self,pathname):
        soup = BeautifulSoup(open(pathname), 'html.parser')
        return soup



    def transform_to_xls(self,soup):
        div_data = soup.find_all('div', class_='content-cell mdl-cell mdl-cell--6-col mdl-typography--body-1')
        data = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [] , 'vlink':[]}

        for dt in div_data:
            a_tag = dt.find_all('a')
            flag = 0

            for a in a_tag:

                if flag > 3:
                    data[5].append(a)
                    break

                link_v=a['href']
                data[flag].append(link_v)
                if flag==0:
                    data['vlink'].append( link_v.split('=')[-1])
                flag += 1
                data[flag].append(a.get_text().replace('\n', '').replace('\r', '').strip())
                flag += 1

            while (flag < 4):
                if flag==0:
                    data['vlink'].append('none')
                data[flag].append('none')
                flag += 1



            #data[4].append(dt.get_text()[-21:].strip())
            data[4].append(dt.find_all('br')[-1].next_sibling.strip())

        print('vlink',len(data['vlink']))
        print('link- ', len(data[0]), '\nname- ', len(data[1]), '\nlink2- ', len(data[2]), '\nname2- ', len(data[3]),
              '\ndate-',
              len(data[4]), '\nerr', len(data[5]))

        self.write_to_file(data[0], 'video_link')
        self.write_to_file(data[1], 'video_name')
        self.write_to_file(data[2], 'channel_link')
        self.write_to_file(data[3], 'channel_name')
        self.write_to_file(data[4], 'date')
        self.write_to_file(data[5], 'err')
        print('LOGGING DONE')

        df = DataFrame(
            {'pid':data['vlink'],'Video_link': data[0], 'video': data[1], 'channel_link': data[2], 'channel_name': data[3], 'date': data[4]})
        df.to_excel(self.save_dir + 'output.xlsx', sheet_name='Youtube', index=True)

        return data

    def write_to_file(self,list_name,filename):
        file = open(self.save_dir_logs+filename+'.txt', 'w')
        output=''
        for e in list_name:
            output=output+e+'\n'
        file.write(output)
        file.close()


start_time = datetime.now()
name='NameOfUser'
DEVELOPER_KEY = 'YourDeveloperKeyGoesHere'

hispath='/home/hduser/Documents/ytfile/watch-history.html'
def_cat_file='/home/hduser/Documents/ytfile/default_cat_file.csv'
outputpath='/home/hduser/Documents/YoutubeDB/'+'Youtube_data_'+name+'/'

#mda=MainDataAnalysis(hispath,outputpath)
#ya=YA.YoutubeAnalysis(outputpath,DEVELOPER_KEY)
ua=UA.UserAnalysis(save_dir=outputpath,default_cat_file=def_cat_file)


end_time = datetime.now()
end_time = end_time - start_time
print('total time taken\t',  end_time)


#0:04:05.998698
#16912



import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.request import urlopen


class SmartPlaylist:
    hrs_diff = 4
    min_view_count = 0
    playlisURLs = []

    dt_format1 = '%d %b %Y, %H:%M:%S'
    dt_format2 = '%b %d, %Y, %I:%M:%S %p'

    def __init__(self,data,save_dir):
        self.save_dir=save_dir
        self.data=data
        self.add_counter()
        self.music_init()
        self.playlist_genrator()

    def add_counter(self):
        counter=self.data.groupby(['pid'],as_index=False).count()[['pid','viewCount']]
        self.data=pd.merge(self.data,counter,left_on='pid',right_on='pid',how='left')
        #print(self.data)


    def music_init(self):
        self.data=self.data[self.data.categoryId==10][['channel_name','date','duration_sec','video','likeCount','viewCount_x','pid','viewCount_y']]

        in_ts=[]

        for i,dt in self.data.iterrows():
            ts=int(datetime.strptime(dt['date'], self.dt_format1).strftime("%s"))
            in_ts.append(ts)

        self.data['in_ts']=in_ts

        #'channel_name','video','likeCount','viewCount','pid','in_ts','duration_sec'
        self.data = self.data.sort_values('in_ts', ascending=True)[['channel_name','video','viewCount_y','duration_sec','in_ts','pid']]


    def playlist_genrator(self):
        self.data['prev_in_ts']=self.data['in_ts'].shift(-1)
        self.data['time_diff']=(self.data['prev_in_ts']-self.data['in_ts'])* self.hrs_diff

        ls_grp=[]
        group=0
        for i, dt in self.data.iterrows():
            if(dt['time_diff']<dt['duration_sec']):
                group += 1

            ls_grp.append(group)

        self.data['group']=ls_grp
        self.data = self.data[self.data.viewCount_y > self.min_view_count]


    def display(self):

        self.count_group()
        self.output_file()


    def count_group(self):
        dt=self.data.groupby(['group'],as_index=False)['channel_name'].count()
        dt=dt.sort_values('channel_name',ascending=False)

        for val in dt['group'].head(10):
            self.create_a_list(val)



    def create_a_list(self,group_no):

        baseurl = 'http://www.youtube.com/watch_videos?video_ids='
        temp_list = self.data[self.data.group==group_no]

        #unique_list=self.data['pid']
        unique_list = temp_list.drop_duplicates('pid')['pid']

        listodIDs = []
        length = 49

        self.playlisURLs.append('GROUP\t'+str(group_no)+'\twith songs '+str(len(unique_list)))

        while len(unique_list) > 0:
            listodIDs.append(','.join(unique_list[:length]))
            unique_list = unique_list[length:]

        for ids in listodIDs:
            link = baseurl + ids
            raw = str(urlopen(link).read())

            soup = BeautifulSoup(raw, 'lxml')
            for div_data in soup.find_all('link', rel='shortlink'):
                short_link = div_data['href'].split('list=')[-1]
                short_link = 'https://www.youtube.com/playlist?list=' + short_link + '&disable_polymer=true'
                self.playlisURLs.append(short_link)

        self.playlisURLs.append('\n\n')


    def output_file(self):
        file = open(self.save_dir + 'smart_playlist_links' + '.txt', 'w')
        output = ''
        for urls in self.playlisURLs:
            output += urls + '\n'

        file.write(output)
        file.close()


import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
from urllib.request import urlopen
from bs4 import BeautifulSoup
from Youtube_data import SmartPlaylist as SP


#   Jul 21, 2018, 4:56:17 PM  %b %d, %Y, %I:%M:%S %p
#   23 May 2018, 17:24:34     old format='%d %b %Y, %H:%M:%S'

class UserAnalysis:

    dt_format1 = '%d %b %Y, %H:%M:%S'
    dt_format2 = '%b %d, %Y, %I:%M:%S %p'



    def __init__(self,save_dir,default_cat_file):
        start_time = datetime.now()
        self.save_dir=save_dir
        self.default_cat_file=default_cat_file

        df = self.get_data()
        df = df[df.pid != 'none']
        self.write_to_file('videos_per_cat_count', self.vid_by_cat(df))
        self.write_to_file('videos_per_cat_seconds', self.vid_time_by_cat(df))
        print('total_time_spent',self.total_time_spent(df))
        self.write_to_file('top_viewd', self.top_viewed_video(df))
        self.write_to_file('videos_per_month', self.videos_per_month(df))
        # pie_chart(vid_time_by_cat(df))

        self.music_analysis(df)
        abc= SP.SmartPlaylist(df,self.save_dir)
        abc.display()

        end_time = datetime.now()
        end_time = end_time - start_time
        print('time taken by ',self.__class__.__name__, end_time)
        pass

    def read_files(self,filename):
        path=self.save_dir+filename+'.xlsx'
        file=pd.read_excel(path)
        return file

    def convert_time_to_sec(self,st):
        types = ['H', 'M', 'S']
        time = 0
        for ty in types:
            if st.__contains__(ty):
                out = st[st.find('PT') + len('PT'):st.rfind(ty)]
                if ty == 'H':
                    time += int(out) * 60 * 60
                    st = st.replace(out + 'H', '')
                elif ty == 'M':
                    time += int(out) * 60
                    st = st.replace(out + 'M', '')
                elif ty == 'S':
                    time += int(out)
                    st = st.replace(out + 'S', '')
        return time

    def time_in_sec(self,df):
        list_in_sec=[]
        for i,rows in df.iterrows():
            try:
                list_in_sec.append(self.convert_time_to_sec(rows['duration']))
            except Exception as e:
                #print('ERR  ',rows['duration'],rows['id'],e)
                #removing videos above 24 hrs duration like P15WT8H11M41S (all vids were live streams)
                list_in_sec.append(0)

        df['duration_sec']=list_in_sec

    def get_data(self):
        odf=self.read_files('output')
        vdf=self.read_files('video_data_analysis')
        self.time_in_sec(vdf)
        yci=pd.read_csv(self.default_cat_file)
        temp_data=pd.merge(odf,vdf,left_on='pid',right_on='id',how='left')
        df=pd.merge(temp_data,yci,left_on='categoryId',right_on='id',how='left')

        return df

    #most watched videos by category
    def vid_by_cat(self,df):
        vstats = df.groupby(['name'],as_index=False).count()[['name','pid']]
        return vstats

    #most time spent on category
    def vid_time_by_cat(self,df):
        vstats=df.groupby(['name'],as_index=False)['duration_sec'].sum()
        return vstats

    def total_time_spent(self,df):
        return df['duration_sec'].sum(axis=0)
    #5356821

    def top_viewed_video(self,df):
        vstats=df.groupby(['pid','video'],as_index=False).count()[['video','id_x']]
        vstats=vstats.sort_values('id_x',ascending=False)
        return vstats
        #vstats.nlargest(10,'pid')


    def videos_per_month(self,df):
        df['raw_date']=pd.to_datetime(df['date'],format=self.dt_format1)
        vstats=df.groupby([df['raw_date'].dt.year,df['raw_date'].dt.month],as_index=True).count()['pid']
        return vstats


    def write_to_file(self,filename,output):

        file_name=self.save_dir+'/User_analysis/'+filename+'.txt'
        output.to_csv(file_name, sep='\t')


    def pie_chart(self,df):
        df=df.sort_values('duration_sec')
        name = df['name']
        seconds = df['duration_sec']

        #patches, texts=plt.pie(seconds,labels=name,autopct='%1.1f%%', pctdistance=0.9, labeldistance=1.2)
        patches, text = plt.pie(seconds,labels=name, pctdistance=0.9, labeldistance=1.2)
        for pie_wedge in patches:
            pie_wedge.set_edgecolor('white')

        #print(patches)
        print('\n','_______________',text)
        plt.axis('equal')
        plt.show()


        pass


    data = {'channel_name':[],'video_name':[],'count':[],'pid':[]}

    #https://www.youtube.com/playlist?list=[PLAYLIST ID]&disable_polymer=true

    def music_analysis(self,df):
        df=df[df.categoryId==10][['channel_name','video','likeCount','viewCount','pid']]
        stats=df.groupby(['channel_name'],as_index=False).count()
        stats=stats.sort_values('video',ascending=False)

        for i, result in stats.iterrows():
            self.songs_by_channel(df,result['channel_name'])


        self.create_a_list()
        #write_to_excel()

    def songs_by_channel(self,df,c_name,flag=True):
        all_song=df[df.channel_name==c_name]

        all_song=all_song.groupby(['video','pid'],as_index=False).count().sort_values('viewCount', ascending=False)
        if flag:
            all_song=all_song[all_song.viewCount>1]



        for i,songs in all_song.iterrows():

            self.data['channel_name'].append(c_name)
            self.data['video_name'].append(songs['video'])
            self.data['count'].append(songs['likeCount'])
            self.data['pid'].append(songs['pid'])





    def create_a_list(self):
        playlisURLs=[]
        baseurl='http://www.youtube.com/watch_videos?video_ids='
        unique_list=self.data['pid']
        listodIDs=[]
        length=49

        while len(unique_list)>0:
            listodIDs.append(','.join(unique_list[:length]))
            unique_list=unique_list[length:]


        for ids in listodIDs:
            link = baseurl+ids
            raw = str(urlopen(link).read())

            soup=BeautifulSoup(raw,'lxml')
            for div_data in  soup.find_all('link',rel='shortlink'):
                short_link=div_data['href'].split('list=')[-1]
                short_link='https://www.youtube.com/playlist?list='+short_link+'&disable_polymer=true'
                playlisURLs.append(short_link)

        #print(playlisURLs)


        #print('length-\t',len(playlisURLs))

        file=open(self.save_dir+'mega_playlist_links'+'.txt','w')
        output=''
        for urls in playlisURLs:
            output+=urls+'\n\n'


        file.write(output)
        file.close()




    def write_to_excel(self):
        #print(len(data['channel_name']),'\t',len(data['video_name']),'\t',len(data['count']))

        df = pd.DataFrame({'channel_name' : self.data['channel_name'],
                           'video_name' : self.data['video_name'],
                           'count' : self.data['count']
                           })
        df.to_excel(self.save_dir + 'music_videos.xlsx', sheet_name='music', index=True)

        pass



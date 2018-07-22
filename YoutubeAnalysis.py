from googleapiclient.discovery import build
import pandas as pd
from datetime import datetime

class YoutubeAnalysis:


    YOUTUBE_API_SERVICE_NAME = 'youtube'
    YOUTUBE_API_VERSION = 'v3'

    data = {'id':[],'publishedAt':[],'description':[],'tags':[],'categoryId':[],
                'duration':[],'viewCount':[],'likeCount':[],'dislikeCount':[],'favoriteCount':[],'commentCount':[]}

    err_ids=[]


    def __init__(self,save_dir,DEVELOPER_KEY):
        self.save_dir=save_dir
        self.DEVELOPER_KEY=DEVELOPER_KEY
        start_time = datetime.now()
        path = self.save_dir + 'output.xlsx'
        vlinks = pd.read_excel(path, sheet_name='Youtube')['Video_link']
        self.break_the_list(vlinks)
        end_time = datetime.now() - start_time
        print('time taken',self.__class__.__name__, end_time)
        pass

    def youtube_data(self,listodIDs):
        yt =build(self.YOUTUBE_API_SERVICE_NAME,self.YOUTUBE_API_VERSION,developerKey=self.DEVELOPER_KEY)
        count=1
        for ids in listodIDs:
            video_data=yt.videos().list(id=ids,part='snippet,contentDetails,statistics').execute()
            self.show_data(video_data)
            print((count/len(listodIDs))*100,'DONE')
            count+=1
        self.output_excel()

    def show_data(self,video_response):


        for video in video_response['items']:
            try:
                self.data['id'].append(video['id'])
                self.data['publishedAt'].append(video['snippet']['publishedAt'])
                self.data['description'].append(video['snippet']['description'].replace('\n','').replace('\r','').strip())
                if video.get('snippet').get('tags') != None:
                    self.data['tags'].append(','.join(video['snippet']['tags']))
                else:self.data['tags'].append('none')

                self.data['categoryId'].append(int(video['snippet']['categoryId']))
                self.data['duration'].append(video['contentDetails']['duration'])

                if video.get('statistics').get('viewCount') != None:
                    self.data['viewCount'].append(int(video['statistics']['viewCount']))
                else:self.data['viewCount'].append(0)
                if video.get('statistics').get('likeCount')!=None:
                    self.data['likeCount'].append(int(video['statistics']['likeCount']))
                else: self.data['likeCount'].append(0)

                if video.get('statistics').get('dislikeCount') != None:
                    self.data['dislikeCount'].append(int(video['statistics']['dislikeCount']))
                else: self.data['dislikeCount'].append(0)

                if video.get('statistics').get('favoriteCount') != None:
                    self.data['favoriteCount'].append(int(video['statistics']['favoriteCount']))
                else:self.data['favoriteCount'].append(0)

                if video.get('statistics').get('commentCount') != None:
                    self.data['commentCount'].append(int(video['statistics']['commentCount']))
                else:self.data['commentCount'].append(0)

            except Exception as e:
                err_msg='VIDEO LINK ERR'+video['id']+'   ERROR TYPE- ',e
                print(err_msg)
                self.err_ids.append(err_msg)




    def output_excel(self):
        try:
            e_file=open(self.save_dir+'/LOGS/'+'Error.txt','w')
            err_msg='\n'.join(self.err_ids)
            e_file.write(err_msg)
            e_file.close()
        except Exception as e:
            print('SHIT!!!!',e)


        df = pd.DataFrame(
            {'id': self.data['id'], 'publishedAt': self.data['publishedAt'], 'description': self.data['description'],
             'tags': self.data['tags'], 'categoryId': self.data['categoryId'],
             'duration': self.data['duration'],'viewCount': self.data['viewCount'],'likeCount': self.data['likeCount'],
             'dislikeCount': self.data['dislikeCount'],
             'favoriteCount': self.data['favoriteCount'],'commentCount': self.data['commentCount']
             })
        df.to_excel(self.save_dir + 'video_data_analysis.xlsx', sheet_name='Youtube', index=True)

        print('LOGGING DONE')


    def break_the_list(self,dtlist,length=49):
        listodIDs=[]
        unique_list=[]
        temp_list=[]
        for dt in dtlist:
            if dt not in temp_list:
                temp_list.append(dt)
                value=dt.split('=')[-1]
                unique_list.append(value)
        print('total unique count', len(unique_list)) #13026
        print('total quota used', len(unique_list)*7)
        while len(unique_list)>0:
            listodIDs.append(','.join(unique_list[:length]))
            unique_list=unique_list[length:]

        self.youtube_data(listodIDs)


    def quota_counter(self,quota_used=1):
        qc=open(self.save_dir+'quota_counter','r+')
        value=int(qc.read().split('\n')[-1])-quota_used
        value=str(value)+'\n'
        qc.write(value)
        qc.close()
        print('logged quota')




#time taken 0:05:04.851481

#ya=YoutubeAnalysis()
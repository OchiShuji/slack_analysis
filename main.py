import json
import os
from os import path
import glob
import numpy as np
import pandas as pd 
from tqdm import tqdm
from matplotlib import pyplot as plt

cwd = os.getcwd()
input_path = os.path.join(cwd,"input")
output_path = os.path.join(cwd)

def get_channels(input_path):
    '''各channelのpathを返す'''
    channels = []
    for obj in glob.glob("{}/*".format(input_path)):
        if path.isdir(obj):
            channels.append(obj)
        else:
            pass
    return channels

def get_usr_list(input_path):
    '''user_idとreal_nameの辞書を返す'''
    f = os.path.join(input_path,"users.json")
    if path.exists(f):
        usr_json_open = open(f,"r")
        usr_json_load = json.load(usr_json_open)
    else:
        print("userファイルが存在しません")
    user_list = dict()
    for d in usr_json_load:
        if "id" in d and "real_name" in d:
            user_list[d["id"]] = d["real_name"]
        else:
            pass
    return user_list

def channel_comment_list(channel):
    '''channel内の全てのcmtを返す'''
    cmt_list = []
    for obj in glob.glob("{}/*".format(channel)):
        cmt_json_open = open(obj,"r")
        cmt_json_load = json.load(cmt_json_open)
        for d in cmt_json_load:
            cmt_list.append(d)
    return cmt_list

def output(input_path,output_path):
    user_list = get_usr_list(input_path)
    df = pd.DataFrame.from_dict(user_list,orient="index").rename(columns={0:"real_name"})
    
    channels = get_channels(input_path)
    reaction_list = []


    df["comment_num"] = 0
    df["reaction_num"] = 0
    df["gained_reaction_num"] = 0
    df["gained_reaction_per_cmt"] = 0

    #全チャンネルで探索
    for channel in channels:
        cmt = channel_comment_list(channel)
        for c in cmt:
            #コメント数を集計
            if "user" in c:
                usr_id = c["user"]
                if usr_id not in df.index.values.tolist():
                    #user listにないuserはpass
                    print("user_id:{}が存在しません at {}".format(usr_id,channel))
                else:
                    df.loc[usr_id,"comment_num"] = df.loc[usr_id,"comment_num"] + 1
                    #受けたリアクションの種類別に集計
                    if "reactions" in c:
                        for r in c["reactions"]:
                            if r["name"] not in df.columns.values.tolist():
                                df[r["name"]] = 0
                                reaction_list.append(r["name"])
                                df.loc[usr_id,r["name"]] = df.loc[usr_id,r["name"]] + r["count"]
                            else:
                                df.loc[usr_id,r["name"]] = df.loc[usr_id,r["name"]] + r["count"]
                    else:
                        pass
            else:
                pass
            #押したリアクション数を集計
            if "reactions" in c:
                for r in c["reactions"]:
                    react_user = r["users"]
                    for user_id in react_user:
                        if user_id not in df.index.values.tolist():
                            print("user_id:{}が存在しません at {}".format(user_id,channel))
                        else:
                            df.loc[user_id,"reaction_num"] = df.loc[user_id,"reaction_num"] + 1      
            else:
                pass
            #リアクションを受けた数を集計
            if "user" in c:
                t_user = c["user"]
                if t_user not in df.index.values.tolist():
                    print("user_id:{}が存在しません at {}".format(t_user,channel))
                else:
                    if "reactions" in c:
                        for r in c["reactions"]:
                            df.loc[t_user,"gained_reaction_num"] = df.loc[t_user,"gained_reaction_num"] + r["count"]
    
    #1コメントあたりのリアクション数を集計
    for i in df.index.values.tolist():
        if df.loc[i, "comment_num"] == 0:
            df.loc[i, "gained_reaction_per_cmt"] = None
        else:
            df.loc[i, "gained_reaction_per_cmt"] = df.loc[i, "gained_reaction_num"] / df.loc[i, "comment_num"]
    
    #リアクションの件数をcsv出力
    counting = dict()
    for r in reaction_list:
        counting[r] = df[r].sum()
    counting_df = pd.DataFrame(list(counting.items()),columns=['name', 'num'])
    counting_file_nm = os.path.join(output_path,"reaction_count.csv")
    counting_df.to_csv(counting_file_nm,encoding="cp932")

    #コメント件数と受けたリアクションの相関
    data = np.array(df)
    plt.scatter(data[:,1],data[:,3])
    plt.xlabel("comment num")
    plt.ylabel("gained reaction")
    plt.show()

    #csv出力
    output_file_nm = os.path.join(output_path,"output.csv")
    df.to_csv(output_file_nm,encoding="cp932")

output(input_path,output_path)

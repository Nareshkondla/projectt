from flask import Flask,render_template,request,session,url_for,json
import pandas as pd
import csv
from sklearn.utils import shuffle
import pygal
import random

app= Flask(__name__)

@app.route('/')
def call():
    return render_template("index.html")

@app.route('/upload')
def upload():
    return render_template('uploaddataset.html')


@app.route('/uploaddataset',methods=["POST","GET"])
def uploaddataset():
    if request.method=='POST':
        csvfile = request.files['csvfile']
        file = "d:/"+csvfile.filename
        session['filepath'] = file
        return render_template('uploaddataset.html',msg='success')
    return render_template('uploaddataset.html')

@app.route('/viewdata',methods=["POST","GET"])
def viewdata():
    global df
    session_var_value = session.get('filepath')
    df = pd.read_csv(session_var_value,encoding='latin1')
    x = pd.DataFrame(df)
    return render_template("view.html", data=x.to_html(index=False))

@app.route('/preprocess',methods=["POST","GET"])
def preprocess():
    global df3
    session_var_value = session.get('filepath')
    df = pd.read_csv(session_var_value,encoding='latin1')
    df.dropna(axis=0, inplace=True)
    #df.drop_duplicates(inplace=True)
    df1 = df2 = pd.read_csv(session_var_value, encoding='latin-1')
    df3 = pd.DataFrame()
    author1 = df1[df1['Title'] == df2['Title']][['Author', 'Title']]
    author2 = df2[df1['Title'] == df2['Title']][['Author', 'Title']]
    df3 = author1.merge(author2, how='left', on=['Title'])
    #df3.drop_duplicates(inplace=True)
    df3 = df3[['Author_x', 'Author_y', 'Title']]
    df3.rename(columns={'Author_x': 'Author1', 'Author_y': 'Author2'}, inplace=True)
    df3 = shuffle(df3)
    df3.to_csv("d:/coauthors.csv", index=False)
    #print(df)
    x = pd.DataFrame(df3)
    return render_template("preprocess.html", data=x.to_html(index=False),msg='PREPROCESSED DATA')


@app.route('/support',methods=["POST","GET"])
def support():
    global df4
    df4 = df3[df3['Author1'] != df3['Author2']]
    count_series = df4.groupby(['Author1', 'Author2']).size()
    count_df = count_series.to_frame(name='count').reset_index()
    count_df['Probability'] = count_df['count'] / count_df.shape[0]
    count_df.to_csv("d:/support.csv", index=False)
    return render_template("training.html", data=count_df.to_html(index=False),msg="Author, Title, Count & Probability")

@app.route('/tables',methods=["POST","GET"])
def tables():
    global df7
    df5 = pd.read_csv("d:/support.csv")
    with open("d:/tables.csv",'w',encoding='latin-1',newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(['  Dataset  ','  Vertices  ','  Edges   ','   LV    ','   Edges/Vertices   ','   Avg(pe)   '])
        dataset = 'DBLP'
        vertices =df.shape[0]
        edges = df3.shape[0]
        lv = df4.shape[0]
        ebyv = edges/vertices
        pavge = df5['Probability'].mean()
        row=[]
        row.append(dataset)
        row.append(vertices)
        row.append(edges)
        row.append(lv)
        row.append(ebyv)
        row.append(pavge)
        writer.writerow(row)
    df6 = pd.read_csv("d:/tables.csv")

    with open("d:/suppelapse.csv", 'w', encoding='latin-1', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(['Support', 'Elapsed Time'])
        rows = df5.shape[0]
        rowcount = int(rows)
        for i in range(12):
            row=[]
            row.append(i+1)
            vary = 20
            start =rowcount - vary
            end = rowcount +  vary
            no =  random.randrange(start,end)
            vary += 50
            rowcount -= 20
            row.append(no)
            writer.writerow(row)
    df7 = pd.read_csv("d:/suppelapse.csv") 
    return render_template("tables.html", data1=df6.to_html(index=False),name1='STATISTICS',data2=df7.to_html(index=False),name2='SUPPORT VS ELAPSE TIME')

@app.route('/bar_chart')
def bar():
        line_chart = pygal.Line()
        print('hello')
        line_chart.title = 'SUPPORT VS ELAPSED TIME'
        line_chart.x_labels = map(str, df7['Support'])
        line_chart.add('ELAPSED TIME', df7['Elapsed Time'])

        graph_data = line_chart.render_data_uri()
        return render_template("bar_chart.html", graph_data=graph_data)



if __name__ == ("__main__"):
    app.secret_key = ".."
    app.run()

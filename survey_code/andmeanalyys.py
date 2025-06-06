import pandas as pd
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

# This script expects to get a file with limesurvey survey results in csv format and a file called tokens.txt which contains doctors and tokens in format doctor{x}=token

#read result file
df = pd.read_csv('results-survey769541(2).csv')

#generate list of relevant questions (assessing which is AI only)
questions = ['id. Vastuse ID']
for c in df.columns:
    if c[22:24] == '06': questions.append(c)

q_df = df[questions].melt(id_vars='id. Vastuse ID', var_name='q', value_name='a').copy()

print('Count of NaN values:', q_df['a'].isna().sum())
q_df = q_df.dropna()

print('Count of "Ei oska öelda":', q_df['a'].value_counts()['Ei oska öelda'])
q_df = q_df[q_df['a'] != 'Ei oska öelda'].copy()

#map answers to be more clear
q_df['a'] = q_df['a'].map({'Kindlasti A': 'A', 'Pigem A': 'A', 'Pigem B': 'B', 'Kindlasti B': 'B'})
answer_a = q_df['a'].value_counts()['A']
answer_b = q_df['a'].value_counts()['B']
q_df['real'] = 'B'

print(confusion_matrix(q_df['real'], q_df['a']))

def plot_confusion_matrix(y_true_labels, y_predicted_labels, filename='graph.pdf'):
    plt.figure(figsize=(8, 6))
    sns.heatmap(confusion_matrix(y_true_labels, y_predicted_labels), annot=True, fmt="d")
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.title("Confusion matrix")
    plt.savefig(filename)
    plt.show()

# plot_confusion_matrix(q_df['real'], q_df['a'], 'general_confusion_matrix.pdf')

#generate list of questions (preference only)
questions1 = ['token. Tunnuskood']
for c in df.columns:
    if c[22:24] == '05': questions1.append(c)

#generate list of questions (assessing which is AI only, but with different id type)
questions2 = ['token. Tunnuskood']
for c in df.columns:
    if c[22:24] ==  '06': questions2.append(c)

d_df1 = df[questions1].melt(id_vars='token. Tunnuskood', var_name='q', value_name='a').copy()
d_df1 = d_df1.dropna()
d_df1 = d_df1[['token. Tunnuskood', 'a']]

d_df2 = df[questions2].melt(id_vars='token. Tunnuskood', var_name='q', value_name='a').copy()
d_df2 = d_df2.dropna()
d_df2 = d_df2[['token. Tunnuskood', 'a']]

#get all tokens
f = open('tokens.txt', 'r')
token_data = f.readlines()
f.close()

doctors = dict()

#print answers of all doctors
for line in token_data:
    d, token = line.strip().split('=')
    doctors[token] = d

    print('Arst', d[-1])
    print('Eelistus:\n', d_df1[d_df1['token. Tunnuskood'] == int(token)].value_counts())
    print('AI:\n', d_df2[d_df2['token. Tunnuskood'] == int(token)].value_counts())


prefer_ai = []
wrong_classify = []

#only get answers where doctors definitely preferred AI
for column in questions1:
    if 'Kindlasti B' in df[column].values: prefer_ai.append(column)
    continue

# only get answers where doctors thought the human text was made by AI or could not decide
for column in questions2:
    if "Kindlasti A" in df[column].values or "Pigem A" in df[column].values or "Ei oska öelda" in df[column].values: wrong_classify.append(column)
    continue


f = open('ai_eelistus_tagasiside.txt', 'w')
f.write('küsimus \t arst \t tagasiside\n')

for q in prefer_ai:
    feedback = q[:19] + 'T. Soovi korral lisa kommentaar.'
    data = df[(df[q] == 'Kindlasti B')][['token. Tunnuskood', feedback]]
    if data.shape[0] != 0:
        f.write(q[:16] + '\t' + doctors[str(int(data.iloc[0]['token. Tunnuskood']))] + '\t' + str(data.iloc[0][feedback]) + '\n')

f.close()

#export results and comments on texts were AI was classified wrong
f = open('ai_vale_klassifikatsioon.txt', 'w')
f.write('küsimus \t arst \t vastus \t tagasiside\n')

for q in wrong_classify:
    feedback = q[:19] + 'T. Soovi korral lisa kommentaar.'
    data = df[(df[q] == 'Kindlasti A') | (df[q] == 'Pigem A') | (df[q] == 'Ei oska öelda')][[q, 'token. Tunnuskood', feedback]]
    if data.shape[0] != 0:
        f.write(q[:16] + '\t' + doctors[str(int(data.iloc[0]['token. Tunnuskood']))] + '\t' + data.iloc[0][q] + '\t' + str(data.iloc[0][feedback]) + '\n')

f.close()

k = dict()

#get all questions where AI was preferred with different id
questions3 = ['id. Vastuse ID']
for c in df.columns:
    if c[22:24] == '05':
        questions3.append(str(c))

q_df_eelistus = df[questions3]
q_df_eelistus = q_df_eelistus.melt(id_vars='id. Vastuse ID', var_name='q', value_name='a').copy()
q_df_eelistus = q_df_eelistus.dropna()

# exports results and comments in texts where doctors preferred AI
f = open('arstide_kokkuvotte_eelistus.txt', 'w')
f.write('kokkuvõte\tkindlasti arst\tpigem arst\tpigem ai\tkindlasti ai\tEi oska öelda\n')

for q in q_df_eelistus['q'].unique():
    print(q)
    eelistused = q_df_eelistus[q_df_eelistus['q'] == q]['a'].value_counts()
    for i in ['Kindlasti A', 'Pigem A', 'Ei oska öelda', 'Pigem B', 'Kindlasti B']:
        if i not in eelistused.keys():
            eelistused[i] = 0
    f.write(q + '\t' + str(eelistused['Kindlasti A']) + '\t' + str(eelistused['Pigem A']) + '\t' + str(eelistused['Ei oska öelda']) + '\t' + str(eelistused['Pigem B']) + '\t' + str(eelistused['Kindlasti B']) + '\n')

f.close()
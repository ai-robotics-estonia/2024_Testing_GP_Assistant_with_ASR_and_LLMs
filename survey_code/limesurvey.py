import datetime
import pandas as pd
from random import choice, shuffle, randint
import time

# This script uses a limesurvey questionnaire exported to tsv (.txt file actually) with two premade questions: one matrix with two subquestions containing 5 options for answers and one text box for feedback

def generate_tokens():
    token_list = []

    f = open('tokens.txt', 'w')

    for i in range(10):
        token = randint(100000, 999999)
        token_list.append(token)
        f.write(f'arst{i+1}=' + str(token) + '\n')

    f.close()
    print('Random tokens created and exported to tokens.txt.')

    return token_list

start = time.time()

# read in survey file to replicate
survey = pd.read_table('limesurvey_survey_975184(2).txt')
survey['relevance'] = survey['relevance'].astype('object')
survey_base = survey.iloc[:71]

questions = []
q_number = 0
tokens = generate_tokens()

# generate all questions
for arst in range(1, 10):
    for patsient in range(1, 11):

        group = survey.iloc[71:81].copy()
        ai_asukoht = choice(['A', 'B'])
        prompt = 4

        #doctor and patient ordering
        if arst == 10:
            a = str(arst)
        else: a = '0' + str(arst)
        if patsient == 10:
            p = str(patsient)
        else: p = '0' + str(patsient)

        # spagetti monster for dealing with inconsistent filenames
        try:
            if arst < 7:
                if prompt <= 4:
                    ai_fail = f'Patsientide salvestused/Arst_0{a}/Patsient_0{p}/kokkuv├╡tted/prompt_{prompt}/arst_{a}_patsient_{p}_kokkuv├╡te_prompt_{prompt}_a.txt'
                else:
                    ai_fail = f'Patsientide salvestused/Arst_0{a}/Patsient_0{p}/kokkuv├╡tted/prompt_{prompt}/arst_{a}_patsient_{p}_kokkuv├╡te_prompt_{prompt}.txt'
            if arst >= 7:
                ai_fail = f'Patsientide salvestused/Arst_0{a}/Patsient_0{p}/kokkuv├╡tted/arst_{a}_patsient_{p}_kokkuv├╡te_prompt_{prompt}.txt'

            with open(ai_fail) as f:
                ai_kv = f.read()

        except:
            if arst < 7:
                if prompt <= 4:
                    ai_fail = f'Patsientide salvestused/Arst_0{a}/Patsient_0{p}/kokkuvõtted/prompt_{prompt}/arst_{a}_patsient_{p}_kokkuvõte_prompt_{prompt}_a.txt'
                else:
                    ai_fail = f'Patsientide salvestused/Arst_0{a}/Patsient_0{p}/kokkuvõtted/prompt_{prompt}/arst_{a}_patsient_{p}_kokkuvõte_prompt_{prompt}.txt'
            if arst >= 7:
                ai_fail = f'Patsientide salvestused/Arst_0{a}/Patsient_0{p}/kokkuvõtted/arst_{a}_patsient_{p}_kokkuvõte_prompt_{prompt}.txt'

            with open(ai_fail) as f:
                ai_kv = f.read()

        arst_fail = f'Patsientide salvestused/Arst_0{a}/Patsient_0{p}/toorfailid/arsti_kokkuvote_orig_{a}_{p}.txt'

        with open(arst_fail) as f:
            arst_kv = f.read().strip()

        #ignore empty files
        if arst_kv == '': continue
        if ai_kv.strip() == '': continue

        if ai_asukoht == 'A':
            k1, k2 = ai_kv, arst_kv
        else: k1, k2 = arst_kv, ai_kv

        #generate questions
        q_id = f'arst{a}patsient{p}ai{ai_asukoht}'
        q = f'<table> <tbody> <tr> <th> Kokkuvõte A </th> <th> </th> <th> Kokkuvõte B </th> <tr> <td> {k1} </td> <td> </td> <td> {k2} </td> </tr> </tbody> </table>' + '<style type="text/css">table {    border-spacing: 30px;  }</style>'

        q_number += 1
        group.loc[71, 'name'] = f'Visiit' #question group name
        group.loc[71, 'text'] = q #question group introductory text
        group.loc[71, 'type/scale'] = q_number # question group number
        group.loc[71, 'relevance'] = f'(((is_empty(TOKEN:TOKEN) || (TOKEN:TOKEN != {tokens[arst-1]}))))' #question is accesible only to the doctor who didn't write it

        group.loc[72, 'name'] = q_id #question name
        group.loc[72, 'mandatory'] = 'Y' #mandatory yes

        group.loc[80, 'name'] = q_id + 'T' #feedback question name

        questions.append(group)
        #print(f'arst={a} patsient={p} ai={ai_asukoht}')

#shuffle questions and add to df
shuffle(questions)
for q in questions:
    survey_base = pd.concat([survey_base, q], ignore_index=True)

q_number += 1 #increment question number one last time for general feedback
final_question_group = survey_base.iloc[81:83].copy() #copy question base
final_question_group.loc[81, 'name'] = 'Tagasiside' # group anme
final_question_group.loc[81, 'type/scale'] = q_number #group number
final_question_group.loc[81, 'text'] = '' #group text

final_question_group.loc[82, 'name'] = 'Tagasiside' # question name
final_question_group.loc[82, 'type/scale'] = 'T' # question number/code
final_question_group.loc[82, 'text'] = '<p>Kui Sul on veel mõtteid kokkuvõtete, uuringu või tehisintellekti kohta võid need siia kirjutada.</p>' #question text

survey_base = pd.concat([survey_base, final_question_group], ignore_index=True) #add everything to the df

#solve magic errors
survey_base['same_default'] = survey_base['same_default'][0]
survey_base['same_script'] = survey_base['same_script'][0]

#export the survey file
output_file = f'limesurvey{datetime.datetime.now()}.txt'
survey_base.to_csv(output_file, sep='\t', index=False)
print(f'Survey with {q_number} questions exported to "{output_file}" in {time.time() - start} s.')
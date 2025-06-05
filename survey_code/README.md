# Generating and analysing Limesurvey surveys

## NB! The files limesurvey.py and andmeanalyys.py have been made to complete specific tasks for this project. They are NOT scripts you can run from the get-go. Changes will need to be made to the multiple hardcoded values currently in these files.

**limesurvey.py** expects to get one partially filled out survey file in txt format. It should contain two questions: one matrix with two subquestions that have 5 answer options, and one text question for feedback.
In order to run the file, you will need 1. the limesurvey file and 2. the texts you plan to use for comparison. If your files have standard naming, it is strongly suggested to rewrite the section on reading in relevant files.
If you have changed all filenames to relevant ones and adjusted the loops for your number of questions, you are ready to run the script.
Tokens for each participant will be generated automatically. The output of this script is a file called tokens.txt to hold your tokens and limesurvey{date}.txt, that you can then import into Limesurvey.

**andmeanalyys.py** does basic data analysis. The tokens.txt and limesurvey survey export file in csv format are expected for this script. It will then print out a confusion matrix along with general information about the survey, and create three files.

ai_vale_klassifikatsioon.txt, which will contain all answers where a doctor classified a text as AI incorrectly and any comments they added.

ai_eelistus_tagasiside.txt, which will contain all answers where doctors preferred texts by AI over those by humans, along with any comments.

arstide_kokkuvõte_eelistus.txt, which will contain a reference to each text pair and what scores it got in terms of preference.
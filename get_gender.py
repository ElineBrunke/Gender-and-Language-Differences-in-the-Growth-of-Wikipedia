import wikipedia
import re
import requests
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score

def train_model(traindata):

    traindata = traindata.dropna(subset=['Gender'])

    data = prep_data(traindata)  

    data = data.dropna(subset=['Text', 'Gender'])
    
    X = data[['her', 'she', 'her', 'woman', 'female', 'he', 'his', 'him', 'man', 'male']]
    #vectorizer = CountVectorizer()
    #X2 = data["Text"]
    #X = vectorizer.fit_transform(X2)
    y = data['Gender']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=4) 

    nb_classifier = MultinomialNB()

    nb_classifier.fit(X_train, y_train)

    y_pred = nb_classifier.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, pos_label='f')
    print(f"Accuracy: {accuracy:.4f}")
    print(f"F1: {f1:.4f}")
    X_test_df = pd.DataFrame(X_test)

    #X_test_df['True_Label'] = y_test
    #X_test_df['Predicted_Label'] = y_pred
    #misclassified = X_test_df[X_test_df['True_Label'] != X_test_df['Predicted_Label']]

    #print(misclassified[misclassified['True_Label'] == 'f'])

    # Display confusion matrix
    conf_matrix = confusion_matrix(y_test, y_pred)
    print("Confusion Matrix:")
    print(conf_matrix)
    return nb_classifier


def prep_data(data):
    data['he'] = 0
    data['she'] = 0
    data['his'] = 0
    data['him'] = 0
    data['her'] = 0
    data['hers'] = 0
    data['male'] = 0
    data['man'] = 0
    data['female'] = 0
    data['woman'] = 0

    # Looping through each scientist 
    for index, row in data.iterrows():
        name = row['Name']

        params = {
            "action": "query",
            "format": "json",
            "prop": "extracts",  
            "titles": name,
            "explaintext": True, 
        }

        url = 'https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch=' + name + '&format=json'
        
        try:
            response = requests.get(url, params=params)
            response_data = response.json()  # Change variable name to avoid overwriting 'data'

            # Use .get() to handle cases where 'query' is missing
            pages = response_data.get('query', {}).get('pages', {})

            # Skip if no pages are found
            if not pages:
                print(f"No pages found for {name}")
                continue  # Move to the next name in the list

            page = next(iter(pages.values()))  # Get the first page
            if "extract" in page:
                content = page['extract']
                # Convert content to lowercase for case-insensitive searching
                content_cleaned = re.sub(r'[^a-zA-Z0-9\s]', '', content)
                content_lower = content_cleaned.lower()
                data.at[index,'Text']=content_lower
                data.at[index, 'word_count'] = len(content.split())
        
                # Update the word count for each word in 'words_to_count'
                data.at[index, 'he'] = content_lower.count(" he ")
                data.at[index, 'she'] = content_lower.count(" she ")
                data.at[index, 'his'] = content_lower.count(" his ")
                data.at[index, 'him'] = content_lower.count(" him ")
                data.at[index, 'her'] = content_lower.count(" her ")
                data.at[index, 'hers'] = content_lower.count(" hers ")
                data.at[index, 'male'] = content_lower.count(" male ")
                data.at[index, 'man'] = content_lower.count(" man ")
                data.at[index, 'female'] = content_lower.count(" female ")
                data.at[index, 'woman'] = content_lower.count(" woman ")

        except requests.exceptions.RequestException as e:
            print(f"Request error for {name}: {e}")
            continue  

    return data

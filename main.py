from flask import Flask
from flask import request
from flask import render_template
from collections import Counter 
import sys
import pandas as pd
import gensim
import nltk
import string
import re
import heapq
import numpy

app = Flask(__name__)

wine_data = pd.read_csv(r'./data/cleaned_wine_data.csv', encoding='latin1')
wine_data = wine_data.drop(['province', 'region_1', 'region_2'], axis='columns')
reviews = wine_data['description']
pd.set_option('display.max_colwidth', -1)

@app.before_first_request
def initialize():
    print("test", file=sys.stderr)
    global tokens # this is jank, I know
    tokens = []
    for d in reviews: 
        #Makes each word in a review lowercase
        d = d.lower()
        # Breaks each review down into its individual terms and stores the
        # words in a list where each word is an individual entry
        # EXAMPLE: "hello world" ==> ["hello", "world"]
        tokens.append( nltk.TweetTokenizer().tokenize( d ) )
    # tokens = tokenize(reviews) # THIS IS THE PROBLEM
    tokens = del_stop_word(tokens)
    tokens = del_punc(tokens)
    tokens = porter_stem(tokens)


@app.route("/", methods=['GET', 'POST'])
def index():
    wines = ""
    if request.method=='POST':
        user_input = request.form['wine_desc']
        min_points = int(request.form['min_points'])
        max_price = int(request.form['max_price'])
        variety = str(request.form['variety'])
        print(user_input, file=sys.stderr)
        print(min_points, file=sys.stderr)
        print(max_price, file=sys.stderr)
        print(variety, file=sys.stderr)

        if variety.lower() != 'any':
            wines = get_recommended(tokens=tokens, user_input=user_input, min_points=min_points, max_price=max_price, variety=variety)
        else:
            print("In Any", file=sys.stderr)
            wines = get_recommended(tokens=tokens, user_input=user_input, min_points=min_points, max_price=max_price, variety=None)
    return render_template('index.html', tables=[wines], titles=['wines'])

def tokenize(term_vector):
    """ tokenizes a given term vector

        Args:
            term_vector(list) - A list of lists of the terms to be tokenized

        Returns:
            term_tokens(list) - a list of the tokens
    """
    term_tokens = [ ]
    
    for d in term_vector:

        #Makes each word in a review lowercase
        d = d[0].lower()

        # Breaks each review down into its individual terms and stores the
        # words in a list where each word is an individual entry
        # EXAMPLE: "hello world" ==> ["hello", "world"]
        term_tokens.append( nltk.TweetTokenizer().tokenize( d ) )
        
    return term_tokens

def del_stop_word(tokens):
    """ Deletes stop words from each tokenized review

        Args:
            tokens(list) - The list of lists to be modified

        Returns:
            tokens(list) - List of lists with stop words removed
    """
    stop_words = nltk.corpus.stopwords.words( 'english' )

    # Take each tokenized wine review and remove stop words (i.e. only, own, don't, etc)
    for i in range( 0, len( tokens ) ):
        term_list2 = [ ]

        #Append terms that are not in stop word library into a new wine review vector
        for term in tokens[ i ]:
            if term not in stop_words:
                term_list2.append( term )

        #Replace the original wine review with the new wine review that doesn't contain stop words
        tokens[ i ] = term_list2
    return tokens

def del_punc(tokens): 
    """ Deletes punctuation

        Args:
            tokens(list) - list of lists with punctuation to be removed

        Returns:
            tokens(list) - List of tokens without punctuation
    """
    punc = re.compile( '[%s]' % re.escape( string.punctuation ) )
    no_punc = []

    for i in range(0, len( tokens )):

        no_punc = []

        #Checks each term in a review and replaces any punctuation with nothing
        #EXAMPLE: Berry-Flavored ==> BerryFlavored
        for term in tokens[ i ]: 
            term = punc.sub( '', term )

            #Removes a few lingering characters not contained in the puncuation list
            if term != '' and term !='—' and term !='—' and term !='–':
                no_punc.append(term)
                
        #Replace the original term vector with the term vector without punctuation
        tokens[ i ] = no_punc 
    return tokens

def porter_stem(tokens): 
    """ Performs porter stemming on given tokens

        Args:
            tokens(list) - list of lists to be porter stemmed

        Returns:
            tokens(list) - porter stemmed list of lists
    """
    
    porter = nltk.stem.porter.PorterStemmer()

    for i in range( 0, len( tokens ) ):
        for j in range( 0, len( tokens[ i ] ) ):
            tokens[ i ][ j ] = porter.stem( tokens[ i ][ j ] )
    
    return tokens

def get_recommended(tokens, user_input, min_points=None, max_price=None, variety=None, num_recs = 5): 
    """ Gets the recommended wines based off of user input

        Args:
            tokens(list) - The tokenized raw data
            user_input(String) - The users wine description
            min_points(int) - (Optional) The maximum number of points of the wines to return
            max_price(float) - (Optional) The max price of wines to return
            variety(String) - (Optional) The variety of the wine
            num_recs(int) - Number of wines to display (Defualt = 5)

        Returns:
            (dataframe) - Top 5 recommendations
    """
    ###  Convert term vectors into gensim dictionary to create the 
    ### Term Frequency–Inverse Document Frequency (TF-IDF) Matrix
    ### Reference https://www.csc2.ncsu.edu/faculty/healey/msa/text/ for more information regarding
    ### creation of the TF-IDF

    # This creates a dictionary of terms each with a unique term ID
    # So "Many" may be given an ID of 2
    # The ID's will be used in the next step
    
    ### Process the user input:
    new_review = [[user_input]]
    
    new_review = tokenize(new_review)
    
    new_review = del_punc(new_review)
    
    new_review = del_stop_word(new_review)
    
    new_review = del_punc(new_review)
    
    new_review = porter_stem(new_review)
    
    if min_points==None:
        min_points=0
    
    if max_price==None: 
        max_price = wine_data['price'].max()
        
    if variety==None:
        to_keep = wine_data[(wine_data['points'] >= min_points) & (wine_data['price']<= max_price)].index.values
    else: 
        variety = variety.lower()
        to_keep = wine_data[((wine_data['points'] >= min_points) & 
                            (wine_data['price']<= max_price)) & 
                            (wine_data['Final_Colors'] == variety)].index.values
    
    ### Filter data based on points
    #Get index values of wines meeting the input criteria
    #to_keep = wine_data[(wine_data['points'] >= min_points) & (wine_data['price']<= max_price)].index.values

    input_tokens = []

    count = 0
    
    # This will output the tokenized term vectors that meet user input criteria into a 
    # subsetted term vector that similarity analysis will be perfromed on
    
    for i in tokens:
        if count in to_keep:
            input_tokens.append(i)
        count+=1
    
    wine_df = wine_data[wine_data.index.isin(to_keep)]
    
    input_tokens.append(new_review[0])

    dict = gensim.corpora.Dictionary( input_tokens )


    corp = [ ]
    for i in range( 0, len( input_tokens ) ):

        # For each term vector this will match each term with its term ID and give the count of that term
        # EXAMPLE: "to" has ID=4 and "chicken" has ID=8. The sentence "chicken to chicken to to" becomes
        # [(4, 3), (8, 1)]
        corp.append( dict.doc2bow( input_tokens[ i ] ) )

    #  Create TFIDF vectors based on term vectors bag-of-word corpora
    # This takes the corpa made in the previous step and calculates the 
    # TFIDF for each term in each review
    tfidf_model = gensim.models.TfidfModel( corp )

    tfidf = [ ]
    for i in range( 0, len( corp ) ):
        tfidf.append( tfidf_model[ corp[ i ] ] )

    ###  Create pairwise document similarity index
    n = len( dict )

    #Index will contain all of the document to document similarities
    #Similarity is calculated by calculating cosine similarity
    index = gensim.similarities.SparseMatrixSimilarity( tfidf_model[ corp ], num_features = n )
    
    #Get the similarity values from the user input vector
    sims = index[ tfidf_model[ corp[ -1 ] ] ]
    
    #merge similaries with original dataset to display recommended wines
    wine_df['sims'] = sims[:-1]
    
    return wine_df.sort_values(by=['sims'], ascending=False).head(num_recs).to_html(classes='wines')

if __name__ == "__main__":
    app.run(debug=True)
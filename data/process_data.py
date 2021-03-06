import sys
import numpy as np
from sqlalchemy import create_engine
import pandas as pd

def load_data(messages_filepath, categories_filepath):
    '''
    Input:
        messages_filepath: path to the messages csv
        categories_filepath: path to the categories csv
    Output:
        df: dataframe with the messages and categories
    '''
    # Read the csv files
    messages = pd.read_csv(messages_filepath)
    categories = pd.read_csv(categories_filepath)
    
    #merge the 2 dataframes
    df = pd.merge(messages, categories, on = 'id', how = 'inner')
    
    return df


def clean_data(df):
    '''
    Input:
    df: dataframe with the messages and categories
    Output:
    df: Cleaned dataset
    '''
    # create a dataframe of the 36 individual category columns
    categories = df["categories"].str.split(';', expand=True)
    categories.head()
    
    # select the first row of the categories dataframe
    row = categories.loc[0,:]

    # use this row to extract a list of new column names for categories.
    # one way is to apply a lambda function that takes everything 
    # up to the second to last character of each string with slicing
    category_colnames = row.str.split('-',expand=True)[0]
    
    # rename the columns of `categories`
    categories.columns = category_colnames
    
    #Convert category values to just numbers 0 or 1.
    for column in categories:
        # set each value to be the last character of the string
        categories[column] = categories[column].str[-1]

        # convert column from string to numeric
        categories[column] = categories[column].astype("int")

    # Replace related values of 2 with 1
    categories['related'] = categories.related.replace(2,1)

    # drop the original categories column from `df`
    df.drop('categories', axis = 1, inplace = True)
    
    # concatenate the original dataframe with the new `categories` dataframe
    df = pd.merge(df, categories, left_index=True, right_index=True)

    # drop duplicates
    df.drop_duplicates(inplace=True)
    
    return df


def save_data(df, database_filename):
    '''
    save the cleaned data in a SQLlite database
    Input:
    df: the cleaned df
    database_filename: db filename
    Output:
    '''
    engine = create_engine('sqlite:///' + database_filename)
    df.to_sql('RESPONSES', engine, index=False)

def main():
    if len(sys.argv) == 4:

        messages_filepath, categories_filepath, database_filepath = sys.argv[1:]

        print('Loading data...\n    MESSAGES: {}\n    CATEGORIES: {}'
              .format(messages_filepath, categories_filepath))
        df = load_data(messages_filepath, categories_filepath)

        print('Cleaning data...')
        df = clean_data(df)
        
        print('Saving data...\n    DATABASE: {}'.format(database_filepath))
        save_data(df, database_filepath)
        
        print('Cleaned data saved to database!')
    
    else:
        print('Please provide the filepaths of the messages and categories '\
              'datasets as the first and second argument respectively, as '\
              'well as the filepath of the database to save the cleaned data '\
              'to as the third argument. \n\nExample: python process_data.py '\
              'disaster_messages.csv disaster_categories.csv '\
              'DisasterResponse.db')


if __name__ == '__main__':
    main()
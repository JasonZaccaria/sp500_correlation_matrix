import pandas as pd
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import seaborn as sns
import yfinance as yf
 
 
class correlation_matrix:
   
    def __init__(self):
        self.corr_sorted = None
 
    def scrape_wiki(self):
        self.url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        self.table_id = 'constituents'
        self.response = requests.get(self.url)
        self.soup = BeautifulSoup(self.response.text, 'html.parser')
        self.soup_find = self.soup.find('table', attrs={'id': self.table_id})
        self.df = pd.read_html(str(self.soup_find))[0]
        self.df = self.df['Symbol'].str.replace('\.', '-', regex=True)
        return self.df
 
    def scrape_yahoo(self):
        self.df_tickers = correlation_matrix.scrape_wiki(self)
        self.download_yahoo = pd.DataFrame()
        self.df_append = pd.DataFrame()
        for i in self.df_tickers:
            self.download_yahoo = yf.download(
                i, period='1y')['Adj Close'].pct_change()
            self.df_append[i] = self.download_yahoo
        self.df_append.to_csv('sp500_pct_change.csv', na_rep='NaN')
       
    def correlation(self):
        self.df_sp500 = pd.read_csv('sp500_pct_change.csv')
        self.corr = self.df_sp500.corr()
        self.corr.to_csv('correlation_matrix.csv')
        self.corr_unstack = self.corr.unstack()
        self.corr_sorted = self.corr_unstack.sort_values(ascending=True)
        self.corr_sorted = self.corr_sorted.drop_duplicates(keep='last')
        return self.corr_sorted
 
    def high_corr_negative(self):
        self.corr_max_negative_head = self.corr_sorted.head(10)
        self.corr_max_negative_df = self.corr_max_negative_head.to_frame()
        self.corr_max_negative_reset_index = (
            self.corr_max_negative_df.reset_index())
        self.corr_max_negative_reset_index['corr_pairs'] = (
            self.corr_max_negative_reset_index['level_0'] +
            '/' + self.corr_max_negative_reset_index['level_1'])
        self.corr_max_negative_rename = (
            self.corr_max_negative_reset_index.rename(
                columns={0: 'high_negative'}))
        self.corr_max_negative = self.corr_max_negative_rename.drop(
            ['level_0', 'level_1'], axis=1)
        print(self.corr_max_negative)
        return self.corr_max_negative
 
    def high_corr_positive(self):
        self.corr_max_positive_under_1 = self.corr_sorted[self.corr_sorted < 1]
        self.corr_max_positive_tail = self.corr_max_positive_under_1.tail(10)
        self.corr_max_positive_df = self.corr_max_positive_tail.to_frame()
        self.corr_max_positive_reset_index = (
            self.corr_max_positive_df.reset_index())
        self.corr_max_positive_reset_index['corr_pairs'] = (
            self.corr_max_positive_reset_index['level_0'] +
            '/' + self.corr_max_positive_reset_index['level_1'])
        self.corr_max_positive_rename = (
            self.corr_max_positive_reset_index.rename(
                columns={0: 'high_positive'}))
        self.corr_max_positive = self.corr_max_positive_rename.drop(
            ['level_0', 'level_1'], axis=1)
        print(self.corr_max_positive)
        return self.corr_max_positive
 
    def min_corr(self):
        self.corr_concat = pd.DataFrame()
        self.corr_sorted_df = self.corr_sorted.to_frame()
        self.corr_lower = self.corr_sorted_df[self.corr_sorted_df[0] < 0]
        self.corr_higher = self.corr_sorted_df[self.corr_sorted_df[0] > 0]
        self.corr_lower_tail = self.corr_lower.tail()
        self.corr_higher_head = self.corr_higher.head()
        self.corr_higher_reset_index = self.corr_higher_head.reset_index()
        self.corr_lower_reset_index = self.corr_lower_tail.reset_index()
        self.corr_lower_reset_index['indexes'] = (
            self.corr_lower_reset_index['level_0'] +
            '/' + self.corr_lower_reset_index['level_1'])
        self.corr_higher_reset_index['indexes'] = (
            self.corr_higher_reset_index['level_0'] +
            '/' + self.corr_higher_reset_index['level_1'])
        self.corr_list = [self.corr_higher_reset_index,
                          self.corr_lower_reset_index]
        self.corr_concat = pd.concat(self.corr_list)
        self.corr_concat_set_index = self.corr_concat.set_index('indexes')
        self.corr_concat_sorted = self.corr_concat_set_index.sort_values(0)
        self.corr_min = pd.DataFrame()
        self.corr_min['min_corr'] = self.corr_concat_sorted[0]
        self.corr_min = self.corr_min.reset_index()
        print(self.corr_min)
        return self.corr_min
       
    def plot_corr_positive(self):
        correlation_matrix.high_corr_positive(self)
        sns.barplot(x= self.corr_max_positive['corr_pairs'],
                    y= self.corr_max_positive['high_positive'])
        plt.show()
 
    def plot_corr_negative(self):
        correlation_matrix.high_corr_negative(self)
        sns.barplot(x= self.corr_max_negative['corr_pairs'],
                    y= self.corr_max_negative['high_negative'])
        plt.show()
 
    def plot_corr_min(self):
        correlation_matrix.min_corr(self)
        sns.barplot(x= self.corr_min['indexes'], y= self.corr_min['min_corr'])
        plt.show()
       
 
    def plot_corr_heatmap(self):
        correlation_matrix.correlation(self)
        sns.heatmap(self.corr, xticklabels=True, yticklabels=True)
        plt.show()
 
    def plot_high_positive_bubble(self):
        correlation_matrix.high_corr_positive(self)
        sns.scatterplot(x= self.corr_max_positive['corr_pairs'],
                        y= self.corr_max_positive['high_positive'],
                        size= self.corr_max_positive['high_positive'],
                        sizes= (20, 500) )
        plt.show()
 
    def plot_high_negative_bubble(self):
        correlation_matrix.high_corr_negative(self)
        sns.scatterplot(x= self.corr_max_negative['corr_pairs'],
                        y= self.corr_max_negative['high_negative'],
                        size= self.corr_max_negative['high_negative'],
                        sizes= (20, 500))
        plt.show()
 
    def plot_corr_min_bubble(self):
        correlation_matrix.min_corr(self)
        sns.scatterplot(x= self.corr_min['indexes'],
                        y= self.corr_min['min_corr'],
                        size= self.corr_min['min_corr'],
                        sizes= (20, 500))
        plt.show()
 
test_variable = correlation_matrix()
test_variable.scrape_yahoo()
test_variable.correlation()
#test_variable.high_corr_negative()
#test_variable.high_corr_positive()
#test_variable.min_corr()
#test_variable.plot_corr_positive()
#test_variable.plot_corr_negative()
#test_variable.plot_corr_min()
#test_variable.plot_corr_heatmap()
#test_variable.plot_high_positive_bubble()
#test_variable.plot_high_negative_bubble()
#test_variable.plot_corr_min_bubble()
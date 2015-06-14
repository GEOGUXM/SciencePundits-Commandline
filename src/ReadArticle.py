from newspaper import Article

def extract_summary(article_url):
	#article_url = raw_input('Please enter the url of the newsarticle \n')
	article_obj = Article(article_url)
	article_obj.download() 
	article_obj.parse() 
	article_obj.nlp() 
	article_summary = article_obj.summary
	return article_summary

def extract_keywords(article_url):
	#article_url = raw_input('Please enter the url of the newsarticle \n')
	article_obj = Article(article_url)
	article_obj.download() 
	article_obj.parse() 
	article_obj.nlp() 
	article_keywords = article_obj.keywords
	return article_keywords
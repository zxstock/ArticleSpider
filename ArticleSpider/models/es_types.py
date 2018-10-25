
from datetime import datetime

from elasticsearch_dsl import DocType, Date, Nested, Boolean, \
    analyzer, Completion, Keyword, Text, Integer

from elasticsearch_dsl.analysis import CustomAnalyzer as _CustomAnalyzer
#new version of dsl replace DocType with Document with new version of ElasticSearch

#from elasticsearch_dsl.connections import connections
#connections.create_connection(host=['localhost'])

class CustomAnalyzer(_CustomAnalyzer):
    def get_analysis_definition(self):
        return {}

ik_analyzer = CustomAnalyzer('ik_max_word', filter = ['lowercase'])  # change all to lower case


class ArticleType(DocType):
    #boleonline type
    suggest = Completion(analyzer=ik_analyzer)  # use elasticsearch_dsl error analyzer='ik_max_word' will be error
    title = Text(analyzer='ik_max_word') # parent index cannot have same title
    create_date = Date()
    url = Keyword()
    url_object_id = Keyword()  #md5 for long url
    front_image_url = Keyword()
    front_image_path = Keyword()  #upgrade in pipiline and settings
    praise_nums = Integer()
    comment_nums = Integer()
    fav_nums = Integer()
    tags = Text(analyzer='ik_max_word')
    content = Text(analyzer='ik_max_word')

    class Meta:
        index = 'jobbole'
        doc_type = 'article'

from elasticsearch_dsl.connections import connections
connections.create_connection(hosts=['localhost'])

if __name__ == "__main__":
    ArticleType.init()

####Must Initialize this py first to generate the structure of elasticsearch

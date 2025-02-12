from typing import Union
from pathlib import Path
import json
from src.data import DATA_DIR
from loguru import logger
from hazm import word_tokenize,Normalizer,sent_tokenize
import arabic_reshaper
from bidi.algorithm import get_display
from wordcloud import WordCloud
from collections import Counter,defaultdict
from src.utils.io import read_file,read_json


class ChatStatistics:
    """Generates chat statistics from a telegram chat json file
    """
    #load chat data
    
    def __init__(self,chat_json: Union[str,Path]):
        """param chat_json: path to telegram export json file 
        """
        logger.info(f"loading chat data from {chat_json}")
        
        self.chat_json = read_json(Path(chat_json))
        self.normalizer  = Normalizer() 
        #load stop words 
        logger.info(f"loading stop wrods from {DATA_DIR  / 'stopwords.txt'}")  
        stop_words = read_file(DATA_DIR / 'stop_words.txt')
        stop_words = list(map(str.strip, stop_words))
        self.stop_words = set(map(self.normalizer.normalize,stop_words))    
    @staticmethod
    def rebuild_msg(sub_messages):
        msg_text = ''
        for sub_msg in sub_messages:
            if isinstance(sub_msg, str):
                msg_text += sub_msg 
            elif 'text' in sub_msg:
                msg_text += sub_msg['text']
        return msg_text         
    def msg_has_question(self,msg): 
        """Checks if a message has a question
        """
        if not isinstance(msg['text'],str):
            msg['text'] = self.rebuild_msg(msg['text'])
            sentences = sent_tokenize(msg["text"])
            for sentence in sentences:
                if('?' not in sentence) and ('؟' not in sentence):
                    continue 
                return True

    def get_top_users(self, top_n:int = 10):
        #chack messages for question
        is_question = defaultdict(bool)
        for msg in self.chat_json['messages']:
            if not  isinstance(msg['text'],str):
                msg['text'] = self.rebuild_msg(msg['text'])
            sentences = sent_tokenize(msg["text"])
            for sentence in sentences:
                if('?' not in sentence) and ('؟' not in sentence):
                    continue 
                
                is_question[msg['id']] = True
                break
    
        logger.info("Getting top users...")
        users = []
        for msg in self.chat_json["messages"]:
            if not msg.get('reply_to_message_id'):
                continue
            #users[msg['from_id']].append(msg["reply_to_message_id"])   
            if not is_question[msg["reply_to_message_id"]] is False:
                continue
            users.append(msg["from"])    
        return dict(Counter(users).most_common(10))
    def generate_word_cloud(self,output_dir):
        """Generats word cloud of the chat data
        param output_dir: path to output directory for word cloud image
        """
        logger.info("loading text content")
        text_content = ''
        for msg in self.chat_json["messages"]:
            if type(msg["text"]) is str:
                tokens = word_tokenize(msg['text'])
                tokens = filter(lambda item: item not in self.stop_words,tokens)
                text_content += f" {' '.join(tokens)}"
        #normalize, reshape for final word cloud
        text_content = self.normalizer.normalize(text_content)
        text_content = arabic_reshaper.reshape(text_content)
        logger.info("Generating word cloud...")
        wordcloud = WordCloud(font_path= DATA_DIR / 'BHoma.ttf',
                              background_color = "white"
                              ).generate(text_content)
        logger.info(f"Saving word cloud to {output_dir}")
        wordcloud.to_file(Path(output_dir) / "wordcloud.png")
if __name__ == "__main__":
    chat_stats = ChatStatistics(chat_json=DATA_DIR / 'result.json')
    chat_stats.generate_word_cloud(output_dir=DATA_DIR)
    top_users = chat_stats.get_top_users(top_n=10)
    print(top_users)
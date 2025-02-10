from typing import Union
from pathlib import Path
import json
from src.data import DATA_DIR
from loguru import logger
from hazm import word_tokenize,Normalizer,normalizer
import arabic_reshaper
from bidi.algorithm import get_display
from wordcloud import WordCloud



class ChatStatistics:
    """Generates chat statistics from a telegram chat json file
    """
    #load chat data
    
    def __init__(self,chat_json: Union[str,Path]):
        """param chat_json: path to telegram export json file 
        """
        logger.info(f"loading chat data from {chat_json}")
        with open(Path(chat_json)) as f:
            self.chat_json = json.load(f)
        self.normalizer  = Normalizer() 
        #load stop words 
        logger.info(f"loading stop wrods from {DATA_DIR  / 'stopwords.txt'}")  
        stop_words = open(DATA_DIR / 'stop_words.txt').readlines()
        stop_words = list(map(str.strip, stop_words))
        self.stop_words = list(map(self.normalizer.normalize,stop_words))    

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

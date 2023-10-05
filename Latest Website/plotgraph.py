from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import yaml
import openai

with open('config.yaml', 'r') as config_file:
    config = yaml.safe_load(config_file)
temperature = config['LLM_Model']['temperature']

class PlotGraph:
    def __init__ (self,api_key):
        openai.api_key = api_key
        self.chatGPT = ChatOpenAI(temperature=temperature)
        self.template_string = """for the following text \
                                that is delimited by triple backticks \
                                you have to generate chart graph on the base of provided information \
                                into a javascript code \
                                in javascript code you have to add these elements  \
                                // Creating the chart \
                                const chart = document.createElement("canvas"); \
                                chart.id = "chart"; \
                                document.getElementById("chart-div").appendChild(chart); \

                                only write javascript not not others like css,html etc \

                                text: ```{text}```
                                if no information include to plot a graph say sorry not much information to plot! \
                                
                            """
        self.prompt_template = ChatPromptTemplate.from_template(self.template_string)
    def generate_plot(self,response_for_plot):
        self.gpt_messages = self.prompt_template.format_messages(
                    text=response_for_plot)
        self.result = self.chatGPT(self.gpt_messages)
        
        return self.result.content
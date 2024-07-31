from diagrams import Diagram, Cluster, Edge
from diagrams.azure.database import SQLServers
from diagrams.azure.ml import CognitiveServices
from diagrams.programming.language import Python
from diagrams.gcp.ml import SpeechToText, TextToSpeech
from diagrams.azure.general import Usericon
from diagrams.elastic.beats import Filebeat

with Diagram("NLP to SQL Architecture", show=False):
    stt = SpeechToText("Speech to Text")
    tts = TextToSpeech("Text to Speech")
    sql_server = SQLServers("SQL Server")
    open_ai = CognitiveServices("OpenAI")

    with Cluster("Orchestrator"):
        orchestrator = Python("Orchestrator")
        with Cluster("Semantic Kernel"):
            semantic_kernel = Python("Semantic Kernel")
            chat_completion = Filebeat("Chat Completion")

            with Cluster("Plugins"):
                query_db = Python("Query DB")
                nlp_to_sql = Filebeat("NLP to SQL")

            semantic_kernel >> Edge(label="interact with chat") << chat_completion
            semantic_kernel >> Edge(label="use translated SQL on the database") << query_db
            semantic_kernel >> Edge(label="translate query to SQL") << nlp_to_sql
            query_db >> Edge() << sql_server
            chat_completion >> Edge() << open_ai
            nlp_to_sql >> Edge() << open_ai

        orchestrator >> Edge() << stt
        orchestrator >> Edge() << tts
        orchestrator >> Edge() << semantic_kernel

    Usericon() >> Edge(label="voice request/response") << orchestrator

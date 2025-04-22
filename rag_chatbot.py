import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_pinecone import PineconeVectorStore
from langchain_cohere import CohereEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from pinecone import Pinecone
from guardrails import Guard
from guardrails.hub import (
    ResponseEvaluator,
    CompetitorCheck,
    ToxicLanguage
)

# Load environment variables
load_dotenv()

# Set up logging
def setup_logging():
    """Setup logging configuration"""
    log_dir = os.getenv("LOG_DIR", "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_filename = f"chatbot_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    logging.basicConfig(
        filename=log_filename,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger('Nova')

def create_guardrails():
    """Create output guards for the chatbot"""
    output_guard = Guard().use_many(
        ResponseEvaluator(
            prompt_questions=[
                "Does the response provide complete and detailed information?",
                "Is the response engaging and conversational?",
                "Does it maintain a friendly and helpful tone?",
                "Are all parts of the question addressed thoroughly?"
            ]
        ),
        CompetitorCheck(
            competitors=[
                "competitor1", "competitor2"  # Add your actual competitors
            ],
            on_fail="filter"
        ),
        ToxicLanguage(
            threshold=0.7,
            validation_method="sentence",
            on_fail="filter"
        )
    )
    return output_guard

def initialize_pinecone():
    """Initialize Pinecone and return the vector store"""
    try:
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))
        
        embeddings = CohereEmbeddings(
            model="embed-english-v3.0",
            cohere_api_key=os.getenv("COHERE_API_KEY")
        )
        
        vector_store = PineconeVectorStore(
            index=index,
            embedding=embeddings,
            text_key="text"
        )
        return vector_store
    except Exception as e:
        raise e

def create_qa_chain(vector_store):
    """Create the QA chain with custom prompt"""
    prompt = PromptTemplate(
        template="""You are Nova, a friendly and engaging AI assistant. You're knowledgeable about the company and genuinely interested in helping people. Your responses should be thorough and warm, while maintaining professionalism.

Context information: {context}

Question: {question}

Previous chat: {chat_history}

Guidelines for your response:
- Start with a brief, natural acknowledgment (mix it up each time).
- Answer the question directly—stick to the point.
- Keep it short: 2–3 sentences or under ~60 words.
- Use a casual, friendly tone suited for quick chat.
- If unsure, say “I’m not sure, but here’s what I know…”
- End with a quick offer to help them

Remember to:
- Focus only on the user’s question and relevant company info.
- Use simple, clear language.
- Be upbeat and genuinely helpful.
- Vary your style—avoid repeating the same phrases.

Response:""",
        input_variables=["context", "question", "chat_history"]
    )

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.7
    )
    
    memory = ConversationBufferWindowMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="answer",
        k=5
    )
    
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vector_store.as_retriever(search_kwargs={"k": 5}),
        memory=memory,
        combine_docs_chain_kwargs={"prompt": prompt},
        return_source_documents=False,
        verbose=False
    )
    return qa_chain

def main():
    # Setup logging
    logger = setup_logging()
    logger.info("Starting Nova chatbot")
    
    print("\n👋 Hi! I'm Nova, your friendly AI assistant. I'm here to help you with any questions you have about our company. Feel free to ask anything, and I'll do my best to provide thorough and helpful information!")
    print("(Type 'exit' or 'quit' to end our chat)\n")
    
    try:
        vector_store = initialize_pinecone()
        qa_chain = create_qa_chain(vector_store)
        output_guard = create_guardrails()
        logger.info("Successfully initialized all components")

        while True:
            try:
                user_input = input("You: ").strip()
                logger.info(f"User Input: {user_input}")

                if user_input.lower() in ("exit", "quit"):
                    print("\nNova: Bye! Take care! 👋")
                    logger.info("Chat session ended by user")
                    break

                if not user_input:
                    continue

                # Get response from the chain
                result = qa_chain.invoke({"question": user_input})
                logger.info(f"Raw Response: {result['answer']}")
                
                # Validate output
                try:
                    validated_response = output_guard.validate(result['answer'])
                    logger.info(f"Validated Response: {validated_response}")
                    print(f"Nova: {validated_response}\n")
                except Exception as e:
                    logger.warning(f"Validation failed: {str(e)}")
                    print(f"Nova: {result['answer']}\n")
                
            except Exception as e:
                logger.error(f"Error in conversation loop: {str(e)}")
                print("Nova: Sorry, could you try asking that again?\n")

    except Exception as e:
        logger.error(f"Critical error: {str(e)}")
        print("Nova: I'm having trouble starting up. Please try again later.")

if __name__ == "__main__":
    main() 
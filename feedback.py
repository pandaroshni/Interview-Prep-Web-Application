import os
import streamlit as st
from groq import Groq
import random

# Set the environment variable for the API key
os.environ["GROQ_API_KEY"] = "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"

# Initialize Groq client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Predefined random questions about ML, SQL, or Python
random_questions = [
    "What is overfitting in machine learning?",
    "Explain the difference between supervised and unsupervised learning.",
    "What is a JOIN operation in SQL?",
    "How do you handle missing values in a dataset?",
    "What is the purpose of the 'self' keyword in Python?",
    "What is the difference between a list and a tuple in Python?",
    "Can you explain what a confusion matrix is?",
    "What is the use of the 'GROUP BY' clause in SQL?",
]

# Function to generate the next question based on the user's previous answer
def ask_next_question(conversation_history):
    prompt = (
        "You are conducting an interview. Ask a single follow-up question based on the candidate's previous answer. "
        "Make sure to only ask one clear, concise question at a time."
    )
    conversation_history.append({"role": "system", "content": prompt})

    completion = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=conversation_history,
        temperature=0.7,
        max_tokens=100,
        top_p=0.9
    )

    response_text = completion.choices[0].message.content.strip()
    return response_text, conversation_history

# Function to provide feedback based on user answers
def provide_feedback(question, user_answer):
    feedback_prompt = (
        f"Evaluate the following answer to the interview question: '{question}'.\n"
        f"Answer: '{user_answer}'.\n"
        "Please provide detailed constructive feedback on this answer, including:\n"
        "1. Strengths of the answer with specific examples if applicable.\n"
        "2. Weaknesses of the answer, detailing why they are weaknesses.\n"
        "3. Suggestions for improvement, including at least two specific steps the candidate could take to enhance their knowledge and answer quality.\n"
        "Make sure your feedback is complete, actionable, and educational."
    )

    try:
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": feedback_prompt}],
            temperature=0.5,
            max_tokens=200,
            top_p=0.9
        )

        feedback_text = completion.choices[0].message.content.strip()
    except Exception as e:
        feedback_text = f"An error occurred while generating feedback: {str(e)}"

    return feedback_text

# Streamlit App
def interview_app():
    st.set_page_config(page_title="Skill Mitra", page_icon=":robot_face:", layout="wide")
    st.title("Skill Mitra - Mock Interview App")
    st.markdown("<style>h1 {color: #4CAF50; text-align: center; font-size: 40px;}</style>", unsafe_allow_html=True)
    st.markdown("<style>h2 {color: #333; text-align: center;}</style>", unsafe_allow_html=True)

    # Initialize session states
    if "question_index" not in st.session_state:
        st.session_state.question_index = 0

    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = [{"role": "system", "content": "You are an interviewer."}]

    if "questions" not in st.session_state:
        st.session_state.questions = ["Introduce yourself"]  # Start with the first question

    if "user_answers" not in st.session_state:
        st.session_state.user_answers = []

    # Initialize show_feedback state
    if "show_feedback" not in st.session_state:
        st.session_state.show_feedback = False

    # Logic for displaying questions
    if st.session_state.question_index < 3:  # First 3 questions based on user response
        current_question = st.session_state.questions[st.session_state.question_index]
    elif st.session_state.question_index < 5:  # Next 2 questions are random
        if st.session_state.question_index == 3:
            # Add 2 random questions when reaching the 4th question
            for _ in range(2):
                random_question = random.choice(random_questions)
                st.session_state.questions.append(random_question)
        current_question = st.session_state.questions[st.session_state.question_index]
    else:
        # Interview completed: Provide feedback
        st.session_state.show_feedback = True  # Set feedback flag to True

        # Provide feedback for each answer using the feedback function
        st.write("Interview completed! Thank you.")

        # Show feedback only after all questions are answered
        for i, (question, answer) in enumerate(zip(st.session_state.questions, st.session_state.user_answers)):
            feedback_text = provide_feedback(question, answer)
            st.write(f"**Question {i + 1}:** {question}")
            st.write(f"**Your Answer:** {answer}")
            st.write(f"**Feedback:** {feedback_text}")

        # Restart button
        if st.button("Restart Interview"):
            st.session_state.question_index = 0
            st.session_state.conversation_history = [{"role": "system", "content": "You are an interviewer."}]
            st.session_state.questions = ["Introduce yourself"]
            st.session_state.user_answers = []
            st.session_state.show_feedback = False  # Reset feedback display
            return  # Stop further execution

        return  # Stop further execution if the interview is completed

    # Set CSS style for reduced font size
    st.markdown("<style>h3 { font-size: 20px; }</style>", unsafe_allow_html=True)

    # Show question only if not completed
    if not st.session_state.show_feedback:
        st.subheader(f"Question {st.session_state.question_index + 1}: {current_question}")

        # JavaScript to manage TTS
        tts_script = f"""
        <script type="text/javascript">
            var synth = window.speechSynthesis;
            var utterThis = new SpeechSynthesisUtterance("{current_question}");
            utterThis.lang = 'en-US';
            synth.cancel(); // Cancel any ongoing speech before starting new
            synth.speak(utterThis);
            
            // Stop speech when the user submits the answer
            document.getElementById('submit_answer').onclick = function() {{
                synth.cancel(); // Stop TTS when answering
            }}; 
        </script>
        """
        # Embed TTS JavaScript in the app after displaying the question
        st.components.v1.html(tts_script, height=0, width=0)

        # Input field for user's answer
        user_answer = st.text_input("Your answer:", key=f"answer_{st.session_state.question_index}")

        # Submit button
        if st.button("Submit Answer", key='submit_answer'):
            if user_answer:
                # Store user answer and proceed
                st.session_state.user_answers.append(user_answer)

                # Update conversation history with the user's answer
                st.session_state.conversation_history.append({"role": "user", "content": user_answer})

                # Generate the next question
                next_question, st.session_state.conversation_history = ask_next_question(
                    st.session_state.conversation_history
                )
                st.session_state.questions.append(next_question)
                st.session_state.question_index += 1

            else:
                st.write("Please provide an answer before submitting.")

if __name__ == "__main__":
    interview_app()

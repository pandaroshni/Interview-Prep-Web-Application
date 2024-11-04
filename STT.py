import os
import streamlit as st
from groq import Groq
import random
import speech_recognition as sr

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

# Initialize the Speech Recognizer
recognizer = sr.Recognizer()

# Function to record audio and convert it to text
def record_audio():
    with sr.Microphone() as source:
        st.write("Recording... Please speak your answer.")
        audio = recognizer.listen(source)
        st.write("Recording stopped.")
        
        try:
            # Recognize speech using Google Web Speech API
            text = recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            st.error("Sorry, I could not understand the audio.")
            return None
        except sr.RequestError:
            st.error("Could not request results from the speech recognition service.")
            return None

# Function to generate the next question based on the user's previous answer
def ask_next_question(conversation_history):
    prompt = (
        "You are conducting an interview for machine learning roles. Ask a single follow-up question based on the candidate's answer. "
        "Start fresh each time with a new question and do not reference previous sessions."
    )
    conversation_history.append({"role": "system", "content": prompt})

    completion = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=conversation_history,
        temperature=0.7,
        max_tokens=50,
        top_p=0.9
    )

    response_text = completion.choices[0].message.content.strip()
    return response_text, conversation_history

# Function to provide feedback based on user answers
def provide_feedback(user_answers):
    feedback = []
    for answer in user_answers:
        if len(answer) < 10:
            feedback.append("Your answer is too short. Try to provide more detail.")
        elif len(answer) > 100:
            feedback.append("Your answer is quite lengthy. Try to be more concise.")
        else:
            feedback.append("Good job! Your answer is well-structured.")
    return feedback

# Streamlit App
def interview_app():
    st.set_page_config(page_title="Skill Mitra", page_icon=":robot_face:", layout="wide")
    st.title("Skill Mitra - Mock Interview App")
    st.markdown("<style>h1 {color: #4CAF50; text-align: center; font-size: 40px;}</style>", unsafe_allow_html=True)
    st.markdown("<style>h2 {color: #333; text-align: center;}</style>", unsafe_allow_html=True)
    
    # Session states to track questions, answers, and conversation history
    if "question_index" not in st.session_state:
        st.session_state.question_index = 0

    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = [{"role": "system", "content": "You are an interviewer."}]

    if "questions" not in st.session_state:
        st.session_state.questions = ["Introduce yourself"]  # Start with the first question

    if "user_answers" not in st.session_state:
        st.session_state.user_answers = []

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
        st.write("Interview completed! Thank you.")

        # Provide feedback for each answer
        feedback = provide_feedback(st.session_state.user_answers)
        for i, (question, answer, feedback_text) in enumerate(zip(st.session_state.questions, st.session_state.user_answers, feedback)):
            st.write(f"**Question {i + 1}:** {question}")
            st.write(f"**Your Answer:** {answer}")
            st.write(f"**Feedback:** {feedback_text}")

        # Restart button
        if st.button("Restart Interview"):
            st.session_state.question_index = 0
            st.session_state.conversation_history = [{"role": "system", "content": "You are an interviewer."}]
            st.session_state.questions = ["Introduce yourself"]
            st.session_state.user_answers = []
            st.session_state.is_recording = False  # Reset recording state
            return  # Stop further execution

        return  # Stop further execution if the interview is completed

    # Set CSS style for reduced font size
    st.markdown("<style>h3 { font-size: 20px; }</style>", unsafe_allow_html=True)
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

    # Manage recording state
    if "is_recording" not in st.session_state:
        st.session_state.is_recording = False  # To track recording state
        st.session_state.current_answer = ""  # To store current answer

    # Start/Stop Recording Button
    if st.button("Start/Stop Recording"):
        if not st.session_state.is_recording:  # If not recording, start recording
            st.session_state.is_recording = True
            st.session_state.current_answer = record_audio()  # Record audio when button is clicked
        else:  # If recording, stop recording
            st.session_state.is_recording = False
            st.write("Recording stopped. Please click 'Submit Answer' to proceed.")

    # Submit button
    if st.button("Submit Answer", key='submit_answer'):
        if st.session_state.current_answer:  # Only proceed if there's a recorded answer
            st.session_state.user_answers.append(st.session_state.current_answer)  # Store the answer
            st.session_state.conversation_history.append({"role": "user", "content": st.session_state.current_answer})  # Update conversation history

            # Generate the next question
            next_question, st.session_state.conversation_history = ask_next_question(st.session_state.conversation_history)
            st.session_state.questions.append(next_question)
            st.session_state.question_index += 1

            # Reset for the next question
            st.session_state.current_answer = ""  # Reset current answer after submission
            st.session_state.is_recording = False  # Reset recording state

        else:
            st.write("Please speak your answer by clicking the 'Start/Stop Recording' button.")

if __name__ == "__main__":
    interview_app()

from dotenv import load_dotenv
import streamlit as st
import speech_recognition as sr
import pyttsx3
import time
import openai
import os 
# Initialize Text-to-Speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Speech rate

# OpenAI API Key
load_dotenv()

# Define constants
CONVERSATION_DURATION = 120  # Conversation lasts for 2 minutes

# Streamlit interface
st.title("ADC Exam Simulation")

adc_criteria = st.text_area("Enter the ADC assessment criteria:", "The student should demonstrate clear communication, accurate diagnosis, and appropriate patient management.")
scenario_text = st.text_area("Enter the dental medical scenario for the patient:", "A patient presents with severe toothache in the lower right molar region.")

openai.api_key = os.getenv('OPENAI_API_KEY')

def generate_response(prompt, model="gpt-4", max_tokens=100):
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful medical assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=max_tokens,
        temperature=0.7,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )
    return response['choices'][0]['message']['content'].strip()


if st.button("Start Simulation"):
    if not adc_criteria.strip():
        st.error("Please provide the ADC assessment criteria before starting the simulation.")
    else:
        # Start conversation
        st.info("Simulation started! Speak to the patient.")

        recognizer = sr.Recognizer()
        mic = sr.Microphone()
        start_time = time.time()
        conversation_log = []

        try:
            while time.time() - start_time < CONVERSATION_DURATION:
                with mic as source:
                    recognizer.adjust_for_ambient_noise(source)
                    st.write("Listening...")
                    audio = recognizer.listen(source, timeout=5)

                try:
                    # Convert speech to text
                    student_input = recognizer.recognize_google(audio)
                    st.write(f"You: {student_input}")

                    # Generate patient response using GPT-4
                    prompt = f"Scenario: {scenario_text}\nStudent: {student_input}\nPatient:"
                    patient_response = generate_response(prompt)
                    st.write(f"Patient: {patient_response}")

                    # Speak the response
                    engine.say(patient_response)
                    engine.runAndWait()

                    # Log the conversation
                    conversation_log.append({"Student": student_input, "Patient": patient_response})

                except sr.UnknownValueError:
                    st.warning("Could not understand the audio. Please try again.")
                except sr.RequestError as e:
                    st.error(f"Could not request results from the speech recognition service; {e}")

        except KeyboardInterrupt:
            st.warning("Simulation interrupted.")

        # Assess conversation using GPT-4
        st.info("Assessing the conversation...")
        conversation_text = "\n".join([f"Student: {log['Student']}\nPatient: {log['Patient']}" for log in conversation_log])
        assessment_prompt = f"ADC Criteria: {adc_criteria}\nConversation: {conversation_text}\nAssessment:"
        assessment_feedback = generate_response(assessment_prompt, max_tokens=300)

        st.subheader("Feedback")
        st.write(assessment_feedback)

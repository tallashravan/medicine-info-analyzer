import streamlit as st
from phi.agent import Agent
from phi.model.google import Gemini
from dotenv import load_dotenv
from phi.tools.tavily import TavilyTools
from prompts import INSTRUCTIONS, SYSTEM_PROMPT
import os
from PIL import Image
import io
import csv
import re
import html

# Load Environment Variables
load_dotenv()

# Set API Keys
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

# Initialize Tavily Agent
tavily_agent = Agent(
    name="tavily",
    instructions=INSTRUCTIONS,
    model=Gemini(id="gemini-2.0-flash-exp"),
    tools=[TavilyTools()],
    markdown=True,
    system_prompt=SYSTEM_PROMPT
)

# Streamlit Page Configuration
st.set_page_config(
    page_title="AI Medicine Analyzer",
    page_icon="💊",
    layout="wide",
)

# App Title and Description
st.title("💊 AI Medicine Analyzer")
st.header("Simplifying Medicine Insights with AI")
st.write(
    "Upload an image of your medicine label or prescription to get started. 📸  Want to see it in action? Explore Example Images for a quick demo! 🖼️ Curious to know more? Check out the About tab for details. ℹ️"
)

# Tabs for Main Upload, Example Images, and About
tab1, tab2, tab3, tab4 = st.tabs(["Upload Image", "Example Images", "About", "Feedback"])

### --- TAB 1: UPLOAD IMAGE ---
with tab1:
    st.header("Upload Image")
    uploaded_file = st.file_uploader("Upload a Medicine or Prescription Image", type=["png", "jpg", "jpeg"])

    # Function to analyze the image
    def analyze_medicine(image_bytes):
        temp_image_path = "temp_image.jpg"
        try:
            # Save Image Temporarily
            with open(temp_image_path, "wb") as f:
                f.write(image_bytes)

            # Analyze Image with Tavily Agent
            response = tavily_agent.run(
                "Analyze the medicine composition image",
                images=[temp_image_path]
            )
            return response.content
        except FileNotFoundError as e:
            st.error(f"File not found: {str(e)}")
            return "An error occurred while analyzing the image. Please try again later."
        except IOError as e:
            st.error(f"IO error: {str(e)}")
            return "An error occurred while analyzing the image. Please try again later."
        except Exception as e:
            st.error(f"An unexpected error occurred: {str(e)}")
            return "An error occurred while analyzing the image. Please try again later."
        finally:
            try:
                if os.path.exists(temp_image_path):
                    os.remove(temp_image_path)
            except Exception as e:
                st.error(f"An error occurred while deleting the temporary file: {str(e)}")

    # Handle Image Upload
    image_bytes = io.BytesIO()
    if uploaded_file:
        try:
            st.image(uploaded_file, caption="Uploaded Image", width=300)
            image = Image.open(uploaded_file)
            image_bytes = io.BytesIO()
            image = image.convert('RGB')
            image.save(image_bytes, format='JPEG')
            image_bytes = image_bytes.getvalue()
        except IOError as e:
            st.error(f"Error opening image file: {str(e)}")
            image_bytes = None

    if st.button("Analyze Uploaded Image"):
        with st.spinner("Analyzing... Please wait."):
            if uploaded_file and image_bytes:
                result = analyze_medicine(image_bytes)
                if result.startswith("Error"):
                    st.error(result)
                else:
                    with st.expander("Analysis Results", expanded=True):
                        st.success("Analysis Complete! Here are the details:")
                        st.markdown(result)
            elif not uploaded_file:
                st.error("Please upload an image to analyze.")
            else:
                st.error("Failed to process the uploaded image. Please try again.")
    else:
        st.info(
            """
            **Upload an image of the medicine label to get started. 📸**  
            - Want to see it in action? Explore **Example Images** for a quick demo! 🖼️  
            - Curious to know more? Check out the **About** tab for details. ℹ️  
            """
        )
    # Disclaimer
    st.warning("💡 **Disclaimer:** This analysis provided by the AI is for informational purposes only and is not intended as medical advice.  Always consult a qualified healthcare professional for medical guidance.")

### --- TAB 2: EXAMPLE IMAGES ---
with tab2:
    st.header("Example Images")
    example_images = {
        "Example 1": "images/benadryl.jpeg",
        "Example 2": "images/dolo.jpeg",
    }

    cols = st.columns(2)
    for idx, (label, image_path) in enumerate(example_images.items()):
        with cols[idx % 2]:
            st.image(image_path, caption=label, width=300)
            if st.button(f"Analyze {label}"):
                with open(image_path, "rb") as f:
                    image_bytes = f.read()
                with st.spinner("Analyzing... Please wait."):
                    result = analyze_medicine(image_bytes)
                    if result.startswith("Error"):
                        st.error(result)
                    else:
                        with st.expander(f"Analysis Results for {label}", expanded=True):
                            st.success("Analysis Complete! Here are the details:")
                            st.markdown(result)
    
    # Disclaimer
    st.warning("💡 **Disclaimer:** This analysis provided by the AI is for informational purposes only and is not intended as medical advice.  Always consult a qualified healthcare professional for medical guidance.")

### --- TAB 3: ABOUT ---
with tab3:
    st.header("About the AI Medicine Analyzer")
    
    # Add an introductory section with a clean, bold text
    st.markdown("""
    In today’s fast-paced world, understanding your prescribed medication shouldn’t be a hassle. We’ve all experienced the frustration of trying to look up complex medicine names, decipher their ingredients, and figure out how they work.  
    That's why I created this app — **AI Medicine Info Analyzer**, a **simple, efficient solution** for anyone looking for quick, reliable, and easy-to-understand information about medicines.
    """)
    
        
    # Add a section explaining how it works
    st.subheader("How It Works 🧠💊")
    st.write("""
    This web app allows users to **upload an image of their medicine or prescription label**, and **AI instantly analyzes** the content to provide detailed insights. It’s as simple as:
    1. **Upload your medicine label image** (either a photo or a scanned image of the label).
    2. **AI analyzes** the contents and extracts key information.
    3. Get detailed insights like:
        - **Uses and benefits** of the medicine
        - **Side effects and safety precautions**
        - **Ingredients** and how the medicine works
    
    Everything you need to know about your medicine, all in one place! 📚
    """)

    # Add a collapsible section to encourage interaction
    with st.expander("🔍 More Details on What the App Does"):
        st.write("""
        The AI Medicine Info Analyzer uses cutting-edge AI technology to analyze medicine labels and prescriptions. The app:
        - Extracts **medicinal ingredients** from images
        - Provides information about the **medicine's purpose** and potential side effects
        - Suggests **safety tips** and possible **precautions**
        - Helps users make **informed health decisions** quickly and efficiently
        
        Whether you're a parent trying to understand a prescription for your child, or just want to know more about the medicine you're taking, this tool is designed to make it **easy for everyone**.
        """)
    
    # Add a section with a call to action for feedback
    st.markdown("### We Value Your Feedback 💬")
    st.write("""
    This app is currently a **proof of concept**, and I am eager to gather **feedback** to improve it further. Your input is invaluable to help refine the app and add more features to make it even more useful.
    
    Feel free to **leave feedback** in the **Feedback** section of the app. Whether it’s suggestions, concerns, or any improvements you’d like to see, I’m here to listen and build a better tool for everyone.
    """)

    # Add a final note with a personal touch
    st.markdown("""
    **Thank you for using the AI Medicine Info Analyzer!** 🙏  
    Together, we can make understanding medication easier and more accessible for everyone. 😊
    """)

with tab4:
    st.header("💬 Share Your Feedback")
    st.write("We'd love to hear your thoughts about the app! 😊")

    # Function to sanitize user inputs
    def sanitize_input(input_text):
        # Escape HTML characters to prevent XSS attacks
        sanitized_text = html.escape(input_text)
        
        # Further validation for special characters or unwanted patterns (like SQL injection patterns)
        sanitized_text = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', sanitized_text)  # Remove control characters
        # Further validation for special characters or unwanted patterns (like SQL injection patterns)
        sanitized_text = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', sanitized_text)  # Remove control characters
        sanitized_text = re.sub(r'(--|;|\'|"|\\|\/|\*|=|<|>)', '', sanitized_text)  # Remove SQL injection patterns
        sanitized_text = re.sub(r'\b(SELECT|INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|REPLACE|RENAME|TRUNCATE|EXEC)\b', '', sanitized_text, flags=re.IGNORECASE)
        return sanitized_text

    # Save feedback to a CSV file
    def save_feedback(name, feedback, rating):
        feedback_file = "local_feedback/feedback.csv"
        
        # Ensure the directory exists
        if not os.path.exists("local_feedback"):
            os.makedirs("local_feedback")

        # Check if the file exists
        file_exists = os.path.exists(feedback_file)

        # Write feedback data
        try:
            with open(feedback_file, mode="a", newline="") as file:
                writer = csv.writer(file)
                if not file_exists:  # Write header if file is new
                    writer.writerow(["Name", "Feedback", "Rating"])
                writer.writerow([name, feedback, rating])
        except Exception as e:
            st.error(f"An error occurred while saving feedback: {str(e)}")

    # Create a feedback form
    with st.form(key="feedback_form"):
        name = st.text_input("Name (Optional):",max_chars=50)
        feedback = st.text_area("Your Feedback:",max_chars=100)
        rating = st.slider("Rate your experience (1 - Poor, 5 - Excellent):", 1, 5, 3)
        submit_button = st.form_submit_button(label="Submit Feedback")

        # Input validation and sanitization
        if submit_button is not None and submit_button:
            # Sanitize the feedback input
            sanitized_feedback = sanitize_input(feedback)
            sanitized_name = sanitize_input(name)  # Optional Name input

            # Validate feedback
            if not sanitized_feedback:
                st.warning("⚠️ Feedback cannot be empty. Please share your thoughts!")
            else:
                save_feedback(sanitized_name, sanitized_feedback, rating)
                st.success("🎉 Thank you for your feedback! 🙌")


### --- SUPPORT SECTION ---
st.markdown("---")
st.markdown(
    """
    ### 🌟 Liked the app?  
    Support this project by **giving it a star⭐ on GitHub**!  👉 https://github.com/tallashravan/medicine-info-analyzer  
    """
)
st.markdown("---")
st.markdown(
    """
    ### 🚀 Want to see more projects like this?  
    **Follow me on GitHub** to stay updated on my latest projects on GitHub**!  👉 https://github.com/tallashravan/
    """
)
st.markdown("---")
st.write("Made with ❤️ by [Shravan](https://github.com/tallashravan/)")
